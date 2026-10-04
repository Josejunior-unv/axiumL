package br.axiuml.acorda

import android.Manifest
import android.content.Context
import android.hardware.Sensor
import android.hardware.SensorEvent
import android.hardware.SensorEventListener
import android.hardware.SensorManager
import android.os.Build
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardActions
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.LinearProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.DisposableEffect
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableLongStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberUpdatedState
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.focus.FocusRequester
import androidx.compose.ui.focus.focusRequester
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.ImeAction
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.ui.viewinterop.AndroidView
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.LifecycleEventObserver
import androidx.lifecycle.compose.LocalLifecycleOwner
import br.axiuml.acorda.nucleo.Codigos
import br.axiuml.acorda.nucleo.Contas
import br.axiuml.acorda.nucleo.DetectorPassos
import br.axiuml.acorda.nucleo.DetectorSacudida
import br.axiuml.acorda.nucleo.Frases
import br.axiuml.acorda.nucleo.Regras
import br.axiuml.acorda.nucleo.Tarefa
import br.axiuml.acorda.nucleo.TipoTarefa
import com.google.zxing.ResultPoint
import com.journeyapps.barcodescanner.BarcodeCallback
import com.journeyapps.barcodescanner.BarcodeResult
import com.journeyapps.barcodescanner.BarcodeView
import com.journeyapps.barcodescanner.DefaultDecoderFactory
import kotlin.random.Random

/**
 * A tarefa a cumprir. [aoConcluir] é chamado uma única vez, quando ela termina.
 * Câmera e sensor podem falhar: nesses casos, depois de alguns minutos aparece uma alternativa
 * trabalhosa (contas difíceis), para ninguém ficar preso num alarme que não desliga nunca.
 */
@Composable
fun TarefaUI(tarefa: Tarefa, aoConcluir: () -> Unit) {
    var feito by rememberSaveable { mutableStateOf(false) }
    val concluir: () -> Unit = {
        if (!feito) {
            feito = true
            aoConcluir()
        }
    }
    var alternativa by rememberSaveable { mutableStateOf(false) }
    val podeFalhar = tarefa.tipo == TipoTarefa.CODIGO || tarefa.tipo == TipoTarefa.PASSOS ||
        tarefa.tipo == TipoTarefa.SACUDIR

    Column(horizontalAlignment = Alignment.CenterHorizontally, verticalArrangement = Arrangement.spacedBy(12.dp)) {
        if (alternativa) {
            Text(
                "Alternativa: ${Regras.ALTERNATIVA.descricao().lowercase()}",
                style = MaterialTheme.typography.titleMedium,
                textAlign = TextAlign.Center,
            )
            TarefaContas(Regras.ALTERNATIVA, concluir)
        } else {
            when (tarefa.tipo) {
                TipoTarefa.CONTAS -> TarefaContas(tarefa, concluir)
                TipoTarefa.FRASE -> TarefaFrase(tarefa, concluir)
                TipoTarefa.SACUDIR -> TarefaSensor(tarefa, concluir, passos = false)
                TipoTarefa.PASSOS -> TarefaSensor(tarefa, concluir, passos = true)
                TipoTarefa.CODIGO -> TarefaCodigo(tarefa, concluir)
            }
            if (podeFalhar) {
                val inicio = rememberSaveable { System.currentTimeMillis() }
                val agora by agoraQueAnda()
                val falta = Regras.ESPERA_ALTERNATIVA_MS - (agora - inicio)
                if (falta <= 0) {
                    TextButton(onClick = { alternativa = true }) {
                        Text(if (tarefa.tipo == TipoTarefa.CODIGO) "Não consigo escanear" else "O sensor não está contando")
                    }
                } else {
                    Text(
                        "Se não funcionar, em ${(falta / 1000 + 59) / 60} min aparece uma alternativa (mais difícil).",
                        style = MaterialTheme.typography.bodySmall,
                        textAlign = TextAlign.Center,
                    )
                }
            }
        }
    }
}

@Composable
fun TarefaContas(tarefa: Tarefa, aoConcluir: () -> Unit) {
    var feitas by rememberSaveable { mutableIntStateOf(0) }
    var semente by rememberSaveable { mutableLongStateOf(Random.nextLong()) }
    val conta = remember(semente) { Contas.gerar(tarefa.dificuldade, Random(semente)) }
    var resposta by rememberSaveable(semente) { mutableStateOf("") }
    var errou by rememberSaveable { mutableStateOf(false) }
    val foco = remember { FocusRequester() }

    val conferir: () -> Unit = {
        if (resposta.toIntOrNull() == conta.resposta) {
            errou = false
            feitas++
            if (feitas >= tarefa.quantidade) aoConcluir() else semente = Random.nextLong()
        } else if (resposta.isNotEmpty()) {
            errou = true
            semente = Random.nextLong()
        }
    }

    LaunchedEffect(semente) { runCatching { foco.requestFocus() } }

    Text("Conta ${minOf(feitas + 1, tarefa.quantidade)} de ${tarefa.quantidade}", style = MaterialTheme.typography.labelLarge)
    LinearProgressIndicator(progress = { feitas / tarefa.quantidade.toFloat() }, modifier = Modifier.fillMaxWidth())
    Text(
        "${conta.texto} = ?",
        fontSize = 34.sp,
        fontWeight = FontWeight.Bold,
        textAlign = TextAlign.Center,
    )
    OutlinedTextField(
        value = resposta,
        onValueChange = { novo ->
            resposta = novo.filter { it.isDigit() }.take(6)
            errou = false
        },
        label = { Text("Resposta") },
        singleLine = true,
        isError = errou,
        supportingText = { if (errou) Text("Errou. Essa conta foi trocada por outra.") },
        keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.NumberPassword, imeAction = ImeAction.Done),
        keyboardActions = KeyboardActions(onDone = { conferir() }),
        textStyle = MaterialTheme.typography.headlineSmall,
        modifier = Modifier.fillMaxWidth().focusRequester(foco),
    )
    Button(onClick = conferir, modifier = Modifier.fillMaxWidth().height(52.dp)) { Text("Conferir") }
}

@Composable
fun TarefaFrase(tarefa: Tarefa, aoConcluir: () -> Unit) {
    val semente = rememberSaveable { Random.nextLong() }
    val frases = remember(semente) { Frases.sortear(Random(semente), tarefa.quantidade) }
    var feitas by rememberSaveable { mutableIntStateOf(0) }
    val alvo = frases[minOf(feitas, frases.size - 1)]
    var texto by rememberSaveable(feitas) { mutableStateOf("") }
    val foco = remember { FocusRequester() }
    LaunchedEffect(feitas) { runCatching { foco.requestFocus() } }

    val total = Frases.normalizar(alvo).length.coerceAtLeast(1)
    val acertos = Frases.acertosNoComeco(texto, alvo)

    Text("Frase ${minOf(feitas + 1, frases.size)} de ${frases.size}", style = MaterialTheme.typography.labelLarge)
    Card(
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.secondaryContainer),
        modifier = Modifier.fillMaxWidth(),
    ) {
        Text(
            alvo,
            Modifier.padding(16.dp),
            style = MaterialTheme.typography.titleLarge,
            color = MaterialTheme.colorScheme.onSecondaryContainer,
        )
    }
    OutlinedTextField(
        value = texto,
        onValueChange = { novo ->
            // Nada de colar: mais de 3 letras de uma vez é recusado.
            if (novo.length - texto.length > 3) return@OutlinedTextField
            texto = novo
            if (Frases.confere(novo, alvo)) {
                if (feitas + 1 >= frases.size) aoConcluir() else feitas++
            }
        },
        label = { Text("Digite a frase acima") },
        isError = texto.isNotEmpty() && acertos < Frases.normalizar(texto).length,
        supportingText = { Text("Acentos, maiúsculas e pontuação não importam.") },
        // Teclado de senha (com o texto visível): sem sugestões nem correção automática.
        keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Password),
        minLines = 2,
        modifier = Modifier.fillMaxWidth().focusRequester(foco),
    )
    LinearProgressIndicator(progress = { acertos / total.toFloat() }, modifier = Modifier.fillMaxWidth())
}

/** Sacudir (acelerômetro) ou andar (sensor de passos, ou acelerômetro se não houver). */
@Composable
fun TarefaSensor(tarefa: Tarefa, aoConcluir: () -> Unit, passos: Boolean) {
    val ctx = LocalContext.current
    var feitas by rememberSaveable { mutableIntStateOf(0) }
    var semSensor by remember { mutableStateOf(false) }
    val concluir by rememberUpdatedState(aoConcluir)

    DisposableEffect(passos) {
        val sm = ctx.getSystemService(SensorManager::class.java)
        val acel = sm?.getDefaultSensor(Sensor.TYPE_ACCELEROMETER)
        val podePassos = Build.VERSION.SDK_INT < 29 || Blindagem.tem(ctx, Manifest.permission.ACTIVITY_RECOGNITION)
        val detectorPassos = if (passos && podePassos) sm?.getDefaultSensor(Sensor.TYPE_STEP_DETECTOR) else null
        val sacudida = DetectorSacudida()
        val passoAcel = DetectorPassos()
        val ouvinte = object : SensorEventListener {
            override fun onSensorChanged(e: SensorEvent) {
                val contou = when {
                    e.sensor.type == Sensor.TYPE_STEP_DETECTOR -> true
                    passos -> passoAcel.amostra(e.values[0], e.values[1], e.values[2], e.timestamp / 1_000_000)
                    else -> sacudida.amostra(e.values[0], e.values[1], e.values[2], e.timestamp / 1_000_000)
                }
                if (contou && feitas < tarefa.quantidade) {
                    feitas++
                    if (feitas >= tarefa.quantidade) concluir()
                }
            }

            override fun onAccuracyChanged(sensor: Sensor?, accuracy: Int) {}
        }
        val sensor = detectorPassos ?: acel
        if (sm == null || sensor == null) {
            semSensor = true
        } else {
            sm.registerListener(ouvinte, sensor, SensorManager.SENSOR_DELAY_GAME)
        }
        onDispose { sm?.unregisterListener(ouvinte) }
    }

    Text(
        if (passos) "Levante e ande pela casa com o celular na mão." else "Sacuda o celular com força.",
        style = MaterialTheme.typography.titleMedium,
        textAlign = TextAlign.Center,
    )
    Text(
        "$feitas / ${tarefa.quantidade}",
        fontSize = 56.sp,
        fontWeight = FontWeight.Bold,
    )
    Text(if (passos) "passos" else "sacudidas", style = MaterialTheme.typography.labelLarge)
    LinearProgressIndicator(progress = { feitas / tarefa.quantidade.toFloat() }, modifier = Modifier.fillMaxWidth())
    if (semSensor) {
        Text(
            "Este celular não tem o sensor necessário. Use a alternativa quando ela aparecer.",
            color = MaterialTheme.colorScheme.error,
            textAlign = TextAlign.Center,
        )
    }
}

@Composable
fun TarefaCodigo(tarefa: Tarefa, aoConcluir: () -> Unit) {
    val ctx = LocalContext.current
    var temCamera by remember { mutableStateOf(Blindagem.tem(ctx, Manifest.permission.CAMERA)) }
    val pedir = rememberLauncherForActivityResult(ActivityResultContracts.RequestPermission()) { temCamera = it }
    var errado by remember { mutableStateOf(false) }

    Text(
        "Vá até o código que você cadastrou e aponte a câmera para ele.",
        style = MaterialTheme.typography.titleMedium,
        textAlign = TextAlign.Center,
    )
    if (temCamera) {
        LeitorCodigo(Modifier.fillMaxWidth().height(320.dp).clip(RoundedCornerShape(16.dp))) { lido ->
            if (Codigos.confere(lido, tarefa.codigo)) aoConcluir() else errado = true
        }
        if (errado) Text("Esse não é o código cadastrado.", color = MaterialTheme.colorScheme.error)
    } else {
        Button(onClick = { pedir.launch(Manifest.permission.CAMERA) }) { Text("Permitir a câmera") }
    }
    Spacer(Modifier.height(4.dp))
}

/** A câmera lendo código de barras ou QR, sem depender do Google Play Services. */
@Composable
fun LeitorCodigo(modifier: Modifier = Modifier, aoLer: (String) -> Unit) {
    val ctx = LocalContext.current
    val dono = LocalLifecycleOwner.current
    val ler by rememberUpdatedState(aoLer)
    val visor = remember { criarVisor(ctx) }

    DisposableEffect(dono) {
        visor.decodeContinuous(object : BarcodeCallback {
            override fun barcodeResult(result: BarcodeResult) {
                result.text?.let { ler(it) }
            }

            override fun possibleResultPoints(resultPoints: MutableList<ResultPoint>) {}
        })
        val obs = LifecycleEventObserver { _, e ->
            when (e) {
                Lifecycle.Event.ON_RESUME -> visor.resume()
                Lifecycle.Event.ON_PAUSE -> visor.pause()
                else -> {}
            }
        }
        dono.lifecycle.addObserver(obs)
        onDispose {
            dono.lifecycle.removeObserver(obs)
            visor.pause()
        }
    }
    AndroidView(factory = { visor }, modifier = modifier)
}

private fun criarVisor(ctx: Context): BarcodeView = BarcodeView(ctx).apply {
    setDecoderFactory(DefaultDecoderFactory())
}
