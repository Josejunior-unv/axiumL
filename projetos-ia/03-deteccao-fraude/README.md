# Detecção de fraude em cartão de crédito

Sistema de pontuação de risco para transações de cartão. Ele compara
**regras de negócio**, **detecção de anomalia não supervisionada (Isolation
Forest)** e **gradient boosting supervisionado**, sob uma restrição real: o time
de analistas só consegue revisar **0,5% das transações**.

## Resultados

190.640 transações de 3.000 clientes em 120 dias, com 0,27% de fraude. O teste
cobre os últimos 30 dias (47.380 transações, 119 fraudes).

| Detector | PR-AUC | Precisão dos alertas | Fraudes pegas | Valor de fraude barrado |
|---|---|---|---|---|
| Regras de negócio | 0,044 | 8,4% | 16,8% | 28,6% |
| Isolation Forest | 0,048 | 6,8% | 13,4% | 29,2% |
| **Gradient boosting** | **0,791** | **42,6%** | **84,9%** | **88,1%** |
| Gradient boosting + nota de anomalia | 0,783 | 42,2% | 84,0% | 86,9% |

*Com 0,5% de alertas e 0,25% de fraude no teste, a precisão máxima possível é
50%. O modelo chega a 42,6%.* Com orçamento de 1%, o gradient boosting pega
91,6% das fraudes e barra 96% do valor.

O que os números mostram:
- **ROC-AUC engana em dados desbalanceados**: as regras têm ROC-AUC de 0,89 e
  mesmo assim deixam passar 83% das fraudes. Por isso a métrica principal é a
  PR-AUC e o recall dentro do orçamento de alertas.
- **Anomalia não é fraude**: o Isolation Forest acha o que é *incomum*
  (viagens, compras grandes, gente que compra de madrugada), e quase tudo isso
  é legítimo. Somar a nota dele ao modelo supervisionado não ajudou.

## Como funciona

**Dados** (`fraude/dados.py`): cada cliente tem hábitos próprios (valor típico,
horário, frequência, sessões de compra com várias transações seguidas). Cartões
comprometidos recebem uma rajada de fraudes que começa com uma transação de
teste de valor baixo, em categorias visadas, muitas vezes em aparelho novo. Há
também ruído legítimo que imita fraude: viagens, compras altas, troca de
celular e clientes notívagos.

**Features comportamentais sem vazamento** (`fraude/features.py`): para cada
transação, só com o passado *daquele cliente*:
- quantidade e valor de transações na última 1h, 24h e 7 dias;
- razão entre o valor atual e a média histórica do cliente;
- minutos desde a transação anterior e se a categoria é nova para ele.

As janelas de tempo são calculadas sem loop por cliente: uma chave composta
(cliente × deslocamento + segundos) e um `searchsorted` acham o começo da janela
de cada transação em O(n log n). Um teste confere que inserir uma transação
futura não altera nenhuma feature do passado.

**Validação temporal**: treina em junho–agosto e testa em setembro. Um corte
aleatório colocaria transações da mesma rajada de fraude no treino e no teste,
e o resultado sairia otimista.

## Como rodar

```bash
cd projetos-ia/03-deteccao-fraude
pip install -r requirements.txt

python -m fraude.avaliar                   # orçamento padrão de 0,5% de alertas
python -m fraude.avaliar --orcamento 0.01  # 1% de alertas
pytest
```

## Estrutura

```
fraude/
├── dados.py      # gerador de transações legítimas e fraudulentas
├── features.py   # features comportamentais por cliente, só com o passado
├── modelo.py     # regras, Isolation Forest, gradient boosting e métricas
└── avaliar.py    # CLI de comparação
tests/
```
