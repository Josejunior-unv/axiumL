"""Exporta saídas reais das ferramentas do agente para dentro da animação (index.html).

    python animacao/exportar_dados.py

Cria o banco de exemplo num diretório temporário e roda as ferramentas de
verdade: listar e descrever tabelas, uma consulta com erro e a corrigida, as
tentativas de escrita (com as mensagens reais de bloqueio) e as comparações da
avaliação. Não chama a API da Anthropic: as falas do modelo na animação são um
roteiro ilustrativo, e tudo o que vem do banco é real.
"""

from __future__ import annotations

import inspect
import json
import re
import sys
import tempfile
from collections import Counter
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from agente_sql.agente import FERRAMENTAS, MODELO, SISTEMA, AgenteSQL  # noqa: E402
from agente_sql.avaliar import PERGUNTAS, normalizar  # noqa: E402
from agente_sql.banco import criar_banco  # noqa: E402
from agente_sql.ferramentas import BancoSomenteLeitura, ErroConsulta  # noqa: E402

PADROES = {n: p.default for n, p in inspect.signature(AgenteSQL.__init__).parameters.items()}
PERGUNTA = "Qual categoria de produto mais faturou em 2025, e quanto?"
FILTRO = "p.status <> 'cancelado' AND p.data_pedido LIKE '2025%'"
SQL_ERRADO = ("SELECT pr.categoria, SUM(i.quantidade * i.preco) AS faturamento FROM itens_pedido i "
              "JOIN pedidos p ON p.id = i.pedido_id JOIN produtos pr ON pr.id = i.produto_id "
              f"WHERE {FILTRO} GROUP BY pr.categoria ORDER BY faturamento DESC")
SQL_CERTO = SQL_ERRADO.replace("i.preco)", "i.preco_unitario)").replace("SUM(", "ROUND(SUM(").replace(") AS faturamento", "), 2) AS faturamento")

ATAQUES = [
    ("Leitura comum", "SELECT COUNT(*) FROM pedidos"),
    ("Duas instruções", "SELECT 1; DROP TABLE clientes"),
    ("Inserir", "INSERT INTO produtos (nome, categoria, preco) VALUES ('x', 'y', 1)"),
    ("Apagar tabela", "DROP TABLE clientes"),
    ("Anexar outro arquivo", "ATTACH DATABASE 'outro.db' AS outro"),
    ("Mudar configuração", "PRAGMA journal_mode = WAL"),
    ("Consulta sem fim", "WITH RECURSIVE r(n) AS (SELECT 1 UNION ALL SELECT n + 1 FROM r) SELECT COUNT(*) FROM r"),
]


def gravar_no_html(dados: dict) -> None:
    pagina = Path(__file__).with_name("index.html")
    bloco = json.dumps(dados, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    html = pagina.read_text()
    novo, n = re.subn(r'(<script id="dados" type="application/json">).*?(</script>)',
                      lambda m: m.group(1) + bloco + m.group(2), html, flags=re.S)
    assert n == 1, "bloco de dados não encontrado"
    pagina.write_text(novo)
    print(f"{len(bloco) / 1024:.0f} KB de dados gravados em {pagina}")


def rodar(banco, consulta):
    try:
        return {"ok": True, **banco.executar_sql(consulta)}
    except ErroConsulta as erro:
        return {"ok": False, "erro": str(erro)}


def main() -> None:
    with tempfile.TemporaryDirectory() as pasta:
        caminho = criar_banco(Path(pasta) / "loja.db")
        banco = BancoSomenteLeitura(caminho)
        tabelas = json.loads(banco.listar_tabelas())
        esquemas = {t: json.loads(banco.descrever_tabela(t)) for t in ("pedidos", "itens_pedido", "produtos", "clientes")}
        errado, certo = rodar(banco, SQL_ERRADO), rodar(banco, SQL_CERTO)
        ataques = []
        for nome, sql in ATAQUES:
            r = rodar(banco, sql)
            ataques.append({"nome": nome, "sql": sql, "ok": r["ok"], "erro": r.get("erro"),
                            "linhas": r.get("linhas")})
        grande = banco.executar_sql("SELECT * FROM itens_pedido")

        # avaliação: o gabarito e duas respostas possíveis do agente para a mesma pergunta
        pergunta_av, gabarito = PERGUNTAS[3]
        gab = banco.executar_sql(gabarito)
        invertida = banco.executar_sql(gabarito.replace("SELECT pr.categoria, ROUND(SUM(i.quantidade * i.preco_unitario), 2) AS total",
                                                        "SELECT ROUND(SUM(i.quantidade * i.preco_unitario), 2) AS total, pr.categoria"))
        com_cancelados = banco.executar_sql(gabarito.replace("WHERE p.status <> 'cancelado' ", ""))
        avaliacao = {
            "pergunta": pergunta_av, "gabarito_sql": gabarito,
            "gabarito": gab, "invertida": invertida, "com_cancelados": com_cancelados,
            "invertida_bate": normalizar(invertida["linhas"]) == normalizar(gab["linhas"]),
            "cancelados_bate": normalizar(com_cancelados["linhas"]) == normalizar(gab["linhas"]),
            "normalizado": [list(k) for k in Counter(normalizar(gab["linhas"])).keys()],
            "n_perguntas": len(PERGUNTAS), "perguntas": [p for p, _ in PERGUNTAS],
        }
        banco.fechar()

    dados = {
        "modelo": MODELO, "max_passos": PADROES["max_passos"], "esforco": PADROES["esforco"],
        "limite_linhas": 200, "tempo_limite": 5,
        "sistema": SISTEMA,
        "ferramentas": [{"nome": f["name"], "descricao": f["description"], "campos": list(f["input_schema"]["properties"])} for f in FERRAMENTAS],
        "pergunta": PERGUNTA, "tabelas": tabelas["tabelas"], "esquemas": esquemas,
        "sql_errado": SQL_ERRADO, "errado": errado, "sql_certo": SQL_CERTO, "certo": certo,
        "ataques": ataques, "grande": {"linhas": len(grande["linhas"]), "truncado": grande["truncado"]},
        "avaliacao": avaliacao,
    }
    gravar_no_html(dados)


if __name__ == "__main__":
    main()
