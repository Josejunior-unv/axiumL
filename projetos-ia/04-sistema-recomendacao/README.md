# Sistema de recomendação de filmes

Recomendador para feedback implícito (assistiu / não assistiu) com três
abordagens: **popularidade**, **ItemKNN** (filtragem colaborativa item a item) e
**ALS implícito**, uma fatoração de matriz **implementada do zero em NumPy**
seguindo Hu, Koren e Volinsky (2008).

## Resultados

2.000 usuários, 800 filmes e 69.479 visualizações (matriz 3,7% preenchida). O
teste usa as 5 últimas visualizações de cada usuário.

| Modelo | Recall@10 | NDCG@10 | Cobertura do catálogo |
|---|---|---|---|
| Popularidade | 0,060 | 0,050 | 4,6% |
| ItemKNN | 0,126 | 0,108 | 53,0% |
| **ALS implícito** | **0,135** | **0,120** | 44,9% |

- Os modelos personalizados acertam mais que o **dobro** da referência de
  popularidade, e recomendam boa parte do catálogo em vez dos mesmos 37 filmes
  para todo mundo.
- O ItemKNN, bem mais simples, chega perto do ALS. É um achado comum na
  literatura (Dacrema et al., 2019) e o motivo de sempre comparar com
  referências fortes.
- O ALS só passou o ItemKNN depois do ajuste de hiperparâmetros. Com 64
  fatores e alpha = 10, ele perdia para o KNN: o gosto dos usuários vive num
  espaço de ~12 gêneros, e fatores demais só aprendem ruído.

Exemplo (`python -m recomendacao.recomendar --usuario 7`): um usuário que vê
principalmente ação recebe uma lista dominada por ação, com uma ou outra
animação e romance, que também aparecem no histórico dele.

## Como funciona

**Dados** (`recomendacao/dados.py`): cada filme mistura alguns de 12 gêneros e
tem popularidade de cauda longa. Cada usuário tem gosto concentrado em poucos
gêneros. A escolha do que assistir combina gosto e popularidade.

**Modelos** (`recomendacao/modelos.py`):
- **ItemKNN**: similaridade de cosseno entre itens com *shrinkage* (encolhe
  pares com pouca coocorrência) e poda para os 200 vizinhos mais próximos.
- **ALS implícito**: cada visualização vira preferência 1 com confiança
  `1 + alpha`, e o resto vira preferência 0 com confiança 1. Os fatores de
  usuários e itens saem em forma fechada, alternando os lados. O truque de
  Hu et al. (`YᵀY` calculado uma vez e corrigido só pelos itens que o usuário
  viu) deixa cada iteração linear no número de interações. Um teste confere que
  a função objetivo nunca aumenta entre iterações.

**Avaliação sem trapaça** (`recomendacao/avaliacao.py`, `recomendacao/ajustar.py`):
divisão temporal por usuário. Os hiperparâmetros saem de uma validação com as 5
interações *anteriores* às de teste, e o teste só é usado no final. Itens já
vistos nunca são recomendados.

## Como rodar

```bash
cd projetos-ia/04-sistema-recomendacao
pip install -r requirements.txt

python -m recomendacao.avaliar                  # tabela de comparação
python -m recomendacao.ajustar                  # busca de hiperparâmetros na validação
python -m recomendacao.recomendar --usuario 7   # histórico + recomendações de um usuário
pytest
```

## Estrutura

```
recomendacao/
├── dados.py        # catálogo e visualizações sintéticas
├── modelos.py      # Popularidade, ItemKNN, ALS implícito e top-k sem itens vistos
├── avaliacao.py    # divisão temporal, Recall@k, NDCG@k e cobertura
├── avaliar.py      # CLI de comparação no teste
├── ajustar.py      # CLI de ajuste na validação
└── recomendar.py   # CLI de demonstração
tests/
```
