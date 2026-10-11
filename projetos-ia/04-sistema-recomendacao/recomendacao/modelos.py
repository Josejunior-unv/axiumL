"""Três recomendadores para feedback implícito (assistiu / não assistiu).

Todos recebem a matriz esparsa usuário x item e expõem `pontuar(usuarios)`,
que devolve uma nota para cada item. Quem decide o top-k e tira os itens já
vistos é `recomendar`.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import sparse


def matriz_interacoes(interacoes: pd.DataFrame, n_usuarios: int, n_itens: int) -> sparse.csr_matrix:
    dados = np.ones(len(interacoes), dtype=np.float64)
    matriz = sparse.csr_matrix(
        (dados, (interacoes["usuario_id"], interacoes["item_id"])), shape=(n_usuarios, n_itens)
    )
    matriz.data[:] = 1.0  # interações repetidas contam uma vez só
    return matriz


class Popularidade:
    """Referência: recomenda o que mais gente assistiu."""

    def fit(self, R: sparse.csr_matrix) -> Popularidade:
        self.contagem = np.asarray(R.sum(axis=0)).ravel()
        return self

    def pontuar(self, usuarios: np.ndarray) -> np.ndarray:
        return np.tile(self.contagem, (len(usuarios), 1))


class ItemKNN:
    """Filtragem colaborativa item a item com similaridade de cosseno.

    A nota de um item é a soma das similaridades dele com o que o usuário já
    assistiu. `encolhimento` reduz a similaridade de pares com pouca evidência.
    """

    def __init__(self, vizinhos: int = 200, encolhimento: float = 10.0):
        self.vizinhos = vizinhos
        self.encolhimento = encolhimento

    def fit(self, R: sparse.csr_matrix) -> ItemKNN:
        coocorrencia = (R.T @ R).toarray()
        norma = np.sqrt(np.diag(coocorrencia))
        similaridade = coocorrencia / (np.outer(norma, norma) + self.encolhimento)
        np.fill_diagonal(similaridade, 0.0)
        if self.vizinhos < similaridade.shape[0]:
            # mantém só os `vizinhos` mais parecidos de cada item
            corte = np.argpartition(-similaridade, self.vizinhos, axis=0)[self.vizinhos:]
            np.put_along_axis(similaridade, corte, 0.0, axis=0)
        self.similaridade = similaridade
        self.R = R
        return self

    def pontuar(self, usuarios: np.ndarray) -> np.ndarray:
        return np.asarray(self.R[usuarios] @ self.similaridade)


class ALSImplicito:
    """Fatoração de matriz para feedback implícito (Hu, Koren e Volinsky, 2008).

    Cada interação observada vira preferência 1 com confiança 1 + alpha; o
    resto é preferência 0 com confiança 1. Os mínimos quadrados alternados
    resolvem os fatores de usuários e itens em forma fechada, um lado por vez.
    """

    def __init__(
        self,
        fatores: int = 12,
        regularizacao: float = 20.0,
        alpha: float = 2.0,
        iteracoes: int = 15,
        semente: int = 0,
    ):
        self.fatores = fatores
        self.regularizacao = regularizacao
        self.alpha = alpha
        self.iteracoes = iteracoes
        self.semente = semente

    def fit(self, R: sparse.csr_matrix) -> ALSImplicito:
        rng = np.random.default_rng(self.semente)
        confianca = (R * self.alpha).tocsr()
        confianca_t = confianca.T.tocsr()
        self.U = rng.normal(0, 0.01, (R.shape[0], self.fatores))
        self.V = rng.normal(0, 0.01, (R.shape[1], self.fatores))
        self.historico_perda = []
        for _ in range(self.iteracoes):
            self.U = self._resolver(confianca, self.V)
            self.V = self._resolver(confianca_t, self.U)
            self.historico_perda.append(self.perda(R))
        return self

    def _resolver(self, confianca: sparse.csr_matrix, Y: np.ndarray) -> np.ndarray:
        """Para cada linha u: (YᵀY + Yᵀ(Cᵤ - I)Y + λI) xᵤ = YᵀCᵤpᵤ.

        YᵀY é comum a todas as linhas; só a parte dos itens observados muda."""
        YtY = Y.T @ Y
        identidade = self.regularizacao * np.eye(self.fatores)
        X = np.zeros((confianca.shape[0], self.fatores))
        for u in range(confianca.shape[0]):
            inicio, fim = confianca.indptr[u], confianca.indptr[u + 1]
            if inicio == fim:
                continue
            Yu = Y[confianca.indices[inicio:fim]]
            c = confianca.data[inicio:fim]
            A = YtY + (Yu.T * c) @ Yu + identidade
            b = Yu.T @ (1.0 + c)
            X[u] = np.linalg.solve(A, b)
        return X

    def perda(self, R: sparse.csr_matrix) -> float:
        """Erro quadrático ponderado pela confiança + regularização."""
        previsto = self.U @ self.V.T
        preferencia = R.toarray()
        confianca = 1.0 + self.alpha * preferencia
        erro = (confianca * (preferencia - previsto) ** 2).sum()
        return float(erro + self.regularizacao * ((self.U**2).sum() + (self.V**2).sum()))

    def pontuar(self, usuarios: np.ndarray) -> np.ndarray:
        return self.U[usuarios] @ self.V.T


def recomendar(modelo, R: sparse.csr_matrix, usuarios: np.ndarray, k: int = 10) -> np.ndarray:
    """Top-k itens por usuário, sem repetir o que ele já assistiu."""
    notas = np.asarray(modelo.pontuar(usuarios), dtype=float).copy()
    vistos = R[usuarios].nonzero()
    notas[vistos] = -np.inf
    candidatos = np.argpartition(-notas, k, axis=1)[:, :k]
    ordem = np.argsort(-np.take_along_axis(notas, candidatos, axis=1), axis=1)
    return np.take_along_axis(candidatos, ordem, axis=1)
