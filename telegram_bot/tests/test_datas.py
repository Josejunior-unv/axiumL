"""Testes da interpretação de datas em português."""

from datetime import datetime
from zoneinfo import ZoneInfo

import pytest

from assistente.datas import (
    formatar_data_hora,
    formatar_duracao,
    interpretar_antecedencia,
    interpretar_quando,
)

SP = ZoneInfo("America/Sao_Paulo")
# Quinta-feira, 10/09/2026, 10:20.
AGORA = datetime(2026, 9, 10, 10, 20, tzinfo=SP)


def quando(texto):
    resultado = interpretar_quando(texto, AGORA)
    assert resultado is not None, f"não interpretou: {texto!r}"
    return resultado


@pytest.mark.parametrize(
    "texto, esperado, titulo",
    [
        ("dentista amanhã às 15h", datetime(2026, 9, 11, 15, 0), "dentista"),
        ("reunião com a Ana sexta 9:30", datetime(2026, 9, 11, 9, 30), "reunião com a Ana"),
        ("corte de cabelo 15h30", datetime(2026, 9, 10, 15, 30), "corte de cabelo"),
        ("jantar às 8 da noite", datetime(2026, 9, 10, 20, 0), "jantar"),
        ("café amanhã de manhã", datetime(2026, 9, 11, 9, 0), "café"),
        ("médico depois de amanhã às 10h", datetime(2026, 9, 12, 10, 0), "médico"),
        ("prova 20 de novembro às 14h", datetime(2026, 11, 20, 14, 0), "prova"),
        ("consulta 15/03 às 8h", datetime(2027, 3, 15, 8, 0), "consulta"),
        ("festa sexta meia-noite", datetime(2026, 9, 11, 0, 0), "festa"),
        ("ligar pro João daqui a 2 horas", datetime(2026, 9, 10, 12, 20), "ligar pro João"),
        ("almoço em 30 minutos", datetime(2026, 9, 10, 10, 50), "almoço"),
    ],
)
def test_casos_do_dia_a_dia(texto, esperado, titulo):
    resultado = quando(texto)
    assert resultado.quando == esperado.replace(tzinfo=SP)
    assert resultado.titulo == titulo


def test_horario_que_ja_passou_vai_para_amanha():
    assert quando("corrida às 7h").quando == datetime(2026, 9, 11, 7, 0, tzinfo=SP)


def test_dia_do_mes_que_ja_passou_vai_para_o_mes_seguinte():
    resultado = quando("pagar aluguel dia 10")
    assert resultado.quando == datetime(2026, 10, 10, 9, 0, tzinfo=SP)
    assert resultado.titulo == "pagar aluguel"


def test_dia_da_semana_de_hoje_com_hora_passada_vai_para_semana_que_vem():
    # Hoje é quinta 10:20; "quinta às 8h" só pode ser a próxima.
    assert quando("aula quinta às 8h").quando == datetime(2026, 9, 17, 8, 0, tzinfo=SP)


def test_sem_hora_e_para_hoje_usa_a_proxima_hora_cheia():
    assert quando("reunião hoje").quando == datetime(2026, 9, 10, 11, 0, tzinfo=SP)


def test_recorrencia_diaria():
    resultado = quando("academia todo dia às 7h")
    assert resultado.recorrencia == "diaria"
    assert resultado.quando == datetime(2026, 9, 11, 7, 0, tzinfo=SP)
    assert resultado.titulo == "academia"


def test_recorrencia_semanal_com_dia_da_semana():
    resultado = quando("terapia toda segunda às 9h")
    assert resultado.recorrencia == "semanal"
    assert resultado.quando == datetime(2026, 9, 14, 9, 0, tzinfo=SP)
    assert resultado.titulo == "terapia"


def test_recorrencia_mensal():
    assert quando("pagar cartão todo mês dia 12").recorrencia == "mensal"


def test_texto_sem_data():
    assert interpretar_quando("o wifi do escritório é casa123", AGORA) is None
    assert interpretar_quando("", AGORA) is None


def test_antecedencia():
    minutos, restante = interpretar_antecedencia("dentista amanhã 15h me avisa 2 horas antes")
    assert minutos == 120
    assert restante == "dentista amanhã 15h"
    assert interpretar_quando(restante, AGORA).titulo == "dentista"


def test_antecedencia_ausente():
    assert interpretar_antecedencia("dentista amanhã") == (None, "dentista amanhã")


def test_formatacao():
    assert formatar_data_hora(datetime(2026, 9, 10, 15, 0, tzinfo=SP), AGORA) == "hoje às 15:00"
    assert formatar_data_hora(datetime(2026, 9, 11, 9, 5, tzinfo=SP), AGORA) == "amanhã às 09:05"
    assert (
        formatar_data_hora(datetime(2026, 9, 14, 9, 0, tzinfo=SP), AGORA)
        == "segunda-feira, 14/09 às 09:00"
    )
    assert formatar_duracao(30) == "30 min"
    assert formatar_duracao(60) == "1 hora"
    assert formatar_duracao(1440) == "1 dia"
