"""Cria o banco SQLite de uma loja online fictícia (2024–2025)."""

from __future__ import annotations

import sqlite3
from pathlib import Path

import numpy as np
import pandas as pd

ESQUEMA = """
CREATE TABLE clientes (
    id            INTEGER PRIMARY KEY,
    nome          TEXT NOT NULL,
    cidade        TEXT NOT NULL,
    estado        TEXT NOT NULL,
    data_cadastro TEXT NOT NULL            -- AAAA-MM-DD
);
CREATE TABLE produtos (
    id        INTEGER PRIMARY KEY,
    nome      TEXT NOT NULL,
    categoria TEXT NOT NULL,
    preco     REAL NOT NULL                -- preço de tabela em R$
);
CREATE TABLE pedidos (
    id          INTEGER PRIMARY KEY,
    cliente_id  INTEGER NOT NULL REFERENCES clientes(id),
    data_pedido TEXT NOT NULL,             -- AAAA-MM-DD
    status      TEXT NOT NULL,             -- entregue | em_transito | cancelado
    canal       TEXT NOT NULL              -- site | app | marketplace
);
CREATE TABLE itens_pedido (
    id             INTEGER PRIMARY KEY,
    pedido_id      INTEGER NOT NULL REFERENCES pedidos(id),
    produto_id     INTEGER NOT NULL REFERENCES produtos(id),
    quantidade     INTEGER NOT NULL,
    preco_unitario REAL NOT NULL           -- preço pago, já com desconto
);
CREATE INDEX idx_pedidos_cliente ON pedidos(cliente_id);
CREATE INDEX idx_pedidos_data ON pedidos(data_pedido);
CREATE INDEX idx_itens_pedido ON itens_pedido(pedido_id);
"""

NOMES = ["Ana", "Bruno", "Carla", "Diego", "Eduarda", "Felipe", "Gabriela", "Henrique", "Isabela",
         "João", "Larissa", "Marcos", "Natália", "Otávio", "Paula", "Rafael", "Sofia", "Thiago",
         "Vanessa", "Wagner"]
SOBRENOMES = ["Silva", "Santos", "Oliveira", "Souza", "Lima", "Pereira", "Costa", "Rodrigues",
              "Almeida", "Nascimento", "Carvalho", "Gomes", "Ribeiro", "Martins", "Rocha"]
CIDADES = [
    ("São Paulo", "SP", 0.22), ("Rio de Janeiro", "RJ", 0.12), ("Belo Horizonte", "MG", 0.08),
    ("Curitiba", "PR", 0.07), ("Porto Alegre", "RS", 0.07), ("Salvador", "BA", 0.07),
    ("Recife", "PE", 0.06), ("Fortaleza", "CE", 0.06), ("Brasília", "DF", 0.07),
    ("Goiânia", "GO", 0.05), ("Manaus", "AM", 0.04), ("Belém", "PA", 0.04), ("Campinas", "SP", 0.05),
]
CATALOGO = {
    "Eletrônicos": (["Fone Bluetooth", "Smartwatch", "Caixa de Som", "Teclado Mecânico",
                     "Mouse Sem Fio", "Carregador Turbo"], 180.0),
    "Casa": (["Jogo de Panelas", "Luminária LED", "Cafeteira", "Jogo de Cama", "Aspirador Vertical"], 160.0),
    "Moda": (["Tênis Casual", "Jaqueta Jeans", "Mochila Urbana", "Óculos de Sol", "Relógio Analógico"], 140.0),
    "Esporte": (["Tapete de Yoga", "Garrafa Térmica", "Halter Ajustável", "Bicicleta Ergométrica"], 120.0),
    "Livros": (["Box de Ficção", "Guia de Python", "Livro de Receitas", "Biografia"], 60.0),
    "Beleza": (["Kit Skincare", "Perfume", "Secador de Cabelo", "Barbeador Elétrico"], 110.0),
}
VERSOES = ["", " Pro", " Lite", " Max"]


def _clientes(rng: np.random.Generator, n: int) -> pd.DataFrame:
    cidades = rng.choice(len(CIDADES), n, p=[c[2] for c in CIDADES])
    cadastro = pd.Timestamp("2022-01-01") + pd.to_timedelta(rng.integers(0, 4 * 365, n), unit="D")
    return pd.DataFrame({
        "id": np.arange(1, n + 1),
        "nome": [f"{rng.choice(NOMES)} {rng.choice(SOBRENOMES)}" for _ in range(n)],
        "cidade": [CIDADES[i][0] for i in cidades],
        "estado": [CIDADES[i][1] for i in cidades],
        "data_cadastro": cadastro.strftime("%Y-%m-%d"),
    })


def _produtos(rng: np.random.Generator) -> pd.DataFrame:
    linhas = []
    for categoria, (nomes, preco_medio) in CATALOGO.items():
        for nome in nomes:
            for versao in rng.choice(VERSOES, rng.integers(1, 4), replace=False):
                fator = {"": 1.0, " Lite": 0.7, " Pro": 1.5, " Max": 2.0}[versao]
                preco = np.floor(preco_medio * fator * rng.uniform(0.6, 1.6)) + 0.90
                linhas.append((f"{nome}{versao}", categoria, round(float(preco), 2)))
    df = pd.DataFrame(linhas, columns=["nome", "categoria", "preco"])
    df.insert(0, "id", np.arange(1, len(df) + 1))
    return df


def _pedidos(rng: np.random.Generator, clientes: pd.DataFrame, n: int) -> pd.DataFrame:
    dias = pd.date_range("2024-01-01", "2025-12-31", freq="D")
    peso = 1.0 + 0.25 * (dias.year == 2025)            # crescimento de um ano para o outro
    peso = peso * np.where(dias.month.isin([11, 12]), 1.6, 1.0)
    black_friday = pd.to_datetime(["2024-11-29", "2025-11-28"])
    peso = peso * np.where(dias.isin(black_friday), 4.0, 1.0)
    datas = rng.choice(dias, n, p=peso / peso.sum())
    cadastro = pd.to_datetime(clientes["data_cadastro"]).to_numpy()
    # cada pedido vai para um cliente já cadastrado na data
    cliente = np.empty(n, dtype=int)
    for i, data in enumerate(datas):
        elegiveis = np.flatnonzero(cadastro <= data)
        cliente[i] = clientes["id"].iloc[rng.choice(elegiveis)]
    datas = pd.DatetimeIndex(datas)
    recente = datas > pd.Timestamp("2025-12-20")
    status = np.where(rng.random(n) < 0.07, "cancelado", np.where(recente, "em_transito", "entregue"))
    df = pd.DataFrame({
        "cliente_id": cliente,
        "data_pedido": datas.strftime("%Y-%m-%d"),
        "status": status,
        "canal": rng.choice(["site", "app", "marketplace"], n, p=[0.45, 0.35, 0.20]),
    }).sort_values("data_pedido", kind="stable", ignore_index=True)
    df.insert(0, "id", np.arange(1, n + 1))
    return df


def _itens(rng: np.random.Generator, pedidos: pd.DataFrame, produtos: pd.DataFrame) -> pd.DataFrame:
    popularidade = rng.lognormal(0, 0.8, len(produtos))
    por_pedido = rng.choice([1, 2, 3, 4], len(pedidos), p=[0.55, 0.28, 0.12, 0.05])
    linhas = []
    for pedido_id, k in zip(pedidos["id"], por_pedido):
        escolhidos = rng.choice(len(produtos), k, replace=False, p=popularidade / popularidade.sum())
        for p in escolhidos:
            quantidade = int(rng.choice([1, 1, 1, 2, 3]))
            desconto = rng.choice([1.0, 0.95, 0.9, 0.8], p=[0.6, 0.2, 0.15, 0.05])
            linhas.append((pedido_id, int(produtos["id"].iloc[p]), quantidade,
                           round(float(produtos["preco"].iloc[p] * desconto), 2)))
    df = pd.DataFrame(linhas, columns=["pedido_id", "produto_id", "quantidade", "preco_unitario"])
    df.insert(0, "id", np.arange(1, len(df) + 1))
    return df


def criar_banco(caminho: str | Path, clientes: int = 1500, pedidos: int = 12000, semente: int = 42) -> Path:
    """Cria (ou recria) o banco em `caminho` e devolve o caminho."""
    caminho = Path(caminho)
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.unlink(missing_ok=True)

    rng = np.random.default_rng(semente)
    tabela_clientes = _clientes(rng, clientes)
    tabela_produtos = _produtos(rng)
    tabela_pedidos = _pedidos(rng, tabela_clientes, pedidos)
    tabela_itens = _itens(rng, tabela_pedidos, tabela_produtos)

    with sqlite3.connect(caminho) as conexao:
        conexao.executescript(ESQUEMA)
        for nome, tabela in [("clientes", tabela_clientes), ("produtos", tabela_produtos),
                             ("pedidos", tabela_pedidos), ("itens_pedido", tabela_itens)]:
            tabela.to_sql(nome, conexao, if_exists="append", index=False)
    return caminho
