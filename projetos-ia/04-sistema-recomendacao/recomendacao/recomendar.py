"""Mostra o histórico de um usuário e o que o ALS recomenda para ele.

    python -m recomendacao.recomendar --usuario 7
"""

from __future__ import annotations

import argparse

import numpy as np

from recomendacao.dados import gerar_interacoes
from recomendacao.modelos import ALSImplicito, matriz_interacoes, recomendar


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--usuario", type=int, default=7)
    parser.add_argument("--k", type=int, default=10)
    args = parser.parse_args()

    interacoes, catalogo = gerar_interacoes()
    n_usuarios = interacoes["usuario_id"].max() + 1
    R = matriz_interacoes(interacoes, n_usuarios, len(catalogo))
    modelo = ALSImplicito().fit(R)

    historico = interacoes[interacoes["usuario_id"] == args.usuario].merge(catalogo, on="item_id")
    print(f"Usuário {args.usuario}: {len(historico)} filmes assistidos")
    print("Gêneros que mais aparecem no histórico:")
    contagem = historico["generos"].str.split(" / ").explode().value_counts()
    for genero, vezes in contagem.head(4).items():
        print(f"  {genero:<20} {vezes}")
    print("\nÚltimos assistidos:")
    for _, linha in historico.sort_values("data_hora").tail(5).iterrows():
        print(f"  {linha['titulo']:<32} {linha['generos']}")

    itens = recomendar(modelo, R, np.array([args.usuario]), args.k)[0]
    print("\nRecomendações:")
    for posicao, item in enumerate(itens, 1):
        filme = catalogo.loc[item]
        print(f"  {posicao:>2}. {filme['titulo']:<32} {filme['generos']}")


if __name__ == "__main__":
    main()
