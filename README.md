# 📊 Trade Marketing — Alocação de Materiais de PDV & Orçamento

Projeto end-to-end de analytics que define **como alocar materiais de ponto de venda (PDV) e um orçamento limitado de trade marketing** em uma rede de distribuidores — desde dados brutos de sell-out até um relatório interativo em Power BI.

> ⚠️ **Nota:** Este é um projeto de portfólio. A empresa ("ACME Snacks Co."), distribuidores, lojas, preços e dados são 100% sintéticos. Nenhum dado real ou proprietário foi utilizado.

---

## 🎯 Problema de Negócio

Uma empresa de bens de consumo (ACME Snacks Co.) vende por meio de distribuidores independentes, que atendem centenas de pontos de venda (PDVs).

O time de trade marketing precisa responder:

- Quais lojas devem receber materiais de PDV (displays, réguas de gôndola, ilhas, etc.)?
- Quantas unidades de cada material cada distribuidor precisa?
- Como distribuir um orçamento limitado de forma justa, eficiente e automatizada?

---

## 🧠 Abordagem Analítica

A solução prioriza o investimento nas lojas com maior retorno esperado e dimensiona automaticamente a necessidade de materiais:

1. **Janela móvel**  
   Considera apenas os últimos 6 períodos de sell-out.

2. **Top 10% de lojas**  
   Dentro de cada distribuidor, seleciona os PDVs no top 10% em receita.

3. **Classificação por segmento**  
   Cada loja pertence a um segmento (Hipermercado, Atacado, Farmácia, etc.).

4. **Kit de materiais por segmento**  
   Cada segmento possui um kit padrão de materiais por loja.

5. **Consolidação da demanda**  
   Quantidade total = kit por loja × número de lojas top 10% no segmento.

6. **Alocação de orçamento (Power BI)**  
   O orçamento é distribuído:
   - proporcional à necessidade
   - limitado ao máximo necessário (cap)
   - convertido em unidades financiáveis de materiais

---

## 📁 Estrutura do Repositório

    trade-budget-allocation/
    ├── README.md
    ├── requirements.txt
    ├── data/
    │   └── generate_sample_data.py   # Gera sellout.csv e dimensão de lojas
    ├── src/
    │   └── pipeline.py               # Pipeline de consolidação (pandas)
    ├── powerbi/
    │   └── dax_measures.md           # Medidas DAX do dashboard
    └── docs/
        └── methodology.md            # Detalhamento da metodologia

---

## ▶️ Como Executar

    pip install -r requirements.txt

    # 1) Gerar dados sintéticos
    python data/generate_sample_data.py

    # 2) Executar pipeline
    python src/pipeline.py

---

## 📤 Saída

O pipeline gera o arquivo:

    data/output/pos_materials_plan.csv

Este dataset consolida a necessidade de materiais por distribuidor e é utilizado como fonte no Power BI.

---

## 📊 Camada de Visualização (Power BI)

O relatório permite simular diferentes cenários de orçamento e analisar:

- 💰 **Orçamento Alocado** → Distribuição proporcional à necessidade de cada distribuidor  
- 📈 **Cobertura (%)** → Percentual da demanda atendida pelo orçamento  
- 📦 **Materiais Financiados** → Quantidade de cada material que pode ser adquirida  

📌 Todas as medidas DAX estão documentadas em:

    powerbi/dax_measures.md

---

## 🛠️ Tecnologias Utilizadas

- **Python (pandas, numpy)** → Pipeline e lógica analítica  
- **Power BI (DAX, What-If)** → Simulação e visualização  
- **Databricks / PySpark** → Versão original (adaptada neste projeto)  

---

## 🚀 Conceitos Demonstrados

- Modelagem analítica orientada ao negócio  
- Priorização de investimento com base em dados  
- Construção de pipelines com pandas  
- Simulação de cenários (what-if analysis)  
- Alocação proporcional com restrições (budget capping)  
- Tradução de dados em decisões acionáveis  

---

## 💡 Possíveis Evoluções

- Otimização com programação linear  
- Inclusão de ROI por material  
- Segmentação avançada (clusterização)  
- Integração com dados reais  
- Deploy como aplicação (Streamlit ou Power BI Service)  

---

## 📌 Observação Final

Este projeto foi desenvolvido para demonstrar habilidades em análise de dados, modelagem de decisão e construção de soluções end-to-end aplicadas ao contexto de trade marketing.
