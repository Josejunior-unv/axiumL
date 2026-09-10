"""Servidorzinho HTTP de saúde.

Existe por uma razão prática: hospedagens gratuitas (Render, por exemplo) só
aceitam processos que abram uma porta, e derrubam o serviço quando ele fica um
tempo sem receber requisição. Este servidor responde nessa porta e serve de alvo
para um "pinger" externo manter o bot acordado.

Em VPS, Docker ou no computador de casa ele nem sobe — só entra em cena quando a
variável PORT está definida.
"""

from __future__ import annotations

import json
import logging
import threading
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Callable

log = logging.getLogger(__name__)

INICIO = datetime.now(timezone.utc)


def _estado_padrao() -> dict:
    ativo_ha = int((datetime.now(timezone.utc) - INICIO).total_seconds())
    return {"status": "ok", "ativo_ha_segundos": ativo_ha}


def criar_servidor(porta: int, estado: Callable[[], dict] | None = None) -> ThreadingHTTPServer:
    """Cria (sem iniciar) o servidor. Porta 0 = o sistema escolhe — usado nos testes."""
    obter_estado = estado or _estado_padrao

    class Manipulador(BaseHTTPRequestHandler):
        def do_GET(self):  # noqa: N802 (nome exigido pela biblioteca)
            corpo = json.dumps(obter_estado()).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(corpo)))
            self.end_headers()
            self.wfile.write(corpo)

        def do_HEAD(self):  # noqa: N802 — alguns monitores usam HEAD
            self.send_response(200)
            self.send_header("Content-Length", "0")
            self.end_headers()

        def log_message(self, *_args):
            pass  # o ping é de minuto em minuto; não polui o log

    return ThreadingHTTPServer(("0.0.0.0", porta), Manipulador)


def iniciar(porta: int, estado: Callable[[], dict] | None = None) -> ThreadingHTTPServer:
    """Sobe o servidor em uma thread de fundo e devolve o servidor."""
    servidor = criar_servidor(porta, estado)
    thread = threading.Thread(target=servidor.serve_forever, daemon=True, name="saude")
    thread.start()
    log.info("porta de saúde ouvindo em %s", servidor.server_address[1])
    return servidor
