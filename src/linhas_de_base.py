"""Linhas de base do benchmark: regressao logistica e XGBoost, em dois protocolos fixos.

  cv        validacao cruzada estratificada 5 vezes (semente 0); IC 95% do AUROC pela
            variancia entre dobras com a correcao de Nadeau e Bengio (k = 5, teste/treino = 1/4)
  temporal  treino nos periodos anteriores ao corte da tarefa, teste nos posteriores; IC 95% do
            AUROC por bootstrap (1.000 reamostragens do conjunto de teste)

    python src/linhas_de_base.py [tarefa ...]   -> resultados/linhas_de_base.csv
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import xgboost as xgb
from scipy import stats
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, roc_auc_score

import tarefas as T

RES = T.RAIZ / "resultados"
CATEGORICAS = {"raca", "escolaridade", "regiao", "estado_civil", "grupo_dx", "dx_cid", "uf"}
# corte temporal por tarefa: periodos >= corte vao para o teste
CORTE = {"sinan_tb_abandono": "2020", "sinan_lv_obito": "2012", "sivep_covid_obito": "2020-08", "sivep_covid_obito_pediatrico": "onda2_2021",
         "sivep_influenza_obito_2024": "2024-07", "sinasc_baixo_peso": "2023", "sinasc_baixo_peso_ao_nascer": "2023",
         "sih_obito_idoso_cardiovascular": "2012"}
XGB = {"objective": "binary:logistic", "eta": 0.05, "max_depth": 4, "min_child_weight": 5,
       "subsample": 0.8, "colsample_bytree": 0.8, "lambda": 1.0, "nthread": 4, "verbosity": 0, "seed": 0}


def _matriz_lr(X: pd.DataFrame, ref: pd.DataFrame) -> np.ndarray:
    """Logistica: categoricas em one-hot, faltante como categoria propria; numericas com
    imputacao pela mediana do treino e indicador de faltante; padronizacao pelo treino."""
    partes = []
    for c in X.columns:
        if c in CATEGORICAS:
            niveis = sorted(ref[c].dropna().unique())
            partes += [(X[c] == v).astype(float).to_numpy() for v in niveis[1:]]
            partes.append(X[c].isna().astype(float).to_numpy())
        else:
            med = ref[c].median()
            v = X[c].fillna(med if pd.notna(med) else 0.0).to_numpy(float)
            m, s = ref[c].mean(), ref[c].std()
            partes.append((v - (m if pd.notna(m) else 0)) / (s if s and pd.notna(s) and s > 0 else 1))
            if ref[c].isna().any():
                partes.append(X[c].isna().astype(float).to_numpy())
    return np.column_stack(partes)


def _xgb(Xtr, ytr, Xte):
    """XGBoost com numero de arvores escolhido em holdout interno de 20% (parada antecipada)."""
    rng = np.random.default_rng(0)
    idx = rng.permutation(len(ytr))
    corte = int(0.8 * len(idx))
    tr, va = idx[:corte], idx[corte:]
    dtr = xgb.DMatrix(Xtr[tr], label=ytr[tr])
    dva = xgb.DMatrix(Xtr[va], label=ytr[va])
    b = xgb.train({**XGB, "eval_metric": "logloss"}, dtr, 2000, evals=[(dva, "va")],
                  early_stopping_rounds=50, verbose_eval=False)
    n = b.best_iteration + 1
    final = xgb.train(XGB, xgb.DMatrix(Xtr, label=ytr), n)
    return final.predict(xgb.DMatrix(Xte)), n


def _metricas(y, p):
    p = np.clip(p, 1e-6, 1 - 1e-6)
    lg = np.log(p / (1 - p))
    slope = LogisticRegression(C=1e6).fit(lg[:, None], y).coef_[0, 0]
    return {"auroc": roc_auc_score(y, p), "auprc": average_precision_score(y, p),
            "brier": float(np.mean((p - y) ** 2)), "slope": float(slope)}


def _ajusta(Xtr_df, ytr, Xte_df):
    A, B = _matriz_lr(Xtr_df, Xtr_df), _matriz_lr(Xte_df, Xtr_df)
    lr = LogisticRegression(max_iter=2000, C=1.0).fit(A, ytr)
    p_xgb, n = _xgb(Xtr_df.to_numpy(float), ytr, Xte_df.to_numpy(float))
    out = {"logistica": lr.predict_proba(B)[:, 1], "xgboost": p_xgb}
    if "hemorragia" in Xte_df and "esplenomegalia" in Xte_df:  # escore publicado da LV, sem ajuste
        esc = T.escore_coura_vital(Xte_df).astype(float)
        out["escore_coura_vital"] = (esc + 0.5) / 15.0  # escala 0-1 so para as metricas; AUROC nao muda
    return out


def avalia(nome: str) -> pd.DataFrame:
    c = T.carrega(nome)
    y = c["outcome"].to_numpy()
    X = c.drop(columns=["outcome", "periodo"])
    linhas = []
    # protocolo cv
    rng = np.random.default_rng(0)
    fold = np.empty(len(y), int)
    for g in (np.where(y == 1)[0], np.where(y == 0)[0]):
        fold[rng.permutation(g)] = np.arange(len(g)) % 5
    por = {}
    for k in range(5):
        te, tr = fold == k, fold != k
        preds = _ajusta(X[tr], y[tr], X[te])
        for m, p in preds.items():
            por.setdefault(m, []).append(_metricas(y[te], p))
    for m, lst in por.items():
        df = pd.DataFrame(lst)
        meia = stats.t.ppf(0.975, 4) * np.sqrt(df["auroc"].var(ddof=1) * (1 / 5 + 1 / 4))
        linhas.append({"tarefa": nome, "protocolo": "cv", "modelo": m, **df.mean().to_dict(),
                       "auroc_li": df["auroc"].mean() - meia, "auroc_ls": df["auroc"].mean() + meia,
                       "n_treino": int((fold != 0).sum()), "n_teste": int((fold == 0).sum())})
    # protocolo temporal
    if nome in CORTE:
        te = (c["periodo"] >= CORTE[nome]).to_numpy()
        preds = _ajusta(X[~te], y[~te], X[te])
        rng = np.random.default_rng(1)
        for m, p in preds.items():
            met = _metricas(y[te], p)
            yt = y[te]
            boot = []
            for _ in range(1000):
                i = rng.integers(0, len(yt), len(yt))
                if 0 < yt[i].sum() < len(i):
                    boot.append(roc_auc_score(yt[i], p[i]))
            linhas.append({"tarefa": nome, "protocolo": "temporal", "modelo": m, **met,
                           "auroc_li": np.percentile(boot, 2.5), "auroc_ls": np.percentile(boot, 97.5),
                           "n_treino": int((~te).sum()), "n_teste": int(te.sum())})
    return pd.DataFrame(linhas)


if __name__ == "__main__":
    RES.mkdir(parents=True, exist_ok=True)
    nomes = sys.argv[1:] or list(T.TAREFAS)
    tabs = [avalia(n) for n in nomes]
    novo = pd.concat(tabs, ignore_index=True)
    arq = RES / "linhas_de_base.csv"
    if arq.exists():
        antigo = pd.read_csv(arq)
        novo = pd.concat([antigo[~antigo["tarefa"].isin(nomes)], novo], ignore_index=True)
    novo.to_csv(arq, index=False)
    print(novo.round(3).to_string(index=False))
