package br.axiuml.acorda.nucleo

/** O que a pessoa precisa fazer para o alarme parar. */
enum class TipoTarefa(val titulo: String, val explicacao: String) {
    CONTAS("Resolver contas", "Contas de cabeça. Errou, vem outra."),
    FRASE("Digitar frases", "Copiar frases inteiras, letra por letra."),
    SACUDIR("Sacudir o celular", "Sacudir com força até completar a conta."),
    PASSOS("Andar", "Levantar e andar pela casa com o celular na mão."),
    CODIGO("Escanear um código", "Ir até um código de barras ou QR que você cadastrou (no banheiro, na cozinha…)."),
}

enum class Dificuldade(val titulo: String) {
    FACIL("Fácil"),
    MEDIO("Média"),
    DIFICIL("Difícil"),
}

data class Tarefa(
    val tipo: TipoTarefa,
    val quantidade: Int,
    val dificuldade: Dificuldade = Dificuldade.MEDIO,
    /** Só para [TipoTarefa.CODIGO]: o conteúdo do código cadastrado. */
    val codigo: String? = null,
) {
    /** Uma tarefa de código sem código cadastrado não tem como ser cumprida. */
    val pronta: Boolean get() = tipo != TipoTarefa.CODIGO || !codigo.isNullOrBlank()

    fun descricao(): String = when (tipo) {
        TipoTarefa.CONTAS -> "Resolver $quantidade ${plural(quantidade, "conta", "contas")} " +
            "(${dificuldade.titulo.lowercase()})"
        TipoTarefa.FRASE -> "Digitar $quantidade ${plural(quantidade, "frase", "frases")}"
        TipoTarefa.SACUDIR -> "Sacudir o celular $quantidade vezes"
        TipoTarefa.PASSOS -> "Andar $quantidade passos"
        TipoTarefa.CODIGO -> "Escanear o código cadastrado"
    }

    companion object {
        fun limites(tipo: TipoTarefa): IntRange = when (tipo) {
            TipoTarefa.CONTAS -> 1..15
            TipoTarefa.FRASE -> 1..5
            TipoTarefa.SACUDIR -> 10..300
            TipoTarefa.PASSOS -> 10..500
            TipoTarefa.CODIGO -> 1..1
        }

        fun passo(tipo: TipoTarefa): Int = when (tipo) {
            TipoTarefa.SACUDIR, TipoTarefa.PASSOS -> 10
            else -> 1
        }

        fun padrao(tipo: TipoTarefa): Tarefa = when (tipo) {
            TipoTarefa.CONTAS -> Tarefa(tipo, 3, Dificuldade.MEDIO)
            TipoTarefa.FRASE -> Tarefa(tipo, 2)
            TipoTarefa.SACUDIR -> Tarefa(tipo, 40)
            TipoTarefa.PASSOS -> Tarefa(tipo, 40)
            TipoTarefa.CODIGO -> Tarefa(tipo, 1)
        }
    }
}

data class Alarme(
    val id: Long,
    val hora: Int,
    val minuto: Int,
    /** Dias da semana em que toca, no padrão ISO (1 = segunda … 7 = domingo). Vazio = toca uma vez só. */
    val dias: Set<Int> = emptySet(),
    val ativo: Boolean = true,
    val rotulo: String = "",
    /** O que precisa ser feito para o som parar. */
    val desligar: Tarefa = Tarefa.padrao(TipoTarefa.CONTAS),
    /** O que precisa ser feito, depois de desligar, para ele não tocar de novo. Nulo = não volta a tocar. */
    val confirmar: Tarefa? = Tarefa.padrao(TipoTarefa.PASSOS),
    /** Quantos minutos a pessoa tem para fazer a [confirmar] antes de o alarme voltar a tocar. */
    val prazoConfirmarMin: Int = 10,
    val vibrar: Boolean = true,
) {
    val horario: String get() = "%02d:%02d".format(hora, minuto)
    val repete: Boolean get() = dias.isNotEmpty()
}

enum class Fase {
    /** O som está tocando e só para com a tarefa de desligar. */
    TOCANDO,

    /** O som parou, mas volta no [Sessao.prazo] se a tarefa de confirmação não for feita. */
    CONFIRMANDO,
}

/** O despertar em andamento. Fica salvo para sobreviver a o app ser fechado ou o celular reiniciar. */
data class Sessao(
    val alarmeId: Long,
    val fase: Fase,
    /** Quando a fase atual começou (relógio de parede, ms). */
    val inicio: Long,
    /** Só em [Fase.CONFIRMANDO]: até quando a confirmação pode ser feita (relógio de parede, ms). */
    val prazo: Long = 0,
    /** Quantas vezes já tocou nesta manhã (sobe a cada confirmação perdida). */
    val rodada: Int = 1,
    /** Disparado pelo botão "Testar": não volta a tocar e não trava nada. */
    val teste: Boolean = false,
)

/**
 * Quando o próximo toque de um alarme foi marcado. Guarda o instante nos dois relógios do
 * Android: o de parede (que a pessoa pode mudar nas configurações) e o que conta desde que o
 * celular ligou (que ninguém mexe). Enquanto o celular não reinicia, é o segundo que vale.
 */
data class Agendamento(
    val alarmeId: Long,
    val quandoWall: Long,
    val quandoElapsed: Long,
    /** Número do boot em que foi marcado; se mudou, o celular reiniciou e o elapsed não vale mais. */
    val boot: Int,
)

data class Config(
    /** Quantos minutos antes de tocar o alarme fica travado. */
    val janelaMin: Int = 60,
    /** Falso = bipe do próprio app (não dá para trocar por um som mudo). */
    val somDoSistema: Boolean = false,
)

internal fun plural(n: Int, um: String, varios: String) = if (n == 1) um else varios
