# 📊 Trade Marketing — Alocação de Materiais de PDV & Orçamento

Projeto end-to-end de analytics que define **como alocar materiais de ponto de venda (PDV) e um orçamento limitado de trade marketing** em uma rede de distribuidores — desde dados brutos de sell-out até um relatório interativo em Power BI.

> ⚠️ **Nota:** Este é um projeto de portfólio. A empresa ("ACME Snacks Co."), distribuidores, lojas, preços e todos os dados são **100% sintéticos**. Nenhum dado real ou proprietário foi utilizado.

---

## 🎯 Problema de Negócio

Uma empresa de bens de consumo (ACME Snacks Co.) vende por meio de dezenas de distribuidores independentes, que atendem centenas de pontos de venda (PDVs).

O time de trade marketing precisa responder:

- Quais lojas devem receber materiais de PDV (displays, réguas de gôndola, ilhas, etc.)?
- Quantas unidades de cada material cada distribuidor precisa?
- Dado um orçamento limitado, como distribuí-lo de forma justa, eficiente e automatizada?

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
   Cada segmento possui um kit padrão por loja.

5. **Consolidação da demanda**  
   Quantidade total = kit por loja × número de lojas top 10% no segmento.

6. **Alocação do orçamento (Power BI)**  
   O orçamento é distribuído:
   - proporcional à necessidade
   - limitado ao máximo necessário (cap)
   - convertido em unidades de materiais financiáveis

---

## 📁 Estrutura do Repositório
