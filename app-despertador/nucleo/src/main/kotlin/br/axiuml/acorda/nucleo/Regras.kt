package br.axiuml.acorda.nucleo

/** As regras do despertar, sem nada de Android, para poderem ser testadas sozinhas. */
object Regras {
    const val MINUTO = 60_000L

    /** Se o celular estava desligado na hora do alarme, ele toca ao ligar — desde que não tenha passado disso. */
    const val TOLERANCIA_PERDIDO_MIN = 180

    /**
     * Quanto falta, de verdade, para o alarme tocar. Se foi agendado neste mesmo boot, mede pelo
     * relógio que conta desde que o celular ligou — adiantar ou atrasar a hora nas configurações
     * não muda esse relógio, então não engana a trava.
     */
    fun restante(ag: Agendamento?, agoraWall: Long, agoraElapsed: Long, boot: Int): Long? {
        if (ag == null) return null
        return if (boot >= 0 && ag.boot == boot) ag.quandoElapsed - agoraElapsed else ag.quandoWall - agoraWall
    }

    /**
     * Travado = não dá para desligar, editar nem apagar. Acontece quando falta menos que a janela
     * (ou o horário já passou e ainda não tocou), e durante todo o despertar até a confirmação.
     */
    fun travado(alarmeId: Long, restante: Long?, sessao: Sessao?, janelaMin: Int): Boolean {
        if (sessao != null && !sessao.teste && sessao.alarmeId == alarmeId) return true
        return restante != null && restante <= janelaMin * MINUTO
    }

    /** A sessão que começa quando um alarme dispara, ou nulo se o disparo deve ser ignorado. */
    fun aoDisparar(atual: Sessao?, alarmeId: Long, agora: Long, teste: Boolean): Sessao? = when {
        atual == null -> Sessao(alarmeId, Fase.TOCANDO, agora, teste = teste)
        // Já está tocando: o outro alarme não interrompe a tarefa em andamento.
        atual.fase == Fase.TOCANDO -> null
        // Um teste nunca apaga a confirmação pendente de um despertar de verdade.
        teste && !atual.teste -> null
        else -> Sessao(alarmeId, Fase.TOCANDO, agora, teste = teste)
    }

    /** O que vem depois de cumprir a tarefa da fase atual. Nulo = acabou, a pessoa está acordada. */
    fun aoConcluir(s: Sessao, alarme: Alarme?, agora: Long): Sessao? = when (s.fase) {
        Fase.TOCANDO -> {
            val c = alarme?.confirmar
            if (alarme != null && c != null && c.pronta) {
                s.copy(fase = Fase.CONFIRMANDO, inicio = agora, prazo = agora + alarme.prazoConfirmarMin * MINUTO)
            } else {
                null
            }
        }
        Fase.CONFIRMANDO -> null
    }

    /** Venceu o prazo da confirmação: volta a tocar. Nulo = não havia o que fazer. */
    fun aoVencerPrazo(s: Sessao?, alarmeId: Long, agora: Long): Sessao? =
        if (s != null && !s.teste && s.fase == Fase.CONFIRMANDO && s.alarmeId == alarmeId) {
            s.copy(fase = Fase.TOCANDO, inicio = agora, prazo = 0, rodada = s.rodada + 1)
        } else {
            null
        }

    /** A tarefa que vale na fase atual. */
    fun tarefaDaFase(s: Sessao, alarme: Alarme): Tarefa = when (s.fase) {
        Fase.TOCANDO -> alarme.desligar
        Fase.CONFIRMANDO -> alarme.confirmar ?: alarme.desligar
    }

    /**
     * Depois de o celular reiniciar: o alarme que deveria ter tocado enquanto ele estava desligado
     * (o mais recente, dentro da tolerância). Desligar o celular não serve para fugir.
     */
    fun perdido(agendamentos: Collection<Agendamento>, agoraWall: Long): Agendamento? =
        agendamentos
            .filter { it.quandoWall <= agoraWall && agoraWall - it.quandoWall <= TOLERANCIA_PERDIDO_MIN * MINUTO }
            .maxByOrNull { it.quandoWall }

    /** Tarefa alternativa para quando a câmera ou o sensor não funcionam: dá trabalho de propósito. */
    val ALTERNATIVA = Tarefa(TipoTarefa.CONTAS, 8, Dificuldade.DIFICIL)

    /** Quanto tempo depois de abrir a tarefa a alternativa aparece. */
    const val ESPERA_ALTERNATIVA_MS = 3 * MINUTO
}
