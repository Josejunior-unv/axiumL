package br.axiuml.acorda

import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.widthIn
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Add
import androidx.compose.material3.FilledTonalIconButton
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.runtime.DisposableEffect
import androidx.compose.runtime.State
import androidx.compose.runtime.getValue
import androidx.compose.runtime.produceState
import androidx.compose.runtime.rememberUpdatedState
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.LifecycleEventObserver
import androidx.lifecycle.compose.LocalLifecycleOwner
import kotlinx.coroutines.delay

private val Claro = lightColorScheme(
    primary = Color(0xFF9A4500),
    onPrimary = Color.White,
    primaryContainer = Color(0xFFFFDCC6),
    onPrimaryContainer = Color(0xFF331200),
    secondary = Color(0xFF3F4A8C),
    onSecondary = Color.White,
    secondaryContainer = Color(0xFFDDE1FF),
    onSecondaryContainer = Color(0xFF00105C),
    background = Color(0xFFFFFBF5),
    surface = Color(0xFFFFFBF5),
    surfaceVariant = Color(0xFFF4E4D8),
    onSurfaceVariant = Color(0xFF52443B),
)

private val Escuro = darkColorScheme(
    primary = Color(0xFFFFB685),
    onPrimary = Color(0xFF532200),
    primaryContainer = Color(0xFF763300),
    onPrimaryContainer = Color(0xFFFFDCC6),
    secondary = Color(0xFFB9C3FF),
    onSecondary = Color(0xFF0E1E6F),
    secondaryContainer = Color(0xFF273388),
    onSecondaryContainer = Color(0xFFDDE1FF),
    background = Color(0xFF12131A),
    surface = Color(0xFF12131A),
    surfaceVariant = Color(0xFF2A2C36),
    onSurfaceVariant = Color(0xFFD6C3B6),
)

@Composable
fun TemaAcorda(conteudo: @Composable () -> Unit) {
    MaterialTheme(colorScheme = if (isSystemInDarkTheme()) Escuro else Claro, content = conteudo)
}

/** A hora atual, atualizada a cada [intervaloMs]. */
@Composable
fun agoraQueAnda(intervaloMs: Long = 1_000): State<Long> = produceState(System.currentTimeMillis(), intervaloMs) {
    while (true) {
        value = System.currentTimeMillis()
        delay(intervaloMs)
    }
}

/** Roda [acao] toda vez que a tela volta a aparecer (ex.: depois de conceder uma permissão nas configurações). */
@Composable
fun AoVoltarParaTela(acao: () -> Unit) {
    val dono = LocalLifecycleOwner.current
    val atual by rememberUpdatedState(acao)
    DisposableEffect(dono) {
        val obs = LifecycleEventObserver { _, e -> if (e == Lifecycle.Event.ON_RESUME) atual() }
        dono.lifecycle.addObserver(obs)
        onDispose { dono.lifecycle.removeObserver(obs) }
    }
}

/** − valor + */
@Composable
fun Contador(
    rotulo: String,
    valor: Int,
    faixa: IntRange,
    passo: Int = 1,
    sufixo: String = "",
    habilitado: Boolean = true,
    aoMudar: (Int) -> Unit,
) {
    Row(verticalAlignment = Alignment.CenterVertically, modifier = Modifier.padding(vertical = 4.dp)) {
        Text(rotulo, Modifier.weight(1f), style = MaterialTheme.typography.bodyLarge)
        FilledTonalIconButton(
            onClick = { aoMudar((valor - passo).coerceIn(faixa)) },
            enabled = habilitado && valor > faixa.first,
        ) { Text("−", style = MaterialTheme.typography.titleLarge) }
        Text(
            "$valor$sufixo",
            Modifier.widthIn(min = 72.dp),
            textAlign = TextAlign.Center,
            style = MaterialTheme.typography.titleMedium,
        )
        FilledTonalIconButton(
            onClick = { aoMudar((valor + passo).coerceIn(faixa)) },
            enabled = habilitado && valor < faixa.last,
        ) { Icon(Icons.Default.Add, contentDescription = "Mais") }
    }
}
