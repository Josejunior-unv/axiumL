import numpy as np
import pandas as pd
import pytest

from recomendacao.avaliacao import cobertura, recall_ndcg, separar_ultimos


def test_separar_ultimos_pega_os_mais_recentes():
    df = pd.DataFrame({
        "usuario_id": [0, 0, 0, 1, 1],
        "item_id": [10, 11, 12, 20, 21],
        "data_hora": pd.to_datetime(["2025-01-03", "2025-01-01", "2025-01-02", "2025-01-05", "2025-01-04"]),
    })
    treino, teste = separar_ultimos(df, n_teste=1)
    assert sorted(teste["item_id"]) == [10, 20]
    assert sorted(treino["item_id"]) == [11, 12, 21]


def test_recall_ndcg():
    recomendados = np.array([[1, 2, 3], [4, 5, 6]])
    relevantes = [{1}, {6, 9}]
    recall, ndcg = recall_ndcg(recomendados, relevantes, k=3)
    assert recall == pytest.approx((1 + 0.5) / 2)
    ndcg_segundo = (1 / np.log2(4)) / (1 + 1 / np.log2(3))
    assert ndcg == pytest.approx((1 + ndcg_segundo) / 2)


def test_cobertura():
    assert cobertura(np.array([[1, 2], [2, 3]]), n_itens=10) == pytest.approx(0.3)
