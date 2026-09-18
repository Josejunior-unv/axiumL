/**
 * Guarda as respostas da pesquisa no banco da própria Vercel.
 *
 * Como ligar (uma vez só, tudo dentro da Vercel):
 *  1. No painel do projeto: Storage -> Create Database -> Upstash for Redis
 *  2. Conecte ao projeto. A Vercel injeta KV_REST_API_URL e KV_REST_API_TOKEN
 *     sozinha, você não copia chave nenhuma.
 *  3. Settings -> Environment Variables -> CHAVE_LEITURA = uma senha sua.
 *     É ela que libera a leitura das respostas; sem ela ninguém baixa nada.
 *  4. Redeploy.
 *
 * O app descobre sozinho que ficou pronto e passa a enviar para cá.
 */

const URL_KV = process.env.KV_REST_API_URL || process.env.UPSTASH_REDIS_REST_URL;
const TOKEN_KV = process.env.KV_REST_API_TOKEN || process.env.UPSTASH_REDIS_REST_TOKEN;
const LISTA = "pesquisa:linhas";
const CABECALHO = "pesquisa:cabecalho";
const IDS = "pesquisa:ids";

const pronto = () => !!(URL_KV && TOKEN_KV);

async function redis(comando) {
  const r = await fetch(URL_KV, {
    method: "POST",
    headers: { Authorization: "Bearer " + TOKEN_KV, "Content-Type": "application/json" },
    body: JSON.stringify(comando)
  });
  const d = await r.json();
  if (d.error) throw new Error(d.error);
  return d.result;
}

module.exports = async (req, res) => {
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Cache-Control", "no-store");

  if (req.method === "OPTIONS") return res.status(204).end();

  try {
    if (req.method === "GET") {
      const q = req.query || {};
      // o app pergunta primeiro se já dá para usar
      if (q.status) return res.json({ ok: true, pronto: pronto() });
      if (!pronto()) return res.json({ ok: false, erro: "banco ainda não conectado" });

      const esperada = process.env.CHAVE_LEITURA;
      if (!esperada) return res.json({ ok: false, erro: "defina CHAVE_LEITURA nas variáveis de ambiente" });
      if (q.chave !== esperada) return res.json({ ok: false, erro: "chave inválida" });

      const cab = await redis(["GET", CABECALHO]);
      const linhas = await redis(["LRANGE", LISTA, "0", "-1"]);
      const valores = [];
      if (cab) valores.push(JSON.parse(cab));
      (linhas || []).forEach(l => { try { valores.push(JSON.parse(l)); } catch (e) {} });
      return res.json({ ok: true, valores });
    }

    if (req.method === "POST") {
      if (!pronto()) return res.json({ ok: false, erro: "banco ainda não conectado" });
      let corpo = req.body;
      if (typeof corpo === "string") corpo = JSON.parse(corpo);
      if (!corpo || !Array.isArray(corpo.linha) || !Array.isArray(corpo.cabecalho))
        return res.json({ ok: false, erro: "formato inesperado" });

      const id = String(corpo.linha[corpo.linha.length - 1] || "");
      // SADD devolve 0 quando o id já estava lá: é reenvio, não grava de novo
      if (id) {
        const novo = await redis(["SADD", IDS, id]);
        if (novo === 0) return res.json({ ok: true, repetida: true });
      }
      await redis(["SET", CABECALHO, JSON.stringify(corpo.cabecalho)]);
      await redis(["RPUSH", LISTA, JSON.stringify(corpo.linha)]);
      return res.json({ ok: true });
    }

    return res.status(405).json({ ok: false, erro: "método não suportado" });
  } catch (erro) {
    return res.status(500).json({ ok: false, erro: String(erro.message || erro) });
  }
};
