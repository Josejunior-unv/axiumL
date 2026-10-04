package br.axiuml.acorda

import android.Manifest
import android.app.AlarmManager
import android.app.NotificationManager
import android.app.admin.DevicePolicyManager
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.net.Uri
import android.os.Build
import android.os.PowerManager
import android.provider.Settings

/** Cada ajuste do Android que fecha uma rota de fuga do alarme. */
data class ItemBlindagem(
    val id: String,
    val titulo: String,
    val explicacao: String,
    val ok: Boolean,
    /** Sem ele, o alarme pode simplesmente não tocar ou ser parado com facilidade. */
    val essencial: Boolean = true,
    /** Resolve-se com o pedido de permissão do próprio app, não numa tela de configurações. */
    val permissao: String? = null,
)

object Blindagem {
    fun itens(ctx: Context): List<ItemBlindagem> = buildList {
        val pkg = ctx.packageName
        if (Build.VERSION.SDK_INT >= 33) {
            add(
                ItemBlindagem(
                    "notificacoes", "Notificações",
                    "Sem elas o alarme não consegue abrir a tela da tarefa nem avisar da confirmação.",
                    tem(ctx, Manifest.permission.POST_NOTIFICATIONS),
                    permissao = Manifest.permission.POST_NOTIFICATIONS,
                ),
            )
        }
        if (Build.VERSION.SDK_INT >= 31) {
            add(
                ItemBlindagem(
                    "exato", "Alarmes no minuto exato",
                    "Para tocar na hora certa mesmo com o celular em economia de bateria.",
                    ctx.getSystemService(AlarmManager::class.java).canScheduleExactAlarms(),
                ),
            )
        }
        if (Build.VERSION.SDK_INT >= 34) {
            add(
                ItemBlindagem(
                    "tela_cheia", "Tela cheia por cima do bloqueio",
                    "Para a tarefa aparecer sozinha, com a tela acesa, sem você precisar desbloquear.",
                    ctx.getSystemService(NotificationManager::class.java).canUseFullScreenIntent(),
                ),
            )
        }
        add(
            ItemBlindagem(
                "admin", "Proteção contra desinstalar e forçar parada",
                "Liga o Acorda! como administrador do aparelho. Enquanto estiver ligada, o Android não deixa " +
                    "desinstalar nem forçar a parada do app. Desligar a proteção perto do alarme faz ele tocar na hora.",
                ctx.getSystemService(DevicePolicyManager::class.java).isAdminActive(ProtecaoAdmin.componente(ctx)),
            ),
        )
        add(
            ItemBlindagem(
                "sobrepor", "Voltar sozinho para a tarefa",
                "\"Sobrepor a outros apps\": se você sair da tela da tarefa (ou apagar a tela) enquanto toca, ela volta em 2 segundos.",
                Settings.canDrawOverlays(ctx),
            ),
        )
        add(
            ItemBlindagem(
                "bateria", "Sem economia de bateria",
                "Impede que o sistema (principalmente Xiaomi, Samsung e Motorola) feche o app de madrugada.",
                ctx.getSystemService(PowerManager::class.java).isIgnoringBatteryOptimizations(pkg),
            ),
        )
        if (Build.VERSION.SDK_INT >= 29) {
            add(
                ItemBlindagem(
                    "atividade", "Contador de passos",
                    "Só para a tarefa de andar. Sem ele, os passos são contados pelo acelerômetro (menos preciso).",
                    tem(ctx, Manifest.permission.ACTIVITY_RECOGNITION),
                    essencial = false,
                    permissao = Manifest.permission.ACTIVITY_RECOGNITION,
                ),
            )
        }
    }

    fun pendentes(ctx: Context): Int = itens(ctx).count { !it.ok && it.essencial }

    fun tem(ctx: Context, permissao: String): Boolean =
        ctx.checkSelfPermission(permissao) == PackageManager.PERMISSION_GRANTED

    /** A tela de configurações onde o item se resolve. */
    fun intent(ctx: Context, id: String): Intent {
        val pacote = Uri.parse("package:${ctx.packageName}")
        return when (id) {
            "notificacoes" -> Intent(Settings.ACTION_APP_NOTIFICATION_SETTINGS)
                .putExtra(Settings.EXTRA_APP_PACKAGE, ctx.packageName)
            "exato" -> Intent(Settings.ACTION_REQUEST_SCHEDULE_EXACT_ALARM, pacote)
            "tela_cheia" -> Intent(Settings.ACTION_MANAGE_APP_USE_FULL_SCREEN_INTENT, pacote)
            "admin" -> Intent(DevicePolicyManager.ACTION_ADD_DEVICE_ADMIN)
                .putExtra(DevicePolicyManager.EXTRA_DEVICE_ADMIN, ProtecaoAdmin.componente(ctx))
                .putExtra(
                    DevicePolicyManager.EXTRA_ADD_EXPLANATION,
                    "Com a proteção ligada, o Acorda! não pode ser desinstalado nem forçado a parar. " +
                        "Ele não usa nenhum outro poder de administrador.",
                )
            "sobrepor" -> Intent(Settings.ACTION_MANAGE_OVERLAY_PERMISSION, pacote)
            "bateria" -> Intent(Settings.ACTION_REQUEST_IGNORE_BATTERY_OPTIMIZATIONS, pacote)
            else -> Intent(Settings.ACTION_APPLICATION_DETAILS_SETTINGS, pacote)
        }
    }

    fun abrir(ctx: Context, id: String) {
        val ok = runCatching { ctx.startActivity(intent(ctx, id)) }.isSuccess
        if (!ok) {
            runCatching {
                ctx.startActivity(
                    Intent(Settings.ACTION_APPLICATION_DETAILS_SETTINGS, Uri.parse("package:${ctx.packageName}")),
                )
            }
        }
    }

    fun desativarProtecao(ctx: Context) {
        val dpm = ctx.getSystemService(DevicePolicyManager::class.java)
        runCatching { dpm.removeActiveAdmin(ProtecaoAdmin.componente(ctx)) }
    }

    fun protecaoAtiva(ctx: Context): Boolean =
        ctx.getSystemService(DevicePolicyManager::class.java).isAdminActive(ProtecaoAdmin.componente(ctx))
}
