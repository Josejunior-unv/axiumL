// EP 08 — Pixel + API de Conversões: sem dados o algoritmo otimiza no escuro
window.VIDEO = {
  ep: 8,
  slug: "pixel-e-api-de-conversoes",
  title: "O algoritmo está cego?",
  theme: { a1: "#2bc46b", a2: "#ffd23f", bg: "yellow" },
  build(E) {
    const { tl } = E;

    // 1 — gancho
    const s1 = E.scene(0, 3.6);
    const c1 = E.el(s1, "center");
    const eyeWrap = E.el(c1, "", "", { position: "relative", width: "260px", height: "260px", marginBottom: "40px" });
    const eye = E.icon("eye", 260, "#17171c", 2.4, "#fff"); eyeWrap.appendChild(eye);
    const slash = E.el(eyeWrap, "abs", "", { left: "-10px", right: "-10px", top: "124px", height: "14px", borderRadius: "9px", background: "#ff5e5b",
      border: "4px solid #17171c", rotate: "-35deg", transformOrigin: "left" });
    E.draw(eye, 0.05, 0.6);
    tl.fromTo(slash, { scaleX: 0 }, { scaleX: 1, duration: 0.3, ease: "expo.out" }, 0.9);
    E.punch(0.9, { amp: 16, flash: 0.3, cue: "glitch" });
    const tx = E.text(c1, "SEU ALGORITMO\nESTÁ [g-red:CEGO]?", "t t-l");
    E.wordsIn(tx, 0.3, { stagger: 0.08 });
    E.glitch(tx.words[3], 1.0);

    // 2 — pixel sozinho x pixel + CAPI
    const s2 = E.scene(3.6, 16.6);
    const t2 = E.text(s2, "SÓ O *PIXEL*", "t t-m", { position: "absolute", top: "320px", left: 0, right: 0, textAlign: "center" });
    E.wordsIn(t2, 3.7);
    const node = (x, y, ic, lb, grad) => {
      const n = E.el(s2, "abs", "", { left: x - 80 + "px", top: y - 80 + "px", width: "160px", display: "flex", flexDirection: "column", alignItems: "center" });
      const b = E.el(n, "badge", "", { width: "160px", height: "160px", borderRadius: "48px", background: grad });
      b.appendChild(E.icon(ic, 86));
      E.el(n, "", lb, { fontFamily: "Inter", fontWeight: 800, fontSize: "34px", marginTop: "16px", whiteSpace: "nowrap" });
      return n;
    };
    const site = node(190, 720, "globe", "Navegador", "#3da5ff");
    const meta = node(890, 900, "brain", "Meta", "#ffd23f");
    E.in([site, meta], 4.0, { from: "pop", stagger: 0.15, cue: "pop" });
    // escudo de bloqueio
    const wall = E.el(s2, "abs", "", { left: "500px", top: "640px", width: "90px", height: "300px", borderRadius: "30px",
      background: "#ff5e5b", border: "5px solid #17171c", boxShadow: "8px 8px 0 #17171c",
      display: "flex", alignItems: "center", justifyContent: "center" });
    wall.appendChild(E.icon("shield", 60, "#17171c", 2.6, "#fff"));
    const wl = E.el(s2, "abs p", "Bloqueador, iOS,<br>cookies", { left: "380px", width: "330px", top: "548px", textAlign: "center", fontSize: "32px", color: "#17171c", fontWeight: 800, lineHeight: 1.15 });
    E.in([wall, wl], 4.5, { from: "down", cue: "hit", vol: 0.6 });
    // pacotes do pixel
    const r = E.rng(5);
    const evs = ["Compra", "Lead", "Carrinho", "Compra", "Visita", "Lead", "Compra", "Carrinho"];
    evs.forEach((ev, i) => {
      const pass = i % 3 === 1;
      const p = E.el(s2, "abs chip", ev, { left: "250px", top: "700px", fontSize: "26px", padding: "8px 18px", borderWidth: "3px", boxShadow: "4px 4px 0 #17171c", opacity: 0 });
      const t = 5.0 + i * 0.42;
      tl.to(p, { opacity: 1, duration: 0.1 }, t);
      if (pass) {
        tl.to(p, { left: 760, top: 880, duration: 0.9, ease: "power1.inOut" }, t);
        tl.to(p, { opacity: 0, scale: 0.4, duration: 0.2 }, t + 0.9);
        E.cue("pop", t + 0.9, 0.35);
      } else {
        tl.to(p, { left: 390, top: 680 + r() * 60, duration: 0.45, ease: "power1.in" }, t);
        tl.to(p, { scale: 1.4, opacity: 0, background: "#ff5e5b", rotate: 25, duration: 0.25 }, t + 0.45);
        E.cue("error", t + 0.45, 0.25);
      }
    });
    const lost = E.el(s2, "abs", "", { left: 0, right: 0, top: "1080px", textAlign: "center" });
    const lc = E.el(lost, "chip", `${E.icon("x", 36, "#ff5e5b", 3.4).outerHTML}<span>Parte das vendas <b>nunca chega</b> na Meta</span>`, { fontSize: "36px" });
    E.in(lc, 8.4, { from: "pop", cue: "pop" });
    E.bgTo(8.2, "coral", 0.3);

    // entra a API de Conversões
    tl.to(lost, { opacity: 0, duration: 0.3 }, 10.0);
    tl.to(t2, { opacity: 0, y: -40, duration: 0.3 }, 10.0);
    const t2b = E.text(s2, "+ *API DE CONVERSÕES*", "t t-s", { position: "absolute", top: "330px", left: 0, right: 0, textAlign: "center", fontSize: "76px" });
    E.wordsIn(t2b, 10.2);
    E.bgTo(10.2, "green");
    const srv = node(190, 1180, "server", "Seu servidor", "#b8f35a");
    E.in(srv, 10.5, { from: "pop", cue: "pop" });
    const pathSvg = E.el(s2, "abs", `<svg width="1080" height="1920" viewBox="0 0 1080 1920"><path class="pp" d="M270 1180 C 520 1200, 700 1150, 820 960" fill="none" stroke="#17171c" stroke-width="10" stroke-dasharray="2 22" stroke-linecap="round"/></svg>`, { left: 0, top: 0 });
    E.draw(pathSvg.querySelector(".pp"), 10.8, 0.6);
    E.cue("whoosh", 10.8, 0.6);
    for (let i = 0; i < 7; i++) {
      const p = E.el(s2, "abs chip", evs[i], { left: "0px", top: "0px", fontSize: "26px", padding: "8px 18px", background: "#b8f35a", borderWidth: "3px", boxShadow: "4px 4px 0 #17171c", opacity: 0 });
      const t = 11.3 + i * 0.4;
      tl.to(p, { opacity: 1, duration: 0.1 }, t);
      tl.fromTo(p, { x: 0, y: 0 }, { motionPath: { path: pathSvg.querySelector(".pp"), align: pathSvg.querySelector(".pp"), alignOrigin: [0.5, 0.5] },
        duration: 1.0, ease: "power1.inOut", immediateRender: false }, t);
      tl.to(p, { opacity: 0, scale: 0.4, duration: 0.2 }, t + 1.0);
      E.cue("pop", t + 1.0, 0.4);
    }
    E.pulse(meta, 14.5, 1.15, 0.4);
    E.cue("ding", 14.5, 0.7);
    const ok = E.el(s2, "abs", "", { left: 0, right: 0, top: "1440px", textAlign: "center" });
    const okc = E.el(ok, "chip", `${E.icon("check", 36, "#1a9e55", 3.6).outerHTML}<span>Do servidor, <b>sem bloqueio</b> no caminho</span>`, { fontSize: "36px" });
    E.in(okc, 14.6, { from: "pop", cue: "pop" });

    // 3 — cadeia de efeito
    const s3 = E.scene(16.6, 22.8);
    E.bgTo(16.5, "sky");
    const t3 = E.text(s3, "PIXEL + CAPI\n*JUNTOS*", "t t-m", { position: "absolute", top: "320px", left: 0, right: 0, textAlign: "center" });
    E.wordsIn(t3, 16.7);
    const chain = [["bolt", "Mais sinal de conversão"], ["brain", "Algoritmo aprende melhor"], ["target", "Entrega pra quem compra"], ["down", "Custo por venda tende a cair"]];
    chain.forEach(([ic, lb], i) => {
      const y = 600 + i * 230;
      const row = E.el(s3, "card abs", "", { left: "120px", right: "120px", top: y + "px", padding: "26px 34px", display: "flex", alignItems: "center", gap: "28px" });
      const b = E.el(row, "badge", "", { flex: "none", width: "100px", height: "100px", borderRadius: "30px",
        background: ["#ffd23f", "#3da5ff", "#ff8a3d", "#b8f35a"][i] });
      b.appendChild(E.icon(ic, 56));
      E.el(row, "", lb, { fontFamily: "Inter", fontWeight: 800, fontSize: "42px" });
      const t = 17.2 + i * 0.8;
      E.in(row, t, { from: "left", cue: "whoosh", vol: 0.6 });
      if (i > 0) {
        const ar = E.el(s3, "abs", "", { left: "520px", top: y - 52 + "px" });
        ar.appendChild(E.icon("play", 40, "#17171c", 2.4, "#17171c"));
        ar.style.rotate = "90deg";
        E.in(ar, t - 0.15, { from: "pop", dur: 0.3 });
      }
    });
    E.punch(19.8, { amp: 12, flash: 0.25, cue: "cash" });

    // 4 — dica técnica
    const s4 = E.scene(22.8, 27.0);
    E.bgTo(22.7, "orange");
    const c4 = E.el(s4, "center");
    const kk = E.el(c4, "kicker", `<span class="dot"></span>Dica de ouro`, { marginBottom: "50px" });
    E.in(kk, 22.9, { from: "pop", cue: "pop" });
    const a4 = E.text(c4, "USE O MESMO\n*EVENT_ID*\nNOS DOIS", "t t-l");
    E.wordsIn(a4, 23.0, { stagger: 0.08 });
    E.punch(23.5, { amp: 12, flash: 0.2 });
    const b4 = E.el(c4, "p", "Assim a Meta junta os eventos repetidos e <b>não conta a mesma venda duas vezes</b>.", { marginTop: "50px", maxWidth: "860px", fontSize: "44px" });
    E.in(b4, 24.2, { from: "up" });

    E.cta(27.0, 31.6, { text: "SALVA E MANDA\nPRO *DEV*", sub: "ou pra quem cuida do [b:seu site]", next: "EP 09: Google ou Meta Ads?" });
  },
};
