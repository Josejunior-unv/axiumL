"""A porta que as hospedagens exigem e que o monitor externo usa."""

import json
import threading
import urllib.request

from assistente import config, saude


def _pedir(porta, caminho="/saude", metodo="GET"):
    # sem passar por proxy: é localhost
    abridor = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    pedido = urllib.request.Request(f"http://127.0.0.1:{porta}{caminho}", method=metodo)
    return abridor.open(pedido, timeout=5)


def test_responde_ok_em_qualquer_caminho():
    servidor = saude.criar_servidor(0)
    porta = servidor.server_address[1]
    thread = threading.Thread(target=servidor.serve_forever, daemon=True)
    thread.start()
    try:
        resposta = _pedir(porta)
        assert resposta.status == 200
        corpo = json.loads(resposta.read())
        assert corpo["status"] == "ok"
        assert corpo["ativo_ha_segundos"] >= 0

        # a raiz também responde (é o que o Render usa para o health check)
        assert _pedir(porta, "/").status == 200
        # e alguns monitores mandam HEAD
        assert _pedir(porta, "/saude", "HEAD").status == 200
    finally:
        servidor.shutdown()
        servidor.server_close()


def test_estado_pode_ser_personalizado():
    servidor = saude.criar_servidor(0, estado=lambda: {"status": "ok", "lembretes": 3})
    porta = servidor.server_address[1]
    threading.Thread(target=servidor.serve_forever, daemon=True).start()
    try:
        assert json.loads(_pedir(porta).read())["lembretes"] == 3
    finally:
        servidor.shutdown()
        servidor.server_close()


def test_porta_vem_da_hospedagem(monkeypatch, tmp_path):
    monkeypatch.setenv("TELEGRAM_TOKEN", "123:abc")
    monkeypatch.setenv("PORT", "10000")
    cfg = config.carregar(env_file=tmp_path / "nao-existe")
    assert cfg.porta == 10000


def test_sem_porta_nao_sobe_servidor(monkeypatch, tmp_path):
    monkeypatch.setenv("TELEGRAM_TOKEN", "123:abc")
    monkeypatch.delenv("PORT", raising=False)
    assert config.carregar(env_file=tmp_path / "nao-existe").porta is None


def test_senha_do_banco_nao_aparece_no_log(monkeypatch, tmp_path):
    monkeypatch.setenv("TELEGRAM_TOKEN", "123:abc")
    monkeypatch.setenv("DATABASE_URL", "postgresql://ana:segredo123@ep-teste.neon.tech/bot")
    cfg = config.carregar(env_file=tmp_path / "nao-existe")
    assert cfg.banco.endswith("/bot")
    assert "segredo123" not in cfg.banco_visivel
    assert cfg.banco_visivel == "postgresql://***@ep-teste.neon.tech/bot"
