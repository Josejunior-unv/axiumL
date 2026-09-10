"""Interpretação e formatação de datas/horas escritas em português.

O objetivo é entender coisas que uma pessoa escreveria no Telegram sem pensar:
"dentista amanhã às 15h", "reunião sexta 9:30", "academia todo dia às 7h",
"pagar aluguel dia 10", "ligar pro João daqui a 2 horas".

A função principal é :func:`interpretar_quando`, que devolve a data/hora e o
texto que sobrou (usado como título do compromisso).
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta

# Hora usada quando a pessoa diz só o dia ("reunião na sexta").
HORA_PADRAO = (9, 0)

# Horas usadas para períodos do dia.
PERIODOS = {
    "manha": (9, 0),
    "tarde": (14, 0),
    "noite": (20, 0),
    "madrugada": (3, 0),
}

MESES = {
    "janeiro": 1, "fevereiro": 2, "marco": 3, "abril": 4, "maio": 5,
    "junho": 6, "julho": 7, "agosto": 8, "setembro": 9, "outubro": 10,
    "novembro": 11, "dezembro": 12,
    "jan": 1, "fev": 2, "mar": 3, "abr": 4, "mai": 5, "jun": 6,
    "jul": 7, "ago": 8, "set": 9, "out": 10, "nov": 11, "dez": 12,
}

DIAS_SEMANA = {
    "segunda": 0, "terca": 1, "quarta": 2, "quinta": 3,
    "sexta": 4, "sabado": 5, "domingo": 6,
}

NOMES_DIAS = [
    "segunda-feira", "terça-feira", "quarta-feira", "quinta-feira",
    "sexta-feira", "sábado", "domingo",
]

NUMEROS_ESCRITOS = {
    "um": 1, "uma": 1, "dois": 2, "duas": 2, "tres": 3, "quatro": 4,
    "cinco": 5, "seis": 6, "sete": 7, "oito": 8, "nove": 9, "dez": 10,
    "meia": 0.5, "meio": 0.5,
}

# Palavras que sobram no começo/fim do título depois de tirar a data.
RUIDO = {
    "a", "as", "à", "às", "ao", "aos", "o", "os", "e", "de", "da", "do", "das",
    "dos", "em", "no", "na", "nos", "nas", "para", "pra", "pro", "por", "que",
    "dia", "hora", "horas", "tenho", "tem", "marcar", "marca", "marque",
    "agendar", "agenda", "agende", "anotar", "anota", "lembrar", "lembre",
    "lembra", "avisa", "avise", "avisar", "aviso", "me", "meu", "minha", "um", "uma", "vou", "ir", "sera", "será",
}

_UNIDADES_MINUTOS = {
    "min": 1, "mins": 1, "minuto": 1, "minutos": 1,
    "h": 60, "hs": 60, "hora": 60, "horas": 60,
    "dia": 1440, "dias": 1440,
    "semana": 10080, "semanas": 10080,
}


def sem_acentos(texto: str) -> str:
    """Remove acentos preservando o tamanho da string (índices continuam válidos)."""
    return "".join(unicodedata.normalize("NFD", ch)[0] for ch in texto)


def normalizar(texto: str) -> str:
    """Versão minúscula e sem acentos, com os mesmos índices do texto original."""
    return sem_acentos(texto).lower()


@dataclass
class Interpretacao:
    """Resultado de :func:`interpretar_quando`."""

    quando: datetime
    titulo: str
    hora_explicita: bool = False
    recorrencia: str | None = None
    trechos: list[tuple[int, int]] = field(default_factory=list)


def _procurar(padrao: str, texto: str, consumidos: list[tuple[int, int]]) -> re.Match | None:
    """Primeira ocorrência de ``padrao`` que não colide com trechos já usados."""
    for m in re.finditer(padrao, texto):
        if not any(m.start() < fim and ini < m.end() for ini, fim in consumidos):
            return m
    return None


def _consumir(consumidos: list[tuple[int, int]], m: re.Match) -> None:
    consumidos.append((m.start(), m.end()))


def _quantidade(bruto: str) -> float:
    bruto = bruto.strip()
    if bruto.isdigit():
        return int(bruto)
    return NUMEROS_ESCRITOS.get(bruto, 1)


def _proximo_dia_semana(base: date, alvo: int, forcar_proxima: bool) -> date:
    delta = (alvo - base.weekday()) % 7
    if delta == 0 and forcar_proxima:
        delta = 7
    return base + timedelta(days=delta)


def _limpar_titulo(original: str, consumidos: list[tuple[int, int]]) -> str:
    restante = list(original)
    for ini, fim in consumidos:
        for i in range(ini, min(fim, len(restante))):
            restante[i] = " "
    texto = re.sub(r"\s+", " ", "".join(restante)).strip(" ,.;:-–—")
    palavras = texto.split()
    while palavras and normalizar(palavras[0]).strip(",.;:") in RUIDO:
        palavras.pop(0)
    while palavras and normalizar(palavras[-1]).strip(",.;:") in RUIDO:
        palavras.pop()
    return " ".join(palavras).strip(" ,.;:-–—")


def _detectar_recorrencia(
    norm: str, consumidos: list[tuple[int, int]]
) -> tuple[str | None, int | None]:
    """Devolve (recorrência, dia_da_semana) quando o texto indica repetição."""
    m = _procurar(r"\b(?:todo|toda|todos|todas)\s+(?:os\s+|as\s+)?dias?\b|\bdiariamente\b", norm, consumidos)
    if m:
        _consumir(consumidos, m)
        return "diaria", None

    m = _procurar(
        r"\b(?:todo|toda|todos|todas)\s+(?:as\s+|os\s+)?"
        r"(segunda|terca|quarta|quinta|sexta|sabado|domingo)s?(?:[-\s]*feiras?)?\b",
        norm,
        consumidos,
    )
    if m:
        _consumir(consumidos, m)
        return "semanal", DIAS_SEMANA[m.group(1)]

    m = _procurar(r"\b(?:toda\s+semana|semanalmente)\b", norm, consumidos)
    if m:
        _consumir(consumidos, m)
        return "semanal", None

    m = _procurar(r"\b(?:todo\s+mes|mensalmente|todo\s+mês)\b", norm, consumidos)
    if m:
        _consumir(consumidos, m)
        return "mensal", None

    return None, None


def _detectar_hora(
    norm: str, consumidos: list[tuple[int, int]]
) -> tuple[tuple[int, int] | None, bool]:
    """Devolve ((hora, minuto), explícita)."""
    m = _procurar(r"\bmeio[-\s]?dia\b", norm, consumidos)
    if m:
        _consumir(consumidos, m)
        return (12, 0), True

    m = _procurar(r"\bmeia[-\s]?noite\b", norm, consumidos)
    if m:
        _consumir(consumidos, m)
        return (0, 0), True

    padroes = [
        r"\b(?:as|ate as)\s*(\d{1,2})\s*[:h.]\s*(\d{2})\b",   # às 15:30 / às 15h30
        r"\b(\d{1,2})\s*[:h]\s*(\d{2})\b",                     # 15:30 / 15h30
        r"\b(?:as)\s*(\d{1,2})\s*(?:h|hs|horas?)?\b",          # às 15 / às 15h
        r"\b(\d{1,2})\s*(?:h|hs|horas)\b",                     # 15h / 15 horas
    ]
    for padrao in padroes:
        m = _procurar(padrao, norm, consumidos)
        if not m:
            continue
        hora = int(m.group(1))
        minuto = int(m.group(2)) if m.lastindex and m.lastindex >= 2 and m.group(2) else 0
        if hora > 23 or minuto > 59:
            continue
        _consumir(consumidos, m)
        # "às 8" com "da noite" logo depois vira 20h.
        if hora < 12 and _procurar(r"\b(?:da|de|a)\s*(?:noite|tarde)\b", norm, consumidos):
            sufixo = _procurar(r"\b(?:da|de|a)\s*(noite|tarde)\b", norm, consumidos)
            if sufixo:
                _consumir(consumidos, sufixo)
                hora += 12 if hora != 12 else 0
        return (hora, minuto), True

    m = _procurar(
        r"\b(?:de|da|pela|pela|na|a|à)\s+(manha|tarde|noite|madrugada)\b", norm, consumidos
    )
    if m:
        _consumir(consumidos, m)
        return PERIODOS[m.group(1)], False

    return None, False


def _detectar_data(
    norm: str, consumidos: list[tuple[int, int]], hoje: date
) -> tuple[date | None, str]:
    """Devolve (data, tipo) — tipo em: hoje, relativa, semana, dia_mes, data, "".""" 
    m = _procurar(r"\bdepois\s+de\s+amanha\b", norm, consumidos)
    if m:
        _consumir(consumidos, m)
        return hoje + timedelta(days=2), "relativa"

    m = _procurar(r"\bamanha\b", norm, consumidos)
    if m:
        _consumir(consumidos, m)
        return hoje + timedelta(days=1), "relativa"

    m = _procurar(r"\bhoje\b", norm, consumidos)
    if m:
        _consumir(consumidos, m)
        return hoje, "hoje"

    m = _procurar(
        r"\b(?:na|no|nesta|neste|nessa|nesse|proxima|proximo)?\s*"
        r"(segunda|terca|quarta|quinta|sexta|sabado|domingo)(?:[-\s]*feira)?"
        r"(\s+que\s+vem|\s+proxima|\s+proximo)?\b",
        norm,
        consumidos,
    )
    if m:
        _consumir(consumidos, m)
        forcar = bool(m.group(2)) or "proxim" in m.group(0)
        return _proximo_dia_semana(hoje, DIAS_SEMANA[m.group(1)], forcar), "semana"

    m = _procurar(r"\b(\d{1,2})/(\d{1,2})(?:/(\d{2,4}))?\b", norm, consumidos)
    if m:
        dia, mes = int(m.group(1)), int(m.group(2))
        ano = int(m.group(3)) if m.group(3) else hoje.year
        if ano < 100:
            ano += 2000
        try:
            data = date(ano, mes, dia)
        except ValueError:
            return None, ""
        _consumir(consumidos, m)
        if not m.group(3) and data < hoje:
            try:
                data = data.replace(year=ano + 1)
            except ValueError:  # 29/02
                data = data + timedelta(days=365)
        return data, "data"

    m = _procurar(
        r"\b(?:dia\s+)?(\d{1,2})\s+de\s+(janeiro|fevereiro|marco|abril|maio|junho|julho|"
        r"agosto|setembro|outubro|novembro|dezembro|jan|fev|mar|abr|mai|jun|jul|ago|set|out|nov|dez)"
        r"(?:\s+de\s+(\d{4}))?\b",
        norm,
        consumidos,
    )
    if m:
        dia, mes = int(m.group(1)), MESES[m.group(2)]
        ano = int(m.group(3)) if m.group(3) else hoje.year
        try:
            data = date(ano, mes, dia)
        except ValueError:
            return None, ""
        _consumir(consumidos, m)
        if not m.group(3) and data < hoje:
            data = data.replace(year=ano + 1)
        return data, "data"

    m = _procurar(r"\bdia\s+(\d{1,2})\b(?!\s*[/:h])", norm, consumidos)
    if m:
        dia = int(m.group(1))
        if 1 <= dia <= 31:
            _consumir(consumidos, m)
            data = _dia_do_mes(hoje, dia)
            return data, "dia_mes"

    return None, ""


def _dia_do_mes(hoje: date, dia: int) -> date:
    """Dia deste mês; se já passou, o mesmo dia do mês seguinte."""
    try:
        data = hoje.replace(day=dia)
    except ValueError:
        data = _ultimo_dia(hoje.year, hoje.month, dia)
    if data < hoje:
        ano = hoje.year + (1 if hoje.month == 12 else 0)
        mes = 1 if hoje.month == 12 else hoje.month + 1
        data = _ultimo_dia(ano, mes, dia)
    return data


def _ultimo_dia(ano: int, mes: int, dia: int) -> date:
    while dia > 28:
        try:
            return date(ano, mes, dia)
        except ValueError:
            dia -= 1
    return date(ano, mes, dia)


def interpretar_quando(texto: str, agora: datetime) -> Interpretacao | None:
    """Extrai data/hora de um texto em português.

    ``agora`` deve ser um ``datetime`` com fuso (o fuso da pessoa). O resultado
    volta no mesmo fuso. Devolve ``None`` quando não há nada parecido com uma
    data no texto.
    """
    if not texto or not texto.strip():
        return None

    norm = normalizar(texto)
    consumidos: list[tuple[int, int]] = []

    recorrencia, dia_semana_recorrente = _detectar_recorrencia(norm, consumidos)

    # "daqui a 20 minutos", "em 2 horas", "dentro de 3 dias"
    relativo = _procurar(
        r"\b(?:daqui\s+a|dentro\s+de|em)\s+(\d{1,3}|um|uma|dois|duas|tres|meia|meio)\s*"
        r"(min|mins|minutos?|h|hs|horas?|dias?|semanas?)\b",
        norm,
        consumidos,
    )
    if relativo and not recorrencia:
        _consumir(consumidos, relativo)
        minutos = _quantidade(relativo.group(1)) * _UNIDADES_MINUTOS[relativo.group(2)]
        quando = (agora + timedelta(minutes=round(minutos))).replace(second=0, microsecond=0)
        return Interpretacao(
            quando=quando,
            titulo=_limpar_titulo(texto, consumidos),
            hora_explicita=True,
            trechos=consumidos,
        )

    hora, hora_explicita = _detectar_hora(norm, consumidos)
    data, tipo_data = _detectar_data(norm, consumidos, agora.date())

    if data is None and hora is None and recorrencia is None:
        return None

    if data is None:
        if recorrencia == "semanal" and dia_semana_recorrente is not None:
            data = _proximo_dia_semana(agora.date(), dia_semana_recorrente, False)
            tipo_data = "semana"
        else:
            data = agora.date()

    if hora is None and data == agora.date() and tipo_data in ("", "hoje"):
        # "reunião hoje", já passou das 9h: joga para a próxima hora cheia.
        hora_cheia = (agora + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
        padrao = agora.replace(
            hour=HORA_PADRAO[0], minute=HORA_PADRAO[1], second=0, microsecond=0
        )
        quando = max(hora_cheia, padrao)
    else:
        h, m = hora if hora else HORA_PADRAO
        quando = agora.replace(
            year=data.year, month=data.month, day=data.day,
            hour=h, minute=m, second=0, microsecond=0,
        )

    if quando <= agora:
        if tipo_data == "":            # só o horário: fica para amanhã
            quando += timedelta(days=1)
        elif tipo_data == "semana":    # "na sexta" com a sexta já passada
            quando += timedelta(days=7)
        elif tipo_data == "dia_mes":   # "dia 10" com o dia 10 já passado
            ano = data.year + (1 if data.month == 12 else 0)
            mes = 1 if data.month == 12 else data.month + 1
            proxima = _ultimo_dia(ano, mes, data.day)
            quando = quando.replace(year=proxima.year, month=proxima.month, day=proxima.day)

    return Interpretacao(
        quando=quando,
        titulo=_limpar_titulo(texto, consumidos),
        hora_explicita=hora_explicita,
        recorrencia=recorrencia,
        trechos=consumidos,
    )


def interpretar_antecedencia(texto: str) -> tuple[int | None, str]:
    """Lê "me avisa 1h antes" e devolve (minutos, texto sem esse trecho)."""
    norm = normalizar(texto)
    m = re.search(
        r"\b(\d{1,3}|um|uma|dois|duas|tres|meia|meio)\s*"
        r"(min|mins|minutos?|h|hs|horas?|dias?)\s+antes\b",
        norm,
    )
    if not m:
        return None, texto
    minutos = _quantidade(m.group(1)) * _UNIDADES_MINUTOS[m.group(2)]
    return round(minutos), _limpar_titulo(texto, [(m.start(), m.end())])


def formatar_data_hora(quando: datetime, agora: datetime | None = None) -> str:
    """"amanhã às 15:00", "sexta-feira, 12/09 às 09:30"."""
    hora = quando.strftime("%H:%M")
    if agora is not None:
        dias = (quando.date() - agora.date()).days
        if dias == 0:
            return f"hoje às {hora}"
        if dias == 1:
            return f"amanhã às {hora}"
        if dias == -1:
            return f"ontem às {hora}"
        if 2 <= dias <= 6:
            return f"{NOMES_DIAS[quando.weekday()]}, {quando.strftime('%d/%m')} às {hora}"
    return f"{NOMES_DIAS[quando.weekday()]}, {quando.strftime('%d/%m/%Y')} às {hora}"


def formatar_duracao(minutos: int) -> str:
    if minutos % 1440 == 0 and minutos >= 1440:
        dias = minutos // 1440
        return f"{dias} dia" + ("s" if dias > 1 else "")
    if minutos % 60 == 0 and minutos >= 60:
        horas = minutos // 60
        return f"{horas} hora" + ("s" if horas > 1 else "")
    return f"{minutos} min"
