"""Converte os .dbc do DATASUS em Parquet, so com as colunas usadas pelas tarefas.

Roda no Linux (WSL), onde o leitor de .dbc compila:
    python dbc_para_parquet.py <pasta_dbc> <saida.parquet> COL1,COL2,...
Imprime so contagens.
"""
import sys
from pathlib import Path

import os
import tempfile

import pandas as pd
from dbfread import DBF
from pyreaddbc import dbc2dbf

pasta, saida, cols = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3].split(",")
partes = []
for arq in sorted(pasta.glob("*.dbc")):
    with tempfile.TemporaryDirectory() as tmp:
        dbf = os.path.join(tmp, arq.stem + ".dbf")
        dbc2dbf(str(arq), dbf)
        tab = DBF(dbf, encoding="latin-1", char_decode_errors="replace")
        usar = [c for c in cols if c in tab.field_names]
        d = pd.DataFrame(({c: r[c] for c in usar} for r in tab), columns=usar)
    d = d.astype(str)
    d["ARQUIVO"] = arq.stem
    partes.append(d)
    print(arq.name, len(d), flush=True)
pd.concat(partes, ignore_index=True).to_parquet(saida, index=False)
print("total", sum(len(p) for p in partes))
