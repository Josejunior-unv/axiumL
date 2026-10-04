package br.axiuml.acorda.nucleo

import java.text.Normalizer
import kotlin.math.sqrt
import kotlin.random.Random

data class Conta(val texto: String, val resposta: Int)

object Contas {
    fun gerar(dificuldade: Dificuldade, rnd: Random): Conta = when (dificuldade) {
        Dificuldade.FACIL -> {
            val a = rnd.nextInt(12, 50)
            val b = rnd.nextInt(12, 50)
            Conta("$a + $b", a + b)
        }
        Dificuldade.MEDIO -> {
            val a = rnd.nextInt(12, 30)
            val b = rnd.nextInt(3, 10)
            val c = rnd.nextInt(11, 100)
            Conta("($a × $b) + $c", a * b + c)
        }
        Dificuldade.DIFICIL -> {
            val a = rnd.nextInt(13, 40)
            val b = rnd.nextInt(4, 10)
            val c = rnd.nextInt(13, 40)
            val d = rnd.nextInt(4, 10)
            Conta("($a × $b) + ($c × $d)", a * b + c * d)
        }
    }
}

object Frases {
    val TODAS = listOf(
        "eu estou acordado e vou levantar da cama agora mesmo",
        "hoje eu escolho levantar na primeira vez que o alarme tocar",
        "cama boa e quentinha mas o meu dia começa agora",
        "lavar o rosto beber um copo de água e abrir a janela",
        "quem levanta cedo tem tempo de sobra para o que importa",
        "mais cinco minutinhos nunca foram só cinco minutinhos",
        "o sono de agora é a pressa de daqui a pouco",
        "estou de pé pronto para começar o dia com calma",
        "o travesseiro não vai fugir ele estará aqui de noite",
        "levantar agora é um favor que eu faço para mim mesmo",
        "abrir os olhos sentar na cama e colocar os pés no chão",
        "a disciplina de hoje é a liberdade de amanhã",
        "café quentinho banho gelado e cabeça acordada",
        "não vou voltar a dormir porque tenho coisas para fazer",
        "a melhor parte da manhã é a que eu não perco dormindo",
        "acordar no horário é a primeira vitória do dia",
    )

    fun sortear(rnd: Random, quantidade: Int): List<String> = TODAS.shuffled(rnd).take(quantidade.coerceIn(1, TODAS.size))

    /** Compara sem ligar para maiúsculas, acentos, pontuação e espaços sobrando. */
    fun confere(digitado: String, alvo: String): Boolean = normalizar(digitado) == normalizar(alvo)

    fun normalizar(s: String): String =
        Normalizer.normalize(s.lowercase(), Normalizer.Form.NFD)
            .replace(Regex("\\p{Mn}+"), "")
            .replace(Regex("[^a-z0-9 ]"), " ")
            .replace(Regex("\\s+"), " ")
            .trim()

    /** Quantos caracteres do começo já batem — para mostrar o progresso enquanto digita. */
    fun acertosNoComeco(digitado: String, alvo: String): Int {
        val d = normalizar(digitado)
        val a = normalizar(alvo)
        var i = 0
        while (i < d.length && i < a.length && d[i] == a[i]) i++
        return i
    }
}

object Codigos {
    fun confere(lido: String?, cadastrado: String?): Boolean =
        !lido.isNullOrBlank() && !cadastrado.isNullOrBlank() && lido.trim() == cadastrado.trim()
}

/** Conta sacudidas a partir do acelerômetro (valores em m/s², tempo em ms). */
class DetectorSacudida(private val limiarG: Float = 2.2f, private val intervaloMs: Long = 220) {
    private var ultimo = Long.MIN_VALUE / 2

    fun amostra(x: Float, y: Float, z: Float, tMs: Long): Boolean {
        val g = sqrt(x * x + y * y + z * z) / GRAVIDADE
        if (g >= limiarG && tMs - ultimo >= intervaloMs) {
            ultimo = tMs
            return true
        }
        return false
    }
}

/**
 * Conta passos pelo acelerômetro, para celulares sem sensor de passos (ou sem a permissão).
 * Um passo = a aceleração sobe acima da média e volta; com um intervalo mínimo entre eles.
 */
class DetectorPassos(
    private val limiarSubida: Float = 1.6f,
    private val limiarDescida: Float = 0.4f,
    private val intervaloMs: Long = 280,
) {
    private var media = GRAVIDADE
    private var acima = false
    private var ultimo = Long.MIN_VALUE / 2

    fun amostra(x: Float, y: Float, z: Float, tMs: Long): Boolean {
        val m = sqrt(x * x + y * y + z * z)
        media = media * 0.92f + m * 0.08f
        val dinamica = m - media
        if (!acima && dinamica >= limiarSubida && tMs - ultimo >= intervaloMs) {
            acima = true
            ultimo = tMs
            return true
        }
        if (acima && dinamica <= limiarDescida) acima = false
        return false
    }
}

const val GRAVIDADE = 9.80665f
