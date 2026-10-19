"""Tarefas do benchmark brasileiro de predicao clinica com dados publicos.

Cada tarefa e uma funcao que le os arquivos brutos (fora do repositorio) e devolve um
DataFrame com uma linha por paciente: as variaveis disponiveis no momento da predicao, a
coluna `outcome` (0/1) e a coluna `periodo` (usada so na validacao temporal, nunca como
preditor). Nenhuma variavel posterior ao momento da predicao entra (UTI, ventilacao, datas de
desfecho, tempo de internacao).

    python src/tarefas.py constroi [tarefa ...]   -> coortes/<tarefa>.parquet e resumo agregado
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
DADOS = Path(os.environ.get("BENCH_BR_DADOS", RAIZ / "../../05_Dados_e_Modelos/Benchmark_Saude_BR")).resolve()
BRUTOS, COORTES = DADOS / "brutos", DADOS / "coortes"

REGIAO = {"RO": "N", "AC": "N", "AM": "N", "RR": "N", "PA": "N", "AP": "N", "TO": "N",
          "MA": "NE", "PI": "NE", "CE": "NE", "RN": "NE", "PB": "NE", "PE": "NE", "AL": "NE", "SE": "NE", "BA": "NE",
          "MG": "SE", "ES": "SE", "RJ": "SE", "SP": "SE", "PR": "S", "SC": "S", "RS": "S",
          "MS": "CO", "MT": "CO", "GO": "CO", "DF": "CO"}
COD_REGIAO = {"N": 1, "NE": 2, "SE": 3, "S": 4, "CO": 5}

# ----------------------------------------------------------------------------- SIVEP-Gripe

SIVEP_COMORB = ["CARDIOPATI", "HEMATOLOGI", "SIND_DOWN", "HEPATICA", "ASMA", "DIABETES", "NEUROLOGIC",
                "PNEUMOPATI", "IMUNODEPRE", "RENAL", "OBESIDADE", "PUERPERA"]
SIVEP_SINTOMAS = ["FEBRE", "TOSSE", "GARGANTA", "DISPNEIA", "DESC_RESP", "SATURACAO", "DIARREIA", "VOMITO",
                  "DOR_ABD", "FADIGA", "PERD_OLFT", "PERD_PALA"]


def _sim_nao(s: pd.Series) -> pd.Series:
    """1 = sim, 2 = nao, 9/vazio = desconhecido (NaN)."""
    v = pd.to_numeric(s, errors="coerce")
    return v.map({1: 1.0, 2: 0.0})


def _idade_anos(d: pd.DataFrame) -> pd.Series:
    n = pd.to_numeric(d["NU_IDADE_N"], errors="coerce")
    tp = pd.to_numeric(d["TP_IDADE"], errors="coerce")
    return np.where(tp == 3, n, np.where(tp.isin([1, 2]), 0.0, np.nan))


def _sivep(anos) -> pd.DataFrame:
    cols = (["DT_NOTIFIC", "DT_SIN_PRI", "DT_INTERNA", "SG_UF_NOT", "CS_SEXO", "NU_IDADE_N", "TP_IDADE", "CS_RACA",
             "CS_ESCOL_N", "CS_ZONA", "CS_GESTANT", "NOSOCOMIAL", "HOSPITAL", "PCR_SARS2", "CLASSI_FIN", "CRITERIO",
             "EVOLUCAO", "POS_PCRFLU", "VACINA", "VACINA_COV"] + SIVEP_COMORB + SIVEP_SINTOMAS)
    partes = []
    for a in anos:
        arq = BRUTOS / "sivep" / f"INFLUD{a % 100:02d}.parquet"
        import pyarrow.parquet as pq
        disp = set(pq.ParquetFile(arq).schema_arrow.names)
        d = pd.read_parquet(arq, columns=[c for c in cols if c in disp])
        for c in cols:
            if c not in d:
                d[c] = np.nan
        partes.append(d)
    return pd.concat(partes, ignore_index=True)


def _preditores_sivep(d: pd.DataFrame) -> pd.DataFrame:
    """Variaveis da notificacao disponiveis na admissao."""
    X = pd.DataFrame(index=d.index)
    X["idade"] = _idade_anos(d)
    X["sexo_masc"] = d["CS_SEXO"].astype(str).map({"M": 1.0, "F": 0.0})
    raca = pd.to_numeric(d["CS_RACA"], errors="coerce")
    X["raca"] = raca.where(raca.isin([1, 2, 3, 4, 5]))
    esc = pd.to_numeric(d["CS_ESCOL_N"], errors="coerce")
    X["escolaridade"] = esc.where(esc.isin([0, 1, 2, 3, 4]))
    X["regiao"] = d["SG_UF_NOT"].astype(str).map(REGIAO).map(COD_REGIAO)
    zona = pd.to_numeric(d["CS_ZONA"], errors="coerce")
    X["zona_urbana"] = zona.map({1: 1.0, 2: 0.0, 3: 1.0})
    X["nosocomial"] = _sim_nao(d["NOSOCOMIAL"])
    for c in SIVEP_COMORB + SIVEP_SINTOMAS:
        X[c.lower()] = _sim_nao(d[c])
    return X


def sivep_covid_obito(d0="2020-02-25", d1="2020-09-21") -> pd.DataFrame:
    """Obito hospitalar entre internados com RT-PCR positivo para SARS-CoV-2 (comparador:
    Baqui et al., Sci Rep 2021, XGBoost AUROC 0,813). Preditores da notificacao; sem UTI,
    ventilacao nem datas de desfecho."""
    d = _sivep([2020])
    dt = pd.to_datetime(d["DT_NOTIFIC"], errors="coerce")
    ev = pd.to_numeric(d["EVOLUCAO"], errors="coerce")
    m = ((pd.to_numeric(d["HOSPITAL"], errors="coerce") == 1) & (pd.to_numeric(d["PCR_SARS2"], errors="coerce") == 1)
         & ev.isin([1, 2, 3]) & (dt >= d0) & (dt <= d1))
    d = d[m]
    X = _preditores_sivep(d)
    X = X[X["idade"].between(0, 110)]
    X["outcome"] = ev.loc[X.index].isin([2, 3]).astype(int)
    X["periodo"] = pd.to_datetime(d.loc[X.index, "DT_NOTIFIC"]).dt.to_period("M").astype(str)
    return X.reset_index(drop=True)


def sivep_covid_obito_pediatrico() -> pd.DataFrame:
    """Obito hospitalar em menores de 20 anos internados com RT-PCR positivo, 16/02/2020 a
    29/05/2021 (comparador: Oliveira et al., J Pediatr 2022, validacao temporal C 0,750,
    com ventilacao entre os preditores). Validacao temporal: 2020 -> 2021."""
    d = _sivep([2020, 2021])
    dt = pd.to_datetime(d["DT_SIN_PRI"], errors="coerce")
    ev = pd.to_numeric(d["EVOLUCAO"], errors="coerce")
    m = ((pd.to_numeric(d["HOSPITAL"], errors="coerce") == 1) & (pd.to_numeric(d["PCR_SARS2"], errors="coerce") == 1)
         & ev.isin([1, 2, 3]) & (dt >= "2020-02-16") & (dt <= "2021-05-29"))
    d = d[m]
    X = _preditores_sivep(d)
    X = X[X["idade"].between(0, 19.999)]
    X["outcome"] = ev.loc[X.index].isin([2, 3]).astype(int)
    X["periodo"] = np.where(dt.loc[X.index] < "2021-01-01", "onda1_2020", "onda2_2021")
    return X.reset_index(drop=True)


def sivep_influenza_obito_2024() -> pd.DataFrame:
    """Obito entre casos de SRAG por influenza confirmados por RT-PCR em 2024, encerrados
    (comparador: Sardinha et al., Immunol Res 2026, AUROC aparente 0,81)."""
    d = _sivep([2024])
    ev = pd.to_numeric(d["EVOLUCAO"], errors="coerce")
    m = (pd.to_numeric(d["POS_PCRFLU"], errors="coerce") == 1) & ev.isin([1, 2, 3])
    d = d[m]
    X = _preditores_sivep(d)
    X["vacina_gripe"] = _sim_nao(d["VACINA"])
    X["vacina_covid"] = _sim_nao(d["VACINA_COV"])
    X = X[X["idade"].between(0, 110)]
    X["outcome"] = ev.loc[X.index].isin([2, 3]).astype(int)
    X["periodo"] = pd.to_datetime(d.loc[X.index, "DT_NOTIFIC"], errors="coerce").dt.to_period("M").astype(str)
    return X.reset_index(drop=True)


# ----------------------------------------------------------------------------- SINASC

SINASC_COLS = ["DTNASC", "PESO", "IDADEMAE", "ESTCIVMAE", "ESCMAE2010", "RACACORMAE", "QTDFILVIVO", "QTDFILMORT",
               "QTDGESTANT", "QTDPARTNOR", "QTDPARTCES", "GRAVIDEZ", "CONSPRENAT", "MESPRENAT", "CODMUNRES"]


def _num(s, validos=None, ign=(9, 99)):
    v = pd.to_numeric(s.replace({"": np.nan, "nan": np.nan, "None": np.nan}), errors="coerce")
    v = v.where(~v.isin(ign))
    return v.where(v.isin(validos)) if validos is not None else v


def sinasc_baixo_peso() -> pd.DataFrame:
    """Baixo peso ao nascer (< 2.500 g), nascidos vivos de maes residentes no estado de SP,
    2019-2023 (comparador: Almeida et al., Sao Paulo Med J 2026, AUROC 0,85 com variaveis do
    parto). Aqui so variaveis conhecidas ANTES do parto (dados da mae, historia obstetrica,
    gestacao multipla, pre-natal); idade gestacional, tipo de parto, Apgar e sexo ficam de fora.
    Validacao temporal: 2019-2022 -> 2023."""
    d = pd.read_parquet(BRUTOS / "sinasc" / "sinasc_sp.parquet")
    peso = _num(d["PESO"], ign=(9999,))
    d = d[peso.between(300, 6500)]
    return sinasc_baixo_peso_de(d).reset_index(drop=True)


def sinasc_baixo_peso_de(d: pd.DataFrame) -> pd.DataFrame:
    """Variaveis pre-parto, desfecho e periodo a partir das linhas validas do SINASC."""
    peso = _num(d["PESO"], ign=(9999,))
    X = pd.DataFrame(index=d.index)
    X["idade_mae"] = _num(d["IDADEMAE"], ign=(99,)).where(lambda v: v.between(10, 60))
    X["estado_civil"] = _num(d["ESTCIVMAE"], validos=[1, 2, 3, 4, 5])
    X["escolaridade"] = _num(d["ESCMAE2010"], validos=[0, 1, 2, 3, 4, 5])
    X["raca"] = _num(d["RACACORMAE"], validos=[1, 2, 3, 4, 5])
    for c in ["QTDFILVIVO", "QTDFILMORT", "QTDGESTANT", "QTDPARTNOR", "QTDPARTCES"]:
        X[c.lower()] = _num(d[c], ign=(99,)).where(lambda v: v.between(0, 30))
    X["gravidez_multipla"] = _num(d["GRAVIDEZ"], validos=[1, 2, 3]).map({1: 0.0, 2: 1.0, 3: 1.0})
    X["consultas_prenatal"] = _num(d["CONSPRENAT"], ign=(99,)).where(lambda v: v.between(0, 60))
    X["mes_inicio_prenatal"] = _num(d["MESPRENAT"], ign=(99,)).where(lambda v: v.between(1, 9))
    X["outcome"] = (peso < 2500).astype(int)
    X["periodo"] = d["ARQUIVO"].str[-4:]
    return X


def sinasc_baixo_peso_ao_nascer() -> pd.DataFrame:
    """Variante para comparacao direta com Almeida et al. (2026): as mesmas variaveis da
    tarefa pre-parto mais as conhecidas no parto que o comparador usou (semanas de gestacao,
    sexo do recem-nascido, anomalia congenita). Nao e predicao pre-parto; existe so para
    fechar a comparacao com o numero publicado."""
    d = pd.read_parquet(BRUTOS / "sinasc" / "sinasc_sp_parto.parquet")
    peso = _num(d["PESO"], ign=(9999,))
    d = d[peso.between(300, 6500)]
    X = sinasc_baixo_peso_de(d)
    X["semanas_gestacao"] = _num(d["SEMAGESTAC"], ign=(99,)).where(lambda v: v.between(20, 45))
    X["sexo_masc"] = d["SEXO"].astype(str).map({"1": 1.0, "M": 1.0, "2": 0.0, "F": 0.0})
    X["anomalia"] = _num(d["IDANOMAL"], validos=[1, 2]).map({1: 1.0, 2: 0.0})
    cols = [c for c in X.columns if c not in ("outcome", "periodo")] + ["outcome", "periodo"]
    return X[cols].reset_index(drop=True)


# ----------------------------------------------------------------------------- SIH/SUS

SIH_COLS = ["DIAG_PRINC", "DIAG_SECUN", "IDADE", "COD_IDADE", "SEXO", "CAR_INT", "MORTE", "RACA_COR",
            "DT_INTER", "COBRANCA", "DIAS_PERM", "UF_ZI", "MUNIC_RES", "IDENT"]
# grupos de diagnostico principal de Cordeiro & Martins (2018)
SIH_GRUPOS = {"hipertensiva": r"^I1[0-5]", "isquemica": r"^I2[0-5]", "icc": r"^I50", "avc": r"^I6[0-4]"}
# comorbidades pelo diagnostico secundario (unico campo no periodo): grupos de Charlson/Elixhauser
SIH_COMORB = {"diabetes": r"^E1[0-4]", "renal_cronica": r"^N1[89]", "dpoc": r"^J4[0-7]", "cancer": r"^C",
              "demencia": r"^(F0[0-3]|G30)", "hepatopatia": r"^K7[0-6]", "fa_arritmia": r"^I4[7-9]",
              "obesidade": r"^E66", "pneumonia": r"^J1[2-8]", "icc_sec": r"^I50", "insuf_renal_aguda": r"^N17"}


def sih_obito_idoso_cardiovascular() -> pd.DataFrame:
    """Obito hospitalar em internacoes de pacientes com 60 anos ou mais e diagnostico principal
    de doenca hipertensiva, isquemica do coracao, insuficiencia cardiaca ou AVC, regiao Sudeste,
    2011-2012 (comparador: Cordeiro & Martins, Rev Saude Publica 2018, modelo 1 C 0,720).
    Preditores conhecidos na admissao: idade, sexo, raca, grupo e codigo do diagnostico
    principal, carater da internacao, comorbidades pelo diagnostico secundario e UF. Tempo de
    permanencia e UTI ficam de fora. AIH tipo 1 (IDENT = 1); uma linha por AIH (a base publica
    nao identifica o paciente). Validacao temporal: 2011 -> 2012."""
    d = pd.read_parquet(BRUTOS / "sih" / "sih_sudeste_2011_2012.parquet")
    idade = _num(d["IDADE"], ign=())
    d = d[(d["IDENT"] == "1") & (d["COD_IDADE"] == "4") & (idade >= 60) & (idade <= 110)]
    dx = d["DIAG_PRINC"].str.strip().str.upper()
    grupo = pd.Series(np.nan, index=d.index)
    for i, (g, rx) in enumerate(SIH_GRUPOS.items(), 1):
        grupo[dx.str.match(rx)] = i
    d, dx, grupo = d[grupo.notna()], dx[grupo.notna()], grupo[grupo.notna()]
    X = pd.DataFrame(index=d.index)
    X["idade"] = _num(d["IDADE"], ign=())
    X["sexo_masc"] = d["SEXO"].map({"1": 1.0, "3": 0.0, "2": 0.0})
    X["raca"] = _num(d["RACA_COR"], validos=[1, 2, 3, 4, 5], ign=(99,))
    X["grupo_dx"] = grupo
    X["dx_cid"] = pd.to_numeric(dx.str[1:3], errors="coerce")  # numero do codigo CID-10 (I10 -> 10)
    X["urgencia"] = d["CAR_INT"].str.strip().map(lambda v: 0.0 if v in ("01", "1") else (1.0 if v not in ("", "nan") else np.nan))
    sec = d["DIAG_SECUN"].str.strip().str.upper().replace({"0000": "", "nan": ""})
    for c, rx in SIH_COMORB.items():
        X[c] = sec.str.match(rx).astype(float)
    X["tem_dx_secundario"] = (sec.str.len() >= 3).astype(float)
    X["uf"] = d["ARQUIVO"].str[2:4].map({"SP": 1, "RJ": 2, "MG": 3, "ES": 4}).astype(float)
    X["outcome"] = (d["MORTE"].str.strip() == "1").astype(int)
    X["periodo"] = "20" + d["ARQUIVO"].str[4:6]
    return X.reset_index(drop=True)


# ----------------------------------------------------------------------------- SINAN

def _idade_sinan(s: pd.Series) -> pd.Series:
    """NU_IDADE_N do SINAN: 1xxx horas, 2xxx dias, 3xxx meses, 4xxx anos."""
    v = pd.to_numeric(s, errors="coerce")
    u, n = v // 1000, v % 1000
    return np.select([u == 4, u == 3, u == 2, u == 1], [n, n / 12, n / 365.25, n / 8766.0], default=np.nan)


def _s(d, c):
    return d[c].astype(str).str.strip()


def sinan_tb_abandono() -> pd.DataFrame:
    """Perda de seguimento (abandono) vs. cura no tratamento da TB pulmonar, SINAN-TB 2015-2022
    (comparador: Rodrigues et al., BMC Public Health 2024, AUROC 0,71-0,72 com subamostragem
    1:1 antes do split). Inclusao como o comparador: idade >= 18, forma pulmonar exclusiva,
    sem diagnostico pos-obito, sem populacoes especiais (rua, privados de liberdade,
    gestantes, imigrantes, profissionais de saude), sem resistencia (TRM ou TSA), encerramento
    cura ou abandono (inclui abandono primario). So caso novo (TRATAMENTO = 1), como
    recomendado no levantamento. Preditores da ficha de notificacao; nada do acompanhamento.
    Validacao temporal: 2015-2019 -> 2020-2022."""
    cols = ["NU_ANO", "SG_UF_NOT", "NU_IDADE_N", "CS_SEXO", "CS_GESTANT", "CS_RACA", "CS_ESCOL_N", "TRATAMENTO",
            "FORMA", "INSTITUCIO", "RAIOX_TORA", "AGRAVAIDS", "AGRAVALCOO", "AGRAVDIABE", "AGRAVDOENC", "AGRAVDROGA",
            "AGRAVTABAC", "BACILOSC_E", "HIV", "TEST_MOLEC", "TEST_SENSI", "POP_LIBER", "POP_RUA", "POP_SAUDE",
            "POP_IMIG", "BENEF_GOV", "SITUA_ENCE"]
    partes = [pd.read_csv(BRUTOS / "sinan_tb" / f"TUBEBR{a:02d}.csv.zip", usecols=lambda c: c in cols, dtype=str,
                          low_memory=False).assign(ANO_ARQUIVO=str(2000 + a)) for a in range(15, 23)]
    d = pd.concat(partes, ignore_index=True)
    idade = pd.Series(_idade_sinan(d["NU_IDADE_N"]), index=d.index)
    sit = pd.to_numeric(_s(d, "SITUA_ENCE"), errors="coerce")
    resist = (_s(d, "TEST_MOLEC") == "2") | _s(d, "TEST_SENSI").isin(["1", "2", "3", "4"])
    especial = ((_s(d, "POP_RUA") == "1") | (_s(d, "POP_LIBER") == "1") | (_s(d, "POP_SAUDE") == "1")
                | (_s(d, "POP_IMIG") == "1") | _s(d, "CS_GESTANT").isin(["1", "2", "3", "4"]))
    m = ((idade >= 18) & (_s(d, "FORMA") == "1") & (_s(d, "TRATAMENTO") == "1") & ~especial & ~resist
         & sit.isin([1, 2, 10]))
    d, idade, sit = d[m], idade[m], sit[m]
    sn = lambda c: pd.to_numeric(_s(d, c), errors="coerce").map({1: 1.0, 2: 0.0})
    X = pd.DataFrame(index=d.index)
    X["idade"] = idade
    X["sexo_masc"] = _s(d, "CS_SEXO").map({"M": 1.0, "F": 0.0})
    X["raca"] = pd.to_numeric(_s(d, "CS_RACA"), errors="coerce").where(lambda v: v.isin([1, 2, 3, 4, 5]))
    X["escolaridade"] = pd.to_numeric(_s(d, "CS_ESCOL_N"), errors="coerce").where(lambda v: v.between(0, 8))
    X["regiao"] = _s(d, "SG_UF_NOT").map({k: COD_REGIAO[v] for k, v in REGIAO.items()} |
                                          dict(zip(["11", "12", "13", "14", "15", "16", "17", "21", "22", "23", "24", "25", "26",
                                                    "27", "28", "29", "31", "32", "33", "35", "41", "42", "43", "50", "51", "52", "53"],
                                                   [1] * 7 + [2] * 9 + [3] * 4 + [4] * 3 + [5] * 4)))
    X["institucionalizado"] = pd.to_numeric(_s(d, "INSTITUCIO"), errors="coerce").map({1: 0.0, 2: 1.0, 3: 1.0, 4: 1.0, 5: 1.0})
    X["raiox_suspeito"] = pd.to_numeric(_s(d, "RAIOX_TORA"), errors="coerce").map({1: 1.0, 2: 0.0, 3: 0.0})
    X["baciloscopia_positiva"] = pd.to_numeric(_s(d, "BACILOSC_E"), errors="coerce").map({1: 1.0, 2: 0.0})
    X["trm_detectavel"] = pd.to_numeric(_s(d, "TEST_MOLEC"), errors="coerce").map({1: 1.0, 3: 0.0})
    X["hiv_positivo"] = pd.to_numeric(_s(d, "HIV"), errors="coerce").map({1: 1.0, 2: 0.0})
    for c, nome in [("AGRAVAIDS", "aids"), ("AGRAVALCOO", "alcool"), ("AGRAVDIABE", "diabetes"),
                    ("AGRAVDOENC", "doenca_mental"), ("AGRAVDROGA", "drogas_ilicitas"), ("AGRAVTABAC", "tabagismo"),
                    ("BENEF_GOV", "beneficio_governo")]:
        X[nome] = sn(c)
    X["outcome"] = sit.isin([2, 10]).astype(int)
    X["periodo"] = d["ANO_ARQUIVO"]  # ano do arquivo do DATASUS (NU_ANO tem casos antigos reabertos)
    return X.reset_index(drop=True)


def sinan_lv_obito() -> pd.DataFrame:
    """Obito por leishmaniose visceral vs. cura, casos novos confirmados, SINAN 2007-2019
    (comparador: Coura-Vital et al., PLoS Negl Trop Dis 2014, escore de 14 pontos, validacao
    AUROC 0,78 em 2007-2011). Exclui obito por outra causa, abandono, transferencia e desfecho
    faltante, como o comparador. Preditores da ficha na suspeita clinica; sem droga, dose,
    falencia, datas de obito ou encerramento. Validacao temporal: 2007-2011 -> 2012-2019."""
    d = pd.read_parquet(BRUTOS / "sinan_lv" / "sinan_lv.parquet")
    ev = pd.to_numeric(_s(d, "EVOLUCAO"), errors="coerce")
    m = (_s(d, "CLASSI_FIN") == "1") & (_s(d, "ENTRADA") == "1") & ev.isin([1, 3])
    d, ev = d[m], ev[m]
    X = pd.DataFrame(index=d.index)
    X["idade"] = _idade_sinan(d["NU_IDADE_N"])
    X["sexo_masc"] = _s(d, "CS_SEXO").map({"M": 1.0, "F": 0.0})
    X["raca"] = pd.to_numeric(_s(d, "CS_RACA"), errors="coerce").where(lambda v: v.isin([1, 2, 3, 4, 5]))
    X["regiao"] = _s(d, "SG_UF_NOT").str[:1].map({"1": 1.0, "2": 2.0, "3": 3.0, "4": 4.0, "5": 5.0})
    for c, nome in [("FEBRE", "febre"), ("FRAQUEZA", "fraqueza"), ("EDEMA", "edema"), ("EMAGRA", "emagrecimento"),
                    ("TOSSE", "tosse_diarreia"), ("PALIDEZ", "palidez"), ("BACO", "esplenomegalia"),
                    ("INFECCIOSO", "quadro_infeccioso"), ("FEN_HEMORR", "hemorragia"), ("FIGADO", "hepatomegalia"),
                    ("ICTERICIA", "ictericia"), ("HIV", "coinfeccao_hiv")]:
        X[nome] = pd.to_numeric(_s(d, c), errors="coerce").map({1: 1.0, 2: 0.0})
    X["outcome"] = (ev == 3).astype(int)
    X["periodo"] = _s(d, "NU_ANO")
    return X[X["idade"].notna()].reset_index(drop=True)


def escore_coura_vital(X: pd.DataFrame) -> np.ndarray:
    """Escore de 14 pontos de Coura-Vital et al. (2014), sinais ausentes contam 0."""
    i = X["idade"]
    pontos_idade = np.select([i <= 0.5, i <= 1, i <= 19, i <= 50, i <= 65], [5, 2, 0, 2, 3], default=5)
    s = lambda c: X[c].fillna(0).to_numpy()
    return (pontos_idade + 3 * s("hemorragia") + s("esplenomegalia") + s("edema") + s("fraqueza") + s("ictericia")
            + s("coinfeccao_hiv") + s("quadro_infeccioso"))


TAREFAS = {
    "sinan_tb_abandono": sinan_tb_abandono,
    "sinan_lv_obito": sinan_lv_obito,
    "sinasc_baixo_peso": sinasc_baixo_peso,
    "sinasc_baixo_peso_ao_nascer": sinasc_baixo_peso_ao_nascer,
    "sih_obito_idoso_cardiovascular": sih_obito_idoso_cardiovascular,
    "sivep_covid_obito": sivep_covid_obito,
    "sivep_covid_obito_pediatrico": sivep_covid_obito_pediatrico,
    "sivep_influenza_obito_2024": sivep_influenza_obito_2024,
}


def constroi(nomes=None) -> pd.DataFrame:
    COORTES.mkdir(parents=True, exist_ok=True)
    resumo = []
    for nome in nomes or TAREFAS:
        c = TAREFAS[nome]()
        c.to_parquet(COORTES / f"{nome}.parquet", index=False)
        X = c.drop(columns=["outcome", "periodo"])
        resumo.append({"tarefa": nome, "pacientes": len(c), "eventos": int(c["outcome"].sum()),
                       "taxa_%": round(100 * c["outcome"].mean(), 1), "preditores": X.shape[1],
                       "faltante_%": round(100 * X.isna().mean().mean(), 1)})
    return pd.DataFrame(resumo)


def carrega(nome: str) -> pd.DataFrame:
    return pd.read_parquet(COORTES / f"{nome}.parquet")


if __name__ == "__main__":
    if sys.argv[1] == "constroi":
        print(constroi(sys.argv[2:] or None).to_string(index=False))
