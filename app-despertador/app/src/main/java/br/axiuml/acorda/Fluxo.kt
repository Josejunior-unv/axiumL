package br.axiuml.acorda

import android.content.Context
import br.axiuml.acorda.nucleo.Fase
import br.axiuml.acorda.nucleo.Regras
import kotlin.math.abs

/** O caminho do despertar: dispara → tarefa → confirmação → acordado (ou toca de novo). */
object Fluxo {
    /** O AlarmManager avisou que chegou a hora marcada de um alarme. */
    fun disparou(ctx: Context, id: Long, previsto: Long) {
        val ag = Armazem.agendamentos(ctx)[id]
        // Disparo velho (o alarme já foi reagendado para outra hora): ignora.
        if (ag == null || abs(ag.quandoWall - previsto) > 60_000) {
            Agenda.reagendarTudo(ctx)
            return
        }
        val alarme = Armazem.alarme(ctx, id)
        if (alarme == null || !alarme.ativo) {
            Agenda.reagendarTudo(ctx)
            return
        }
        if (!alarme.repete) Armazem.salvarAlarme(ctx, alarme.copy(ativo = false))
        Agenda.reagendarTudo(ctx, naoAntesDe = mapOf(id to previsto + 1_000))
        comecar(ctx, id, teste = false)
    }

    /** Toque fora de hora: teste, punição por desativar a proteção, retomada ou vigia. */
    fun tocarFora(ctx: Context, id: Long, teste: Boolean) {
        val atual = Armazem.sessao(ctx)
        if (Armazem.alarme(ctx, id) == null && atual?.alarmeId != id) return
        comecar(ctx, id, teste)
    }

    private fun comecar(ctx: Context, id: Long, teste: Boolean) {
        val atual = Armazem.sessao(ctx)
        val nova = Regras.aoDisparar(atual, id, Relogio.agora(), teste)
        if (nova == null) {
            // Já está tocando: só garante que o som continua.
            if (atual?.fase == Fase.TOCANDO) ToqueService.iniciar(ctx)
            return
        }
        if (atual?.fase == Fase.CONFIRMANDO) {
            Agenda.cancelarPrazo(ctx)
            Notificacoes.limparConfirmacao(ctx)
        }
        Armazem.salvarSessao(ctx, nova)
        ToqueService.iniciar(ctx)
    }

    /** Venceu o prazo da confirmação sem ela ser feita: volta a tocar. */
    fun prazoVenceu(ctx: Context, id: Long) {
        val nova = Regras.aoVencerPrazo(Armazem.sessao(ctx), id, Relogio.agora()) ?: return
        Notificacoes.limparConfirmacao(ctx)
        Armazem.salvarSessao(ctx, nova)
        ToqueService.iniciar(ctx)
    }

    /**
     * A tela avisa que a tarefa foi cumprida. Só vale se ainda for a mesma fase que a tela mostrava
     * (evita que um toque a mais, de uma tarefa repetida, pule a confirmação).
     */
    fun concluiu(ctx: Context, fase: Fase, inicio: Long) {
        val s = Armazem.sessao(ctx) ?: return
        if (s.fase != fase || s.inicio != inicio) return
        val alarme = Armazem.alarme(ctx, s.alarmeId)
        val proxima = Regras.aoConcluir(s, alarme, Relogio.agora())
        Armazem.salvarSessao(ctx, proxima)
        if (proxima == null) {
            Agenda.cancelarPrazo(ctx)
            Notificacoes.limparConfirmacao(ctx)
        } else {
            if (!proxima.teste) Agenda.marcarPrazo(ctx, proxima.alarmeId, proxima.prazo)
            Notificacoes.mostrarConfirmacao(ctx, proxima, alarme)
        }
        ToqueService.parar(ctx)
    }

    /**
     * Celular ligou (ou o app foi atualizado): o AlarmManager esquece tudo nessas horas, então
     * remarca. Se estava no meio de um despertar, continua. Se um alarme passou com o celular
     * desligado, toca agora.
     */
    fun retomar(ctx: Context, ligou: Boolean) {
        val agora = Relogio.agora()
        val s = Armazem.sessao(ctx)
        val perdido = if (ligou) Regras.perdido(Armazem.agendamentos(ctx).values, agora) else null
        when {
            s?.fase == Fase.TOCANDO -> Agenda.tocarJa(ctx, s.alarmeId, s.teste, 2_000)
            s?.fase == Fase.CONFIRMANDO && s.teste -> Armazem.salvarSessao(ctx, null)
            s?.fase == Fase.CONFIRMANDO -> {
                Agenda.marcarPrazo(ctx, s.alarmeId, maxOf(s.prazo, agora + 2_000))
                Notificacoes.mostrarConfirmacao(ctx, s, Armazem.alarme(ctx, s.alarmeId))
            }
            perdido != null -> {
                val a = Armazem.alarme(ctx, perdido.alarmeId)
                if (a != null && a.ativo) {
                    if (!a.repete) Armazem.salvarAlarme(ctx, a.copy(ativo = false))
                    Agenda.tocarJa(ctx, a.id, teste = false, atrasoMs = 2_000)
                }
            }
        }
        Agenda.reagendarTudo(ctx)
    }
}
