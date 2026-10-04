package br.axiuml.acorda

import android.app.AlarmManager
import android.app.PendingIntent
import android.content.Context
import android.content.Intent
import android.os.Build
import br.axiuml.acorda.nucleo.Agendamento
import br.axiuml.acorda.nucleo.Calendario
import br.axiuml.acorda.nucleo.Regras
import java.time.ZoneId

/** Conversa com o AlarmManager: é ele que acorda o app no minuto certo, mesmo com o celular dormindo. */
object Agenda {
    const val ACAO_DISPARAR = "br.axiuml.acorda.DISPARAR"
    const val ACAO_EXTRA = "br.axiuml.acorda.EXTRA"
    const val ACAO_PRAZO = "br.axiuml.acorda.PRAZO"
    const val ACAO_VIGIA = "br.axiuml.acorda.VIGIA"
    const val EXTRA_ALARME = "alarme"
    const val EXTRA_PREVISTO = "previsto"
    const val EXTRA_TESTE = "teste"

    private const val CODIGO_PRAZO = 900_001
    private const val CODIGO_EXTRA = 900_002
    private const val CODIGO_VIGIA = 900_003
    private const val CODIGO_TELA = 900_004

    private const val FLAGS = PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE

    private fun am(ctx: Context): AlarmManager = ctx.getSystemService(AlarmManager::class.java)

    fun podeExato(ctx: Context): Boolean = Build.VERSION.SDK_INT < 31 || am(ctx).canScheduleExactAlarms()

    private fun intent(ctx: Context, acao: String, alarmeId: Long) =
        Intent(ctx, AlarmeReceiver::class.java).setAction(acao).putExtra(EXTRA_ALARME, alarmeId)

    private fun piDisparo(ctx: Context, alarmeId: Long, previsto: Long): PendingIntent =
        PendingIntent.getBroadcast(
            ctx,
            alarmeId.toInt(),
            intent(ctx, ACAO_DISPARAR, alarmeId).putExtra(EXTRA_PREVISTO, previsto),
            FLAGS,
        )

    private fun piPrazo(ctx: Context, alarmeId: Long): PendingIntent =
        PendingIntent.getBroadcast(ctx, CODIGO_PRAZO, intent(ctx, ACAO_PRAZO, alarmeId), FLAGS)

    private fun piExtra(ctx: Context, codigo: Int, alarmeId: Long, teste: Boolean): PendingIntent =
        PendingIntent.getBroadcast(ctx, codigo, intent(ctx, ACAO_EXTRA, alarmeId).putExtra(EXTRA_TESTE, teste), FLAGS)

    /**
     * Marca como "despertador" (setAlarmClock): é o tipo que o Android trata com mais prioridade —
     * ignora a economia de bateria e mostra o reloginho na barra de status.
     */
    private fun marcar(ctx: Context, quando: Long, pi: PendingIntent) {
        val am = am(ctx)
        val tela = PendingIntent.getActivity(ctx, CODIGO_TELA, Intent(ctx, MainActivity::class.java), FLAGS)
        try {
            if (podeExato(ctx)) {
                am.setAlarmClock(AlarmManager.AlarmClockInfo(quando, tela), pi)
            } else {
                am.setAndAllowWhileIdle(AlarmManager.RTC_WAKEUP, quando, pi)
            }
        } catch (e: SecurityException) {
            am.setAndAllowWhileIdle(AlarmManager.RTC_WAKEUP, quando, pi)
        }
    }

    /**
     * Recalcula e marca o próximo toque de todos os alarmes.
     *
     * Alarme travado (a menos da janela do toque) mantém o instante medido no relógio que não volta:
     * se alguém atrasar a hora do celular para escapar, ele toca no momento real assim mesmo.
     *
     * [naoAntesDe]: para o alarme que acabou de tocar, o próximo toque só pode vir depois disso.
     */
    fun reagendarTudo(ctx: Context, naoAntesDe: Map<Long, Long> = emptyMap()) {
        val agora = Relogio.agora()
        val el = Relogio.elapsed()
        val boot = Relogio.boot(ctx)
        val janela = Armazem.config(ctx).janelaMin * Regras.MINUTO
        val zona = ZoneId.systemDefault()
        val antigos = Armazem.agendamentos(ctx)
        val alarmes = Armazem.alarmes(ctx)
        val novos = mutableMapOf<Long, Agendamento>()

        // Alarmes apagados: desmarca.
        for (id in antigos.keys - alarmes.map { it.id }.toSet()) am(ctx).cancel(piDisparo(ctx, id, 0))

        for (a in alarmes) {
            if (!a.ativo) {
                am(ctx).cancel(piDisparo(ctx, a.id, 0))
                continue
            }
            val ant = antigos[a.id]
            val ancorado = ant != null && boot >= 0 && ant.boot == boot && a.id !in naoAntesDe
            val restante = if (ancorado) Regras.restante(ant, agora, el, boot) else null
            val quando = if (restante != null && restante <= janela) {
                agora + maxOf(restante, 1_000L)
            } else {
                val base = maxOf(agora, naoAntesDe[a.id] ?: 0L)
                Calendario.proximoMs(a, base, zona) ?: continue
            }
            novos[a.id] = Agendamento(a.id, quando, el + (quando - agora), boot)
            marcar(ctx, quando, piDisparo(ctx, a.id, quando))
        }
        Armazem.salvarAgendamentos(ctx, novos)
    }

    /** O alarme volta a tocar neste instante se a confirmação não for feita. */
    fun marcarPrazo(ctx: Context, alarmeId: Long, prazo: Long) = marcar(ctx, prazo, piPrazo(ctx, alarmeId))

    fun cancelarPrazo(ctx: Context) = am(ctx).cancel(piPrazo(ctx, 0))

    /**
     * Toca fora de hora (teste, punição, retomada depois de reiniciar). Passa pelo AlarmManager de
     * propósito: só um disparo de despertador dá ao app o direito de começar a tocar em segundo plano.
     */
    fun tocarJa(ctx: Context, alarmeId: Long, teste: Boolean, atrasoMs: Long = 1_000) =
        marcar(ctx, Relogio.agora() + atrasoMs, piExtra(ctx, CODIGO_EXTRA, alarmeId, teste))

    /**
     * Enquanto toca, mantém um disparo marcado logo à frente e vai empurrando. Se o sistema matar o
     * app no meio do toque, esse disparo chega e o som volta.
     */
    fun vigiar(ctx: Context, alarmeId: Long) =
        marcar(ctx, Relogio.agora() + 45_000, piVigia(ctx, alarmeId))

    fun pararVigia(ctx: Context) = am(ctx).cancel(piVigia(ctx, 0))

    private fun piVigia(ctx: Context, alarmeId: Long): PendingIntent =
        PendingIntent.getBroadcast(ctx, CODIGO_VIGIA, intent(ctx, ACAO_VIGIA, alarmeId), FLAGS)
}
