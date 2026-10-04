@file:OptIn(ExperimentalMaterial3Api::class)

package br.axiuml.acorda

import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.selection.selectable
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material.icons.filled.CheckCircle
import androidx.compose.material.icons.filled.Lock
import androidx.compose.material.icons.filled.Warning
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.FilledTonalButton
import androidx.compose.material3.FilterChip
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.RadioButton
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.semantics.Role
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp

@Composable
fun TelaBlindagem(aoVoltar: () -> Unit) {
    val ctx = LocalContext.current
    var voltou by remember { mutableIntStateOf(0) }
    AoVoltarParaTela { voltou++ }
    val versao by Armazem.versao.collectAsState()
    val itens = remember(voltou) { Blindagem.itens(ctx) }
    val config = remember(versao) { Armazem.config(ctx) }
    val algumTravado = remember(versao, voltou) { Trava.algumTravado(ctx) }
    val protecao = remember(voltou, versao) { Blindagem.protecaoAtiva(ctx) }

    // Permissão negada de vez: o pedido nem aparece mais, então manda para as configurações.
    var pedindo by remember { mutableStateOf<String?>(null) }
    val pedir = rememberLauncherForActivityResult(ActivityResultContracts.RequestPermission()) { ok ->
        val id = pedindo
        if (!ok && id != null) Blindagem.abrir(ctx, id)
        pedindo = null
        voltou++
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Proteção e ajustes") },
                navigationIcon = { IconButton(onClick = aoVoltar) { Icon(Icons.Default.ArrowBack, contentDescription = "Voltar") } },
            )
        },
    ) { pad ->
        Column(
            Modifier
                .padding(pad)
                .verticalScroll(rememberScrollState())
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp),
        ) {
            Text(
                "Cada item fecha uma rota de fuga. Os marcados como essenciais fazem o alarme tocar de verdade e não deixam o app ser parado.",
                style = MaterialTheme.typography.bodyMedium,
            )
            for (item in itens) {
                ItemDaLista(item) {
                    val permissao = item.permissao
                    if (permissao != null) {
                        pedindo = item.id
                        pedir.launch(permissao)
                    } else {
                        Blindagem.abrir(ctx, item.id)
                    }
                }
            }

            HorizontalDivider()
            Text("Trava antes do alarme", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold)
            Text(
                "Quanto tempo antes de tocar o alarme fica impossível de desligar, mudar ou apagar.",
                style = MaterialTheme.typography.bodySmall,
            )
            Row(Modifier.horizontalScroll(rememberScrollState()), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                for (min in listOf(30, 60, 90, 120, 180)) {
                    FilterChip(
                        selected = config.janelaMin == min,
                        enabled = !algumTravado,
                        onClick = { Armazem.salvarConfig(ctx, config.copy(janelaMin = min)) },
                        label = { Text(if (min % 60 == 0) "${min / 60} h" else "$min min") },
                    )
                }
            }

            Text("Som", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold)
            OpcaoSom(
                "Bipe do Acorda!",
                "Recomendado: alto, irritante e impossível de trocar por um som mudo.",
                selecionado = !config.somDoSistema,
                habilitado = !algumTravado,
            ) { Armazem.salvarConfig(ctx, config.copy(somDoSistema = false)) }
            OpcaoSom(
                "Som de alarme do sistema",
                "O toque escolhido nas configurações do Android. Se falhar, toca o bipe.",
                selecionado = config.somDoSistema,
                habilitado = !algumTravado,
            ) { Armazem.salvarConfig(ctx, config.copy(somDoSistema = true)) }

            if (algumTravado) {
                Card(colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.primaryContainer)) {
                    Row(Modifier.padding(12.dp), verticalAlignment = Alignment.CenterVertically) {
                        Icon(Icons.Default.Lock, contentDescription = null)
                        Text(
                            "Ajustes travados: tem alarme a menos de ${config.janelaMin} min de tocar.",
                            Modifier.padding(start = 12.dp),
                        )
                    }
                }
            }

            if (protecao) {
                HorizontalDivider()
                Text("Desinstalar", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold)
                Text(
                    "Para desinstalar o app, desligue a proteção primeiro. Isso só é possível fora da janela de trava.",
                    style = MaterialTheme.typography.bodySmall,
                )
                OutlinedButton(onClick = { Blindagem.desativarProtecao(ctx) }, enabled = !algumTravado) {
                    Text("Desligar a proteção")
                }
            }
            Spacer(Modifier.height(24.dp))
        }
    }
}

@Composable
private fun ItemDaLista(item: ItemBlindagem, aoResolver: () -> Unit) {
    val cor = when {
        item.ok -> MaterialTheme.colorScheme.primary
        item.essencial -> MaterialTheme.colorScheme.error
        else -> MaterialTheme.colorScheme.onSurfaceVariant
    }
    Card(Modifier.fillMaxWidth()) {
        Row(Modifier.padding(12.dp), verticalAlignment = Alignment.CenterVertically) {
            Icon(if (item.ok) Icons.Default.CheckCircle else Icons.Default.Warning, contentDescription = null, tint = cor)
            Column(
                Modifier
                    .weight(1f)
                    .padding(horizontal = 12.dp),
            ) {
                Text(item.titulo, style = MaterialTheme.typography.titleSmall, fontWeight = FontWeight.Bold)
                Text(item.explicacao, style = MaterialTheme.typography.bodySmall)
                if (!item.essencial) Text("Opcional", style = MaterialTheme.typography.labelSmall, color = cor)
            }
            if (!item.ok) FilledTonalButton(onClick = aoResolver) { Text("Ativar") }
        }
    }
}

@Composable
private fun OpcaoSom(
    titulo: String,
    explicacao: String,
    selecionado: Boolean,
    habilitado: Boolean,
    aoEscolher: () -> Unit,
) {
    Row(
        Modifier
            .fillMaxWidth()
            .selectable(selected = selecionado, enabled = habilitado, role = Role.RadioButton, onClick = aoEscolher)
            .padding(vertical = 4.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        RadioButton(selected = selecionado, onClick = null, enabled = habilitado)
        Column(Modifier.padding(start = 8.dp)) {
            Text(titulo, style = MaterialTheme.typography.bodyLarge)
            Text(explicacao, style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
        }
    }
}
