"""Pergunte ao banco da loja em português.

    python -m agente_sql "Qual foi o faturamento por mês em 2025?"
    python -m agente_sql            # modo conversa (digite 'sair' para encerrar)
"""

from __future__ import annotations

import argparse
from pathlib import Path

import anthropic

from agente_sql.agente import AgenteSQL, ErroAgente
from agente_sql.banco import criar_banco
from agente_sql.ferramentas import BancoSomenteLeitura

BANCO_PADRAO = Path("dados/loja.db")


def mostrar_ferramenta(nome: str, entrada: dict) -> None:
    detalhe = " ".join(str(v) for v in entrada.values())
    print(f"  · {nome} {detalhe[:110]}{'…' if len(detalhe) > 110 else ''}")


def responder(agente: AgenteSQL, pergunta: str) -> None:
    try:
        resposta = agente.perguntar(pergunta)
    except anthropic.AuthenticationError:
        print("Credencial da API inválida ou ausente: defina ANTHROPIC_API_KEY.")
    except anthropic.RateLimitError:
        print("Limite de requisições atingido; tente de novo em instantes.")
    except anthropic.APIConnectionError:
        print("Sem conexão com a API da Anthropic.")
    except anthropic.APIStatusError as erro:
        print(f"Erro da API ({erro.status_code}): {erro.message}")
    except ErroAgente as erro:
        print(f"Não consegui responder: {erro}")
    else:
        print(f"\n{resposta.texto}\n")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("pergunta", nargs="?")
    parser.add_argument("--banco", type=Path, default=BANCO_PADRAO)
    parser.add_argument("--esforco", default="medium", choices=["low", "medium", "high", "xhigh", "max"])
    args = parser.parse_args()

    if not args.banco.exists():
        print(f"Criando o banco de exemplo em {args.banco}...")
        criar_banco(args.banco)

    agente = AgenteSQL(BancoSomenteLeitura(args.banco), esforco=args.esforco,
                       ao_usar_ferramenta=mostrar_ferramenta)
    if args.pergunta:
        responder(agente, args.pergunta)
        return

    print("Pergunte sobre clientes, produtos e pedidos da loja. 'nova' recomeça a conversa, 'sair' encerra.")
    while True:
        try:
            pergunta = input("\n> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if pergunta.lower() in {"sair", "exit", "quit"}:
            break
        if pergunta.lower() == "nova":
            agente.reiniciar()
            print("Conversa reiniciada.")
        elif pergunta:
            responder(agente, pergunta)


if __name__ == "__main__":
    main()
