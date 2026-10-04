package br.axiuml.acorda

import android.app.Notification
import android.app.Service
import android.content.Context
import android.content.Intent
import android.content.pm.ServiceInfo
import android.media.AudioAttributes
import android.media.AudioFocusRequest
import android.media.AudioManager
import android.media.MediaPlayer
import android.media.RingtoneManager
import android.os.Build
import android.os.Handler
import android.os.IBinder
import android.os.Looper
import android.os.PowerManager
import android.os.VibrationAttributes
import android.os.VibrationEffect
import android.os.Vibrator
import android.os.VibratorManager
import android.provider.Settings
import androidx.core.content.ContextCompat
import br.axiuml.acorda.nucleo.Alarme
import br.axiuml.acorda.nucleo.Fase

/**
 * Toca. Sem parar, no volume máximo, até a tarefa ser feita. Abaixar o volume não adianta (ele
 * volta), sair da tela não adianta (ela volta), e se o sistema matar o app o vigia faz tocar de novo.
 */
class ToqueService : Service() {
    companion object {
        @Volatile
        var tocando = false
            private set

        fun iniciar(ctx: Context) {
            runCatching { ContextCompat.startForegroundService(ctx, Intent(ctx, ToqueService::class.java)) }
        }

        fun parar(ctx: Context) {
            ctx.stopService(Intent(ctx, ToqueService::class.java))
        }
    }

    private val atributos: AudioAttributes = AudioAttributes.Builder()
        .setUsage(AudioAttributes.USAGE_ALARM)
        .setContentType(AudioAttributes.CONTENT_TYPE_SONIFICATION)
        .build()

    private val handler = Handler(Looper.getMainLooper())
    private var player: MediaPlayer? = null
    private var vibrador: Vibrator? = null
    private var wakeLock: PowerManager.WakeLock? = null
    private var foco: AudioFocusRequest? = null
    private var volumeOriginal = -1
    private var voltasDoVigia = 0

    private val vigia = object : Runnable {
        override fun run() {
            val s = Armazem.sessao(this@ToqueService)
            if (s == null || s.fase != Fase.TOCANDO) {
                stopSelf()
                return
            }
            forcarVolume()
            val p = player
            if (p == null || !runCatching { p.isPlaying }.getOrDefault(false)) {
                runCatching { p?.release() }
                player = null
                tocarSom()
            }
            abrirTela()
            if (voltasDoVigia++ % 10 == 0) Agenda.vigiar(this@ToqueService, s.alarmeId)
            handler.postDelayed(this, 2_000)
        }
    }

    override fun onBind(intent: Intent?): IBinder? = null

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        val s = Armazem.sessao(this)
        val alarme = s?.let { Armazem.alarme(this, it.alarmeId) }
        if (!primeiroPlano(Notificacoes.tocando(this, s, alarme))) {
            // Sem direito a tocar daqui (ex.: reiniciado pelo sistema): pede ao AlarmManager, que tem.
            if (s != null && s.fase == Fase.TOCANDO) Agenda.tocarJa(this, s.alarmeId, s.teste, 3_000)
            stopSelf()
            return START_NOT_STICKY
        }
        if (s == null || s.fase != Fase.TOCANDO) {
            stopSelf()
            return START_NOT_STICKY
        }
        if (!tocando) comecar(alarme)
        abrirTela()
        return START_STICKY
    }

    private fun primeiroPlano(n: Notification): Boolean = try {
        when {
            Build.VERSION.SDK_INT >= 34 -> try {
                startForeground(Notificacoes.ID_TOCANDO, n, ServiceInfo.FOREGROUND_SERVICE_TYPE_SYSTEM_EXEMPTED)
            } catch (e: Exception) {
                startForeground(Notificacoes.ID_TOCANDO, n, ServiceInfo.FOREGROUND_SERVICE_TYPE_MEDIA_PLAYBACK)
            }
            Build.VERSION.SDK_INT >= 29 ->
                startForeground(Notificacoes.ID_TOCANDO, n, ServiceInfo.FOREGROUND_SERVICE_TYPE_MEDIA_PLAYBACK)
            else -> startForeground(Notificacoes.ID_TOCANDO, n)
        }
        true
    } catch (e: Exception) {
        false
    }

    private fun comecar(alarme: Alarme?) {
        tocando = true
        wakeLock = getSystemService(PowerManager::class.java)
            .newWakeLock(PowerManager.PARTIAL_WAKE_LOCK, "acorda:toque")
            .apply { acquire(2 * 60 * 60_000L) }
        val am = getSystemService(AudioManager::class.java)
        foco = AudioFocusRequest.Builder(AudioManager.AUDIOFOCUS_GAIN_TRANSIENT)
            .setAudioAttributes(atributos)
            .build()
            .also { runCatching { am.requestAudioFocus(it) } }
        forcarVolume()
        tocarSom()
        if (alarme?.vibrar != false) vibrar()
        handler.removeCallbacks(vigia)
        handler.post(vigia)
    }

    /** Alarme no máximo. Se a pessoa abaixar, volta no próximo giro do vigia. */
    private fun forcarVolume() {
        val am = getSystemService(AudioManager::class.java)
        if (volumeOriginal < 0) volumeOriginal = am.getStreamVolume(AudioManager.STREAM_ALARM)
        val max = am.getStreamMaxVolume(AudioManager.STREAM_ALARM)
        if (am.getStreamVolume(AudioManager.STREAM_ALARM) < max) {
            runCatching { am.setStreamVolume(AudioManager.STREAM_ALARM, max, 0) }
        }
    }

    private fun tocarSom() {
        val fontes = mutableListOf<(MediaPlayer) -> Unit>()
        if (Armazem.config(this).somDoSistema) {
            val uri = runCatching { RingtoneManager.getActualDefaultRingtoneUri(this, RingtoneManager.TYPE_ALARM) }.getOrNull()
            if (uri != null) fontes += { mp -> mp.setDataSource(this, uri) }
        }
        // O bipe do app vem sempre por último: se o som do sistema falhar (ou estiver mudo), ele toca.
        fontes += { mp ->
            resources.openRawResourceFd(R.raw.bipe).use { afd ->
                mp.setDataSource(afd.fileDescriptor, afd.startOffset, afd.length)
            }
        }
        for (fonte in fontes) {
            val mp = MediaPlayer()
            try {
                mp.setAudioAttributes(atributos)
                fonte(mp)
                mp.isLooping = true
                mp.setWakeMode(this, PowerManager.PARTIAL_WAKE_LOCK)
                mp.prepare()
                mp.start()
                player = mp
                return
            } catch (e: Exception) {
                mp.release()
            }
        }
    }

    private fun vibrar() {
        val v = if (Build.VERSION.SDK_INT >= 31) {
            getSystemService(VibratorManager::class.java).defaultVibrator
        } else {
            getSystemService(Vibrator::class.java)
        }
        val efeito = VibrationEffect.createWaveform(longArrayOf(0, 700, 500), 0)
        runCatching {
            if (Build.VERSION.SDK_INT >= 33) {
                v.vibrate(efeito, VibrationAttributes.createForUsage(VibrationAttributes.USAGE_ALARM))
            } else {
                @Suppress("DEPRECATION")
                v.vibrate(efeito, atributos)
            }
        }
        vibrador = v
    }

    /** Traz a tela da tarefa de volta se a pessoa saiu dela (ou apagou a tela). */
    private fun abrirTela() {
        if (DespertarActivity.visivel) return
        if (Build.VERSION.SDK_INT >= 29 && !Settings.canDrawOverlays(this)) return
        runCatching { startActivity(DespertarActivity.abrir(this)) }
    }

    override fun onDestroy() {
        handler.removeCallbacks(vigia)
        runCatching { player?.stop() }
        runCatching { player?.release() }
        player = null
        runCatching { vibrador?.cancel() }
        val am = getSystemService(AudioManager::class.java)
        if (volumeOriginal >= 0) runCatching { am.setStreamVolume(AudioManager.STREAM_ALARM, volumeOriginal, 0) }
        foco?.let { runCatching { am.abandonAudioFocusRequest(it) } }
        runCatching { if (wakeLock?.isHeld == true) wakeLock?.release() }
        tocando = false
        // Parou sem a tarefa ter sido feita (o sistema derrubou o serviço): o vigia continua marcado
        // e faz voltar a tocar. Se a tarefa foi feita, não precisa mais dele.
        val s = Armazem.sessao(this)
        if (s == null || s.fase != Fase.TOCANDO) Agenda.pararVigia(this)
        super.onDestroy()
    }
}
