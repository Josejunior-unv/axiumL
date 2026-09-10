"""Testes das ferramentas que o modelo chama (sem tocar na API)."""

from datetime import timedelta
from pathlib import Path

import pytest

from assistente import servicos
from assistente.config import Config
from assistente.ia import Assistente


@pytest.fixture()
def assistente(conn):
    config = Config(
        token="x", caminho_db=Path("/tmp/x.db"), fuso_padrao="America/Sao_Paulo",
        chats_permitidos=frozenset(), antecedencia_padrao=30, hora_resumo_padrao="08:00",
        intervalo_lembretes=30, chave_anthropic=None, modelo="claude-opus-5",
        esforco="low", max_tokens=16000, usar_fallback=True, historico_max=20,
    )
    return Assistente(conn, config)


def test_sem_chave_o_assistente_fica_inativo(assistente):
    assert assistente.ativo is False


def test_criar_e_listar_compromisso(assistente, conn, usuario):
    amanha = (usuario.agora() + timedelta(days=1)).replace(hour=15, minute=0)
    resposta = assistente._executar(
        usuario,
        "criar_compromisso",
        {"titulo": "Dentista", "quando": amanha.strftime("%Y-%m-%dT%H:%M"), "local": "Clínica"},
    )
    assert "Dentista" in resposta

    agenda = assistente._executar(usuario, "listar_compromissos", {"periodo": "amanha"})
    assert "Dentista" in agenda and "Clínica" in agenda
    assert "Nada na agenda" in assistente._executar(
        usuario, "listar_compromissos", {"periodo": "passados"}
    )


def test_data_invalida_nao_quebra(assistente, usuario):
    resposta = assistente._executar(usuario, "criar_compromisso", {"titulo": "X", "quando": "sei lá"})
    assert "Não entendi a data" in resposta


def test_data_em_texto_livre_ainda_funciona(assistente, conn, usuario):
    # O modelo deveria mandar ISO, mas se escorregar a interpretação em PT salva.
    resposta = assistente._executar(
        usuario, "criar_compromisso", {"titulo": "Café", "quando": "amanhã às 9h"}
    )
    assert "criado" in resposta
    assert servicos.proximos_compromissos(conn, usuario)[0].titulo == "Café"


def test_remarcar_e_concluir(assistente, conn, usuario):
    depois = (usuario.agora() + timedelta(days=2)).replace(hour=10, minute=0)
    assistente._executar(usuario, "criar_compromisso",
                         {"titulo": "Reunião", "quando": depois.strftime("%Y-%m-%dT%H:%M")})
    compromisso = servicos.proximos_compromissos(conn, usuario)[0]

    novo = depois + timedelta(hours=3)
    assistente._executar(usuario, "atualizar_compromisso",
                         {"id": compromisso.id, "quando": novo.strftime("%Y-%m-%dT%H:%M")})
    assert servicos.obter_compromisso(conn, usuario, compromisso.id).quando.hour == 13

    assistente._executar(usuario, "mudar_status_compromisso",
                         {"id": compromisso.id, "status": "concluido"})
    assert servicos.obter_compromisso(conn, usuario, compromisso.id).status == "concluido"


def test_compromisso_inexistente(assistente, usuario):
    assert "Não existe" in assistente._executar(
        usuario, "mudar_status_compromisso", {"id": 999, "status": "cancelado"}
    )


def test_notas_pelas_ferramentas(assistente, conn, usuario):
    assistente._executar(usuario, "salvar_nota", {"texto": "senha do wifi: casa123"})
    assert "casa123" in assistente._executar(usuario, "buscar_notas", {"termo": "wifi"})
    assert "Nenhuma nota" in assistente._executar(usuario, "buscar_notas", {"termo": "carro"})
    nota = servicos.listar_notas(conn, usuario)[0]
    assert "apagada" in assistente._executar(usuario, "apagar_nota", {"id": nota.id}).lower()


def test_lembrete_avulso(assistente, conn, usuario):
    daqui = (usuario.agora() + timedelta(hours=3)).strftime("%Y-%m-%dT%H:%M")
    assert "Lembrete" in assistente._executar(
        usuario, "criar_lembrete", {"texto": "tomar remédio", "quando": daqui}
    )
    total = conn.execute("SELECT COUNT(*) c FROM lembretes WHERE tipo = 'avulso'").fetchone()["c"]
    assert total == 1


def test_preferencias_pela_ferramenta(assistente, conn, usuario):
    resposta = assistente._executar(
        usuario, "ajustar_preferencias", {"fuso": "Europe/Lisbon", "hora_resumo": "07:30"}
    )
    assert "Europe/Lisbon" in resposta and "07:30" in resposta
    assert servicos.obter_usuario(conn, usuario.chat_id).fuso == "Europe/Lisbon"


def test_ferramenta_desconhecida(assistente, usuario):
    assert "desconhecida" in assistente._executar(usuario, "voar", {})


# --------------------------------------------------------------------------- #
# Laço de conversa (com um cliente falso no lugar da API)
# --------------------------------------------------------------------------- #

class _Bloco:
    def __init__(self, **campos):
        self.__dict__.update(campos)


class _Resposta:
    def __init__(self, content, stop_reason="end_turn"):
        self.content = content
        self.stop_reason = stop_reason


class _ClienteFalso:
    """Devolve respostas pré-programadas e guarda o que foi enviado."""

    def __init__(self, respostas):
        self.respostas = list(respostas)
        self.chamadas = []
        criar = self._criar

        class _Mensagens:
            create = staticmethod(criar)

        class _Beta:
            messages = _Mensagens()

        self.messages = _Mensagens()
        self.beta = _Beta()

    async def _criar(self, **parametros):
        self.chamadas.append(parametros)
        return self.respostas.pop(0)


@pytest.mark.asyncio
async def test_conversa_chama_ferramenta_e_responde(assistente, conn, usuario):
    amanha = (usuario.agora() + timedelta(days=1)).replace(hour=15, minute=0)
    assistente._cliente = _ClienteFalso(
        [
            _Resposta(
                [
                    _Bloco(type="text", text="Já marco aqui."),
                    _Bloco(
                        type="tool_use", id="tu_1", name="criar_compromisso",
                        input={"titulo": "Dentista", "quando": amanha.strftime("%Y-%m-%dT%H:%M")},
                    ),
                ],
                stop_reason="tool_use",
            ),
            _Resposta([_Bloco(type="text", text="Pronto, dentista amanhã às 15:00. 🦷")]),
        ]
    )

    resposta = await assistente.responder(usuario, "marca dentista amanhã 15h")

    assert "dentista" in resposta.lower()
    assert servicos.proximos_compromissos(conn, usuario)[0].titulo == "Dentista"
    # O histórico guarda a pergunta e a resposta final.
    assert servicos.historico(conn, usuario.chat_id) == [
        {"role": "user", "content": "marca dentista amanhã 15h"},
        {"role": "assistant", "content": resposta},
    ]
    # A segunda chamada levou o resultado da ferramenta de volta ao modelo.
    segunda = assistente._cliente.chamadas[1]["messages"]
    assert segunda[-1]["content"][0]["tool_use_id"] == "tu_1"


@pytest.mark.asyncio
async def test_erro_na_ferramenta_volta_para_o_modelo(assistente, conn, usuario):
    assistente._cliente = _ClienteFalso(
        [
            _Resposta(
                [_Bloco(type="tool_use", id="tu_1", name="apagar_nota", input={"id": "abacaxi"})],
                stop_reason="tool_use",
            ),
            _Resposta([_Bloco(type="text", text="Não consegui apagar essa nota.")]),
        ]
    )
    resposta = await assistente.responder(usuario, "apaga a nota abacaxi")
    assert "não consegui" in resposta.lower()
    resultado = assistente._cliente.chamadas[1]["messages"][-1]["content"][0]
    assert resultado["is_error"] is True


@pytest.mark.asyncio
async def test_recusa_do_modelo_vira_mensagem_amigavel(assistente, usuario):
    assistente._cliente = _ClienteFalso([_Resposta([], stop_reason="refusal")])
    resposta = await assistente.responder(usuario, "faz algo proibido")
    assert "não consigo ajudar" in resposta.lower()
