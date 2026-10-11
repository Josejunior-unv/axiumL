import numpy as np
import pandas as pd
import pytest

from recomendacao.avaliacao import recall_ndcg, separar_ultimos
from recomendacao.dados import gerar_interacoes
from recomendacao.modelos import ALSImplicito, ItemKNN, Popularidade, matriz_interacoes, recomendar


@pytest.fixture(scope="module")
def base():
    interacoes, catalogo = gerar_interacoes(n_usuarios=400, n_itens=200, semente=3)
    treino, teste = separar_ultimos(interacoes)
    R = matriz_interacoes(treino, 400, 200)
    relevantes = teste.groupby("usuario_id")["item_id"].apply(set).reindex(range(400)).tolist()
    return R, relevantes


def test_matriz_binaria():
    df = pd.DataFrame({"usuario_id": [0, 0, 1], "item_id": [2, 2, 0]})
    R = matriz_interacoes(df, 2, 3)
    assert R.toarray().tolist() == [[0, 0, 1], [1, 0, 0]]


def test_nunca_recomenda_o_que_ja_foi_visto(base):
    R, _ = base
    usuarios = np.arange(50)
    for modelo in (Popularidade(), ItemKNN(), ALSImplicito(iteracoes=3)):
        recomendados = recomendar(modelo.fit(R), R, usuarios, k=10)
        vistos = R[usuarios].toarray().astype(bool)
        assert not np.take_along_axis(vistos, recomendados, axis=1).any()
        assert all(len(set(linha)) == 10 for linha in recomendados)


def test_item_knn_recomenda_o_par_mais_frequente():
    # quem vê o item 0 quase sempre vê o 1; o usuário 9 só viu o 0
    linhas = [(u, 0) for u in range(8)] + [(u, 1) for u in range(8)] + [(u, 2) for u in range(3)]
    linhas += [(8, 2), (8, 3), (9, 0)]
    df = pd.DataFrame(linhas, columns=["usuario_id", "item_id"])
    R = matriz_interacoes(df, 10, 4)
    assert recomendar(ItemKNN(encolhimento=0).fit(R), R, np.array([9]), k=1)[0, 0] == 1


def test_als_perda_nao_aumenta(base):
    R, _ = base
    perdas = ALSImplicito(iteracoes=6).fit(R).historico_perda
    assert all(depois <= antes * (1 + 1e-9) for antes, depois in zip(perdas, perdas[1:]))


def test_modelos_personalizados_superam_popularidade(base):
    R, relevantes = base
    usuarios = np.arange(R.shape[0])
    ndcg = {
        nome: recall_ndcg(recomendar(m.fit(R), R, usuarios), relevantes, 10)[1]
        for nome, m in {"pop": Popularidade(), "knn": ItemKNN(), "als": ALSImplicito()}.items()
    }
    assert ndcg["knn"] > ndcg["pop"]
    assert ndcg["als"] > ndcg["pop"]
