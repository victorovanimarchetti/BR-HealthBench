#!/bin/bash
# Converte os .dbc do DATASUS em Parquet com as colunas usadas pelas tarefas (Linux ou WSL; o
# leitor de .dbc compila no Linux). Precisa de: pip install pyreaddbc dbfread pandas pyarrow
# Uso: BENCH_BR_DADOS=/caminho/dos/dados bash src/prepara_dbc.sh
set -e
D="${BENCH_BR_DADOS:-$(dirname "$0")/../../../05_Dados_e_Modelos/Benchmark_Saude_BR}/brutos"
S="$(dirname "$0")/dbc_para_parquet.py"
python "$S" "$D/sinasc" "$D/sinasc/sinasc_sp.parquet" \
  DTNASC,PESO,IDADEMAE,ESTCIVMAE,ESCMAE2010,RACACORMAE,QTDFILVIVO,QTDFILMORT,QTDGESTANT,QTDPARTNOR,QTDPARTCES,GRAVIDEZ,CONSPRENAT,MESPRENAT,CODMUNRES
python "$S" "$D/sinasc" "$D/sinasc/sinasc_sp_parto.parquet" \
  DTNASC,PESO,IDADEMAE,ESTCIVMAE,ESCMAE2010,RACACORMAE,QTDFILVIVO,QTDFILMORT,QTDGESTANT,QTDPARTNOR,QTDPARTCES,GRAVIDEZ,CONSPRENAT,MESPRENAT,SEMAGESTAC,GESTACAO,SEXO,IDANOMAL
python "$S" "$D/sih" "$D/sih/sih_sudeste_2011_2012.parquet" \
  DIAG_PRINC,DIAG_SECUN,IDADE,COD_IDADE,SEXO,CAR_INT,MORTE,RACA_COR,DT_INTER,COBRANCA,DIAS_PERM,UF_ZI,MUNIC_RES,IDENT
python "$S" "$D/sinan_lv" "$D/sinan_lv/sinan_lv.parquet" \
  NU_ANO,DT_NOTIFIC,SG_UF_NOT,NU_IDADE_N,CS_SEXO,CS_GESTANT,CS_RACA,CS_ESCOL_N,FEBRE,FRAQUEZA,EDEMA,EMAGRA,TOSSE,PALIDEZ,BACO,INFECCIOSO,FEN_HEMORR,FIGADO,ICTERICIA,HIV,ENTRADA,CLASSI_FIN,CRITERIO,EVOLUCAO,TPAUTOCTO
