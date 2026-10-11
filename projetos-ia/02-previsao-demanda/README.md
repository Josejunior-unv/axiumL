# Previsão de demanda no varejo

Previsão diária de vendas para as próximas **4 semanas** de 50 séries
(5 lojas × 10 produtos), com **intervalo de previsão de 80%** e validação por
**backtest com origem móvel**, do jeito que um time de planejamento de estoque
usaria.

## Resultados (3 janelas de 28 dias, out–dez/2025)

| Método | WAPE | MAE | Viés |
|---|---|---|---|
| Sazonal ingênuo (mesmo dia, 4 semanas antes) | 0,408 | 8,73 | -5,6% |
| Média das últimas 4 semanas no mesmo dia da semana | 0,328 | 7,02 | -7,2% |
| **Gradient boosting global** | **0,257** | **5,51** | **-3,1%** |

- O modelo reduz o erro em **22%** frente à melhor referência simples.
- Na **Black Friday** ele previu 2.448 unidades para 2.573 vendidas. A média
  das 4 semanas previu 1.196, menos da metade.
- O intervalo p10–p90 cobriu **75%** dos dias, perto dos 80% nominais.

*WAPE = soma dos erros absolutos / soma das vendas. Viés negativo = previsão
abaixo do realizado.*

## Como funciona

**Dados** (`demanda/dados.py`): vendas sintéticas de 2023 a 2025 com nível por
loja e produto, tendência, sazonalidade semanal e anual, feriados nacionais,
Black Friday, véspera de Natal, promoções (+45%) e ruído de contagem com
sobredispersão.

**Estratégia direta, sem vazamento** (`demanda/features.py`): toda feature que
olha vendas passadas usa defasagem de **pelo menos 28 dias** (lags de 28 a 364
dias e médias móveis deslocadas). Assim um único modelo prevê qualquer dia das
próximas 4 semanas usando só o que já existia no dia da previsão. Promoções e
feriados entram como features porque são conhecidos com antecedência. Um teste
automatizado adultera as vendas futuras e confere que nenhuma feature muda.

**Modelo** (`demanda/modelo.py`): um `HistGradientBoostingRegressor` global
(uma árvore para todas as séries, com loja e produto como categóricas):
- perda **Poisson** para a previsão pontual, adequada a contagens;
- perda **quantílica** (q = 0,1 e 0,9) para o intervalo de previsão.

**Backtest**: para cada origem, treina só com o passado e prevê os 28 dias
seguintes. Nenhum dia da janela de teste entra no treino.

## Como rodar

```bash
cd projetos-ia/02-previsao-demanda
pip install -r requirements.txt

python -m demanda.backtest   # compara os métodos e salva artefatos/backtest.csv
python -m demanda.prever     # previsão das próximas 4 semanas em artefatos/previsao.csv
pytest
```

Para incluir promoções planejadas na previsão, passe um DataFrame com
`data, loja, produto, promocao` para `prever_futuro(vendas, promocoes=plano)`.

## Estrutura

```
demanda/
├── dados.py      # gerador das séries e calendário (feriados, Black Friday)
├── features.py   # lags, médias móveis e calendário, todos com defasagem >= 28 dias
├── modelo.py     # modelo, métricas, backtest e previsão do futuro
├── backtest.py   # CLI do backtest
└── prever.py     # CLI da previsão
tests/            # inclui o teste de não vazamento
```
