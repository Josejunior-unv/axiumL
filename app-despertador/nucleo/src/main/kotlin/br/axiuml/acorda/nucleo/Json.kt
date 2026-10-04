package br.axiuml.acorda.nucleo

import org.json.JSONArray
import org.json.JSONObject

/**
 * Converte o modelo para JSON e de volta. Usa org.json, que o Android já traz; campos que
 * faltarem (de versões antigas do app) caem no valor padrão em vez de quebrar.
 */
object Json {
    fun tarefa(t: Tarefa): JSONObject = JSONObject()
        .put("tipo", t.tipo.name)
        .put("quantidade", t.quantidade)
        .put("dificuldade", t.dificuldade.name)
        .put("codigo", t.codigo ?: "")

    fun tarefa(o: JSONObject): Tarefa {
        val tipo = enumOu(o.optString("tipo", ""), TipoTarefa.CONTAS)
        val padrao = Tarefa.padrao(tipo)
        return Tarefa(
            tipo = tipo,
            quantidade = o.optInt("quantidade", padrao.quantidade).coerceIn(Tarefa.limites(tipo)),
            dificuldade = enumOu(o.optString("dificuldade", ""), padrao.dificuldade),
            codigo = o.optString("codigo", "").ifBlank { null },
        )
    }

    fun alarme(a: Alarme): JSONObject = JSONObject()
        .put("id", a.id)
        .put("hora", a.hora)
        .put("minuto", a.minuto)
        .put("dias", JSONArray().apply { a.dias.sorted().forEach { put(it) } })
        .put("ativo", a.ativo)
        .put("rotulo", a.rotulo)
        .put("desligar", tarefa(a.desligar))
        .put("confirmar", a.confirmar?.let { tarefa(it) } ?: JSONObject.NULL)
        .put("prazoConfirmarMin", a.prazoConfirmarMin)
        .put("vibrar", a.vibrar)

    fun alarme(o: JSONObject): Alarme {
        val dias = mutableSetOf<Int>()
        val arr = o.optJSONArray("dias")
        if (arr != null) for (i in 0 until arr.length()) dias += arr.getInt(i)
        return Alarme(
            id = o.getLong("id"),
            hora = o.getInt("hora").coerceIn(0, 23),
            minuto = o.getInt("minuto").coerceIn(0, 59),
            dias = dias.filter { it in 1..7 }.toSet(),
            ativo = o.optBoolean("ativo", true),
            rotulo = o.optString("rotulo", ""),
            desligar = o.optJSONObject("desligar")?.let { tarefa(it) } ?: Tarefa.padrao(TipoTarefa.CONTAS),
            confirmar = o.optJSONObject("confirmar")?.let { tarefa(it) },
            prazoConfirmarMin = o.optInt("prazoConfirmarMin", 10).coerceIn(1, 120),
            vibrar = o.optBoolean("vibrar", true),
        )
    }

    fun alarmes(lista: List<Alarme>): String = JSONArray().apply { lista.forEach { put(alarme(it)) } }.toString()

    fun alarmes(texto: String?): List<Alarme> {
        if (texto.isNullOrBlank()) return emptyList()
        val arr = JSONArray(texto)
        return (0 until arr.length()).map { alarme(arr.getJSONObject(it)) }
    }

    fun sessao(s: Sessao?): String? = s?.let {
        JSONObject()
            .put("alarmeId", it.alarmeId)
            .put("fase", it.fase.name)
            .put("inicio", it.inicio)
            .put("prazo", it.prazo)
            .put("rodada", it.rodada)
            .put("teste", it.teste)
            .toString()
    }

    fun sessao(texto: String?): Sessao? {
        if (texto.isNullOrBlank()) return null
        val o = JSONObject(texto)
        return Sessao(
            alarmeId = o.getLong("alarmeId"),
            fase = enumOu(o.optString("fase", ""), Fase.TOCANDO),
            inicio = o.optLong("inicio", 0),
            prazo = o.optLong("prazo", 0),
            rodada = o.optInt("rodada", 1),
            teste = o.optBoolean("teste", false),
        )
    }

    fun agendamentos(m: Map<Long, Agendamento>): String = JSONArray().apply {
        m.values.forEach {
            put(
                JSONObject()
                    .put("alarmeId", it.alarmeId)
                    .put("quandoWall", it.quandoWall)
                    .put("quandoElapsed", it.quandoElapsed)
                    .put("boot", it.boot),
            )
        }
    }.toString()

    fun agendamentos(texto: String?): Map<Long, Agendamento> {
        if (texto.isNullOrBlank()) return emptyMap()
        val arr = JSONArray(texto)
        return (0 until arr.length()).map { i ->
            val o = arr.getJSONObject(i)
            Agendamento(o.getLong("alarmeId"), o.getLong("quandoWall"), o.getLong("quandoElapsed"), o.optInt("boot", -1))
        }.associateBy { it.alarmeId }
    }

    fun config(c: Config): String = JSONObject()
        .put("janelaMin", c.janelaMin)
        .put("somDoSistema", c.somDoSistema)
        .toString()

    fun config(texto: String?): Config {
        if (texto.isNullOrBlank()) return Config()
        val o = JSONObject(texto)
        return Config(
            janelaMin = o.optInt("janelaMin", 60).coerceIn(0, 24 * 60),
            somDoSistema = o.optBoolean("somDoSistema", false),
        )
    }

    private inline fun <reified E : Enum<E>> enumOu(nome: String, padrao: E): E =
        enumValues<E>().firstOrNull { it.name == nome } ?: padrao
}
