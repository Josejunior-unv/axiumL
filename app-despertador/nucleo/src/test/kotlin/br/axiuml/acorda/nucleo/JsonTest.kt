package br.axiuml.acorda.nucleo

import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertNull

class JsonTest {
    @Test
    fun `alarmes vao e voltam iguais`() {
        val lista = listOf(
            Alarme(
                id = 7, hora = 5, minuto = 45, dias = setOf(1, 3, 5), rotulo = "Academia",
                desligar = Tarefa(TipoTarefa.CODIGO, 1, codigo = "7891000100103"),
                confirmar = Tarefa(TipoTarefa.FRASE, 3),
                prazoConfirmarMin = 15, vibrar = false,
            ),
            Alarme(id = 8, hora = 22, minuto = 0, ativo = false, confirmar = null),
        )
        assertEquals(lista, Json.alarmes(Json.alarmes(lista)))
    }

    @Test
    fun `sessao agendamentos e config vao e voltam`() {
        val s = Sessao(3, Fase.CONFIRMANDO, 100, prazo = 900, rodada = 2, teste = true)
        assertEquals(s, Json.sessao(Json.sessao(s)))
        assertNull(Json.sessao(Json.sessao(null as Sessao?)))

        val ags = mapOf(1L to Agendamento(1, 10, 20, 3), 2L to Agendamento(2, 30, 40, 3))
        assertEquals(ags, Json.agendamentos(Json.agendamentos(ags)))

        val c = Config(janelaMin = 90, somDoSistema = true)
        assertEquals(c, Json.config(Json.config(c)))
    }

    @Test
    fun `dados velhos ou faltando caem no padrao`() {
        val a = Json.alarmes("""[{"id":1,"hora":6,"minuto":30}]""").single()
        assertEquals(Alarme(1, 6, 30, confirmar = null), a)
        assertEquals(Config(), Json.config(null))
        assertEquals(emptyList(), Json.alarmes(""))
    }
}
