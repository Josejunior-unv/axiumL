package br.axiuml.acorda.nucleo

import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertFalse
import kotlin.test.assertNotNull
import kotlin.test.assertNull
import kotlin.test.assertTrue

class RegrasTest {
    private val min = Regras.MINUTO

    @Test
    fun `trava a partir de uma hora antes`() {
        assertFalse(Regras.travado(1, 61 * min, null, 60))
        assertTrue(Regras.travado(1, 60 * min, null, 60))
        assertTrue(Regras.travado(1, 5 * min, null, 60))
        // Já passou da hora e ainda não tocou: continua travado.
        assertTrue(Regras.travado(1, -2 * min, null, 60))
        // Sem agendamento (alarme desligado): livre.
        assertFalse(Regras.travado(1, null, null, 60))
    }

    @Test
    fun `fica travado durante o despertar inteiro`() {
        val tocando = Sessao(1, Fase.TOCANDO, 0)
        val confirmando = Sessao(1, Fase.CONFIRMANDO, 0, prazo = 10 * min)
        assertTrue(Regras.travado(1, 23 * 60 * min, tocando, 60))
        assertTrue(Regras.travado(1, 23 * 60 * min, confirmando, 60))
        // Outro alarme não fica travado por causa deste.
        assertFalse(Regras.travado(2, 23 * 60 * min, tocando, 60))
        // Teste não trava.
        assertFalse(Regras.travado(1, 23 * 60 * min, tocando.copy(teste = true), 60))
    }

    @Test
    fun `mudar a hora do celular nao engana a trava`() {
        // Agendado para daqui a 30 min, no boot 4.
        val ag = Agendamento(1, quandoWall = 1_000_000 + 30 * min, quandoElapsed = 500 + 30 * min, boot = 4)
        // A pessoa atrasa o relógio de parede em 3 horas; o elapsed segue andando normal.
        val wallAtrasado = 1_000_000 - 3 * 60 * min
        val restante = Regras.restante(ag, wallAtrasado, 500, 4)
        assertEquals(30 * min, restante)
        assertTrue(Regras.travado(1, restante, null, 60))
    }

    @Test
    fun `depois de reiniciar vale o relogio de parede`() {
        val ag = Agendamento(1, quandoWall = 1_000_000 + 30 * min, quandoElapsed = 99 * 60 * min, boot = 4)
        assertEquals(30 * min, Regras.restante(ag, 1_000_000, 10, 5))
    }

    @Test
    fun `desligar leva para a confirmacao e confirmar encerra`() {
        val alarme = Alarme(1, 6, 30, prazoConfirmarMin = 10)
        val s = Regras.aoDisparar(null, 1, 1000, teste = false)
        assertNotNull(s)
        assertEquals(Fase.TOCANDO, s.fase)

        val c = Regras.aoConcluir(s, alarme, 5000)
        assertNotNull(c)
        assertEquals(Fase.CONFIRMANDO, c.fase)
        assertEquals(5000 + 10 * min, c.prazo)

        assertNull(Regras.aoConcluir(c, alarme, 6000))
    }

    @Test
    fun `sem confirmacao desligar ja encerra`() {
        val alarme = Alarme(1, 6, 30, confirmar = null)
        val s = Sessao(1, Fase.TOCANDO, 0)
        assertNull(Regras.aoConcluir(s, alarme, 10))
    }

    @Test
    fun `confirmacao de codigo sem codigo cadastrado nao prende ninguem`() {
        val alarme = Alarme(1, 6, 30, confirmar = Tarefa(TipoTarefa.CODIGO, 1, codigo = null))
        assertNull(Regras.aoConcluir(Sessao(1, Fase.TOCANDO, 0), alarme, 10))
    }

    @Test
    fun `perder o prazo faz tocar de novo`() {
        val c = Sessao(1, Fase.CONFIRMANDO, 0, prazo = 10 * min)
        val de = Regras.aoVencerPrazo(c, 1, 10 * min)
        assertNotNull(de)
        assertEquals(Fase.TOCANDO, de.fase)
        assertEquals(2, de.rodada)
        // Já confirmou (sessão nula) ou é de outro alarme: nada acontece.
        assertNull(Regras.aoVencerPrazo(null, 1, 0))
        assertNull(Regras.aoVencerPrazo(c, 2, 0))
        // Teste não volta a tocar.
        assertNull(Regras.aoVencerPrazo(c.copy(teste = true), 1, 0))
    }

    @Test
    fun `disparo durante outro toque e ignorado`() {
        val tocando = Sessao(1, Fase.TOCANDO, 0)
        assertNull(Regras.aoDisparar(tocando, 2, 10, teste = false))
        // Mas um novo alarme assume no lugar de uma confirmação pendente.
        val confirmando = Sessao(1, Fase.CONFIRMANDO, 0, prazo = 99)
        assertEquals(2, Regras.aoDisparar(confirmando, 2, 10, teste = false)?.alarmeId)
        // Um teste não atropela a confirmação de verdade.
        assertNull(Regras.aoDisparar(confirmando, 2, 10, teste = true))
    }

    @Test
    fun `alarme perdido com o celular desligado toca ao ligar`() {
        val agora = 1_000 * min
        val ags = listOf(
            Agendamento(1, agora - 30 * min, 0, 1),
            Agendamento(2, agora - 10 * min, 0, 1),
            Agendamento(3, agora + 60 * min, 0, 1),
            Agendamento(4, agora - 5 * 60 * min, 0, 1),
        )
        assertEquals(2, Regras.perdido(ags, agora)?.alarmeId)
        assertNull(Regras.perdido(listOf(ags[2], ags[3]), agora))
    }
}
