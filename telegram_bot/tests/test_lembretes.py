"""Testes da fila de lembretes, da recorrência e do resumo diário."""

from datetime import datetime, timedelta, timezone

from assistente import db, lembretes, servicos


def _fuso_do_meio_dia() -> str:
    """Fuso em que 'agora' cai perto do meio-dia — deixa os testes previsíveis."""
    deslocamento = (12 - datetime.now(timezone.utc).hour) % 24
    if deslocamento > 12:
        deslocamento -= 24
    # Em 'Etc/GMT-3' o sinal é invertido: GMT-3 significa UTC+3.
    return f"Etc/GMT{-deslocamento:+d}"


def test_fila_devolve_so_o_que_ja_venceu(conn, usuario, daqui):
    servicos.criar_compromisso(conn, usuario, "Daqui a pouco", daqui(minutes=10),
                               antecedencia_min=5)
    servicos.criar_lembrete_avulso(conn, usuario, "remédio", daqui(minutes=-1))
    servicos.criar_lembrete_avulso(conn, usuario, "só amanhã", daqui(days=1))

    devidos = lembretes.lembretes_devidos(conn, db.agora_utc())
    assert [d.texto for d in devidos] == ["remédio"]
    assert devidos[0].atrasado is False

    lembretes.marcar_enviado(conn, devidos[0].id)
    assert lembretes.lembretes_devidos(conn, db.agora_utc()) == []


def test_lembrete_muito_antigo_vem_marcado_como_atrasado(conn, usuario, daqui):
    servicos.criar_lembrete_avulso(conn, usuario, "antigo", daqui(hours=-30))
    devidos = lembretes.lembretes_devidos(conn, db.agora_utc())
    assert len(devidos) == 1 and devidos[0].atrasado is True


def test_proxima_ocorrencia():
    base = datetime(2026, 1, 31, 9, 0, tzinfo=timezone.utc)
    assert lembretes.proxima_ocorrencia(base, "diaria").day == 1
    assert lembretes.proxima_ocorrencia(base, "semanal") == base + timedelta(days=7)
    # 31 de janeiro + 1 mês = 28 de fevereiro (não estoura o mês).
    assert lembretes.proxima_ocorrencia(base, "mensal") == base.replace(month=2, day=28)
    assert lembretes.proxima_ocorrencia(base, None) is None


def test_recorrencia_pula_ocorrencias_perdidas(conn, usuario, daqui):
    # Compromisso diário que ficou 3 dias sem o bot no ar.
    compromisso = servicos.criar_compromisso(
        conn, usuario, "Academia", daqui(days=-3, hours=2), recorrencia="diaria"
    )
    atualizado = lembretes.avancar_recorrencia(conn, usuario, compromisso)
    assert atualizado is not None
    assert atualizado.quando > usuario.agora()
    assert atualizado.quando < usuario.agora() + timedelta(days=1)
    # E os lembretes da nova data (hoje daqui a 2h) foram criados.
    pendentes = conn.execute(
        "SELECT COUNT(*) c FROM lembretes WHERE compromisso_id = ? AND enviado = 0",
        (compromisso.id,),
    ).fetchone()["c"]
    assert pendentes == 2


def test_resumo_diario_pendente_e_registrado(conn):
    fuso = _fuso_do_meio_dia()
    servicos.garantir_usuario(conn, chat_id=7, nome="Ana", fuso_padrao=fuso)
    servicos.atualizar_preferencias(conn, 7, hora_resumo="09:00")  # já passou (é ~meio-dia)

    pendentes = lembretes.resumos_pendentes(conn)
    assert [u.chat_id for u in pendentes] == [7]

    hoje_local = pendentes[0].agora().strftime("%Y-%m-%d")
    servicos.registrar_resumo_enviado(conn, 7, hoje_local)
    assert lembretes.resumos_pendentes(conn) == []


def test_resumo_so_dispara_depois_do_horario_e_dentro_da_janela(conn):
    fuso = _fuso_do_meio_dia()
    servicos.garantir_usuario(conn, chat_id=8, fuso_padrao=fuso)

    servicos.atualizar_preferencias(conn, 8, hora_resumo="23:00")  # ainda vai chegar
    assert lembretes.resumos_pendentes(conn) == []

    servicos.atualizar_preferencias(conn, 8, hora_resumo="02:00")  # passou há muito
    assert lembretes.resumos_pendentes(conn) == []


def test_sem_hora_de_resumo_nao_entra_na_fila(conn, usuario):
    assert lembretes.resumos_pendentes(conn) == []
