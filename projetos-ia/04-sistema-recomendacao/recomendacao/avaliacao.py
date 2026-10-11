"""Divisão temporal por usuário e métricas de ranking."""

from __future__ import annotations

import numpy as np
import pandas as pd


def separar_ultimos(interacoes: pd.DataFrame, n_teste: int = 5) -> tuple[pd.DataFrame, pd.DataFrame]:
    """As `n_teste` últimas interações de cada usuário viram teste: o modelo
    precisa prever o que a pessoa vai assistir a seguir, não o que ela viu no meio."""
    ordenadas = interacoes.sort_values(["usuario_id", "data_hora"])
    posicao_do_fim = ordenadas.groupby("usuario_id").cumcount(ascending=False)
    return ordenadas[posicao_do_fim >= n_teste], ordenadas[posicao_do_fim < n_teste]


def recall_ndcg(recomendados: np.ndarray, relevantes: list[set[int]], k: int) -> tuple[float, float]:
    """Médias de Recall@k e NDCG@k sobre os usuários."""
    desconto = 1.0 / np.log2(np.arange(2, k + 2))
    recalls, ndcgs = [], []
    for lista, alvo in zip(recomendados[:, :k], relevantes):
        acertos = np.array([item in alvo for item in lista], dtype=float)
        recalls.append(acertos.sum() / len(alvo))
        ideal = desconto[: min(len(alvo), k)].sum()
        ndcgs.append((acertos * desconto).sum() / ideal)
    return float(np.mean(recalls)), float(np.mean(ndcgs))


def cobertura(recomendados: np.ndarray, n_itens: int) -> float:
    """Fração do catálogo que aparece em pelo menos uma recomendação."""
    return len(np.unique(recomendados)) / n_itens
