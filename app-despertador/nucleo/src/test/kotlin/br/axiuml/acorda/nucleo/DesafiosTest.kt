package br.axiuml.acorda.nucleo

import kotlin.math.PI
import kotlin.math.sin
import kotlin.random.Random
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertFalse
import kotlin.test.assertTrue

class DesafiosTest {
    @Test
    fun `contas tem a resposta certa`() {
        val rnd = Random(42)
        repeat(500) {
            for (d in Dificuldade.entries) {
                val c = Contas.gerar(d, rnd)
                assertEquals(avaliar(c.texto), c.resposta, c.texto)
            }
        }
    }

    /** Avalia "a + b", "(a × b) + c" e "(a × b) + (c × d)" de forma independente do gerador. */
    private fun avaliar(texto: String): Int = texto.split(" + ").sumOf { parte ->
        parte.trim('(', ')').split(" × ").map { it.trim().toInt() }.reduce { x, y -> x * y }
    }

    @Test
    fun `frase confere sem ligar para acento maiuscula e pontuacao`() {
        val alvo = "café quentinho banho gelado e cabeça acordada"
        assertTrue(Frases.confere("Cafe quentinho, banho gelado e CABECA acordada!", alvo))
        assertTrue(Frases.confere("  café   quentinho banho gelado e cabeça acordada ", alvo))
        assertFalse(Frases.confere("café quentinho banho gelado", alvo))
        assertEquals(5, Frases.acertosNoComeco("CAFÉ x", alvo)) // "cafe " bate, o "x" não
    }

    @Test
    fun `sorteio de frases nao repete`() {
        val f = Frases.sortear(Random(1), 5)
        assertEquals(5, f.toSet().size)
    }

    @Test
    fun `codigo precisa bater exatamente`() {
        assertTrue(Codigos.confere(" 7891000100103 ", "7891000100103"))
        assertFalse(Codigos.confere("7891000100104", "7891000100103"))
        assertFalse(Codigos.confere("qualquer", null))
        assertFalse(Codigos.confere(null, "x"))
    }

    @Test
    fun `celular parado nao conta sacudida nem passo`() {
        val s = DetectorSacudida()
        val p = DetectorPassos()
        var sac = 0
        var pas = 0
        for (t in 0L until 5_000L step 20) {
            if (s.amostra(0.1f, 0.2f, GRAVIDADE, t)) sac++
            if (p.amostra(0.1f, 0.2f, GRAVIDADE, t)) pas++
        }
        assertEquals(0, sac)
        assertEquals(0, pas)
    }

    @Test
    fun `sacudidas fortes sao contadas uma a uma`() {
        val s = DetectorSacudida()
        var n = 0
        // 10 picos de 3 g, um a cada 400 ms, cada pico durando 3 amostras.
        for (i in 0 until 10) {
            val base = i * 400L
            for (k in 0 until 3) if (s.amostra(3 * GRAVIDADE, 0f, 0f, base + k * 20)) n++
            for (k in 3 until 20) if (s.amostra(0f, 0f, GRAVIDADE, base + k * 20)) n++
        }
        assertEquals(10, n)
    }

    @Test
    fun `caminhada simulada conta perto do numero de passos`() {
        val p = DetectorPassos()
        var n = 0
        // 30 passos a ~1,8 passo/s: oscilação de ±3 m/s² somada à gravidade.
        val periodo = 550.0
        var t = 0L
        while (t < (30 * periodo).toLong()) {
            val z = GRAVIDADE + 3f * sin(2 * PI * t / periodo).toFloat()
            if (p.amostra(0.3f, 0.2f, z, t)) n++
            t += 20
        }
        assertTrue(n in 27..31, "contou $n passos")
    }
}
