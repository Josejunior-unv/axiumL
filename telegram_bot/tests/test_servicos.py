"""Testes da camada de regras: agenda, lembretes programados e notas."""

from datetime import timedelta

import pytest

from assistente import servicos


def _lembretes(conn, compromisso_id):
    return conn.execute(
        "SELECT tipo, enviado FROM lembretes WHERE compromisso_id = ? ORDER BY disparo_utc",
        (compromisso_id,),
    ).fetchall()


def test_criar_compromisso_programa_dois_lembretes(conn, usuario, daqui):
    compromisso = servicos.criar_compromisso(
        conn, usuario, "Dentista", daqui(hours=3), local="Clínica"
    )
    assert compromisso.id > 0
    assert compromisso.local == "Clínica"
    assert [l["tipo"] for l in _lembretes(conn, compromisso.id)] == ["antes", "na_hora"]


def test_compromisso_no_passado_nao_gera_lembrete(conn, usuario, daqui):
    compromisso = servicos.criar_compromisso(conn, usuario, "Já foi", daqui(hours=-2))
    assert _lembretes(conn, compromisso.id) == []


def test_antecedencia_zero_gera_so_o_aviso_da_hora(conn, usuario, daqui):
    compromisso = servicos.criar_compromisso(
        conn, usuario, "Sem antecedência", daqui(hours=2), antecedencia_min=0
    )
    assert [l["tipo"] for l in _lembretes(conn, compromisso.id)] == ["na_hora"]


def test_listar_por_periodo(conn, usuario, daqui):
    servicos.criar_compromisso(conn, usuario, "Hoje", daqui(hours=2))
    servicos.criar_compromisso(conn, usuario, "Semana que vem", daqui(days=8))
    agora = usuario.agora()
    proximos_dois_dias = servicos.listar_compromissos(
        conn, usuario, inicio=agora, fim=agora + timedelta(days=2)
    )
    assert [c.titulo for c in proximos_dois_dias] == ["Hoje"]
    assert len(servicos.proximos_compromissos(conn, usuario)) == 2


def test_reagendar_recria_os_lembretes(conn, usuario, daqui):
    compromisso = servicos.criar_compromisso(conn, usuario, "Reunião", daqui(hours=2))
    novo = servicos.reagendar_compromisso(conn, usuario, compromisso.id, daqui(days=1))
    assert novo is not None and novo.quando > compromisso.quando
    assert len(_lembretes(conn, compromisso.id)) == 2  # os antigos foram apagados


def test_cancelar_remove_lembretes_pendentes(conn, usuario, daqui):
    compromisso = servicos.criar_compromisso(conn, usuario, "Cancelar", daqui(hours=5))
    servicos.mudar_status(conn, usuario, compromisso.id, "cancelado")
    assert _lembretes(conn, compromisso.id) == []
    assert servicos.obter_compromisso(conn, usuario, compromisso.id).status == "cancelado"


def test_compromisso_de_outra_pessoa_nao_aparece(conn, usuario, daqui):
    outro = servicos.garantir_usuario(conn, chat_id=99, nome="Bruno")
    compromisso = servicos.criar_compromisso(conn, outro, "Segredo", daqui(hours=1))
    assert servicos.obter_compromisso(conn, usuario, compromisso.id) is None
    assert servicos.proximos_compromissos(conn, usuario) == []


def test_editar_compromisso(conn, usuario, daqui):
    compromisso = servicos.criar_compromisso(conn, usuario, "Consulta", daqui(hours=4))
    editado = servicos.editar_compromisso(
        conn, usuario, compromisso.id, titulo="Consulta com Dr. Silva", local="Centro"
    )
    assert editado.titulo == "Consulta com Dr. Silva"
    assert editado.local == "Centro"


def test_status_invalido(conn, usuario, daqui):
    compromisso = servicos.criar_compromisso(conn, usuario, "X", daqui(hours=1))
    with pytest.raises(ValueError):
        servicos.mudar_status(conn, usuario, compromisso.id, "sumido")


def test_notas(conn, usuario):
    servicos.salvar_nota(conn, usuario, "wifi do escritório: casa123", etiquetas="senha")
    servicos.salvar_nota(conn, usuario, "presente da mãe: livro de jardinagem")
    assert len(servicos.listar_notas(conn, usuario)) == 2
    achadas = servicos.buscar_notas(conn, usuario, "wifi")
    assert len(achadas) == 1 and "casa123" in achadas[0].texto
    assert servicos.buscar_notas(conn, usuario, "senha")  # busca também nas etiquetas
    assert servicos.apagar_nota(conn, usuario, achadas[0].id) is True
    assert servicos.apagar_nota(conn, usuario, 12345) is False


def test_preferencias(conn, usuario):
    atualizado = servicos.atualizar_preferencias(
        conn, usuario.chat_id, fuso="Europe/Lisbon", hora_resumo="8", antecedencia_min=15
    )
    assert atualizado.fuso == "Europe/Lisbon"
    assert atualizado.hora_resumo == "08:00"
    assert atualizado.antecedencia_min == 15
    desligado = servicos.atualizar_preferencias(conn, usuario.chat_id, desligar_resumo=True)
    assert desligado.hora_resumo is None


def test_fuso_invalido_cai_no_padrao(conn, usuario):
    atualizado = servicos.atualizar_preferencias(conn, usuario.chat_id, fuso="Marte/Olympus")
    assert atualizado.fuso == "America/Sao_Paulo"


def test_historico_da_conversa(conn, usuario):
    servicos.salvar_mensagem(conn, usuario.chat_id, "user", "oi")
    servicos.salvar_mensagem(conn, usuario.chat_id, "assistant", "olá!")
    assert servicos.historico(conn, usuario.chat_id) == [
        {"role": "user", "content": "oi"},
        {"role": "assistant", "content": "olá!"},
    ]
    servicos.limpar_historico(conn, usuario.chat_id)
    assert servicos.historico(conn, usuario.chat_id) == []


def test_historico_e_normalizado_para_a_api(conn, usuario):
    # Uma resposta que nunca chegou (erro de rede) deixa duas mensagens seguidas da pessoa.
    servicos.salvar_mensagem(conn, usuario.chat_id, "assistant", "sobra de antes")
    servicos.salvar_mensagem(conn, usuario.chat_id, "user", "oi")
    servicos.salvar_mensagem(conn, usuario.chat_id, "user", "tá aí?")
    servicos.salvar_mensagem(conn, usuario.chat_id, "assistant", "tô sim")

    assert servicos.historico(conn, usuario.chat_id) == [
        {"role": "user", "content": "oi\ntá aí?"},
        {"role": "assistant", "content": "tô sim"},
    ]


# --------------------------------------------------------------------------- #
# É um bot de uma pessoa só
# --------------------------------------------------------------------------- #

def test_o_primeiro_chat_vira_dono_e_tranca_o_resto(conn):
    assert servicos.obter_dono(conn) is None
    assert servicos.autorizar(conn, 111) is True          # primeira pessoa: entra e vira dona
    assert servicos.obter_dono(conn) == 111
    assert servicos.autorizar(conn, 222) is False         # qualquer outro fica de fora
    assert servicos.autorizar(conn, 111) is True          # a dona continua entrando


def test_lista_no_env_tem_prioridade_sobre_o_dono(conn):
    servicos.definir_dono(conn, 111)
    permitidos = frozenset({999})
    assert servicos.autorizar(conn, 999, permitidos=permitidos) is True
    assert servicos.autorizar(conn, 111, permitidos=permitidos) is False


def test_modo_aberto_nao_tranca_em_ninguem(conn):
    assert servicos.autorizar(conn, 555, aberto=True) is True
    assert servicos.autorizar(conn, 666, aberto=True) is True
    assert servicos.obter_dono(conn) is None
