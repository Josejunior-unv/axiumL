"""Compara popularidade, ItemKNN e ALS nas últimas 5 interações de cada usuário.

    python -m recomendacao.avaliar
"""

from __future__ import annotations

import argparse
import time

import numpy as np
import pandas as pd

from recomendacao.avaliacao import cobertura, recall_ndcg, separar_ultimos
from recomendacao.dados import gerar_interacoes
from recomendacao.modelos import ALSImplicito, ItemKNN, Popularidade, matriz_interacoes, recomendar


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--k", type=int, default=10)
    parser.add_argument("--semente", type=int, default=42)
    args = parser.parse_args()

    interacoes, catalogo = gerar_interacoes(semente=args.semente)
    n_usuarios, n_itens = interacoes["usuario_id"].max() + 1, len(catalogo)
    treino, teste = separar_ultimos(interacoes)
    R = matriz_interacoes(treino, n_usuarios, n_itens)
    densidade = R.nnz / (n_usuarios * n_itens)
    print(f"{n_usuarios:,} usuários, {n_itens:,} filmes, {len(interacoes):,} visualizações "
          f"(matriz {densidade:.1%} preenchida)")

    usuarios = np.arange(n_usuarios)
    relevantes = teste.groupby("usuario_id")["item_id"].apply(set).reindex(usuarios).tolist()

    linhas = []
    for nome, modelo in {
        "popularidade": Popularidade(),
        "item_knn": ItemKNN(),
        "als_implicito": ALSImplicito(),
    }.items():
        t0 = time.perf_counter()
        modelo.fit(R)
        recomendados = recomendar(modelo, R, usuarios, args.k)
        recall, ndcg = recall_ndcg(recomendados, relevantes, args.k)
        linhas.append({
            "modelo": nome,
            f"Recall@{args.k}": recall,
            f"NDCG@{args.k}": ndcg,
            "cobertura": cobertura(recomendados, n_itens),
            "segundos": time.perf_counter() - t0,
        })

    tabela = pd.DataFrame(linhas).set_index("modelo")
    print()
    print(tabela.to_string(float_format=lambda v: f"{v:.3f}"))


if __name__ == "__main__":
    main()
