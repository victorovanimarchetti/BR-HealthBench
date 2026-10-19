# Benchmark_Saude_BR

Benchmark de predição clínica com dados públicos brasileiros de saúde: tarefas fixas, coortes em
código, lista de preditores por momento da predição, partições fixas (validação cruzada e
temporal) e comparação com o AUROC publicado de um estudo com dado real.

**Status (19/10/2026):** benchmark completo e reconstruível por qualquer pessoa: 7 tarefas e uma
variante de comparação (SINASC com dados do parto), coortes em código, linhas de base nos
protocolos de validação cruzada e temporal, todas comparadas com o AUROC publicado. Todos os
arquivos vêm de fontes abertas sem cadastro; `src/baixa_dados.py` baixa e confere o SHA-256 de
cada um (130 de 130 conferem; URLs testadas em 19/10/2026). Manuscrito em `docs/02_manuscrito.md`.
A tarefa FAPESP COVID-19 Data Sharing/BR foi descartada: exige cadastro e aceite de termos.

**Próximo passo bloqueante:** publicar este repositório (git local pronto) num repositório
público; depende de autorização do autor.

## Tarefas

| Tarefa | Base | Desfecho | Comparador publicado |
|---|---|---|---|
| `sivep_covid_obito` | SIVEP-Gripe 2020 | Óbito hospitalar, COVID-19 por RT-PCR | Baqui 2021, AUROC 0,813 |
| `sivep_covid_obito_pediatrico` | SIVEP-Gripe 2020–2021 | Idem, menores de 20 anos | Oliveira 2022, C 0,750 (temporal) |
| `sivep_influenza_obito_2024` | SIVEP-Gripe 2024 | Óbito, influenza por RT-PCR | Sardinha 2026, 0,81 (aparente) |
| `sinasc_baixo_peso` | SINASC SP 2019–2023 | Peso < 2.500 g, preditores pré-parto | Almeida 2026, 0,85 (com variáveis do parto) |
| `sih_obito_idoso_cardiovascular` | SIH/SUS Sudeste 2011–2012 | Óbito hospitalar, 60+ cardiovascular | Cordeiro & Martins 2018, C 0,720 |
| `sinan_tb_abandono` | SINAN-TB 2015–2022 | Abandono vs. cura, TB pulmonar | Rodrigues 2024, 0,71–0,72 |
| `sinan_lv_obito` | SINAN-LV 2007–2019 | Óbito vs. cura, leishmaniose visceral | Coura-Vital 2014, 0,78 (validação) |

## Conteúdo

| Caminho | O que é |
|---|---|
| `docs/01_levantamento.md` | Levantamento: benchmarks existentes, estudos com AUROC, acesso às bases |
| `docs/02_manuscrito.md` | Manuscrito do benchmark |
| `src/tarefas.py` | Definição de cada coorte (inclusão, desfecho, preditores, período) |
| `src/linhas_de_base.py` | Regressão logística, XGBoost e escores publicados, nos protocolos `cv` e `temporal` |
| `src/baixa_dados.py` | Baixa os arquivos das fontes oficiais e confere tamanho e SHA-256 contra o manifesto |
| `src/prepara_dbc.sh` | Converte os `.dbc` em Parquet com as colunas usadas (Linux/WSL) |
| `src/dbc_para_parquet.py` | Conversão de uma pasta de `.dbc` (chamada pelo `prepara_dbc.sh`) |
| `docs/manifesto_dados.csv` | Arquivo, tamanho, data e SHA-256 de cada arquivo bruto |
| `resultados/linhas_de_base.csv` | Métricas agregadas (sem dado de paciente) |

## Dados

Os arquivos brutos e as coortes ficam fora do repositório, em
`05_Dados_e_Modelos/Benchmark_Saude_BR/` (`brutos/` e `coortes/`). As bases são públicas e
desidentificadas, mas trazem quase-identificadores (data de nascimento, município). Registros
nunca são enviados a serviços de LLM. A licença do portal de dados abertos do Ministério da
Saúde é CC BY-ND: o benchmark distribui o código e as regras, não arquivos derivados.

## Como reconstruir

```bash
pip install pandas pyarrow numpy scikit-learn xgboost
export BENCH_BR_DADOS=/caminho/para/os/dados   # opcional; padrão: ../../05_Dados_e_Modelos/Benchmark_Saude_BR
python src/baixa_dados.py                      # ~600 MB; baixa e confere os 130 arquivos
pip install pyreaddbc dbfread && bash src/prepara_dbc.sh   # Linux/WSL: .dbc -> Parquet
python src/tarefas.py constroi                 # coortes em $BENCH_BR_DADOS/coortes
python src/linhas_de_base.py                   # linhas de base -> resultados/linhas_de_base.csv
python src/tabelas.py                          # tabelas 1 e 2 do manuscrito
```
