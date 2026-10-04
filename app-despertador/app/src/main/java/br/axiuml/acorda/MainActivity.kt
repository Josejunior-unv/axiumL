@file:OptIn(ExperimentalMaterial3Api::class)

package br.axiuml.acorda

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.BackHandler
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Add
import androidx.compose.material.icons.filled.Lock
import androidx.compose.material.icons.filled.Settings
import androidx.compose.material.icons.filled.Warning
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.ExtendedFloatingActionButton
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.SnackbarHost
import androidx.compose.material3.SnackbarHostState
import androidx.compose.material3.Switch
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.material3.TopAppBar
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import br.axiuml.acorda.nucleo.Alarme
import br.axiuml.acorda.nucleo.Calendario
import br.axiuml.acorda.nucleo.Fase
import br.axiuml.acorda.nucleo.Regras
import java.time.ZoneId
import kotlinx.coroutines.launch

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        Notificacoes.criarCanais(this)
        setContent { TemaAcorda { AppAcorda() } }
    }

    override fun onResume() {
        super.onResume()
        Agenda.reagendarTudo(this)
    }
}

private enum class Tela { LISTA, EDITOR, BLINDAGEM }

@Composable
private fun AppAcorda() {
    var tela by rememberSaveable { mutableStateOf(Tela.LISTA) }
    var editando by rememberSaveable { mutableStateOf<Long?>(null) }
    BackHandler(enabled = tela != Tela.LISTA) { tela = Tela.LISTA }
    when (tela) {
        Tela.LISTA -> TelaLista(
            aoEditar = { id ->
                editando = id
                tela = Tela.EDITOR
            },
            aoBlindagem = { tela = Tela.BLINDAGEM },
        )
        Tela.EDITOR -> TelaEditor(editando, aoVoltar = { tela = Tela.LISTA })
        Tela.BLINDAGEM -> TelaBlindagem(aoVoltar = { tela = Tela.LISTA })
    }
}

@Composable
private fun TelaLista(aoEditar: (Long?) -> Unit, aoBlindagem: () -> Unit) {
    val ctx = LocalContext.current
    val versao by Armazem.versao.collectAsState()
    val agora by agoraQueAnda(10_000)
    var voltou by remember { mutableIntStateOf(0) }
    AoVoltarParaTela { voltou++ }

    val alarmes = remember(versao) { Armazem.alarmes(ctx) }
    val travas = remember(versao, agora, voltou) { Trava.todos(ctx) }
    val sessao = remember(versao, voltou) { Armazem.sessao(ctx) }
    val pendentes = remember(voltou) { Blindagem.pendentes(ctx) }
    val janela = remember(versao) { Armazem.config(ctx).janelaMin }

    val snackbar = remember { SnackbarHostState() }
    val escopo = rememberCoroutineScope()
    val avisar: (String) -> Unit = { msg -> escopo.launch { snackbar.showSnackbar(msg) } }
    var confirmarLigar by remember { mutableStateOf<Alarme?>(null) }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Acorda!", fontWeight = FontWeight.Bold) },
                actions = {
                    IconButton(onClick = aoBlindagem) { Icon(Icons.Default.Settings, contentDescription = "Proteção e ajustes") }
                },
            )
        },
        floatingActionButton = {
            ExtendedFloatingActionButton(
                onClick = { aoEditar(null) },
                icon = { Icon(Icons.Default.Add, contentDescription = null) },
                text = { Text("Novo alarme") },
            )
        },
        snackbarHost = { SnackbarHost(snackbar) },
    ) { pad ->
        LazyColumn(
            contentPadding = PaddingValues(
                start = 16.dp,
                end = 16.dp,
                top = pad.calculateTopPadding() + 8.dp,
                bottom = pad.calculateBottomPadding() + 96.dp,
            ),
            verticalArrangement = Arrangement.spacedBy(12.dp),
        ) {
            if (sessao != null) {
                item {
                    CartaoDestaque(
                        titulo = if (sessao.fase == Fase.TOCANDO) "Alarme tocando" else "Falta confirmar que você acordou",
                        texto = if (sessao.fase == Fase.TOCANDO) "Faça a tarefa para desligar."
                        else "Faça a tarefa até ${Notificacoes.hora(sessao.prazo)} ou ele toca de novo.",
                        botao = "Abrir tarefa",
                        erro = true,
                    ) { ctx.startActivity(DespertarActivity.abrir(ctx)) }
                }
            }
            if (pendentes > 0) {
                item {
                    CartaoDestaque(
                        titulo = "Proteção incompleta",
                        texto = "Faltam $pendentes ${if (pendentes == 1) "ajuste" else "ajustes"} para o alarme ser à prova de fuga.",
                        botao = "Resolver",
                        erro = false,
                        aoClicar = aoBlindagem,
                    )
                }
            }
            if (alarmes.isEmpty()) {
                item {
                    Column(Modifier.fillMaxWidth().padding(vertical = 48.dp), horizontalAlignment = Alignment.CenterHorizontally) {
                        Text("⏰", style = MaterialTheme.typography.displayMedium)
                        Text("Nenhum alarme ainda.", style = MaterialTheme.typography.titleMedium)
                        Text(
                            "Toque em \"Novo alarme\" e escolha o que você vai ter que fazer para ele parar.",
                            style = MaterialTheme.typography.bodyMedium,
                        )
                    }
                }
            }
            items(alarmes, key = { it.id }) { a ->
                val trava = travas[a.id] ?: Trava.Estado(false, null)
                CartaoAlarme(
                    alarme = a,
                    trava = trava,
                    janelaMin = janela,
                    podeTestar = sessao == null,
                    aoClicar = {
                        if (Trava.de(ctx, a.id).travado) avisar(textoTravado(trava, janela)) else aoEditar(a.id)
                    },
                    aoAlternar = { ligar ->
                        when {
                            Trava.de(ctx, a.id).travado -> avisar(textoTravado(trava, janela))
                            ligar && nasceTravado(a, janela) -> confirmarLigar = a
                            else -> {
                                Armazem.salvarAlarme(ctx, a.copy(ativo = ligar))
                                Agenda.reagendarTudo(ctx)
                            }
                        }
                    },
                    aoTestar = {
                        Agenda.tocarJa(ctx, a.id, teste = true, atrasoMs = 5_000)
                        avisar("Toca em 5 segundos. Pode bloquear a tela para ver como fica.")
                    },
                )
            }
        }
    }

    confirmarLigar?.let { a ->
        AvisoNasceTravado(
            alarme = a,
            janelaMin = janela,
            aoConfirmar = {
                Armazem.salvarAlarme(ctx, a.copy(ativo = true))
                Agenda.reagendarTudo(ctx)
                confirmarLigar = null
            },
            aoCancelar = { confirmarLigar = null },
        )
    }
}

private fun textoTravado(trava: Trava.Estado, janelaMin: Int): String {
    val quando = trava.restanteMs?.takeIf { it > 0 }?.let { " Toca ${Calendario.descreverEspera(it)}." } ?: ""
    return "Travado: a menos de $janelaMin min do alarme não dá para desligar, mudar nem apagar.$quando"
}

/** Se ligar (ou salvar) agora, o alarme já cai dentro da janela de trava. */
fun nasceTravado(a: Alarme, janelaMin: Int): Boolean {
    val agora = System.currentTimeMillis()
    val proximo = Calendario.proximoMs(a.copy(ativo = true), agora, ZoneId.systemDefault()) ?: return false
    return proximo - agora <= janelaMin * Regras.MINUTO
}

@Composable
fun AvisoNasceTravado(alarme: Alarme, janelaMin: Int, aoConfirmar: () -> Unit, aoCancelar: () -> Unit) {
    val agora = System.currentTimeMillis()
    val falta = Calendario.proximoMs(alarme.copy(ativo = true), agora, ZoneId.systemDefault())?.minus(agora) ?: 0
    AlertDialog(
        onDismissRequest = aoCancelar,
        icon = { Icon(Icons.Default.Lock, contentDescription = null) },
        title = { Text("Ele já nasce travado") },
        text = {
            Text(
                "Este alarme toca ${Calendario.descreverEspera(falta)}, dentro da janela de $janelaMin min. " +
                    "Depois de confirmar, não dá mais para desligar, mudar nem apagar até ele tocar e você fazer a tarefa.",
            )
        },
        confirmButton = { TextButton(onClick = aoConfirmar) { Text("Confirmar") } },
        dismissButton = { TextButton(onClick = aoCancelar) { Text("Cancelar") } },
    )
}

@Composable
private fun CartaoDestaque(
    titulo: String,
    texto: String,
    botao: String,
    erro: Boolean,
    aoClicar: () -> Unit,
) {
    val fundo = if (erro) MaterialTheme.colorScheme.errorContainer else MaterialTheme.colorScheme.secondaryContainer
    val frente = if (erro) MaterialTheme.colorScheme.onErrorContainer else MaterialTheme.colorScheme.onSecondaryContainer
    Card(onClick = aoClicar, colors = CardDefaults.cardColors(containerColor = fundo, contentColor = frente)) {
        Row(Modifier.padding(16.dp), verticalAlignment = Alignment.CenterVertically) {
            Icon(Icons.Default.Warning, contentDescription = null)
            Spacer(Modifier.width(12.dp))
            Column(Modifier.weight(1f)) {
                Text(titulo, style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold)
                Text(texto, style = MaterialTheme.typography.bodyMedium)
            }
            TextButton(onClick = aoClicar) { Text(botao, color = frente) }
        }
    }
}

@Composable
private fun CartaoAlarme(
    alarme: Alarme,
    trava: Trava.Estado,
    janelaMin: Int,
    podeTestar: Boolean,
    aoClicar: () -> Unit,
    aoAlternar: (Boolean) -> Unit,
    aoTestar: () -> Unit,
) {
    val apagado = !alarme.ativo
    val cor = if (apagado) MaterialTheme.colorScheme.onSurface.copy(alpha = 0.45f) else MaterialTheme.colorScheme.onSurface
    Card(onClick = aoClicar, modifier = Modifier.fillMaxWidth()) {
        Column(Modifier.padding(start = 16.dp, end = 16.dp, top = 12.dp, bottom = 4.dp)) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Column(Modifier.weight(1f)) {
                    Text(alarme.horario, style = MaterialTheme.typography.displaySmall, fontWeight = FontWeight.Bold, color = cor)
                    Text(
                        listOf(alarme.rotulo.ifBlank { "Alarme" }, Calendario.descreverDias(alarme.dias)).joinToString(" · "),
                        style = MaterialTheme.typography.bodyMedium,
                        color = cor,
                    )
                }
                if (trava.travado) {
                    Icon(
                        Icons.Default.Lock,
                        contentDescription = "Travado",
                        tint = MaterialTheme.colorScheme.primary,
                        modifier = Modifier.padding(end = 8.dp).size(20.dp),
                    )
                }
                Switch(checked = alarme.ativo, onCheckedChange = aoAlternar, enabled = !trava.travado)
            }
            Spacer(Modifier.padding(top = 6.dp))
            Text("Para desligar: ${alarme.desligar.descricao().replaceFirstChar { it.lowercase() }}", style = MaterialTheme.typography.bodySmall, color = cor)
            Text(
                alarme.confirmar?.let {
                    "Para não tocar de novo: ${it.descricao().replaceFirstChar { c -> c.lowercase() }} em até ${alarme.prazoConfirmarMin} min"
                } ?: "Sem confirmação: não volta a tocar depois de desligado",
                style = MaterialTheme.typography.bodySmall,
                color = cor,
            )
            Row(verticalAlignment = Alignment.CenterVertically) {
                val restante = trava.restanteMs
                Text(
                    when {
                        trava.travado && restante != null && restante > 0 -> "🔒 Travado · toca ${Calendario.descreverEspera(restante)}"
                        trava.travado -> "🔒 Travado até você confirmar que acordou"
                        alarme.ativo && restante != null -> "Toca ${Calendario.descreverEspera(restante)} · trava $janelaMin min antes"
                        else -> "Desligado"
                    },
                    style = MaterialTheme.typography.labelLarge,
                    color = if (trava.travado) MaterialTheme.colorScheme.primary else cor,
                    modifier = Modifier.weight(1f),
                )
                TextButton(onClick = aoTestar, enabled = podeTestar) { Text("Testar") }
            }
        }
    }
}
