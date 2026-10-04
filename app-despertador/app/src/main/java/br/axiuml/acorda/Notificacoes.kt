package br.axiuml.acorda

import android.Manifest
import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.content.Context
import android.content.pm.PackageManager
import android.os.Build
import androidx.core.app.NotificationCompat
import br.axiuml.acorda.nucleo.Alarme
import br.axiuml.acorda.nucleo.Regras
import br.axiuml.acorda.nucleo.Sessao
import java.time.Instant
import java.time.ZoneId
import java.time.format.DateTimeFormatter

object Notificacoes {
    const val CANAL_TOCANDO = "tocando"
    const val CANAL_CONFIRMAR = "confirmar"
    const val ID_TOCANDO = 41
    const val ID_CONFIRMAR = 42

    private fun nm(ctx: Context) = ctx.getSystemService(NotificationManager::class.java)

    fun criarCanais(ctx: Context) {
        val nm = nm(ctx)
        nm.createNotificationChannel(
            NotificationChannel(CANAL_TOCANDO, "Alarme tocando", NotificationManager.IMPORTANCE_HIGH).apply {
                description = "Abre a tela da tarefa por cima de tudo. O som é tocado pelo próprio app."
                setSound(null, null)
                enableVibration(false)
                setBypassDnd(true)
                lockscreenVisibility = Notification.VISIBILITY_PUBLIC
            },
        )
        nm.createNotificationChannel(
            NotificationChannel(CANAL_CONFIRMAR, "Confirmação de que acordou", NotificationManager.IMPORTANCE_HIGH).apply {
                description = "Lembra a tarefa que falta para o alarme não tocar de novo."
                setSound(null, null)
                lockscreenVisibility = Notification.VISIBILITY_PUBLIC
            },
        )
    }

    private fun piTela(ctx: Context): PendingIntent = PendingIntent.getActivity(
        ctx,
        77,
        DespertarActivity.abrir(ctx),
        PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE,
    )

    fun tocando(ctx: Context, s: Sessao?, a: Alarme?): Notification {
        criarCanais(ctx)
        val tarefa = if (s != null && a != null) Regras.tarefaDaFase(s, a) else null
        val titulo = a?.rotulo?.ifBlank { null } ?: "Hora de acordar!"
        val texto = tarefa?.let { "Para desligar: ${it.descricao().replaceFirstChar { c -> c.lowercase() }}" }
            ?: "Toque para abrir"
        return NotificationCompat.Builder(ctx, CANAL_TOCANDO)
            .setSmallIcon(R.drawable.ic_notificacao)
            .setContentTitle(titulo)
            .setContentText(texto)
            .setCategory(NotificationCompat.CATEGORY_ALARM)
            .setPriority(NotificationCompat.PRIORITY_MAX)
            .setOngoing(true)
            .setAutoCancel(false)
            .setVisibility(NotificationCompat.VISIBILITY_PUBLIC)
            .setContentIntent(piTela(ctx))
            .setFullScreenIntent(piTela(ctx), true)
            .setForegroundServiceBehavior(NotificationCompat.FOREGROUND_SERVICE_IMMEDIATE)
            .build()
    }

    fun mostrarConfirmacao(ctx: Context, s: Sessao, a: Alarme?) {
        val tarefa = a?.confirmar ?: return
        if (!podeNotificar(ctx)) return
        criarCanais(ctx)
        val titulo = if (s.teste) "Teste: falta a confirmação" else "Confirme que acordou até ${hora(s.prazo)}"
        val texto = "${tarefa.descricao()}. Se não fizer, o alarme toca de novo."
        val n = NotificationCompat.Builder(ctx, CANAL_CONFIRMAR)
            .setSmallIcon(R.drawable.ic_notificacao)
            .setContentTitle(titulo)
            .setContentText(texto)
            .setStyle(NotificationCompat.BigTextStyle().bigText(texto))
            .setCategory(NotificationCompat.CATEGORY_REMINDER)
            .setPriority(NotificationCompat.PRIORITY_HIGH)
            .setOngoing(true)
            .setVisibility(NotificationCompat.VISIBILITY_PUBLIC)
            .setWhen(s.prazo)
            .setShowWhen(true)
            .setUsesChronometer(true)
            .setChronometerCountDown(true)
            .setContentIntent(piTela(ctx))
            .build()
        nm(ctx).notify(ID_CONFIRMAR, n)
    }

    fun limparConfirmacao(ctx: Context) = nm(ctx).cancel(ID_CONFIRMAR)

    fun podeNotificar(ctx: Context): Boolean =
        Build.VERSION.SDK_INT < 33 ||
            ctx.checkSelfPermission(Manifest.permission.POST_NOTIFICATIONS) == PackageManager.PERMISSION_GRANTED

    fun hora(ms: Long): String =
        DateTimeFormatter.ofPattern("HH:mm").format(Instant.ofEpochMilli(ms).atZone(ZoneId.systemDefault()))
}
