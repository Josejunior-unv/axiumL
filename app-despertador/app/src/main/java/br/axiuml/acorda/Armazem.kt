package br.axiuml.acorda

import android.content.Context
import android.content.SharedPreferences
import android.os.SystemClock
import android.provider.Settings
import br.axiuml.acorda.nucleo.Agendamento
import br.axiuml.acorda.nucleo.Alarme
import br.axiuml.acorda.nucleo.Calendario
import br.axiuml.acorda.nucleo.Config
import br.axiuml.acorda.nucleo.Json
import br.axiuml.acorda.nucleo.Regras
import br.axiuml.acorda.nucleo.Sessao
import java.time.ZoneId
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow

/**
 * Tudo o que o app guarda. Fica no armazenamento que já funciona antes do primeiro desbloqueio,
 * para o alarme tocar mesmo se o celular reiniciou de madrugada e ninguém digitou a senha.
 */
object Armazem {
    private const val ARQUIVO = "acorda"

    private val _versao = MutableStateFlow(0)

    /** Sobe a cada gravação: as telas observam para se atualizar sozinhas. */
    val versao: StateFlow<Int> = _versao

    private fun prefs(ctx: Context): SharedPreferences =
        ctx.createDeviceProtectedStorageContext().getSharedPreferences(ARQUIVO, Context.MODE_PRIVATE)

    // commit() e não apply(): quem grava muitas vezes é um receiver que pode morrer logo depois.
    private fun gravar(ctx: Context, bloco: SharedPreferences.Editor.() -> Unit) {
        prefs(ctx).edit().apply(bloco).commit()
        _versao.value = _versao.value + 1
    }

    fun alarmes(ctx: Context): List<Alarme> =
        runCatching { Json.alarmes(prefs(ctx).getString("alarmes", null)) }.getOrDefault(emptyList())

    fun alarme(ctx: Context, id: Long): Alarme? = alarmes(ctx).firstOrNull { it.id == id }

    fun salvarAlarme(ctx: Context, a: Alarme) {
        val lista = (alarmes(ctx).filter { it.id != a.id } + a).sortedBy { it.hora * 60 + it.minuto }
        gravar(ctx) { putString("alarmes", Json.alarmes(lista)) }
    }

    fun removerAlarme(ctx: Context, id: Long) {
        val lista = alarmes(ctx).filter { it.id != id }
        gravar(ctx) { putString("alarmes", Json.alarmes(lista)) }
    }

    fun novoId(ctx: Context): Long {
        val id = prefs(ctx).getLong("ultimoId", 0) + 1
        gravar(ctx) { putLong("ultimoId", id) }
        return id
    }

    fun sessao(ctx: Context): Sessao? = runCatching { Json.sessao(prefs(ctx).getString("sessao", null)) }.getOrNull()

    fun salvarSessao(ctx: Context, s: Sessao?) = gravar(ctx) { putString("sessao", Json.sessao(s)) }

    fun agendamentos(ctx: Context): Map<Long, Agendamento> =
        runCatching { Json.agendamentos(prefs(ctx).getString("agendamentos", null)) }.getOrDefault(emptyMap())

    fun salvarAgendamentos(ctx: Context, m: Map<Long, Agendamento>) =
        gravar(ctx) { putString("agendamentos", Json.agendamentos(m)) }

    fun config(ctx: Context): Config = runCatching { Json.config(prefs(ctx).getString("config", null)) }.getOrDefault(Config())

    fun salvarConfig(ctx: Context, c: Config) = gravar(ctx) { putString("config", Json.config(c)) }
}

object Relogio {
    fun agora(): Long = System.currentTimeMillis()

    /** Tempo desde que o celular ligou. Não muda quando alguém mexe na hora. */
    fun elapsed(): Long = SystemClock.elapsedRealtime()

    fun boot(ctx: Context): Int =
        runCatching { Settings.Global.getInt(ctx.contentResolver, Settings.Global.BOOT_COUNT) }.getOrDefault(-1)
}

/** A trava: a menos de [br.axiuml.acorda.nucleo.Config.janelaMin] do toque, o alarme não pode ser mexido. */
object Trava {
    data class Estado(val travado: Boolean, val restanteMs: Long?)

    fun todos(ctx: Context): Map<Long, Estado> {
        val agora = Relogio.agora()
        val el = Relogio.elapsed()
        val boot = Relogio.boot(ctx)
        val ags = Armazem.agendamentos(ctx)
        val sessao = Armazem.sessao(ctx)
        val janela = Armazem.config(ctx).janelaMin
        val zona = ZoneId.systemDefault()
        return Armazem.alarmes(ctx).associate { a ->
            val restante = if (!a.ativo) {
                null
            } else {
                Regras.restante(ags[a.id], agora, el, boot)
                    ?: Calendario.proximoMs(a, agora, zona)?.minus(agora)
            }
            a.id to Estado(Regras.travado(a.id, restante, sessao, janela), restante)
        }
    }

    fun de(ctx: Context, id: Long): Estado = todos(ctx)[id] ?: Estado(false, null)

    fun algumTravado(ctx: Context): Boolean = todos(ctx).values.any { it.travado }

    /** O alarme que está travado agora (o do despertar em andamento, ou o mais próximo de tocar). */
    fun alarmeTravado(ctx: Context): Long? {
        val s = Armazem.sessao(ctx)
        if (s != null && !s.teste) return s.alarmeId
        return todos(ctx).filter { it.value.travado }.minByOrNull { it.value.restanteMs ?: Long.MAX_VALUE }?.key
    }
}
