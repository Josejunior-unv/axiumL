"""Escolhe hiperparâmetros numa validação que não toca o teste.

As 5 últimas interações de cada usuário são o teste. As 5 anteriores a elas
são a validação, e o ajuste treina só com o que vem antes.

    python -m recomendacao.ajustar
"""

from __future__ import annotations

import itertools

import numpy as np

from recomendacao.avaliacao import recall_ndcg, separar_ultimos
from recomendacao.dados import gerar_interacoes
from recomendacao.modelos import ALSImplicito, ItemKNN, matriz_interacoes, recomendar


def main() -> None:
    interacoes, catalogo = gerar_interacoes()
    n_usuarios, n_itens = interacoes["usuario_id"].max() + 1, len(catalogo)
    treino, _teste = separar_ultimos(interacoes)
    treino_ajuste, validacao = separar_ultimos(treino)
    R = matriz_interacoes(treino_ajuste, n_usuarios, n_itens)
    usuarios = np.arange(n_usuarios)
    relevantes = validacao.groupby("usuario_id")["item_id"].apply(set).reindex(usuarios).tolist()

    grades = {
        "item_knn": (ItemKNN, {"vizinhos": [50, 100, 200], "encolhimento": [0, 10, 50]}),
        "als_implicito": (ALSImplicito, {
            "fatores": [12, 32], "regularizacao": [1, 20], "alpha": [2, 10], "iteracoes": [10],
        }),
    }
    for nome, (classe, grade) in grades.items():
        print(f"\n{nome}")
        resultados = []
        for valores in itertools.product(*grade.values()):
            parametros = dict(zip(grade, valores))
            recomendados = recomendar(classe(**parametros).fit(R), R, usuarios)
            recall, ndcg = recall_ndcg(recomendados, relevantes, 10)
            resultados.append((ndcg, recall, parametros))
        for ndcg, recall, parametros in sorted(resultados, key=lambda r: r[0], reverse=True):
            print(f"  NDCG@10 {ndcg:.4f} | Recall@10 {recall:.4f} | {parametros}")


if __name__ == "__main__":
    main()
