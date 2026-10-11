"""Mede a acurácia de execução do agente num conjunto de perguntas com gabarito.

A resposta conta como certa quando a última consulta do agente devolve as
mesmas linhas que a consulta gabarito (ordem das linhas e das colunas é
ignorada, números arredondados em 2 casas). É a métrica "execution accuracy"
usada em benchmarks de text-to-SQL como o Spider.

Cada pergunta chama a API, então rodar o conjunto tem custo.

    python -m agente_sql.avaliar
"""

from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path

from agente_sql.agente import AgenteSQL, ErroAgente
from agente_sql.banco import criar_banco
from agente_sql.ferramentas import BancoSomenteLeitura, ErroConsulta

NAO_CANCELADO = "p.status <> 'cancelado'"

PERGUNTAS = [
    ("Quantos clientes temos cadastrados?",
     "SELECT COUNT(*) FROM clientes"),
    ("Quantos pedidos foram cancelados em 2025?",
     "SELECT COUNT(*) FROM pedidos WHERE status = 'cancelado' AND data_pedido LIKE '2025%'"),
    ("Qual foi o faturamento total de 2024?",
     f"SELECT ROUND(SUM(i.quantidade * i.preco_unitario), 2) FROM itens_pedido i "
     f"JOIN pedidos p ON p.id = i.pedido_id WHERE {NAO_CANCELADO} AND p.data_pedido LIKE '2024%'"),
    ("Qual categoria de produto mais faturou no período todo? Traga a categoria e o valor.",
     f"SELECT pr.categoria, ROUND(SUM(i.quantidade * i.preco_unitario), 2) AS total FROM itens_pedido i "
     f"JOIN pedidos p ON p.id = i.pedido_id JOIN produtos pr ON pr.id = i.produto_id "
     f"WHERE {NAO_CANCELADO} GROUP BY pr.categoria ORDER BY total DESC LIMIT 1"),
    ("Quantos pedidos foram feitos por canal em 2025?",
     "SELECT canal, COUNT(*) FROM pedidos WHERE data_pedido LIKE '2025%' GROUP BY canal"),
    ("Qual foi o dia com mais pedidos e quantos foram?",
     "SELECT data_pedido, COUNT(*) AS n FROM pedidos GROUP BY data_pedido ORDER BY n DESC LIMIT 1"),
    ("Quais são os 3 estados com mais clientes, e quantos clientes cada um tem?",
     "SELECT estado, COUNT(*) AS n FROM clientes GROUP BY estado ORDER BY n DESC LIMIT 3"),
    ("Qual o ticket médio dos pedidos entregues em 2025, em reais?",
     "SELECT ROUND(AVG(total), 2) FROM (SELECT p.id, SUM(i.quantidade * i.preco_unitario) AS total "
     "FROM pedidos p JOIN itens_pedido i ON i.pedido_id = p.id "
     "WHERE p.status = 'entregue' AND p.data_pedido LIKE '2025%' GROUP BY p.id)"),
]


def normalizar(linhas: list[list]) -> Counter:
    def valor(v):
        return round(float(v), 2) if isinstance(v, (int, float)) else str(v)

    return Counter(tuple(sorted(map(valor, linha), key=str)) for linha in linhas)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--banco", type=Path, default=Path("dados/loja.db"))
    parser.add_argument("--esforco", default="medium")
    args = parser.parse_args()
    if not args.banco.exists():
        criar_banco(args.banco)

    banco = BancoSomenteLeitura(args.banco, limite_linhas=10_000)
    agente = AgenteSQL(banco, esforco=args.esforco)
    acertos = 0
    for pergunta, gabarito in PERGUNTAS:
        agente.reiniciar()
        esperado = normalizar(banco.executar_sql(gabarito)["linhas"])
        try:
            consulta = agente.perguntar(pergunta).ultima_consulta
            obtido = normalizar(banco.executar_sql(consulta)["linhas"]) if consulta else Counter()
        except (ErroAgente, ErroConsulta) as erro:
            consulta, obtido = f"(falhou: {erro})", Counter()
        certo = obtido == esperado
        acertos += certo
        print(f"[{'ok' if certo else 'ERRO'}] {pergunta}")
        if not certo:
            print(f"       consulta do agente: {consulta}")
    print(f"\nAcurácia de execução: {acertos}/{len(PERGUNTAS)} ({acertos / len(PERGUNTAS):.0%})")


if __name__ == "__main__":
    main()
