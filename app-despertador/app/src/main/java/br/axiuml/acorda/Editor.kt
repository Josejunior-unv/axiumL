@file:OptIn(ExperimentalMaterial3Api::class)

package br.axiuml.acorda

import android.Manifest
import android.os.Build
import androidx.activity.compose.BackHandler
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.imePadding
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.selection.selectable
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.Delete
import androidx.compose.material.icons.filled.Lock
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.FilterChip
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.RadioButton
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Surface
import androidx.compose.material3.Switch
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.material3.TimePicker
import androidx.compose.material3.TopAppBar
import androidx.compose.material3.rememberTimePickerState
import androidx.compose.runtime.Composable
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
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import br.axiuml.acorda.nucleo.Alarme
import br.axiuml.acorda.nucleo.Calendario
import br.axiuml.acorda.nucleo.Dificuldade
import br.axiuml.acorda.nucleo.Tarefa
import br.axiuml.acorda.nucleo.TipoTarefa

private enum class Alvo { DESLIGAR, CONFIRMAR }

@Composable
fun TelaEditor(id: Long?, aoVoltar: () -> Unit) {
    val ctx = LocalContext.current
    val original = remember(id) { id?.let { Armazem.alarme(ctx, it) } }
    val inicial = remember(id) { original ?: Alarme(id = 0, hora = 6, minuto = 30) }
    val janela = remember { Armazem.config(ctx).janelaMin }

    val horario = rememberTimePickerState(initialHour = inicial.hora, initialMinute = inicial.minuto, is24Hour = true)
    var dias by remember { mutableStateOf(inicial.dias) }
    var rotulo by remember { mutableStateOf(inicial.rotulo) }
    var desligar by remember { mutableStateOf(inicial.desligar) }
    var confirmar by remember { mutableStateOf(inicial.confirmar) }
    var prazo by remember { mutableIntStateOf(inicial.prazoConfirmarMin) }
    var vibrar by remember { mutableStateOf(inicial.vibrar) }

    var lendo by remember { mutableStateOf<Alvo?>(null) }
    var erro by remember { mutableStateOf<String?>(null) }
    var perguntarTrava by remember { mutableStateOf<Alarme?>(null) }
    var perguntarApagar by remember { mutableStateOf(false) }

    // Abriu fora da janela, mas o tempo passou enquanto editava? Não deixa salvar.
    val travado = id != null && Trava.de(ctx, id).travado
    if (travado) {
        Travado(aoVoltar)
        return
    }

    lendo?.let { alvo ->
        CadastroCodigo(
            aoLer = { codigo ->
                when (alvo) {
                    Alvo.DESLIGAR -> desligar = desligar.copy(codigo = codigo)
                    Alvo.CONFIRMAR -> confirmar = confirmar?.copy(codigo = codigo)
                }
                lendo = null
            },
            aoCancelar = { lendo = null },
        )
        return
    }

    fun montar() = Alarme(
        id = original?.id ?: 0,
        hora = horario.hour,
        minuto = horario.minute,
        dias = dias,
        ativo = true,
        rotulo = rotulo.trim(),
        desligar = desligar,
        confirmar = confirmar,
        prazoConfirmarMin = prazo,
        vibrar = vibrar,
    )

    fun gravar(a: Alarme) {
        if (id != null && Trava.de(ctx, id).travado) {
            erro = "Travou enquanto você editava: agora falta menos de $janela min para ele tocar."
            return
        }
        val final = if (a.id == 0L) a.copy(id = Armazem.novoId(ctx)) else a
        Armazem.salvarAlarme(ctx, final)
        Agenda.reagendarTudo(ctx)
        aoVoltar()
    }

    val salvar: () -> Unit = {
        val a = montar()
        when {
            !a.desligar.pronta -> erro = "Cadastre o código que vai desligar o alarme (ou escolha outra tarefa)."
            a.confirmar?.pronta == false -> erro = "Cadastre o código da confirmação (ou escolha outra tarefa)."
            nasceTravado(a, janela) -> perguntarTrava = a
            else -> gravar(a)
        }
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text(if (original == null) "Novo alarme" else "Editar alarme") },
                navigationIcon = { IconButton(onClick = aoVoltar) { Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = "Voltar") } },
                actions = { TextButton(onClick = salvar) { Text("Salvar", fontWeight = FontWeight.Bold) } },
            )
        },
    ) { pad ->
        Column(
            Modifier
                .padding(pad)
                .imePadding()
                .verticalScroll(rememberScrollState())
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp),
        ) {
            Box(Modifier.fillMaxWidth(), contentAlignment = Alignment.Center) { TimePicker(state = horario) }

            Secao("Dias")
            Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                for (d in 1..7) {
                    val marcado = d in dias
                    Surface(
                        shape = CircleShape,
                        color = if (marcado) MaterialTheme.colorScheme.primary else MaterialTheme.colorScheme.surfaceVariant,
                        contentColor = if (marcado) MaterialTheme.colorScheme.onPrimary else MaterialTheme.colorScheme.onSurfaceVariant,
                        onClick = { dias = if (marcado) dias - d else dias + d },
                        modifier = Modifier.size(42.dp),
                    ) {
                        Box(contentAlignment = Alignment.Center) { Text(Calendario.LETRAS[d - 1], fontWeight = FontWeight.Bold) }
                    }
                }
            }
            Text(
                if (dias.isEmpty()) "Nenhum dia marcado: toca uma vez só." else "Repete: ${Calendario.descreverDias(dias)}.",
                style = MaterialTheme.typography.bodySmall,
            )

            OutlinedTextField(
                value = rotulo,
                onValueChange = { rotulo = it.take(40) },
                label = { Text("Nome (opcional)") },
                singleLine = true,
                modifier = Modifier.fillMaxWidth(),
            )

            HorizontalDivider()
            Secao("Para DESLIGAR o som")
            Text("O alarme toca sem parar, no volume máximo, até isto ser feito.", style = MaterialTheme.typography.bodySmall)
            EditorTarefa(desligar, aoMudar = { desligar = it }, aoCadastrarCodigo = { lendo = Alvo.DESLIGAR })

            HorizontalDivider()
            Row(verticalAlignment = Alignment.CenterVertically) {
                Column(Modifier.weight(1f)) {
                    Secao("Para NÃO TOCAR DE NOVO")
                    Text(
                        "Depois de desligar, você tem um prazo para fazer uma segunda tarefa. Se não fizer, ele volta a tocar.",
                        style = MaterialTheme.typography.bodySmall,
                    )
                }
                Switch(
                    checked = confirmar != null,
                    onCheckedChange = { liga -> confirmar = if (liga) Tarefa.padrao(TipoTarefa.PASSOS) else null },
                )
            }
            confirmar?.let { c ->
                EditorTarefa(c, aoMudar = { confirmar = it }, aoCadastrarCodigo = { lendo = Alvo.CONFIRMAR })
                Contador("Prazo para fazer", prazo, 1..60, sufixo = " min") { prazo = it }
            }

            HorizontalDivider()
            Row(verticalAlignment = Alignment.CenterVertically) {
                Text("Vibrar também", Modifier.weight(1f), style = MaterialTheme.typography.bodyLarge)
                Switch(checked = vibrar, onCheckedChange = { vibrar = it })
            }

            Card(Modifier.fillMaxWidth()) {
                Row(Modifier.padding(12.dp), verticalAlignment = Alignment.CenterVertically) {
                    Icon(Icons.Default.Lock, contentDescription = null, tint = MaterialTheme.colorScheme.primary)
                    Text(
                        "A partir de $janela min antes de tocar, este alarme trava: não dá para desligar, mudar nem apagar.",
                        Modifier.padding(start = 12.dp),
                        style = MaterialTheme.typography.bodySmall,
                    )
                }
            }

            Button(onClick = salvar, modifier = Modifier.fillMaxWidth().height(52.dp)) { Text("Salvar") }
            if (original != null) {
                OutlinedButton(onClick = { perguntarApagar = true }, modifier = Modifier.fillMaxWidth()) {
                    Icon(Icons.Default.Delete, contentDescription = null)
                    Text("Apagar alarme", Modifier.padding(start = 8.dp))
                }
            }
            Spacer(Modifier.height(24.dp))
        }
    }

    erro?.let {
        AlertDialog(
            onDismissRequest = { erro = null },
            title = { Text("Não deu para salvar") },
            text = { Text(it) },
            confirmButton = { TextButton(onClick = { erro = null }) { Text("Ok") } },
        )
    }
    perguntarTrava?.let { a ->
        AvisoNasceTravado(
            alarme = a,
            janelaMin = janela,
            aoConfirmar = {
                perguntarTrava = null
                gravar(a)
            },
            aoCancelar = { perguntarTrava = null },
        )
    }
    if (perguntarApagar && original != null) {
        AlertDialog(
            onDismissRequest = { perguntarApagar = false },
            title = { Text("Apagar o alarme das ${original.horario}?") },
            confirmButton = {
                TextButton(onClick = {
                    perguntarApagar = false
                    if (Trava.de(ctx, original.id).travado) {
                        erro = "Travado: falta menos de $janela min para ele tocar."
                    } else {
                        Armazem.removerAlarme(ctx, original.id)
                        Agenda.reagendarTudo(ctx)
                        aoVoltar()
                    }
                }) { Text("Apagar") }
            },
            dismissButton = { TextButton(onClick = { perguntarApagar = false }) { Text("Cancelar") } },
        )
    }
}

@Composable
private fun Secao(titulo: String) {
    Text(titulo, style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold, color = MaterialTheme.colorScheme.primary)
}

@Composable
private fun EditorTarefa(tarefa: Tarefa, aoMudar: (Tarefa) -> Unit, aoCadastrarCodigo: () -> Unit) {
    val ctx = LocalContext.current
    val pedirPassos = rememberLauncherForActivityResult(ActivityResultContracts.RequestPermission()) {}

    Column(verticalArrangement = Arrangement.spacedBy(2.dp)) {
        for (tipo in TipoTarefa.entries) {
            val escolhido = tarefa.tipo == tipo
            Row(
                Modifier
                    .fillMaxWidth()
                    .selectable(
                        selected = escolhido,
                        role = Role.RadioButton,
                        onClick = {
                            if (!escolhido) {
                                aoMudar(Tarefa.padrao(tipo))
                                if (tipo == TipoTarefa.PASSOS && Build.VERSION.SDK_INT >= 29 &&
                                    !Blindagem.tem(ctx, Manifest.permission.ACTIVITY_RECOGNITION)
                                ) {
                                    pedirPassos.launch(Manifest.permission.ACTIVITY_RECOGNITION)
                                }
                            }
                        },
                    )
                    .padding(vertical = 4.dp),
                verticalAlignment = Alignment.CenterVertically,
            ) {
                RadioButton(selected = escolhido, onClick = null)
                Column(Modifier.padding(start = 8.dp)) {
                    Text(tipo.titulo, style = MaterialTheme.typography.bodyLarge)
                    Text(tipo.explicacao, style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
                }
            }
        }

        Surface(
            shape = RoundedCornerShape(12.dp),
            border = BorderStroke(1.dp, MaterialTheme.colorScheme.outlineVariant),
            modifier = Modifier.fillMaxWidth().padding(top = 8.dp),
        ) {
            Column(Modifier.padding(12.dp)) {
                when (tarefa.tipo) {
                    TipoTarefa.CONTAS -> {
                        Contador("Quantas contas", tarefa.quantidade, Tarefa.limites(tarefa.tipo)) {
                            aoMudar(tarefa.copy(quantidade = it))
                        }
                        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                            for (d in Dificuldade.entries) {
                                FilterChip(
                                    selected = tarefa.dificuldade == d,
                                    onClick = { aoMudar(tarefa.copy(dificuldade = d)) },
                                    label = { Text(d.titulo) },
                                )
                            }
                        }
                        Text(
                            when (tarefa.dificuldade) {
                                Dificuldade.FACIL -> "Ex.: 27 + 38"
                                Dificuldade.MEDIO -> "Ex.: (17 × 6) + 45"
                                Dificuldade.DIFICIL -> "Ex.: (23 × 7) + (36 × 8)"
                            },
                            style = MaterialTheme.typography.bodySmall,
                        )
                    }
                    TipoTarefa.FRASE -> Contador("Quantas frases", tarefa.quantidade, Tarefa.limites(tarefa.tipo)) {
                        aoMudar(tarefa.copy(quantidade = it))
                    }
                    TipoTarefa.SACUDIR -> Contador(
                        "Quantas sacudidas", tarefa.quantidade, Tarefa.limites(tarefa.tipo), Tarefa.passo(tarefa.tipo),
                    ) { aoMudar(tarefa.copy(quantidade = it)) }
                    TipoTarefa.PASSOS -> Contador(
                        "Quantos passos", tarefa.quantidade, Tarefa.limites(tarefa.tipo), Tarefa.passo(tarefa.tipo),
                    ) { aoMudar(tarefa.copy(quantidade = it)) }
                    TipoTarefa.CODIGO -> {
                        val codigo = tarefa.codigo
                        Text(
                            if (codigo == null) "Nenhum código cadastrado ainda." else "Código cadastrado: ${codigo.take(30)}",
                            style = MaterialTheme.typography.bodyMedium,
                            fontWeight = FontWeight.Bold,
                            color = if (codigo == null) MaterialTheme.colorScheme.error else MaterialTheme.colorScheme.onSurface,
                        )
                        Text(
                            "Dica: o código de barras de algo que fica longe da cama — a pasta de dente no banheiro, " +
                                "o pacote de café na cozinha. Ou imprima um QR e cole na parede.",
                            style = MaterialTheme.typography.bodySmall,
                        )
                        Button(onClick = aoCadastrarCodigo, modifier = Modifier.padding(top = 8.dp)) {
                            Text(if (codigo == null) "Escanear e cadastrar" else "Trocar código")
                        }
                    }
                }
            }
        }
    }
}

@Composable
private fun CadastroCodigo(aoLer: (String) -> Unit, aoCancelar: () -> Unit) {
    val ctx = LocalContext.current
    var temCamera by remember { mutableStateOf(Blindagem.tem(ctx, Manifest.permission.CAMERA)) }
    val pedir = rememberLauncherForActivityResult(ActivityResultContracts.RequestPermission()) { temCamera = it }
    var lido by remember { mutableStateOf<String?>(null) }
    BackHandler(onBack = aoCancelar)

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Cadastrar código") },
                navigationIcon = { IconButton(onClick = aoCancelar) { Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = "Voltar") } },
            )
        },
    ) { pad ->
        Column(
            Modifier.padding(pad).padding(16.dp).fillMaxSize(),
            verticalArrangement = Arrangement.spacedBy(12.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
        ) {
            Text(
                "Aponte para o código de barras ou QR que vai ficar longe da cama. Na hora do alarme, você vai ter que ir até ele.",
                textAlign = TextAlign.Center,
            )
            val atual = lido
            if (atual == null) {
                if (temCamera) {
                    LeitorCodigo(Modifier.fillMaxWidth().height(360.dp)) { if (lido == null) lido = it }
                } else {
                    Button(onClick = { pedir.launch(Manifest.permission.CAMERA) }) { Text("Permitir a câmera") }
                }
            } else {
                Text("Lido:", style = MaterialTheme.typography.labelLarge)
                Text(atual, style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold, textAlign = TextAlign.Center)
                Button(onClick = { aoLer(atual) }, modifier = Modifier.fillMaxWidth()) { Text("Usar este código") }
                OutlinedButton(onClick = { lido = null }, modifier = Modifier.fillMaxWidth()) { Text("Ler outro") }
            }
        }
    }
}

@Composable
private fun Travado(aoVoltar: () -> Unit) {
    BackHandler(onBack = aoVoltar)
    Column(
        Modifier.fillMaxSize().padding(32.dp),
        verticalArrangement = Arrangement.Center,
        horizontalAlignment = Alignment.CenterHorizontally,
    ) {
        Icon(Icons.Default.Lock, contentDescription = null, modifier = Modifier.size(56.dp), tint = MaterialTheme.colorScheme.primary)
        Text("Travado", style = MaterialTheme.typography.headlineMedium, fontWeight = FontWeight.Bold)
        Text(
            "Falta pouco para este alarme tocar. Agora ele só destrava depois que tocar e você fizer as tarefas.",
            textAlign = TextAlign.Center,
            modifier = Modifier.padding(vertical = 12.dp),
        )
        Button(onClick = aoVoltar) { Text("Voltar") }
    }
}
