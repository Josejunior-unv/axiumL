package br.axiuml.acorda

import android.app.admin.DeviceAdminReceiver
import android.content.BroadcastReceiver
import android.content.ComponentName
import android.content.Context
import android.content.Intent
import br.axiuml.acorda.nucleo.Fase

/** Recebe os disparos marcados no AlarmManager. */
class AlarmeReceiver : BroadcastReceiver() {
    override fun onReceive(ctx: Context, intent: Intent) {
        val id = intent.getLongExtra(Agenda.EXTRA_ALARME, -1)
        when (intent.action) {
            Agenda.ACAO_DISPARAR -> Fluxo.disparou(ctx, id, intent.getLongExtra(Agenda.EXTRA_PREVISTO, 0))
            Agenda.ACAO_EXTRA -> Fluxo.tocarFora(ctx, id, intent.getBooleanExtra(Agenda.EXTRA_TESTE, false))
            Agenda.ACAO_PRAZO -> Fluxo.prazoVenceu(ctx, id)
            // O vigia só religa um toque que já existe; nunca começa um novo.
            Agenda.ACAO_VIGIA -> if (Armazem.sessao(ctx)?.fase == Fase.TOCANDO) ToqueService.iniciar(ctx)
        }
    }
}

/** Celular ligou, app atualizou, hora ou fuso mudou: remarca tudo. */
class SistemaReceiver : BroadcastReceiver() {
    override fun onReceive(ctx: Context, intent: Intent) {
        when (intent.action) {
            Intent.ACTION_LOCKED_BOOT_COMPLETED, Intent.ACTION_BOOT_COMPLETED -> Fluxo.retomar(ctx, ligou = true)
            Intent.ACTION_MY_PACKAGE_REPLACED -> Fluxo.retomar(ctx, ligou = false)
            else -> Agenda.reagendarTudo(ctx)
        }
    }
}

/**
 * Administrador do dispositivo. Enquanto ativo, o Android não deixa desinstalar nem "forçar parada"
 * do app. Desativar dá para fazer nas configurações — mas, perto do alarme, isso faz ele tocar na hora.
 */
class ProtecaoAdmin : DeviceAdminReceiver() {
    companion object {
        fun componente(ctx: Context) = ComponentName(ctx, ProtecaoAdmin::class.java)
    }

    override fun onDisableRequested(context: Context, intent: Intent): CharSequence {
        val janela = Armazem.config(context).janelaMin
        return if (Trava.algumTravado(context)) {
            "ATENÇÃO: falta menos de $janela min para um alarme. Se você desativar a proteção agora, " +
                "o alarme toca IMEDIATAMENTE e só para com a tarefa."
        } else {
            "Sem a proteção, o Acorda! pode ser desinstalado ou forçado a parar, e o alarme deixa de ser à prova de fuga."
        }
    }

    override fun onDisabled(context: Context, intent: Intent) {
        val alvo = Trava.alarmeTravado(context) ?: return
        Agenda.tocarJa(context, alvo, teste = false)
    }
}
