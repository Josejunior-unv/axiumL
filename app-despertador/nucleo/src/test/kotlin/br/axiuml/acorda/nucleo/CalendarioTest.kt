package br.axiuml.acorda.nucleo

import java.time.ZoneId
import java.time.ZonedDateTime
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertNull

class CalendarioTest {
    private val sp = ZoneId.of("America/Sao_Paulo")

    // 2026-10-05 é uma segunda-feira.
    private fun em(dia: Int, hora: Int, minuto: Int, segundo: Int = 0) =
        ZonedDateTime.of(2026, 10, dia, hora, minuto, segundo, 0, sp)

    @Test
    fun `alarme de uma vez toca hoje se ainda nao passou`() {
        val a = Alarme(1, 6, 30)
        assertEquals(em(5, 6, 30), Calendario.proximo(a, em(5, 5, 0)))
    }

    @Test
    fun `alarme de uma vez vai para amanha se ja passou`() {
        val a = Alarme(1, 6, 30)
        assertEquals(em(6, 6, 30), Calendario.proximo(a, em(5, 7, 0)))
    }

    @Test
    fun `no exato minuto do alarme o proximo e o do dia seguinte`() {
        val a = Alarme(1, 6, 30)
        assertEquals(em(6, 6, 30), Calendario.proximo(a, em(5, 6, 30)))
    }

    @Test
    fun `dias uteis pulam o fim de semana`() {
        val a = Alarme(1, 6, 30, dias = setOf(1, 2, 3, 4, 5))
        // Sexta 9/10 às 7h: o próximo é segunda 12/10.
        assertEquals(em(12, 6, 30), Calendario.proximo(a, em(9, 7, 0)))
    }

    @Test
    fun `alarme so de domingo`() {
        val a = Alarme(1, 9, 0, dias = setOf(7))
        assertEquals(em(11, 9, 0), Calendario.proximo(a, em(5, 10, 0)))
    }

    @Test
    fun `mesmo dia da semana que ja passou vai para a semana seguinte`() {
        val a = Alarme(1, 6, 0, dias = setOf(1))
        assertEquals(em(12, 6, 0), Calendario.proximo(a, em(5, 6, 0, 1)))
    }

    @Test
    fun `alarme desligado nao tem proximo`() {
        assertNull(Calendario.proximo(Alarme(1, 6, 30, ativo = false), em(5, 5, 0)))
    }

    @Test
    fun `descricoes`() {
        assertEquals("dias úteis", Calendario.descreverDias(setOf(1, 2, 3, 4, 5)))
        assertEquals("todo dia", Calendario.descreverDias((1..7).toSet()))
        assertEquals("seg, qua, sex", Calendario.descreverDias(setOf(5, 1, 3)))
        assertEquals("em 42 min", Calendario.descreverEspera(42 * 60_000L + 30_000))
        assertEquals("em 7 h 05 min", Calendario.descreverEspera((7 * 60 + 5) * 60_000L))
        assertEquals("em menos de 1 min", Calendario.descreverEspera(20_000))
    }
}
