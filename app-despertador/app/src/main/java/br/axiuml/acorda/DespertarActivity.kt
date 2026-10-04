package br.axiuml.acorda

import android.content.Context
import android.content.Intent
import android.os.Build
import android.os.Bundle
import android.view.KeyEvent
import android.view.WindowManager
import androidx.activity.ComponentActivity
import androidx.activity.OnBackPressedCallback
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.imePadding
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.systemBarsPadding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.key
import androidx.compose.runtime.remember
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import br.axiuml.acorda.nucleo.Alarme
import br.axiuml.acorda.nucleo.Fase
import br.axiuml.acorda.nucleo.Regras
import br.axiuml.acorda.nucleo.Sessao
import br.axiuml.acorda.nucleo.Tarefa
import br.axiuml.acorda.nucleo.TipoTarefa
import kotlinx.coroutines.delay

/**
 * A tela da tarefa. Abre por cima da tela de bloqueio, acende a tela, não sai com o botão voltar e
 * não deixa mexer no volume enquanto toca.
 */
class DespertarActivity : ComponentActivity() {
    companion object {
        @Volatile
        var visivel = false
            private set

        fun abrir(ctx: Context): Intent =
            Intent(ctx, DespertarActivity::class.java).addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        if (Build.VERSION.SDK_INT >= 27) {
            setShowWhenLocked(true)
            setTurnScreenOn(true)
        } else {
            @Suppress("DEPRECATION")
            window.addFlags(
                WindowManager.LayoutParams.FLAG_SHOW_WHEN_LOCKED or WindowManager.LayoutParams.FLAG_TURN_SCREEN_ON,
            )
        }
        window.addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON)
        enableEdgeToEdge()
        onBackPressedDispatcher.addCallback(this, object : OnBackPressedCallback(true) {
            override fun handleOnBackPressed() {
                // Voltar não sai da tarefa.
            }
        })
        setContent { TemaAcorda { TelaDespertar(aoTerminar = { finishAndRemoveTask() }) } }
    }

    override fun onStart() {
        super.onStart()
        visivel = true
    }

    override fun onStop() {
        visivel = false
        super.onStop()
    }

    override fun onKeyDown(keyCode: Int, event: KeyEvent?): Boolean {
        val volume = keyCode == KeyEvent.KEYCODE_VOLUME_UP || keyCode == KeyEvent.KEYCODE_VOLUME_DOWN ||
            keyCode == KeyEvent.KEYCODE_VOLUME_MUTE
        if (volume && Armazem.sessao(this)?.fase == Fase.TOCANDO) return true
        return super.onKeyDown(keyCode, event)
    }
}

@Composable
fun TelaDespertar(aoTerminar: () -> Unit) {
    val ctx = LocalContext.current
    val versao by Armazem.versao.collectAsState()
    val sessao = remember(versao) { Armazem.sessao(ctx) }
    val alarme = remember(versao, sessao?.alarmeId) { sessao?.let { Armazem.alarme(ctx, it.alarmeId) } }
    val agora by agoraQueAnda()

    Surface(Modifier.fillMaxSize(), color = MaterialTheme.colorScheme.background) {
        Column(
            Modifier
                .systemBarsPadding()
                .imePadding()
                .verticalScroll(rememberScrollState())
                .padding(horizontal = 20.dp, vertical = 16.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.spacedBy(12.dp),
        ) {
            when {
                sessao == null -> BomDia(aoTerminar)
                sessao.fase == Fase.TOCANDO -> key(sessao.fase, sessao.inicio) { Tocando(sessao, alarme, agora) }
                else -> key(sessao.fase, sessao.inicio) { Confirmando(sessao, alarme, agora, aoTerminar) }
            }
        }
    }
}

@Composable
private fun Tocando(sessao: Sessao, alarme: Alarme?, agora: Long) {
    val ctx = LocalContext.current
    val tarefa = alarme?.let { Regras.tarefaDaFase(sessao, it) } ?: Tarefa.padrao(TipoTarefa.CONTAS)
    Text(Notificacoes.hora(agora), fontSize = 64.sp, fontWeight = FontWeight.Bold)
    Text(
        alarme?.rotulo?.ifBlank { null } ?: "Hora de acordar!",
        style = MaterialTheme.typography.headlineSmall,
        textAlign = TextAlign.Center,
    )
    if (sessao.teste) Text("Teste", color = MaterialTheme.colorScheme.secondary)
    if (sessao.rodada > 1) {
        Aviso("Você não confirmou a tempo. Tocando de novo (${sessao.rodada}ª vez).")
    }
    Text(
        "Para desligar: ${tarefa.descricao().replaceFirstChar { it.lowercase() }}",
        style = MaterialTheme.typography.titleMedium,
        textAlign = TextAlign.Center,
    )
    Spacer(Modifier.height(4.dp))
    TarefaUI(tarefa) { Fluxo.concluiu(ctx, sessao.fase, sessao.inicio) }
}

@Composable
private fun Confirmando(sessao: Sessao, alarme: Alarme?, agora: Long, aoTerminar: () -> Unit) {
    val ctx = LocalContext.current
    val tarefa = alarme?.confirmar ?: Tarefa.padrao(TipoTarefa.CONTAS)
    val restante = (sessao.prazo - agora).coerceAtLeast(0)

    Text("O som parou.", style = MaterialTheme.typography.headlineMedium, fontWeight = FontWeight.Bold)
    Card(
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.primaryContainer),
        modifier = Modifier.fillMaxWidth(),
    ) {
        Column(Modifier.padding(16.dp), horizontalAlignment = Alignment.CenterHorizontally) {
            Text(
                if (sessao.teste) "No alarme de verdade, ele toca de novo se você não fizer isto:"
                else "Para ele não tocar de novo às ${Notificacoes.hora(sessao.prazo)}, falta:",
                textAlign = TextAlign.Center,
                color = MaterialTheme.colorScheme.onPrimaryContainer,
            )
            Text(
                tarefa.descricao(),
                style = MaterialTheme.typography.titleLarge,
                fontWeight = FontWeight.Bold,
                textAlign = TextAlign.Center,
                color = MaterialTheme.colorScheme.onPrimaryContainer,
            )
            if (!sessao.teste) {
                Text(
                    "%d:%02d".format(restante / 60_000, (restante / 1000) % 60),
                    fontSize = 40.sp,
                    fontWeight = FontWeight.Bold,
                    color = MaterialTheme.colorScheme.onPrimaryContainer,
                )
            }
        }
    }
    TarefaUI(tarefa) { Fluxo.concluiu(ctx, sessao.fase, sessao.inicio) }
    OutlinedButton(onClick = aoTerminar, modifier = Modifier.fillMaxWidth()) {
        Text("Fazer daqui a pouco (a notificação traz de volta)")
    }
}

@Composable
private fun BomDia(aoTerminar: () -> Unit) {
    LaunchedEffect(Unit) {
        delay(8_000)
        aoTerminar()
    }
    Spacer(Modifier.height(48.dp))
    Text("☀️", fontSize = 72.sp)
    Text("Bom dia!", style = MaterialTheme.typography.displaySmall, fontWeight = FontWeight.Bold)
    Text(
        "Você está acordado de verdade. O alarme não vai tocar de novo.",
        style = MaterialTheme.typography.titleMedium,
        textAlign = TextAlign.Center,
    )
    Spacer(Modifier.height(16.dp))
    Button(onClick = aoTerminar, modifier = Modifier.fillMaxWidth()) { Text("Fechar") }
}

@Composable
fun Aviso(texto: String) {
    Card(
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.errorContainer),
        modifier = Modifier.fillMaxWidth(),
    ) {
        Text(
            texto,
            Modifier.padding(12.dp),
            color = MaterialTheme.colorScheme.onErrorContainer,
            textAlign = TextAlign.Center,
        )
    }
}
