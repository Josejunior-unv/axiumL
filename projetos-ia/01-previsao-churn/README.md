# Previsão de churn com limiar de negócio

Modelo que estima a chance de um cliente de telecom cancelar o plano e decide
**para quem vale a pena oferecer um desconto de retenção**, servido por uma API
FastAPI.

O diferencial é o limiar: em vez do 0,5 padrão, o corte é escolhido para
**maximizar o lucro da campanha de retenção**. Cada oferta custa R$ 120, e se o
cliente ia mesmo sair, ela o segura com 30% de chance, preservando um ano de
mensalidade.

## Resultados (base de 7.000 clientes, semente 42)

| Etapa | ROC-AUC | PR-AUC |
|---|---|---|
| Regressão logística (validação cruzada) | 0,828 | 0,665 |
| Gradient boosting (validação cruzada) | 0,817 | 0,644 |
| **Regressão logística no teste** | **0,835** | **0,682** |

| Estratégia de retenção (conjunto de teste) | Lucro |
|---|---|
| **Oferecer para quem o modelo aponta (limiar 0,36, 30% da base)** | **R$ 44.489** |
| Oferecer para todos | R$ -31.559 |
| Não fazer campanha | R$ 0 |

Variáveis mais importantes (queda de ROC-AUC ao embaralhar a coluna):
tempo de casa, tipo de contrato, total gasto e chamados no suporte.

A regressão logística vence o gradient boosting porque o gerador de dados é,
ele mesmo, quase logístico. Num caso real, com relações mais tortas, o boosting
costuma levar vantagem. O pipeline compara os dois e escolhe sozinho.

## Como funciona

1. **Dados** (`churn/dados.py`): base sintética com efeitos conhecidos
   (contrato mensal, boleto, atrasos, fibra com muitos chamados no suporte...),
   então dá para conferir se o modelo aprende o que existe nos dados.
2. **Features** (`churn/modelo.py`): log do tempo de casa, gasto médio mensal e
   flag de cliente novo, criadas *dentro* do pipeline do scikit-learn. A API
   recebe só os campos brutos.
3. **Seleção de modelo**: validação cruzada estratificada de 5 folds no treino.
4. **Limiar**: escolhido nas previsões fora da amostra do treino. O conjunto de
   teste só é usado no fim, para o número final não sair otimista.
5. **Explicabilidade**: importância por permutação nas colunas originais.

## Como rodar

```bash
cd projetos-ia/01-previsao-churn
pip install -r requirements.txt

python -m churn.treinar          # gera dados, treina e salva artefatos/modelo.joblib
uvicorn churn.api:app --reload   # sobe a API em http://localhost:8000/docs
pytest                           # testes
```

Exemplo de chamada:

```bash
curl -X POST localhost:8000/prever -H 'Content-Type: application/json' -d '{
  "contrato": "mensal", "internet": "fibra", "pagamento": "boleto",
  "regiao": "Sul", "meses_cliente": 3, "idade": 30, "dependentes": 0,
  "streaming": true, "mensalidade": 120.0, "total_gasto": 360.0,
  "chamados_suporte": 4, "atrasos_pagamento": 1
}'
# {"probabilidade_churn": 0.9407, "acionar_retencao": true, "limiar": 0.36}
```

## Estrutura

```
churn/
├── dados.py     # gerador da base sintética
├── modelo.py    # pipeline, validação, lucro da campanha e limiar ótimo
├── treinar.py   # treino de ponta a ponta (CLI)
└── api.py       # API FastAPI
tests/           # testes de dados, modelo e API
```
