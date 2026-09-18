/* Service worker do app da pesquisa.
   Estratégia: REDE PRIMEIRO, cache como reserva.
   Assim o app continua funcionando sem internet, mas uma versão nova
   publicada nunca fica presa no aparelho — o erro da versão anterior,
   que servia sempre a cópia guardada e nunca ia checar o servidor. */
const CACHE = "pesquisa-es-v6";
const ESSENCIAIS = [
  "./",
  "./index.html",
  "./manifest.webmanifest",
  "./icones/icone-192.png",
  "./icones/icone-512.png",
  "./icones/icone-maskable-512.png"
];

self.addEventListener("install", evento => {
  evento.waitUntil(
    caches.open(CACHE)
      // um arquivo que falhe não pode derrubar a instalação inteira
      .then(cache => Promise.all(ESSENCIAIS.map(u => cache.add(u).catch(() => {}))))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener("activate", evento => {
  evento.waitUntil(
    caches.keys()
      .then(chaves => Promise.all(chaves.filter(c => c !== CACHE).map(c => caches.delete(c))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", evento => {
  const req = evento.request;
  if (req.method !== "GET") return;

  evento.respondWith(
    fetch(req)
      .then(resposta => {
        if (resposta && (resposta.ok || resposta.type === "opaque")){
          const copia = resposta.clone();
          caches.open(CACHE).then(cache => cache.put(req, copia)).catch(() => {});
        }
        return resposta;
      })
      .catch(() => caches.match(req).then(guardado => {
        if (guardado) return guardado;
        if (req.mode === "navigate") return caches.match("./index.html");
        return new Response("", { status: 504, statusText: "Sem conexão" });
      }))
  );
});
