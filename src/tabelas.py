"""Tabelas do manuscrito (so agregados): coortes e linhas de base contra os comparadores.

    python src/tabelas.py   -> resultados/tabela1_coortes.csv, resultados/tabela2_desempenho.csv e markdown
"""
import pandas as pd

import tarefas as T

COMPARADOR = {
    "sivep_covid_obito": ("Baqui 2021 (Sci Rep)", "XGBoost, 80/20 + CV", 0.813, "231,112 / 37.7%"),
    "sivep_covid_obito_pediatrico": ("Oliveira 2022 (J Pediatr)", "Fine-Gray score, temporal", 0.750, "21,591 / 7.7%"),
    "sivep_influenza_obito_2024": ("Sardinha 2026 (Immunol Res)", "logistic, apparent", 0.81, "15,995 / 12.1%"),
    "sinasc_baixo_peso": ("none direct (Almeida 2026 used at-birth predictors)", "-", float("nan"), "-"),
    "sinasc_baixo_peso_ao_nascer": ("Almeida 2026 (Sao Paulo Med J)", "logistic, 80/20, at-birth predictors", 0.85, "2,548,570 / 9.5%"),
    "sih_obito_idoso_cardiovascular": ("Cordeiro & Martins 2018 (Rev Saude Publica)", "logistic model 1, apparent", 0.720, "385,784 / 13.0%"),
    "sinan_tb_abandono": ("Rodrigues 2024 (BMC Public Health)", "LightGBM/LR, 1:1 undersampled", 0.715, "243,726 / 17%"),
    "sinan_lv_obito": ("Coura-Vital 2014 (PLoS NTD)", "14-point score, 1/3 validation", 0.78, "18,501 / 6.2%"),
}
ORDEM = list(COMPARADOR)


def tabela1() -> pd.DataFrame:
    linhas = []
    for t in ORDEM:
        c = T.carrega(t)
        X = c.drop(columns=["outcome", "periodo"])
        linhas.append({"task": t, "records": len(c), "events": int(c["outcome"].sum()),
                       "event_rate_%": round(100 * c["outcome"].mean(), 1), "predictors": X.shape[1],
                       "missing_cells_%": round(100 * X.isna().mean().mean(), 1),
                       "periods": f"{c['periodo'].min()} to {c['periodo'].max()}",
                       "published_cohort": COMPARADOR[t][3]})
    return pd.DataFrame(linhas)


def tabela2() -> pd.DataFrame:
    lb = pd.read_csv(T.RAIZ / "resultados" / "linhas_de_base.csv")
    linhas = []
    for t in ORDEM:
        ref, desenho, auc, _ = COMPARADOR[t]
        d = lb[lb["tarefa"] == t]
        if d.empty:
            continue
        f = lambda p, m: d[(d["protocolo"] == p) & (d["modelo"] == m)]
        row = {"task": t, "comparator": ref, "comparator_design": desenho, "comparator_auroc": auc}
        for p in ("cv", "temporal"):
            for m in ("logistica", "xgboost", "escore_coura_vital"):
                r = f(p, m)
                if len(r):
                    r = r.iloc[0]
                    row[f"{p}_{m}"] = f"{r['auroc']:.3f} ({r['auroc_li']:.3f}-{r['auroc_ls']:.3f})"
        x = f("temporal", "xgboost")
        if len(x):
            x = x.iloc[0]
            row["temporal_xgb_auprc"], row["temporal_xgb_brier"], row["temporal_xgb_slope"] = (
                round(x["auprc"], 3), round(x["brier"], 3), round(x["slope"], 2))
        linhas.append(row)
    return pd.DataFrame(linhas)


if __name__ == "__main__":
    t1, t2 = tabela1(), tabela2()
    t1.to_csv(T.RAIZ / "resultados" / "tabela1_coortes.csv", index=False)
    t2.to_csv(T.RAIZ / "resultados" / "tabela2_desempenho.csv", index=False)
    print(t1.to_markdown(index=False))
    print()
    print(t2.to_markdown(index=False))
