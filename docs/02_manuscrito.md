> **Nota de contexto (pt-BR):** manuscrito do benchmark, em inglês por ser o artefato de
> submissão. Números de `resultados/linhas_de_base.csv`; levantamento em
> `01_levantamento.md`. Revista-alvo sugerida: *Scientific Data* (descritor de benchmark) ou
> *JAMIA Open*.

# BR-HealthBench: a benchmark of clinical prediction tasks built on public Brazilian health data

**Authors:** Victor Marchetti

## Abstract

**Background.** Brazil publishes de-identified, patient-level records from its national health
information systems, covering hundreds of millions of events. They are widely used for
prediction studies, but each study defines its own cohort, predictors and validation, so
results cannot be compared and leakage is common. No benchmark of prediction tasks exists for
these data.

**Methods.** We surveyed published prediction studies on Brazilian public health data and built
a benchmark of tasks that (i) use only public, de-identified files that anyone can download without registration or accepting terms of use, (ii) have a
peer-reviewed comparator that reported discrimination on real data, (iii) use only information
available at the time of prediction, and (iv) have enough events. Each task has a cohort defined
in code, an explicit list of forbidden (post-prediction) fields, a random cross-validation
protocol and a temporal validation protocol, and baselines (logistic regression, gradient
boosting and, where published, the original clinical score).

**Results.** No benchmark existed. Seven tasks entered from four national systems (SIVEP-Gripe,
SINASC, SIH/SUS, SINAN), with 14,505 to 2,676,548 records and 1,372 to 257,231 events: death in
adults and in under-20s hospitalised with COVID-19, death in influenza, low birth weight from
pre-delivery information, in-hospital death of older adults with cardiovascular disease, loss to
follow-up in tuberculosis and death in visceral leishmaniasis. Where the published model used
only prediction-time information, gradient boosting reproduced or exceeded the published AUROC
(for example 0.724 against 0.720 in SIH/SUS, 0.713 against 0.71–0.72 in tuberculosis, and 0.804
against 0.78 for a published leishmaniasis score, which itself gave 0.773 on our data). With
pre-delivery information only, low birth weight reached 0.753; adding the at-birth predictors
the comparator used gave 0.897 against 0.85. The one remaining gap (adult COVID-19, 0.791 against
0.813) is explained by hospital- and municipality-level covariates absent from the notification
file. Temporal validation lowered AUROC by at most
0.020, and calibration slopes were 0.91–1.07.

**Conclusions.** Public Brazilian health files support a reproducible benchmark whose baselines
match the published literature once post-prediction information is excluded. Fixed cohorts,
explicit leakage rules and temporal validation make future results comparable.

## 1. Introduction

Brazil's Unified Health System (SUS) records notifications, hospital admissions, births and
deaths in national information systems maintained by the Ministry of Health (DATASUS). Their
de-identified microdata are public and have supported a large literature of risk-prediction
studies: COVID-19 death from the severe acute respiratory illness surveillance system
(SIVEP-Gripe) [Baqui 2021], neonatal outcomes from the live-birth system (SINASC) [Batista
2021; Almeida 2026], in-hospital mortality from hospital admission records (SIH/SUS)
[Martins 2010; Cordeiro 2018; Schilling 2024], tuberculosis treatment outcomes and visceral
leishmaniasis death from the notifiable diseases system (SINAN) [Rodrigues 2024; Coura-Vital
2014].

Three problems limit this literature. First, every study defines its own cohort and predictors,
so reported AUROCs cannot be compared. Second, fields recorded after the prediction time are
often used as predictors: intensive care admission and ventilation in SIVEP-Gripe studies, time
to outcome, length of stay in SIH studies. Our survey found AUROCs inflated from about 0.75–0.81
to 0.80–0.90 by such fields. Third, validation is usually a random split or none; temporal
validation is rare and geographic validation absent.

Benchmarks solved the same problem elsewhere: fixed tasks, cohorts, splits and baselines for
intensive care data [Harutyunyan 2019; van de Water 2024], electronic health records [Wornow
2023] and general tabular data [TabArena]. We found none for Brazilian health data: existing
resources are access tools (PySUS, microdatasus, OmniSUS), single-task curated datasets, or aggregate
forecasting challenges; no Brazilian health dataset appears in TabArena.

We present a benchmark of prediction tasks on public Brazilian health data, each paired with a
published real-data comparator, with leakage rules written in code and temporal validation.

## 2. Methods

### 2.1 Survey and task selection

We searched for (a) existing benchmarks on Brazilian health data (GitHub, Hugging Face, Kaggle,
OpenML, TabArena, Papers with Code) and (b) peer-reviewed studies that predicted a binary,
patient-level outcome from public Brazilian microdata and reported discrimination. Each source
was opened and graded as verified in full text, abstract only, or unverified (Supplementary
File S1). A task entered the benchmark if (1) its files are public and downloadable by anyone
without registration, credentials or acceptance of terms of use, so that every user of the
benchmark can rebuild it; (2) at least one verified study reported an AUROC on real data for a comparable
cohort; (3) predictors exist at a clinically meaningful prediction time; and (4) it has at least
several hundred events. Tasks needing record linkage by personal identifiers (for example
neonatal death from SINASC–SIM linkage) were excluded.

### 2.2 Data sources

- **SIVEP-Gripe**: national surveillance of hospitalised severe acute respiratory illness
  (SARI), Parquet files from the Ministry of Health open-data portal (dadosabertos.saude.gov.br),
  version of 23 March 2026.
- **SINASC**: live-birth declarations, files `DNSP2019`–`DNSP2023` from the DATASUS FTP.
- **SIH/SUS**: reduced hospital admission records (AIH, `RD` files), São Paulo, Rio de Janeiro,
  Minas Gerais and Espírito Santo, January 2011 to December 2012, DATASUS FTP.
- **SINAN**: tuberculosis (`TUBEBR15`–`TUBEBR22`, open-data CSV) and visceral leishmaniasis
  (`LEIVBR07`–`LEIVBR19`, final files), DATASUS FTP.

Download dates and file hashes are recorded with the code (the portal rewrites "live" files).

### 2.3 Tasks

**Table 1. Tasks.** Records, events, predictors and missing cells; the last column gives the
published comparator's cohort (records / event rate). Inclusion rules, prediction time and
forbidden fields for each task are in `src/tarefas.py` and Supplementary Table S2.

| task                           |   records |   events |   event_rate_% |   predictors |   missing_cells_% | periods                  | published_cohort   |
|:-------------------------------|----------:|---------:|---------------:|-------------:|------------------:|:-------------------------|:-------------------|
| sivep_covid_obito              |    309316 |   107612 |           34.8 |           31 |              40.3 | 2020-02 to 2020-09       | 231,112 / 37.7%    |
| sivep_covid_obito_pediatrico   |     14505 |     1372 |            9.5 |           31 |              45.5 | onda1_2020 to onda2_2021 | 21,591 / 7.7%      |
| sivep_influenza_obito_2024     |     16542 |     2317 |           14   |           33 |              34.7 | 2024-01 to 2025-06       | 15,995 / 12.1%     |
| sinasc_baixo_peso              |   2676548 |   257231 |            9.6 |           12 |               0.4 | 2019 to 2023             | -                  |
| sinasc_baixo_peso_ao_nascer    |   2676548 |   257231 |            9.6 |           15 |               0.3 | 2019 to 2023             | 2,548,570 / 9.5%   |
| sih_obito_idoso_cardiovascular |    421919 |    50254 |           11.9 |           19 |               1.5 | 2011 to 2012             | 385,784 / 13.0%    |
| sinan_tb_abandono              |    317086 |    46441 |           14.6 |           17 |              19.4 | 2015 to 2022             | 243,726 / 17%      |
| sinan_lv_obito                 |     33876 |     2957 |            8.7 |           16 |               4.2 | 2007 to 2019             | 18,501 / 6.2%      |

### 2.4 Protocols, baselines and metrics

Each task has two fixed protocols. **CV**: stratified 5-fold cross-validation (seed 0); 95% CI
of the AUROC from the between-fold variance with the Nadeau–Bengio correction. **Temporal**:
training on earlier periods and testing on later ones (cut-offs in Table 1); 95% CI by
bootstrap of the test set (1,000 resamples). Baselines: L2-regularised logistic regression
(categorical predictors one-hot encoded, missing values as their own category or median-imputed
with an indicator) and XGBoost (depth 4, learning rate 0.05, number of trees by early stopping
on a 20% internal hold-out; missing values handled natively). Where the comparator is a clinical
score (visceral leishmaniasis), the score is recomputed on our data without refitting. Metrics:
AUROC, AUPRC, Brier score and calibration slope.

## 3. Results

### 3.1 Survey

No existing benchmark of patient-level prediction tasks on Brazilian public health data was
found. Access libraries (PySUS, microdatasus, OmniSUS [github.com/raphaelfh/omnisus, pre-1.0, October 2026]), mirrors (Base dos Dados, PCDaS, healthbr-data),
single-task curated deposits (a SIVEP-Gripe COVID-19 versus influenza dataset, the SPNeoDeath
neonatal file) and aggregate forecasting challenges (Infodengue–Mosqlimate sprints) exist; none
fixes tasks, cohorts, splits and baselines. No Brazilian health dataset is part of TabArena.
Among the eleven SIVEP-Gripe studies with an AUROC, seven used post-admission fields (ICU
admission, ventilation or time to outcome) as predictors, and two of the seven SIH/SUS studies
used length of stay or ICU days; only three
SIVEP-Gripe studies published code; temporal validation was rare and geographic validation
absent (Supplementary File S1).

### 3.2 Tasks

Seven tasks across four information systems entered the benchmark (Table 1), plus one
comparison variant: 309,316 adult COVID-19 admissions (34.8% died), 14,505 paediatric
COVID-19 admissions (9.5%), 16,542 influenza cases in 2024 (14.0%), 2,676,548 live births
(9.6% low birth weight), 421,919 admissions of older adults with cardiovascular disease (11.9%
died), 317,086 pulmonary tuberculosis cases ending in cure or loss to follow-up (14.6% lost),
and 33,876 visceral leishmaniasis cases (8.7% died). Event counts range from 1,372 to 257,231.
Missing cells are frequent in notification forms (35–46% in SIVEP-Gripe, 19% in SINAN-TB) and
rare in birth and admission records (under 2%).

### 3.3 Baselines against published comparators

**Table 2. Baselines against published comparators** (AUROC with 95% CI; cv = 5-fold
cross-validation, temporal = later period held out).

| task                           | comparator                                          | comparator_design                    |   comparator_auroc | cv_logistica        | cv_xgboost          | temporal_logistica   | temporal_xgboost    |   temporal_xgb_auprc |   temporal_xgb_brier |   temporal_xgb_slope | cv_escore_coura_vital   | temporal_escore_coura_vital   |
|:-------------------------------|:----------------------------------------------------|:-------------------------------------|-------------------:|:--------------------|:--------------------|:---------------------|:--------------------|---------------------:|---------------------:|---------------------:|:------------------------|:------------------------------|
| sivep_covid_obito              | Baqui 2021 (Sci Rep)                                | XGBoost, 80/20 + CV                  |              0.813 | 0.779 (0.775-0.783) | 0.791 (0.786-0.795) | 0.773 (0.769-0.776)  | 0.782 (0.779-0.785) |                0.608 |                0.174 |                 1    | nan                     | nan                           |
| sivep_covid_obito_pediatrico   | Oliveira 2022 (J Pediatr)                           | Fine-Gray score, temporal            |              0.75  | 0.791 (0.772-0.810) | 0.802 (0.783-0.820) | 0.779 (0.761-0.798)  | 0.789 (0.770-0.808) |                0.32  |                0.077 |                 1.07 | nan                     | nan                           |
| sivep_influenza_obito_2024     | Sardinha 2026 (Immunol Res)                         | logistic, apparent                   |              0.81  | 0.817 (0.795-0.838) | 0.826 (0.808-0.845) | 0.802 (0.787-0.816)  | 0.806 (0.792-0.820) |                0.346 |                0.099 |                 0.91 | nan                     | nan                           |
| sinasc_baixo_peso              | none direct (Almeida 2026 used at-birth predictors) | -                                    |            nan     | 0.741 (0.738-0.744) | 0.753 (0.751-0.756) | 0.735 (0.733-0.738)  | 0.748 (0.745-0.750) |                0.364 |                0.078 |                 0.98 | nan                     | nan                           |
| sinasc_baixo_peso_ao_nascer    | Almeida 2026 (Sao Paulo Med J)                      | logistic, 80/20, at-birth predictors |              0.85  | 0.891 (0.889-0.892) | 0.897 (0.896-0.898) | 0.892 (0.890-0.893)  | 0.898 (0.897-0.900) |                0.67  |                0.053 |                 1.01 | nan                     | nan                           |
| sih_obito_idoso_cardiovascular | Cordeiro & Martins 2018 (Rev Saude Publica)         | logistic model 1, apparent           |              0.72  | 0.718 (0.713-0.722) | 0.724 (0.720-0.728) | 0.718 (0.715-0.722)  | 0.724 (0.720-0.727) |                0.255 |                0.097 |                 1    | nan                     | nan                           |
| sinan_tb_abandono              | Rodrigues 2024 (BMC Public Health)                  | LightGBM/LR, 1:1 undersampled        |              0.715 | 0.703 (0.699-0.707) | 0.713 (0.709-0.717) | 0.696 (0.692-0.700)  | 0.704 (0.700-0.708) |                0.329 |                0.13  |                 0.92 | nan                     | nan                           |
| sinan_lv_obito                 | Coura-Vital 2014 (PLoS NTD)                         | 14-point score, 1/3 validation       |              0.78  | 0.778 (0.765-0.790) | 0.804 (0.786-0.822) | 0.768 (0.756-0.780)  | 0.789 (0.778-0.799) |                0.313 |                0.076 |                 0.93 | 0.773 (0.754-0.793)     | 0.766 (0.755-0.776)           |

Gradient boosting reproduced or exceeded every comparator that used only
prediction-time information, and fell short only where the comparator used information we
excluded:

- **SIH/SUS, older adults with cardiovascular disease:** logistic regression 0.718
  (0.713–0.722), against C = 0.720 for the published model 1; XGBoost 0.724; identical in the
  temporal split (2011 → 2012).
- **SINAN-TB, loss to follow-up:** XGBoost 0.713 (0.709–0.717) against 0.71–0.72, without the
  comparator's 1:1 undersampling before the split; temporal (2015–2019 → 2020–2022) 0.704.
- **SINAN visceral leishmaniasis, death:** the published 14-point score, recomputed on our data,
  gave 0.773 (cross-validation) and 0.766 (temporal) against 0.78 published; XGBoost on the same
  notification fields reached 0.804 and 0.789.
- **SIVEP-Gripe, influenza 2024:** XGBoost 0.826 (0.808–0.845) against an apparent 0.81;
  temporal 0.806.
- **SIVEP-Gripe, paediatric COVID-19:** temporal validation (2020 → 2021) 0.789 (0.770–0.808)
  without ventilation, against 0.750 for the published score that includes it.
- **SIVEP-Gripe, adult COVID-19:** XGBoost 0.791 (0.786–0.795) against 0.813; the comparator
  added municipal HDI, hospital funding, distance to hospital and hospital load, which are not
  in the notification file.
- **SINASC, low birth weight:** 0.753 with pre-delivery information only. With the at-birth information the comparator used
  (weeks of gestation, sex of the newborn, congenital anomaly), logistic regression reached
  0.891 (0.889–0.892) and XGBoost 0.897, against 0.85 published for logistic regression.

Temporal validation lowered the AUROC of the boosted model by 0.000–0.020 compared with random
cross-validation. Calibration slopes of the boosted models were between 0.91 and 1.07.

## 4. Discussion

A benchmark of seven prediction tasks can be built entirely from public Brazilian health files
and, for each task, the published real-data AUROC can be reproduced within about 0.02 when the
published model used only information available at prediction time. The one gap has a clear
cause: the adult COVID-19 comparator added area- and hospital-level variables that are not in
the notification file. For low birth weight, the comparator's number depends on information
known only at birth; with that information our baseline exceeded it, and without it the
task is harder (0.753) but clinically more useful. In the other direction, removing a post-admission predictor
did not lower discrimination in the paediatric COVID-19 task, which suggests that the
published score's ventilation item added little beyond what the notification already
contains.

Three properties distinguish the benchmark from the literature it builds on: each cohort and
its forbidden fields are defined in code; a temporal split is the primary protocol; and every
task reports calibration and AUPRC, which half of the comparators omitted. Because the portal's
licence does not allow redistribution of derived files, the benchmark is distributed as code
and split rules, with file hashes of the downloads.

**Limitations.** Public files cannot be linked across systems by identifiers, which excludes
outcomes such as neonatal death after birth or readmission. Hospital admission records
describe admissions, not patients. Notification forms are filled in variably across regions
and years, and our missing-value handling treats "ignored" and blank alike. Two comparators
report only apparent performance. No task uses laboratory values: the one open Brazilian source
with them, the FAPESP COVID-19 Data Sharing/BR repository, requires registration and acceptance
of terms, which fails criterion (1), and its cohort with a published comparator is small.

## 5. Data and code availability

Code: `src/` (task definitions, baselines, tables). Raw data: public and downloadable without
registration from ftp.datasus.gov.br (SIH/SUS, SINASC, SINAN) and from the Ministry of Health
open-data portal (SIVEP-Gripe, version of 23 March 2026); file names, sizes, dates and SHA-256
hashes are in `docs/manifesto_dados.csv`. `src/baixa_dados.py` downloads every file from its
official source and checks it against the manifest (all 130 files matched on 19 October 2026),
`src/prepara_dbc.sh` converts the DATASUS `.dbc` files, and `src/tarefas.py` builds the cohorts;
no data file is redistributed.

## References

References marked † were not verified in full text in the survey and must be checked before
submission.

1. Almeida AVA, Santos AORD, Nascimento LFC. Predictive modeling with machine learning for low birth weight in the state of São Paulo. *São Paulo Med J* 2026;144(3):e20253373. doi:10.1590/1516-3180.2025.3373.04052026.
2. Baqui P, Marra V, Alaa AM, Bica I, Ercole A, van der Schaar M. Comparing COVID-19 risk factors in Brazil using machine learning: the importance of socioeconomic, demographic and structural factors. *Sci Rep* 2021;11:15591. doi:10.1038/s41598-021-95004-8.
3. Batista AFM, Diniz CSG, Bonilha EA, Kawachi I, Chiavegatto Filho ADP. Neonatal mortality prediction with routinely collected data: a machine learning approach. *BMC Pediatr* 2021;21:322. doi:10.1186/s12887-021-02788-9.
4. Cordeiro P, Martins M. Hospital mortality in older patients in the Brazilian Unified Health System, Southeast region. *Rev Saúde Pública* 2018;52:69. doi:10.11606/S1518-8787.2018052000146.
5. Coura-Vital W, Araújo VEM, Reis IA, Amancio FF, Reis AB, Carneiro M. Prognostic factors and scoring system for death from visceral leishmaniasis: an historical cohort study in Brazil. *PLoS Negl Trop Dis* 2014;8:e3374. doi:10.1371/journal.pntd.0003374.
6. Harutyunyan H, Khachatrian H, Kale DC, Ver Steeg G, Galstyan A. Multitask learning and benchmarking with clinical time series data. *Sci Data* 2019;6:96. †
7. Martins M. Uso de medidas de comorbidades para predição de risco de óbito em pacientes brasileiros hospitalizados. *Rev Saúde Pública* 2010;44(3):448–56. doi:10.1590/S0034-89102010005000003.
8. Oliveira EA, Simões e Silva AC, Oliveira MCL, et al. Comparison of the first and second waves of the COVID-19 pandemic in children and adolescents in a middle-income country. *J Pediatr* 2022;244:178–185.e3. doi:10.1016/j.jpeds.2022.01.001.
9. Rodrigues MMS, Barreto-Duarte B, et al., Andrade BB. Machine learning prediction of loss to follow-up of tuberculosis treatment in Brazil. *BMC Public Health* 2024;24:1385. doi:10.1186/s12889-024-18815-0. (title to be checked †)
10. Saldanha RF, Bastos RR, Barcellos C. Microdatasus: pacote para download e pré-processamento de microdados do Departamento de Informática do SUS (DATASUS). *Cad Saúde Pública* 2019;35(9):e00032419.
11. Sardinha DM, et al. Association between COVID-19 booster vaccination and influenza mortality: a nationwide retrospective cohort study using the SIVEP-Gripe database in Brazil. *Immunol Res* 2026;74:62. doi:10.1007/s12026-026-09792-0. (abstract only †)
12. Schilling MPR, Portela MC, Martins M. Razão de mortalidade hospitalar padronizada: limites e potencialidades do indicador. *Cad Saúde Pública* 2024;40(2). doi:10.1590/0102-311XPT080723.
13. TabArena: a living benchmark for machine learning on tabular data. arXiv:2506.16791, 2025. †
14. van de Water R, Schmidt H, Elbers P, Thoral P, Arnrich B, Rockenschaub P. Yet Another ICU Benchmark: a flexible multi-center framework for clinical machine learning. *ICLR* 2024.
15. Wornow M, Thapa R, Steinberg E, Fries JA, Shah NH. EHRSHOT: an EHR benchmark for few-shot evaluation of foundation models. *NeurIPS Datasets and Benchmarks* 2023.
