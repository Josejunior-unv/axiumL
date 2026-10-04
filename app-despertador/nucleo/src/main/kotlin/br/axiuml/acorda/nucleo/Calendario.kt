package br.axiuml.acorda.nucleo

import java.time.Instant
import java.time.LocalTime
import java.time.ZoneId
import java.time.ZonedDateTime

object Calendario {
    /** O próximo instante, estritamente depois de [aPartirDe], em que o alarme toca. */
    fun proximo(alarme: Alarme, aPartirDe: ZonedDateTime): ZonedDateTime? {
        if (!alarme.ativo) return null
        val hora = LocalTime.of(alarme.hora, alarme.minuto)
        for (i in 0L..7L) {
            val dia = aPartirDe.toLocalDate().plusDays(i)
            if (alarme.dias.isNotEmpty() && dia.dayOfWeek.value !in alarme.dias) continue
            val quando = ZonedDateTime.of(dia, hora, aPartirDe.zone)
            if (quando.isAfter(aPartirDe)) return quando
        }
        return null
    }

    fun proximoMs(alarme: Alarme, aPartirDeMs: Long, zona: ZoneId): Long? =
        proximo(alarme, Instant.ofEpochMilli(aPartirDeMs).atZone(zona))?.toInstant()?.toEpochMilli()

    /** "seg, qua, sex", "todo dia", "dias úteis"… */
    fun descreverDias(dias: Set<Int>): String = when {
        dias.isEmpty() -> "uma vez"
        dias.size == 7 -> "todo dia"
        dias == setOf(1, 2, 3, 4, 5) -> "dias úteis"
        dias == setOf(6, 7) -> "fim de semana"
        else -> dias.sorted().joinToString(", ") { NOMES_CURTOS[it - 1] }
    }

    val NOMES_CURTOS = listOf("seg", "ter", "qua", "qui", "sex", "sáb", "dom")
    val LETRAS = listOf("S", "T", "Q", "Q", "S", "S", "D")

    /** "em 7 h 05 min", "em 42 min", "em menos de 1 min". */
    fun descreverEspera(ms: Long): String {
        val totalMin = ms / 60_000
        if (totalMin < 1) return "em menos de 1 min"
        val dias = totalMin / (24 * 60)
        val horas = (totalMin / 60) % 24
        val min = totalMin % 60
        return when {
            dias > 0 -> "em $dias d ${horas} h"
            horas > 0 -> "em $horas h %02d min".format(min)
            else -> "em $min min"
        }
    }
}
