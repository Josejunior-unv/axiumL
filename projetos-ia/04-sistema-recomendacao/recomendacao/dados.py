"""Catálogo de filmes e histórico de visualizações sintéticos.

Cada filme mistura alguns gêneros e tem uma popularidade de cauda longa. Cada
usuário tem gosto concentrado em poucos gêneros. As escolhas misturam gosto e
popularidade, então "recomendar os mais vistos" funciona, mas mal, e há espaço
para um modelo que aprenda preferências individuais.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

GENEROS = [
    "Ação", "Comédia", "Drama", "Terror", "Ficção científica", "Romance",
    "Animação", "Documentário", "Suspense", "Fantasia", "Musical", "Policial",
]

_ADJETIVOS = [
    "Silencioso", "Perdido", "Eterno", "Secreto", "Distante", "Selvagem", "Esquecido",
    "Invisível", "Proibido", "Dourado", "Sombrio", "Final", "Infinito", "Quebrado",
]
_SUBSTANTIVOS = [
    "Horizonte", "Segredo", "Caminho", "Reino", "Destino", "Verão", "Código",
    "Labirinto", "Oceano", "Planeta", "Coração", "Inverno", "Espelho", "Sinal",
]


def gerar_catalogo(n_itens: int, rng: np.random.Generator) -> tuple[pd.DataFrame, np.ndarray]:
    mistura = rng.dirichlet(np.full(len(GENEROS), 0.15), n_itens)
    titulos, vistos = [], {}
    for _ in range(n_itens):
        titulo = f"O {rng.choice(_SUBSTANTIVOS)} {rng.choice(_ADJETIVOS)}"
        vistos[titulo] = vistos.get(titulo, 0) + 1
        # título repetido vira continuação: "O Reino Sombrio 2"
        titulos.append(titulo if vistos[titulo] == 1 else f"{titulo} {vistos[titulo]}")
    principais = [
        " / ".join(GENEROS[g] for g in np.argsort(-linha)[:2] if linha[g] > 0.2) or "Variados"
        for linha in mistura
    ]
    catalogo = pd.DataFrame({"item_id": np.arange(n_itens), "titulo": titulos, "generos": principais})
    return catalogo, mistura


def gerar_interacoes(
    n_usuarios: int = 2000,
    n_itens: int = 800,
    semente: int = 42,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Devolve (interacoes, catalogo). Cada interação é um filme assistido."""
    rng = np.random.default_rng(semente)
    catalogo, generos_item = gerar_catalogo(n_itens, rng)
    popularidade = rng.lognormal(0, 1.0, n_itens)

    gosto = rng.dirichlet(np.full(len(GENEROS), 0.2), n_usuarios)
    atividade = np.clip(rng.lognormal(3.3, 0.7, n_usuarios), 8, min(300, n_itens // 2)).astype(int)
    inicio = pd.Timestamp("2025-01-01")

    linhas = []
    for u in range(n_usuarios):
        afinidade = 8 * generos_item @ gosto[u]
        peso = np.exp(afinidade - afinidade.max()) * popularidade**0.8
        itens = rng.choice(n_itens, size=atividade[u], replace=False, p=peso / peso.sum())
        momentos = np.sort(rng.uniform(0, 365, atividade[u]))
        linhas.append(
            pd.DataFrame(
                {
                    "usuario_id": u,
                    "item_id": itens,
                    "data_hora": inicio + pd.to_timedelta(momentos, unit="D"),
                }
            )
        )
    return pd.concat(linhas, ignore_index=True), catalogo
