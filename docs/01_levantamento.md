# 01 — Levantamento: benchmark de predição clínica com microdado público brasileiro de saúde

> **Status:** levantamento v1, 17/10/2026. Cinco tarefas já definidas pela equipe (três SIVEP rodadas, SINASC e SIH em construção); este documento confere os comparadores publicados, documenta o acesso às bases e recomenda **duas tarefas adicionais** (SINAN-TB e SINAN-LV).
> **Próximo passo bloqueante:** aceite dos termos do FAPESP COVID-19 Data Sharing/BR pelo usuário (tarefa T6), e decisão sobre incluir T7 e T8 (seção 4).

## Como ler este documento

- **Escopo.** Bases públicas, baixáveis e desidentificadas, com pacientes reais, que permitam tarefa binária no nível do paciente/registro (uma linha por paciente), com preditores disponíveis no momento da predição. DATASUS é o núcleo, mas o escopo foi ampliado para outras bases brasileiras abertas.
- **Grau de verificação**, usado em todas as tabelas:
  - **V** — fonte aberta nesta sessão (texto completo ou página oficial).
  - **R** — só o resumo foi aberto (Europe PMC/PubMed).
  - **E** — informação passada pela equipe, não reconferida por mim.
  - **NV** — não verificado (página não abriu, ou vem de memória). Não citar como fato.
- **Nomes de campo.** Nomes de variáveis DATASUS marcados com † vêm de conhecimento prévio dos dicionários e **não foram reconferidos nesta sessão**. Conferir no dicionário oficial antes de codificar.
- Referências ficam no idioma original. Lista completa na seção 6.

---

## 1. Já existe um benchmark de ML com microdado público brasileiro de saúde?

**Resposta curta: não encontrei.** Não há, até onde foi possível verificar, nenhum conjunto fixo de tarefas + coortes + partições + baselines sobre DATASUS ou outra base brasileira aberta, no molde de YAIB, EHRSHOT, benchmarks MIMIC (Harutyunyan 2019) ou TabArena. O que existe são **ferramentas de acesso**, **datasets curados de tarefa única** e **código de artigos isolados**.

| Item | O que é | Tarefas / partições / baselines | Distância de um benchmark | Verif. |
|---|---|---|---|---|
| **PySUS** (github.com/AlertaDengue/PySUS) | Biblioteca Python de download e limpeza: SINAN, SIM, SINASC, SIH, SIA, CIHA, CNES, PNI; lê FTP, dadosabertos.saude.gov.br e espelho S3/Parquet. GPL-3.0 | Nenhuma. Não cita SIVEP | Ferramenta de acesso, não benchmark | V |
| **microdatasus** (github.com/rfsaldanha/microdatasus) | Pacote R de download e recodificação (SIM, SINASC, SIH-RD, SIA-PA, CNES, SINAN). MIT. Saldanha, Bastos & Barcellos, *Cad Saúde Pública* 2019, doi:10.1590/0102-311x00032419 | Nenhuma | Ferramenta de acesso | V |
| **Mendeley Data f6sjz6by8k** — Santos IAB, Barros MHLFS, Endo PT et al., 2024, doi:10.17632/f6sjz6by8k.1, CC BY 4.0 | SIVEP-Gripe 2020–2022 (3.395.398 registros, 166 atributos) pré-processado em 24 atributos para **diagnóstico diferencial COVID-19 vs. influenza** (alvo = CLASSI_FIN), com 4 versões balanceadas (idade; idade+sexo; idade+sexo+região; idade+sexo+desfecho) | Uma tarefa; sem partição fixa nem baseline declarados | Dataset curado de tarefa única. Alvo é diagnóstico, não prognóstico. Balanceamento "por desfecho" impede estimar desempenho na prevalência real | V |
| **XCOVID-BR** (github.com/PedroBaqui/XCOVID-BR) | Código e modelo de Baqui et al. 2021 (SIVEP, óbito COVID) | Uma tarefa, split 80/20 do artigo | Código de artigo reprodutível; não é benchmark | V (link no artigo) |
| **TBPrediction** (github.com/rodriguesmsb/TBPrediction) | Código de Rodrigues et al. 2024 (SINAN-TB, perda de seguimento) | Uma tarefa | Idem | V (link no artigo) |
| **Meningitis-DiagnosisML** (GitHub, Audency) | Código de Victor et al. 2025 (SINAN meningite SP) | Uma tarefa diagnóstica | Idem | V (citado no artigo, não aberto) |
| PMLB, OpenML-CC18, TabArena, TabZilla, Grinsztajn | Coleções gerais de datasets tabulares | Não identifiquei base de saúde brasileira nelas | — | NV (busca não exaustiva) |
| FAPESP COVID-19 Data Sharing/BR | Repositório aberto de dados de 5 instituições (ver 3.2) | Sem tarefas definidas | Fonte de dado, não benchmark | V |

**Ressalva.** A busca dedicada a benchmarks (Hugging Face, Kaggle, Papers with Code, OpenML) foi delegada e não retornou até o fechamento desta versão. O veredito acima se apoia nas buscas diretas que fiz (GitHub/benchmark/SIVEP/DATASUS) e no fato de nenhum dos ~20 artigos lidos citar um benchmark brasileiro. Grau de confiança: moderado. Se um benchmark aparecer depois, a seção 4 continua válida como desenho, mas o enquadramento de "primeiro benchmark" teria de cair.

**Implicação.** A lacuna é real e o produto diferencial do projeto é exatamente o que falta: **partições fixas (incluindo temporal), definição de coorte em código, lista de preditores por momento de predição e comparação com AUROC publicada**.

---

## 2. Estudos publicados com dado real e AUROC para desfecho binário individual

Legenda: **aparente** = AUROC medida nos mesmos dados de ajuste (sem validação). n.r. = não reportado.

### 2.1 SIVEP-Gripe (SRAG hospitalizada)

| # | Referência | Período | Coorte | Desfecho | Preditores | Momento | Modelo / validação | n; eventos | AUROC | Código | Verif. |
|---|---|---|---|---|---|---|---|---|---|---|---|
| S1 | Baqui P, Marra V, Alaa AM, Bica I, Ercole A, van der Schaar M. Comparing COVID-19 risk factors in Brazil using machine learning: the importance of socioeconomic, demographic and structural factors. *Sci Rep* 2021;11:15591. doi:10.1038/s41598-021-95004-8 | 25/02–21/09/2020 | Hospitalizados com RT-PCR+ para SARS-CoV-2, desfecho conhecido, idade ≤110, com geografia e tipo de financiamento (público/privado) | Óbito hospitalar vs. alta | 30 candidatos: idade, sexo, raça/cor, comorbidades, sintomas, escolaridade, UF, IDHM, tipo de cidade, **distância paciente–hospital**, **pressão hospitalar** (internações da semana / internações SIVEP 2019), financiamento | Não explicitado (admissão, implícito) | XGBoost (XCOVID-BR), LR, KNN, RF, SVM, NN. Split aleatório 80/20 + CV 10 | 231.112; 87.223 (37,7%) | XGBoost **0,813 (0,810–0,817)**; LR 0,766 (0,761–0,770) | Sim | V |
| S2 | Oliveira EA, Simões e Silva AC, Oliveira MCL, Colosimo EA, Mak RH, et al. Comparison of the first and second waves of the COVID-19 pandemic in children and adolescents in a middle-income country: clinical impact associated with SARS-CoV-2 Gamma lineage. *J Pediatr* 2022;244:178–185.e3. doi:10.1016/j.jpeds.2022.01.001 | Onda 1: 16/02–31/12/2020; Onda 2: 01/01–29/05/2021 | <20 anos, hospitalizados, RT-PCR+ | Óbito hospitalar (riscos competitivos, alta como evento competidor) | Faixa etária, região, raça/cor, nº de sintomas respiratórios, nº de comorbidades, **"ventilação invasiva sem UTI"** | Admissão (mas ver vazamento) | Escore de pontos; derivação onda 1, **validação temporal onda 2**; imputação múltipla | Derivação 11.428 / 896; validação 9.988 / 765 (≈7,7%) | Derivação 0,762 (0,746–0,779); **validação 0,750 (0,741–0,758)** | Não | V |
| S3 | Sardinha DM, Neves NMM, Soares TN, et al. Association between COVID-19 booster vaccination and influenza mortality: a nationwide retrospective cohort study using the SIVEP-Gripe database in Brazil. *Immunol Res* 2026;74:62. doi:10.1007/s12026-026-09792-0 | 2024 | Adultos hospitalizados com influenza confirmada por RT-PCR, desfecho conhecido | Óbito hospitalar | Regressão multivariável: vacina influenza, reforço COVID, **oseltamivir**, dispneia, desconforto respiratório, SpO2 baixa, obesidade, diabetes, doença hepática, imunossupressão, tipo viral (A/B) | Admissão (inferencial) | LR + IPTW; sem validação | 15.995; ≈1.935 (12,1%) | **0,81 (0,80–0,82)**, aparente | n.r. | R |
| S4 | Leung C, Su L, Simões e Silva AC. *Int J Epidemiol* 2022;51:1733–44. doi:10.1093/ije/dyac157 | 2020–2021 | Gestantes e puérperas com COVID RT-PCR+ | Óbito hospitalar | Clínicos e sociodemográficos; **UTI e ventilação excluídas** | Admissão | Modelo explicativo; sem validação | 9.389; 11,4% | 0,775 (0,761–0,788), aparente | n.r. | V (agente) |
| S5 | Cini Oliveira M, Eleuterio TA, et al., Medronho RA. *BMC Infect Dis* 2021;21:687. doi:10.1186/s12879-021-06384-1 | Mar–set/2020, município do RJ | e-SUS Notifica (SG) + SIVEP (SRAG) **linkados ao SIM** | Óbito (SIM) | Sociodemográficos, sintomas, comorbidades | Notificação | XGBoost + SMOTE-ENN (ordem em relação ao split n.r.) | 243.509; 18.076 (7,4%) | 0,94 | n.r. | V (agente) |

Outros SIVEP vistos e **não usados como comparador**: Oliveira EA et al. *Lancet Child Adolesc Health* 2021 (estimação de fatores de risco; os próprios autores dizem que não é modelo preditivo); Lages dos Santos et al., *PeerJ Comput Sci* 2025 (12 modelos, óbito pediátrico, LR AUROC 0,801; R, desenho de validação não confirmado).

**Pendente:** a busca dedicada a SIVEP (Wollenstein-Betech 2020, de Souza 2021 *PLoS One*, Fernandes 2021 *Sci Rep* etc.) não retornou até esta versão. Os comparadores das três tarefas SIVEP já estão cobertos por S1–S3.

### 2.2 SIH/SUS (AIH reduzida, RD)

| # | Referência | Período | Coorte | Desfecho | Preditores | Modelo / validação | n; eventos | AUROC (C) | Verif. |
|---|---|---|---|---|---|---|---|---|---|
| H1 | Cordeiro P, Martins M. Hospital mortality in older patients in the Brazilian Unified Health System, Southeast region. *Rev Saúde Pública* 2018;52:69. doi:10.11606/s1518-8787.2018052000146 | 2011–2012 | Idade ≥60, hospitais SUS de MG, ES, RJ e SP; diagnóstico principal I10, I11, I15 (hipertensivas), I20–I22, I24, I25 (isquêmica), I50 (ICC), I60–I64 (AVC); AIH tipo 1 (tipo 5 excluída); alta ou óbito; hospitais com <500 internações excluídos | Óbito hospitalar | **Modelo 1:** faixa etária, sexo, diagnóstico principal, caráter (eletiva/urgência), Charlson (Quan), condições de Elixhauser (anemia, arritmia, hipertensão, hipo/hipertireoidismo, perda de peso, outras neurológicas), pneumonia J18, outro diagnóstico secundário. **Modelo 2:** + tempo de permanência. **Modelo 3:** + cirurgia + UTI | Regressão logística; **sem validação**, sem Hosmer-Lemeshow | 385.784; 50.317 (13,0%) | **Modelo 1: 0,720 (0,717–0,722)**; M2 0,768; M3 0,795 (aparentes) | V |

Comorbidade veio do **único campo de diagnóstico secundário** do SIH na época. Pelo artigo, esse campo é preenchido na saída, o que é limitação conhecida.

**Pendente:** busca dedicada a SIH (IAM, AVC, fratura de fêmur, CRM; ex.: Piegas 2009 *Arq Bras Cardiol*; Noronha 2004 *Cad Saúde Pública*) não retornou até esta versão. O comparador da tarefa SIH da equipe está coberto por H1.

### 2.3 SINASC e SINASC–SIM

| # | Referência | Período / região | Coorte | Desfecho | Preditores | Modelo / validação | n; eventos | AUROC | Verif. |
|---|---|---|---|---|---|---|---|---|---|
| N1 | Almeida AVA, Santos AORD, Nascimento LFC. Predictive modeling with machine learning for low birth weight in the state of São Paulo: a retrospective population-based study. *São Paulo Med J* 2026;144(3):e20253373. doi:10.1590/1516-3180.2025.3373.04052026 | SP, 2019–2023 | Todos os nascidos vivos; exclusão de registros com campo faltante ou "ignorado" (análise de caso completo); gemelares mantidos | Peso <2.500 g | Idade materna, filhos mortos prévios, paridade, tipo de gravidez, escolaridade, estado civil, raça/cor, nº de consultas, mês de início do pré-natal, **idade gestacional ao nascer (categoria)**, **anomalia congênita**, **sexo do RN** | LR e RF (class_weight); split aleatório 80/20 | 2.548.570; 241.065 (9,46%) | **LR 0,850**; RF 0,81 (não balanceado), 0,78 (balanceado); AUPRC LR 0,57–0,60 | V |
| N2 | Magalhães SCO, Azevedo KS, de Souza LC, Dalmolin M, Fernandes MAC. Predição de mortalidade em prematuros no Brasil com otimização de limiar orientada à sensibilidade clínica e validação temporal. *Anais SBCAS* 2026:13–24. doi:10.5753/sbcas.2026.20234 | Brasil, 2014–2022 | Prematuros; **coorte nacional vinculada SINASC–SIM** | Óbito até 365 dias | n.r. na página | XGBoost; validação temporal 2021–2022 | 3.064.338; 1,78% | 0,930 (geral); **0,931 (temporal)** | R (anais, não periódico) |

**Atenção, N1:** o comparador inclui idade gestacional ao nascer, anomalia e sexo, que só são conhecidos no parto. Uma tarefa com preditores **só pré-parto** (como a da equipe) deve esperar AUROC menor. A diferença é de desenho e não indica pior modelo. Reportar as duas versões (com e sem IG) para fechar a comparação.

**N2** depende de linkage SINASC–SIM com identificadores, inviável só com arquivos públicos. Serve como referência, não como tarefa.

**Pendente:** Batista AFM et al., *BMC Pediatr* 2021 (óbito neonatal, SP, SINASC–SIM) e demais estudos SINASC; a busca dedicada não retornou.

### 2.4 SINAN e e-SUS Notifica (seção completa)

**Achado principal:** não encontrei ML revisado por pares com AUROC para **óbito ou internação por dengue/chikungunya** com SINAN nacional. O único prognóstico de dengue com AUROC (Pinto 2016) é regressão logística aparente, regional e com linkage ao SIM. Os trabalhos de ML com SINAN-dengue são **diagnósticos** (caso confirmado vs. descartado). Há um protocolo em preprint (Delpino FM et al., medRxiv 2026, SINAN 2017–2025, validação temporal) que não consegui abrir (NV).

#### 2.4.1 Prognóstico com SINAN / e-SUS e AUROC

| # | Referência | Agravo, base, período | Coorte | Desfecho | Preditores | Modelo / validação | n; eventos | AUROC | Código | Verif. |
|---|---|---|---|---|---|---|---|---|---|---|
| A1 | Rodrigues MMS, Barreto-Duarte B, et al., Andrade BB. *BMC Public Health* 2024;24:1385. doi:10.1186/s12889-024-18815-0 | **Tuberculose**, SINAN-TB nacional, 2015–2022 | Adultos ≥18 com TB **pulmonar**. Excluídos: diagnóstico pós-morte; populações especiais (situação de rua, privados de liberdade, gestantes, imigrantes, profissionais de saúde); resistência a R/H/Z/E; formas pulmonar + extrapulmonar; desfechos que não fossem cura ou perda de seguimento | **Perda de seguimento** (abandono) vs. cura | 8 de linha de base (RFECV): escolaridade, sexo, TB prévia, HIV, álcool, drogas, tabaco, idade | LR, RF, LightGBM. **Subamostragem 1:1 antes do split**; 70/30 (Métodos) ou 80/20 (resumo); calibração e SHAP | 243.726; 41.373 (17%) | **0,71–0,72** (sem IC; por modelo só no suplemento) | Sim | V |
| A2 | Lima SVMA, Araújo KCGM, Nunes MAP, Nunes C. *Heliyon* 2021;7:e06788. doi:10.1016/j.heliyon.2021.e06788 | Tuberculose, SINAN-TB Sergipe, 2015–2018 | Casos com desfecho de perda de seguimento ou conclusão | Perda de seguimento | Multinível, seleção backward | Logística + nomograma; sem validação | 2.449; 18,2% | 0,771 (0,741–0,802), aparente | n.r. | V (agente) |
| A3 | Coura-Vital W, Araújo VEM, Reis IA, Amancio FF, Reis AB, Carneiro M. *PLoS Negl Trop Dis* 2014;8:e3374. doi:10.1371/journal.pntd.0003374 | **Leishmaniose visceral**, SINAN nacional, 2007–2011 | Casos novos confirmados com desfecho cura ou óbito por LV. Excluídos: não confirmados, classificação faltante, óbito por outra causa, abandono, transferência, desfecho faltante | Óbito por LV vs. cura | Escore 0–14 "na suspeita clínica": sangramento (3 pts); esplenomegalia, edema, fraqueza, icterícia, coinfecção HIV, infecção bacteriana (1 pt cada); idade (≤0,5 a: 5; 0,5–1: 2; 1–19: 0; 19–50: 2; 50–65: 3; ≥65: 5) | Logística → escore; **split aleatório estratificado 2/3 vs. 1/3** | 18.501; 1.156 (6,2%). Derivação 12.333 / 770; validação 6.168 / ≈386 | Derivação 0,80 (0,78–0,82); **validação 0,78 (0,75–0,81)**; calibração boa exceto escores 11–13 | n.r. | V |
| A4 | de Araújo VEM, Morais MHF, Reis IA, Rabello A, Carneiro M. *PLoS Negl Trop Dis* 2012;6:e1511. doi:10.1371/journal.pntd.0001511 | LV, SINAN + SIM, Belo Horizonte, 2002–2009 | Casos de LV | Óbito por LV | Sinais clínicos (parte registrada no acompanhamento, segundo os autores) | Logística/escore; aparente | 888; 111 | 0,756, aparente | n.r. | V (agente) |
| A5 | Pinto RC, Castro DB, et al., Braga JU. *PLoS ONE* 2016;11:e0161884. doi:10.1371/journal.pone.0161884 | **Dengue**, SINAN + SIM, Amazonas, 2001–2013 | Dengue grave confirmada | Óbito | Sinais e exames da internação (sangramento, plaquetas etc.) | Logística stepwise; aparente | 1.605; 61 (3,8%) | 0,843, aparente | n.r. | V (agente) |
| A6 | Cini Oliveira M et al. 2021 (= S5) | COVID, e-SUS Notifica + SIVEP + SIM, RJ | — | Óbito via SIM | — | — | 243.509; 18.076 | 0,94 | — | V (agente) |
| A7 | De Souza FSH, Hojo-Souza NS, dos Santos EB, da Silva CM, Guidoni DL. *Front Artif Intell* 2021;4:579931. doi:10.3389/frai.2021.579931 | COVID, portal estadual de notificações do ES (provavelmente e-SUS VS; inferência), fev–mai/2020 | Só casos encerrados | Óbito vs. cura | Sociodemográficos, sintomas, comorbidades | 7 modelos; oversampling nos folds; **validação temporal** | 4.826 treino (8,2%); 3.617 validação (6,1%) | 0,92 (melhor modelo, não confirmado qual) | n.r. | V (agente) |

#### 2.4.2 Outros SINAN com AUROC: diagnóstico ou risco de vazamento por construção

| # | Referência | Base e desfecho | n; prevalência | AUROC | Por que não serve como comparador limpo | Verif. |
|---|---|---|---|---|---|---|
| A8 | Freitas LRS, Freitas JAO, Penna GO, Duarte EC. *Trop Med Infect Dis* 2025;10:131. doi:10.3390/tropicalmed10050131 | **Hanseníase** 2018–2022; grau 2 de incapacidade no diagnóstico | 128.069; 11,6% | 0,89–0,94 por região | Transversal. Nº de nervos afetados, forma clínica e classificação PB/MB saem do mesmo exame que gradua a incapacidade. SMOTE sem ordem informada | V (agente) |
| A9 | Victor A, Santos DAM, et al., Carvalhanas TRMP. *PLOS Digit Health* 2025;4:e0000925. doi:10.1371/journal.pdig.0000925 | **Meningite** SP 2007–2024; etiologia bacteriana | 101.224; 27% | CatBoost 0,95 | Diagnóstico. Leucócitos no líquor entram na definição de caso. Especificidade 0,09–0,17. Código no GitHub | V (agente) |
| A10 | Reis BQ, Raposo LM. *Int J Med Inform* 2026;222:106736. doi:10.1016/j.ijmedinf.2026.106736 | Transtorno mental relacionado ao trabalho (SINAN) 2006–2025; afastamento | 21.601; 64,3% | RF 0,697 (0,682–0,710); AUPRC 0,802 | Desfecho não clínico, prevalência alta. É o estudo mais alinhado ao TRIPOD+AI desta lista | V (agente) |
| — | Lu X et al. *Front Med* 2026, doi:10.3389/fmed.2026.1814257 | Chikungunya confirmada vs. descartada | — | 0,785 | Diagnóstico | R |
| — | Nguyen TH, Le NQK. *TMID* 2026, doi:10.3390/tropicalmed11020040 | Arboviroses, multiclasse | — | 0,99 com SMOTE | Diagnóstico; provavelmente inflada | R |
| — | Bohm BC et al. *BMC Public Health* 2024, doi:10.1186/s12889-024-19083-8 | Dengue confirmada vs. descartada | — | só acurácia | Sem AUROC | R |

**Descartados ou sem AUROC:**
- Filho FGS et al., *J Clin Med* 2025 (TBWEB-SP, não SINAN): usa duração do tratamento, doses e situação de encerramento como preditores.
- Phat NK et al., *BMC Med Inform Decis Mak* 2025 (SINAN-TB óbito): só sensibilidade e especificidade.
- Silva AF et al., *Sci Rep* 2024 (leptospirose PA): só acurácia.
- Mendonça MFS et al., *RSBMT* 2023 (dengue/chik PE): fatores associados.
- Coelho LG et al., *Microorganisms* 2026: só OR.
- Barros MHLFS et al., *Informatics* 2021;8:27 (óbito por TB, AM, 24.015 casos, 1.139 óbitos): AUROC não lida (NV, página 403).
- Sífilis congênita (Teixeira 2023, dados do Programa Mãe Coruja, não SINAN), animais peçonhentos, Chagas, HIV/AIDS, sífilis gestacional: nada revisado por pares com AUROC encontrado.

**e-SUS Notifica não tem óbito confiável.** O único estudo forte com essa base (S5/A6) obteve o óbito por linkage ao SIM.

#### 2.4.3 Riscos de vazamento recorrentes na literatura SINAN

1. **Subamostragem ou SMOTE antes do split.** É certo em A1 e possível em A6, A8 e A9. O teste fica balanceado, então AUPRC, VPP e calibração deixam de valer na prevalência real. A AUROC é pouco sensível a isso, mas não imune.
2. **Preditor do mesmo exame que define o desfecho** (A8, A9).
3. **Sinais registrados na investigação, depois da notificação** (A3–A5). Na ficha de dengue, sinais de alarme, sinais de gravidade, HOSPITALIZ e CLASSI_FIN embutem gravidade; isto é inferência minha, não lida em artigo.
4. **Coorte restrita a casos encerrados ou com desfecho conhecido** (A2, A3, A7), o que gera seleção dependente do desfecho.
5. **AUROC aparente** em A2, A4, A5, S3, S4 e H1. Validação temporal só em S2, A7 e N2; externa em nenhum.

### 2.5 Bases não DATASUS

| # | Referência | Base | Coorte / desfecho | Preditores | Validação | n; eventos | AUROC | Verif. |
|---|---|---|---|---|---|---|---|---|
| F1 | Araújo DC, Veloso AA, Borges KBG, Carvalho MG. Prognosing the risk of COVID-19 death through a machine learning-based routine blood panel: a retrospective study in Brazil. *Int J Med Inform* 2022;165:104835. doi:10.1016/j.ijmedinf.2022.104835 | "Dois grandes hospitais brasileiros" (resumo). A equipe informa HSL + BP, do FAPESP COVID-19 Data Sharing/BR (E; o resumo não nomeia) | Internados RT-PCR+; óbito vs. alta | Hemograma (linfócitos, VCM, plaquetas, RDW) + PCR, janela de 24 h | 5 cenários, 2 com validação externa | 6.979; 291 (4,2%) | **0,91 ± 0,01** (média) | R + E |

**Pendente (busca delegada sem retorno; tudo NV):** Einstein/Kaggle "Diagnosis of COVID-19 and its clinical spectrum" (≈5.644 pacientes; positividade e admissão em enfermaria/semi-UTI/UTI); Sírio-Libanês/Kaggle ICU (≈385 pacientes, pequeno demais para o critério de eventos); PNS 2013/2019 e Vigitel (inquéritos de desfecho autorreferido; exigem tratamento de desenho amostral); ELSA-Brasil e Brazilian COVID-19 Registry (acesso por proposta, provavelmente restrito); SPNeoDeath (Synapse; condições não verificadas).

**ELSI-Brasil:** os arquivos públicos não têm variável de óbito (E: conferido pela equipe).

---

## 3. Acesso prático às bases

### 3.1 DATASUS / Ministério da Saúde

Fatos de infraestrutura verificados em 17/10/2026:

- **opendatasus.saude.gov.br redireciona (302) para dadosabertos.saude.gov.br** (Portal de Dados Abertos do SUS, CKAN). Links antigos de artigos (ex.: `opendatasus.saude.gov.br/dataset/srag-2021-a-2024`) não abrem mais o dataset. Usar os slugs novos abaixo.
- **Licença declarada pelo portal: Creative Commons Atribuição-SemDerivações 3.0 (CC BY-ND 3.0).** "SemDerivações" é uma restrição relevante para um benchmark. **Recomendação:** distribuir **código de construção de coorte + hashes/IDs de partição**, e não arquivos derivados. O ND é discutível para dado bruto de governo, mas evitar redistribuir é a escolha conservadora.
- **FTP ftp://ftp.datasus.gov.br/dissemin/publicos/ continua no ar** (listado por curl em 17/10/2026). Diretórios: ANS, CIH, CIHA, CMD, CNES, Dados_Abertos, ESUSNOTIFICA, IBGE, PNI, SIASUS, SIHSUS, SIM, SINAN, SINASC, SISCAN, SISPRENATAL, entre outros. Acesso por HTTPS ao mesmo host recusou conexão. A página datasus.saude.gov.br/transferencia-de-arquivos/ tem formulário web dinâmico (V).
- **Formato .dbc** (dBase comprimido, específico do DATASUS). Ler com `read.dbc`/microdatasus (R) ou PySUS/`pyreaddbc` (Python).
- **Desidentificação:** arquivos públicos não trazem nome, CPF ou CNS. A página SRAG diz que as bases "passam por tratamento que envolve a anonimização", em linha com a LGPD (V). Ficam quase-identificadores: datas, município, CNES do estabelecimento.
- **Linkage entre sistemas com arquivos públicos: não é possível de forma determinística** (sem identificador comum). Estudos com SINASC–SIM (N2) ou SINAN/e-SUS–SIM (S5, A4, A5) usaram dados identificados sob acordo. Não verifiquei se o DO público traz NUMERODN para óbitos infantis (NV); mesmo que traga, o vínculo cobriria só uma parte e deve ser tratado como experimental.

| Base | Onde baixar (verificado) | Formato | Anos disponíveis | Tamanho observado | Verif. |
|---|---|---|---|---|---|
| **SIVEP-Gripe (SRAG hospitalizado)** | dadosabertos.saude.gov.br/dataset/**srag-2019-a-2026**; também srag-2013-2018 e srag-2009-2012. Dicionário "2019 a 2025 – Dicionário de Dados" no mesmo dataset | CSV, JSON, **Parquet**, XML por ano | 2009–2026. Bases 2019–2024 descritas como "congeladas", mas os recursos têm rótulo "Banco vivo 23/03/2026" (inconsistência da própria página). 2025–2026 atualizados semanalmente (última: 12/10/2026) | Não exibido | V |
| **SIH/SUS RD** | ftp://ftp.datasus.gov.br/dissemin/publicos/SIHSUS/200801_/Dados/RD{UF}{AA}{MM}.dbc | .dbc mensal por UF | 2008→ nesse diretório (anos anteriores em diretório próprio, NV) | RDSP1101.dbc = 13,6 MB (SP, 1 mês) | V (listagem e tamanho) |
| **SINASC** | ftp://…/SINASC/1996_/Dados/DNRES/DN{UF}{AAAA}.dbc; preliminares em SINASC/PRELIM/DNRES/ | .dbc anual por UF | Definitivos até 2024; preliminares 2025–2026 | DNSP2023.dbc = 24,8 MB | V |
| **SIM** | ftp://…/SIM/CID10/DORES/DO{UF}{AAAA}.dbc | .dbc anual por UF | Até 2024 (DOSP2024 listado) | — | V |
| **SINAN (agravos)** | ftp://…/SINAN/DADOS/FINAIS/{AGRAVO}BR{AA}.dbc e …/SINAN/DADOS/PRELIM/ | .dbc anual nacional | **Dengue:** finais 2000–2025, prelim 2026. **TB (TUBE):** finais 2001–2019, **prelim 2020–2025**. **LV (LEIV):** finais 2000–2025 | DENGBR24 = 287,6 MB; TUBEBR19 = 5,3 MB; LEIVBR19 = 0,55 MB | V |
| **SINAN dengue/chik/zika (portal)** | dadosabertos.saude.gov.br/dataset/arboviroses-dengue (e -febre-de-chikungunya, -zika-virus); dicionário de dados de dengue atualizado em 14/07/2025 | Não exibido (recursos por ano, 2000–2026) | 2000–2026, atualização semanal | — | V |
| **e-SUS Notifica** | ftp://…/ESUSNOTIFICA/ (diretório listado); portal dadosabertos | — | — | — | Parcial (só existência do diretório). Óbito não confiável (2.4) |
| **SIA/SUS, CNES** | ftp://…/SIASUS/, ftp://…/CNES/ (listados) | .dbc mensal | — | — | Parcial |

**Observações por base (todas NV salvo indicação):**
- **SIH:** uma internação longa gera várias AIH (tipo 5 = longa permanência; Cordeiro & Martins usaram só tipo 1, V). Transferências geram registros duplicados do mesmo episódio. Os diagnósticos secundários passaram a ter vários campos (DIAGSEC1–9†) em anos recentes; em 2011–2012 havia um campo (V, pelo artigo H1). Valores e caráter de atendimento mudam com as portarias de tabela SIGTAP.
- **SINAN TB:** a mudança de FINAIS para PRELIM em 2020 importa. Registros preliminares têm encerramento incompleto, e casos sem SITUA_ENCE† preenchida enviesam a coorte em direção a desfechos rápidos.
- **SIVEP:** a ficha mudou em 2019/2020 (inclusão de COVID-19), em 2021 (campos de vacina COVID) e em anos seguintes. Conferir o dicionário de cada ano.

### 3.2 Bases não DATASUS

| Base | Acesso | Conteúdo | Licença | Verif. |
|---|---|---|---|---|
| **FAPESP COVID-19 Data Sharing/BR** (repositoriodatasharingfapesp.uspdigital.usp.br) | Página diz "aberto e gratuito"; há login no site. A equipe informa que o download exige **aceite de termos de uso** pelo usuário (E) | 5 instituições: Fleury, Einstein, Sírio-Libanês (30/06/2020), HC-FMUSP (17/02/2021), Beneficência Portuguesa (28/04/2021). Demografia (sexo, ano de nascimento, região), exames laboratoriais, movimentação hospitalar e **desfecho (recuperação/óbito) quando disponível** | **CC-BY**; citação obrigatória; dados pseudonimizados pelas instituições | V |
| Einstein/Kaggle, Sírio-Libanês/Kaggle | Conta Kaggle (registro gratuito) | Ver 2.5 | NV | NV |
| ELSI-Brasil | Arquivos públicos | Sem variável de óbito | — | E |
| ELSA-Brasil, Brazilian COVID-19 Registry | Provavelmente por proposta | — | — | NV |

---

## 4. Recomendação: conjunto final de tarefas

### 4.1 Critérios aplicados

(a) só arquivos públicos, desidentificados e sem linkage por identificador; (b) pelo menos um comparador publicado com dado real e AUROC; (c) sistemas e tipos de desfecho diferentes; (d) ≥ algumas centenas de eventos; (e) preditores conhecidos no momento da predição. Para as tarefas novas, exigência adicional da equipe: comparador **verificado** e download **sem credencial**.

### 4.2 Conjunto recomendado (8 tarefas)

| ID | Tarefa | Base / anos | Status | Comparador (AUROC) | Eventos esperados | Acesso |
|---|---|---|---|---|---|---|
| T1 | Óbito hospitalar por COVID-19, adultos (e versão todas as idades) | SIVEP-Gripe 2020 | **Rodada** | Baqui 2021: XGBoost 0,813; LR 0,766 (split aleatório) | ~87 mil (37,7% no recorte de Baqui) | Livre |
| T2 | Óbito hospitalar por COVID-19, <20 anos, validação temporal 2020→2021 | SIVEP-Gripe 2020–2021 | **Rodada** | Oliveira 2022: validação temporal 0,750 | 896 + 765 | Livre |
| T3 | Óbito hospitalar por influenza | SIVEP-Gripe 2024 | **Rodada** | Sardinha 2026: 0,81 (aparente) | ~1.900 | Livre |
| T4 | Baixo peso ao nascer, preditores só pré-parto | SINASC SP 2019–2023 | Em construção | Almeida 2026: LR 0,850 (**com IG ao nascer**) | ~241 mil | Livre (FTP) |
| T5 | Óbito hospitalar em idosos com diagnóstico principal cardiovascular | SIH/SUS RD, Sudeste, 2011–2012 | Em construção | Cordeiro & Martins 2018: modelo 1 C = 0,720 | ~50 mil | Livre (FTP) |
| T6 | Óbito em COVID-19 hospitalizado a partir de exames de 24 h | FAPESP COVID-19 Data Sharing (HSL + BP) | **Aguardando aceite de termos** | Araújo 2022: 0,91 ± 0,01 | ~291 (limítrofe) | Termos de uso |
| **T7** | **Perda de seguimento no tratamento da TB pulmonar** | **SINAN-TB 2015–2019 (finais) + 2020–2022 (prelim.)** | **Nova, recomendada** | **Rodrigues 2024: 0,71–0,72**; Lima 2021: 0,771 (aparente, regional) | ~41 mil | Livre (FTP) |
| **T8** | **Óbito por leishmaniose visceral** | **SINAN-LV 2007–2011 (+ 2012–2019 para validação temporal)** | **Nova, recomendada** | **Coura-Vital 2014: validação 0,78 (0,75–0,81)** | 1.156 em 2007–2011 | Livre (FTP) |

**Por que só duas novas, e por que estas:**
- **T7 e T8 cumprem todos os critérios.** O comparador é verificado em texto completo, nacional e com validação em dados separados; os arquivos estão no FTP sem credencial (verificado); há eventos de sobra. As duas também trazem coisas que o conjunto ainda não tem: **desfecho de processo de cuidado** (adesão, em T7) e **doença negligenciada com escore clínico simples** (T8, bom teste para ver se o ML supera um escore de 14 pontos). T7 tem código público do comparador.
- **Dengue grave/óbito: não recomendado agora.** Não há comparador validado com SINAN público. Pinto 2016 é aparente, regional e linkado ao SIM; os estudos de ML com dengue são diagnósticos. Reavaliar quando o protocolo Delpino 2026 virar artigo.
- **Hanseníase (A8) e meningite (A9): não recomendados.** O comparador tem vazamento por construção (2.4.2), então "bater" ou "perder" do número publicado não significa nada.
- **COVID em gestantes (S4):** viável, mas seria a quarta tarefa SIVEP e o comparador é aparente. Fica como reserva.
- **Óbito neonatal/infantil (N2):** exige linkage SINASC–SIM; fora do critério (a).

### 4.3 Especificação das tarefas novas

#### T7 — Perda de seguimento no tratamento da TB pulmonar (SINAN-TB)

| Item | Especificação |
|---|---|
| Arquivos | TUBEBR15–19.dbc (FINAIS) e TUBEBR20–22.dbc (PRELIM), ftp://ftp.datasus.gov.br/dissemin/publicos/SINAN/DADOS/ |
| Inclusão (replicando Rodrigues 2024) | Idade ≥18; forma pulmonar exclusiva (FORMA† = pulmonar); excluir diagnóstico pós-morte; excluir populações especiais (POP_RUA†, POP_LIBER†, gestante, imigrante POP_IMIG†, profissional de saúde POP_SAUDE†); excluir resistência a R/H/Z/E (campos de TSA/TRM†); manter só encerramento cura ou abandono. Rodrigues não declara se usou só caso novo; **recomendo fixar TRATAMENTO† = caso novo** e reportar análise de sensibilidade com todos os tipos de entrada |
| Desfecho | SITUA_ENCE† = abandono (incluir "abandono primário", código separado em versões recentes, decisão a documentar) vs. cura |
| Preditores no momento da notificação | Os 8 do comparador (idade, sexo, escolaridade, TB prévia via TRATAMENTO†, HIV†, alcoolismo AGRAVALCOO†, drogas AGRAVDROGA†, tabagismo AGRAVTABAC†) + outros da ficha de notificação: raça/cor, AIDS AGRAVAIDS†, diabetes AGRAVDIABE†, doença mental AGRAVDOENC†, baciloscopia de escarro do diagnóstico BACILOSC_E†, raio-X RAIOX_TORA†, teste molecular TESTE_MOLE†, beneficiário de transferência de renda BENEF_GOV†, UF/município de residência |
| **Vazamento a excluir** | Campos de acompanhamento: baciloscopias de 2º–6º mês (BACILOSC_1…6†), TRAT_SUPER† (TDO realizado), DT_ENCERRA†, DT_MUDANCA†, contatos examinados†, resultado de cultura liberado depois, nº de contatos registrados no seguimento |
| Partições | (i) réplica: split aleatório estratificado **sem subamostragem prévia** (reportar também a versão subamostrada, para comparar com Rodrigues); (ii) principal: **temporal 2015–2019 → 2020–2022** |
| Armadilhas | Desfechos faltantes concentrados em PRELIM (2020+) e efeito da pandemia no abandono; o comparador subamostrou antes do split (teste balanceado; AUROC comparável, AUPRC não); inconsistências internas no artigo (8 vs. 6 vs. 7 preditores; 70/30 vs. 80/20) |

#### T8 — Óbito por leishmaniose visceral (SINAN-LV)

| Item | Especificação |
|---|---|
| Arquivos | LEIVBR07–11.dbc (desenvolvimento) e LEIVBR12–19.dbc (validação temporal), FINAIS |
| Inclusão (replicando Coura-Vital 2014) | Casos novos†, confirmados (CLASSI_FIN† = confirmado), evolução cura ou óbito por LV. Excluir: óbito por outra causa, abandono, transferência, desfecho ou classificação faltante |
| Desfecho | EVOLUCAO† = óbito por LV vs. cura |
| Preditores na suspeita clínica | Idade (em dias/anos, NU_IDADE_N† decodificado), sexo, raça/cor, UF, sinais da ficha: febre, fraqueza, edema, emagrecimento, tosse/diarreia, palidez, esplenomegalia, hepatomegalia, quadro infeccioso, fenômenos hemorrágicos, icterícia (nomes de campo†); coinfecção HIV† |
| **Vazamento a excluir** | Droga inicial, dose e falência de tratamento†, DT_OBITO†, data de encerramento†, critério de confirmação se registrado depois (avaliar) |
| Partições | (i) réplica: split aleatório estratificado 2/3–1/3 em 2007–2011; (ii) principal: temporal 2007–2011 → 2012–2019 |
| Baseline obrigatório | O **escore de 14 pontos** de Coura-Vital, recalculado nos nossos dados, ao lado de LR e GBM. Com isso a comparação fica contra o mesmo escore no mesmo dado, além do número publicado |
| Armadilhas | Parte dos sinais pode ter sido registrada no acompanhamento, e não na notificação (de Araújo 2012 admite isso para BH); excluir abandono e transferência gera seleção dependente do desfecho (replicar, mas reportar uma sensibilidade com abandono/transferência como "não óbito"); calibração ruim nos extremos do escore |

### 4.4 Notas sobre as cinco tarefas já definidas (conferência dos comparadores)

| Tarefa | O que conferi | Cuidado para a comparação |
|---|---|---|
| T1 (Baqui) | V, texto completo | Baqui usa **distância paciente–hospital** e **pressão hospitalar**, que não estão prontas no arquivo: a distância exige coordenadas (CNES/IBGE) e a pressão é construída a partir do SIVEP 2019. Sem elas, espere AUROC algo menor. A coorte exige RT-PCR+, desfecho conhecido e geografia completa; a mortalidade de 37,7% é alta porque o desfecho conhecido seleciona. Excluir UTI, SUPORT_VEN†, DT_EVOLUCA†, DT_ENCERRA† e exames de imagem/laboratório de resultado posterior |
| T2 (Oliveira 2022) | V, texto completo | O escore inclui **"ventilação invasiva sem UTI"**, informação pós-admissão. Nossa versão sem esse item é mais limpa e pode dar AUROC menor. O IC da validação diverge entre resumo e texto (0,741–0,758 vs. 0,738–0,768); citar o do resumo e anotar a divergência |
| T3 (Sardinha 2026) | R (só resumo; texto atrás de paywall) | O modelo é **inferencial** (IPTW para o efeito do reforço COVID), com AUROC **aparente**. Inclui **uso de oseltamivir** e vacinação como covariáveis; oseltamivir pode ser iniciado depois da admissão (vazamento possível). O número de óbitos não é dado diretamente (≈1.935 calculado de 12,1%) |
| T4 (Almeida 2026) | V, texto completo | O comparador inclui **IG ao nascer, anomalia congênita e sexo do RN** (pós-parto). A tarefa pré-parto da equipe não é comparável um a um: reportar também uma versão "com IG" para fechar a comparação. Caso completo (descarta "ignorado"), sem restrição a feto único. Sem código. Há inconsistências menores no artigo (categorias de escolaridade, data do CEP) |
| T5 (Cordeiro & Martins 2018) | V, texto completo | Comparar com o **modelo 1 (C = 0,720)**. Os modelos 2 e 3 usam permanência, cirurgia e UTI (pós-admissão). Comorbidade vem do diagnóstico secundário, preenchido na alta: é vazamento brando, que o comparador também tem. Excluir COBRANCA† (motivo de saída codifica óbito), DIAS_PERM†, DT_SAIDA†, UTI_MES_TO†/MARCA_UTI†, VAL_TOT†, CID_MORTE†. Sem validação no artigo |
| T6 (Araújo 2022) | R + E | Só o resumo foi lido; a identificação HSL + BP vem da equipe. Com 291 óbitos, a tarefa é **limítrofe** para o critério de eventos. Exames das primeiras 24 h exigem janela definida a partir da data de admissão (risco de pegar exame posterior). AUROC 0,91 é média de cenários, incluindo validação externa |

### 4.5 Regras transversais recomendadas para o benchmark

1. **Duas partições por tarefa:** uma **réplica** do desenho do comparador (para o número ser comparável) e uma **temporal** como partição principal. A temporal é o que falta na literatura: só S2, A7 e N2 a usam.
2. **Nunca balancear antes do split**; reportar AUROC, AUPRC (com prevalência do teste), Brier e calibração (intercepto/inclinação). Metade dos comparadores não reporta calibração.
3. **Lista explícita de campos proibidos por tarefa** (seções 4.3–4.4), versionada no código.
4. **Licença CC BY-ND do portal:** distribuir receitas (código + IDs de partição), não CSVs derivados.
5. **Congelar a extração:** registrar a data do download e o hash dos arquivos. O portal regrava as bases ("banco vivo") e muda contagens retroativamente.

---

## 5. Incertezas e pendências

| Item | Situação |
|---|---|
| Busca dedicada de benchmarks (Kaggle/HF/OpenML/Papers with Code) | Não retornou; veredito da seção 1 com confiança moderada |
| Buscas dedicadas SIVEP, SIH/SINASC e bases não DATASUS | Não retornaram. Os comparadores das tarefas definidas foram verificados diretamente por mim; os demais candidatos (Batista 2021, Wollenstein-Betech 2020, Einstein/Sírio Kaggle, PNS, Vigitel, SPNeoDeath) ficam **NV** |
| Nomes de campo marcados com † | Não reconferidos no dicionário nesta sessão (baixar dicionário é passo seguinte; o download de arquivos não foi feito por regra de permissão) |
| Sardinha 2026 | Só resumo; preditores exatos e tratamento de oseltamivir não confirmados |
| Araújo 2022 | Hospitais (HSL + BP) e uso do FAPESP Data Sharing informados pela equipe, não lidos no artigo |
| Licença CC BY-ND do portal | Declarada no rodapé do portal, sem campo de licença por dataset visível; interpretação jurídica não feita |
| NUMERODN no DO público | NV |
| Rótulo "congelado" vs. "banco vivo 23/03/2026" nas bases SRAG 2019–2024 | Inconsistência na própria página oficial |

---

## 6. Referências

**Benchmarks e ferramentas**
- PySUS. https://github.com/AlertaDengue/PySUS (V)
- Saldanha RF, Bastos RR, Barcellos C. Microdatasus: pacote para download e pré-processamento de microdados do DATASUS. *Cad Saúde Pública* 2019;35(9):e00032419. doi:10.1590/0102-311x00032419. https://github.com/rfsaldanha/microdatasus (V)
- Santos IAB, Barros MHLFS, Endo PT, Rodrigues MGA, Sampaio V. Brazilian datasets classified to support differential diagnosis of SARS caused by COVID-19 and influenza. Mendeley Data 2024, v1. doi:10.17632/f6sjz6by8k.1 (V)

**SIVEP-Gripe**
- Baqui P et al. *Sci Rep* 2021;11:15591. doi:10.1038/s41598-021-95004-8. https://pmc.ncbi.nlm.nih.gov/articles/PMC8329284/ (V)
- Oliveira EA et al. *J Pediatr* 2022;244:178–185.e3. doi:10.1016/j.jpeds.2022.01.001. https://pmc.ncbi.nlm.nih.gov/articles/PMC8750833/ (V)
- Sardinha DM et al. *Immunol Res* 2026;74:62. doi:10.1007/s12026-026-09792-0 (R, Europe PMC)
- Leung C, Su L, Simões e Silva AC. *Int J Epidemiol* 2022;51:1733–44. doi:10.1093/ije/dyac157 (V, agente)
- Cini Oliveira M et al. *BMC Infect Dis* 2021;21:687. doi:10.1186/s12879-021-06384-1 (V, agente)

**SIH/SUS**
- Cordeiro P, Martins M. *Rev Saúde Pública* 2018;52:69. doi:10.11606/s1518-8787.2018052000146. Europe PMC PMC6052847 (V)

**SINASC / SIM**
- Almeida AVA, Santos AORD, Nascimento LFC. *São Paulo Med J* 2026;144(3):e20253373. doi:10.1590/1516-3180.2025.3373.04052026. PMC13398868 (V)
- Magalhães SCO et al. *Anais SBCAS* 2026:13–24. doi:10.5753/sbcas.2026.20234 (R)

**SINAN / e-SUS**
- Rodrigues MMS et al. *BMC Public Health* 2024;24:1385. doi:10.1186/s12889-024-18815-0. https://pmc.ncbi.nlm.nih.gov/articles/PMC11112756/ (V)
- Lima SVMA et al. *Heliyon* 2021;7:e06788. doi:10.1016/j.heliyon.2021.e06788 (V, agente)
- Coura-Vital W et al. *PLoS Negl Trop Dis* 2014;8:e3374. doi:10.1371/journal.pntd.0003374. PMC4263605 (V)
- de Araújo VEM et al. *PLoS Negl Trop Dis* 2012;6:e1511. doi:10.1371/journal.pntd.0001511 (V, agente)
- Pinto RC et al. *PLoS ONE* 2016;11:e0161884. doi:10.1371/journal.pone.0161884 (V, agente)
- De Souza FSH et al. *Front Artif Intell* 2021;4:579931. doi:10.3389/frai.2021.579931 (V, agente)
- Freitas LRS et al. *Trop Med Infect Dis* 2025;10:131. doi:10.3390/tropicalmed10050131 (V, agente)
- Victor A et al. *PLOS Digit Health* 2025;4:e0000925. doi:10.1371/journal.pdig.0000925 (V, agente)
- Reis BQ, Raposo LM. *Int J Med Inform* 2026;222:106736. doi:10.1016/j.ijmedinf.2026.106736 (V, agente)

**Não DATASUS**
- Araújo DC, Veloso AA, Borges KBG, Carvalho MG. *Int J Med Inform* 2022;165:104835. doi:10.1016/j.ijmedinf.2022.104835 (R)
- FAPESP COVID-19 Data Sharing/BR. https://repositoriodatasharingfapesp.uspdigital.usp.br/ (V)

**Portais oficiais (abertos em 17/10/2026)**
- https://dadosabertos.saude.gov.br/dataset/srag-2019-a-2026 (V)
- https://dadosabertos.saude.gov.br/dataset/arboviroses-dengue (V)
- ftp://ftp.datasus.gov.br/dissemin/publicos/ (V, listagem via curl)
- https://datasus.saude.gov.br/transferencia-de-arquivos/ (V)
