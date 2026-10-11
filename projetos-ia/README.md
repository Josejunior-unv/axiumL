# Projetos de IA e dados

Cinco projetos independentes de ciência de dados e IA. Cada um tem código,
testes, README com os resultados e roda com um comando. Todos geram os próprios
dados sintéticos com semente fixa: não precisa baixar nada e os números do
README se reproduzem.

| # | Projeto | O que faz | Técnicas |
|---|---|---|---|
| 1 | [Previsão de churn](01-previsao-churn/) | Prevê cancelamento de clientes de telecom e escolhe para quem oferecer retenção | scikit-learn, validação cruzada, limiar ótimo por lucro, importância por permutação, API FastAPI |
| 2 | [Previsão de demanda](02-previsao-demanda/) | Prevê 4 semanas de vendas diárias de 50 séries de varejo, com intervalo de 80% | gradient boosting global, perda Poisson e quantílica, features sem vazamento, backtest com origem móvel |
| 3 | [Detecção de fraude](03-deteccao-fraude/) | Pontua o risco de transações de cartão com orçamento limitado de alertas | features comportamentais causais, Isolation Forest, gradient boosting, PR-AUC, validação temporal |
| 4 | [Sistema de recomendação](04-sistema-recomendacao/) | Recomenda filmes a partir do histórico de visualização | ALS implícito do zero em NumPy, ItemKNN, Recall@k, NDCG@k, ajuste em validação |
| 5 | [Agente text-to-SQL](05-agente-text-to-sql/) | Responde perguntas em português consultando um banco SQLite | Claude com tool use, SQL somente leitura em três camadas, acurácia de execução |

## Destaques

- **Churn**: o limiar de negócio dá R$ 44 mil de lucro na campanha de retenção.
  Oferecer desconto para todos daria prejuízo de R$ 32 mil.
- **Demanda**: WAPE de 0,257 contra 0,328 da melhor referência simples. Na
  Black Friday, o modelo previu 2.448 unidades para 2.573 vendidas.
- **Fraude**: revisando só 0,5% das transações, o modelo pega 85% das fraudes,
  contra 17% das regras de negócio.
- **Recomendação**: o ALS acerta mais que o dobro da referência de popularidade
  (NDCG@10 de 0,120 contra 0,050).
- **Text-to-SQL**: o agente não consegue escrever no banco. Os testes tentam
  `DROP`, `UPDATE`, `ATTACH` e outras escritas e conferem que o arquivo fica
  intacto.

## Como rodar

Cada pasta é autocontida (Python 3.10+):

```bash
cd projetos-ia/01-previsao-churn
pip install -r requirements.txt
pytest
```

O README de cada projeto traz os comandos de treino e avaliação. A integração
contínua (`.github/workflows/projetos-ia.yml`) roda os testes dos cinco a cada
mudança nesta pasta.
