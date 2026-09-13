/* Service worker: deixa o app funcionar sem internet depois da primeira abertura. */
const CACHE = "pesquisa-tec-v1";
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
      .then(cache => cache.addAll(ESSENCIAIS))
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
    caches.match(req).then(guardado => {
      if (guardado) return guardado;
      return fetch(req).then(resposta => {
        // guarda também as fontes do Google para uso offline
        if (resposta && (resposta.ok || resposta.type === "opaque")){
          const copia = resposta.clone();
          caches.open(CACHE).then(cache => cache.put(req, copia)).catch(() => {});
        }
        return resposta;
      }).catch(() => {
        if (req.mode === "navigate") return caches.match("./index.html");
        return new Response("", { status: 504, statusText: "Sem conexão" });
      });
    })
  );
});
