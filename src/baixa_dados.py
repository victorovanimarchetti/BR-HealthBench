"""Baixa os arquivos brutos do benchmark das fontes oficiais e confere tamanho e SHA-256 contra
`docs/manifesto_dados.csv`. Nenhum dado e redistribuido por este repositorio.

    python src/baixa_dados.py              # baixa o que falta em $BENCH_BR_DADOS/brutos e confere tudo
    python src/baixa_dados.py --verifica   # so confere os arquivos ja presentes
    python src/baixa_dados.py --um sinan_lv/LEIVBR07.dbc --destino /tmp/x   # um arquivo, outra pasta

Fontes (sem cadastro nem aceite de termos):
  - DATASUS, ftp://ftp.datasus.gov.br/dissemin/publicos/ (SIH/SUS, SINASC, SINAN)
  - Portal de dados abertos do Ministerio da Saude (SIVEP-Gripe), copia em S3 do CKAN, versao
    de 23/03/2026
Depois do download, os .dbc sao convertidos em Parquet por `src/prepara_dbc.sh` (Linux/WSL).
"""
from __future__ import annotations

import csv
import hashlib
import os
import re
import sys
import urllib.request
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
DADOS = Path(os.environ.get("BENCH_BR_DADOS", RAIZ / "../../05_Dados_e_Modelos/Benchmark_Saude_BR")).resolve()
FTP = "ftp://ftp.datasus.gov.br/dissemin/publicos"
S3 = "https://s3.sa-east-1.amazonaws.com/ckan.saude.gov.br/SRAG"
VERSAO_SIVEP = "23-03-2026"


def url(arquivo: str) -> str:
    pasta, nome = arquivo.split("/")
    if pasta == "sih":
        return f"{FTP}/SIHSUS/200801_/{'Doc' if nome.endswith('.pdf') else 'Dados'}/{nome}"
    if pasta == "sinasc":
        return f"{FTP}/SINASC/1996_/{'Doc' if nome.endswith('.pdf') else 'Dados/DNRES'}/{nome}"
    if pasta == "sinan_lv":
        return f"{FTP}/SINAN/DADOS/FINAIS/{nome}"
    if pasta == "sinan_tb":
        return f"{FTP}/Dados_Abertos/SINAN/Tuberculose/csv/{nome}"
    if pasta == "sivep":
        if nome.endswith(".pdf"):
            return f"{S3}/{nome}"
        aa = re.fullmatch(r"INFLUD(\d\d)\.parquet", nome).group(1)
        return f"{S3}/20{aa}/INFLUD{aa}-{VERSAO_SIVEP}.parquet"
    raise ValueError(arquivo)


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for bloco in iter(lambda: f.read(1 << 20), b""):
            h.update(bloco)
    return h.hexdigest()


def manifesto():
    with open(RAIZ / "docs" / "manifesto_dados.csv", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def confere(destino: Path, linha) -> str:
    p = destino / linha["arquivo"]
    if not p.exists():
        return "falta"
    if p.stat().st_size != int(linha["bytes"]):
        return "tamanho diferente"
    return "ok" if sha256(p) == linha["sha256"] else "hash diferente"


def baixa(destino: Path, linha) -> None:
    p = destino / linha["arquivo"]
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(p.suffix + ".parcial")
    with urllib.request.urlopen(url(linha["arquivo"]), timeout=600) as r, open(tmp, "wb") as f:
        while bloco := r.read(1 << 20):
            f.write(bloco)
    tmp.replace(p)


def main(args):
    destino = Path(args[args.index("--destino") + 1]) if "--destino" in args else DADOS / "brutos"
    linhas = manifesto()
    if "--um" in args:
        alvo = args[args.index("--um") + 1]
        linhas = [l for l in linhas if l["arquivo"] == alvo]
    problemas = 0
    for l in linhas:
        estado = confere(destino, l)
        if estado != "ok" and "--verifica" not in args:
            print("baixando", l["arquivo"], flush=True)
            baixa(destino, l)
            estado = confere(destino, l)
        if estado != "ok":
            problemas += 1
        print(f"{estado:18s} {l['arquivo']}")
    print(f"{len(linhas) - problemas} de {len(linhas)} arquivos conferem")
    return 1 if problemas else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
