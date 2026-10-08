// EP 12 — Teste A/B do jeito certo (narrado, trilha lo-fi)
window.VIDEO = {
  ep: 12,
  slug: "teste-ab-do-jeito-certo",
  title: "Teste A/B do jeito certo",
  music: "lofi",
  theme: { a1: "#3da5ff", a2: "#ffd23f", bg: "sky" },
  narr: [
    { id: "a", text: "Você testou dois anúncios e não sabe qual ganhou?", gap: 0.5 },
    { id: "b", text: "Provavelmente você mudou coisa demais." },
    { id: "c", text: "A regra de ouro do teste A B: muda uma coisa só por vez.", cap: "A regra de ouro do teste A/B: muda uma coisa só por vez." },
    { id: "d", text: "Exemplo prático: mesmo vídeo, mesma oferta, mesmo público. Só o gancho muda.", gap: 0.4 },
    { id: "e", text: "Gancho A: você está jogando dinheiro fora com anúncio." },
    { id: "f", text: "Gancho B: três erros que fazem seu anúncio não vender.", cap: "Gancho B: 3 erros que fazem seu anúncio não vender." },
    { id: "g", text: "Deixa rodar até cada um ter dados suficientes. Nada de decidir no primeiro dia.", gap: 0.4 },
    { id: "h", text: "Resultado do exemplo: o gancho B vende a vinte e dois reais. O A, a trinta e cinco.",
      cap: "Resultado do exemplo: o gancho B vende a R$ 22. O A, a R$ 35." },
    { id: "i", text: "B vira o campeão. E o próximo teste é a oferta. Sempre uma variável por vez." },
    { id: "j", text: "Salva pra fazer seu próximo teste do jeito certo.", gap: 0.5, nocap: true },
  ],
  build(E) {
    const { tl, N } = E;
    const brl = (v) => "R$ " + Math.round(v).toLocaleString("pt-BR");
    const adCard = (parent, x, label, col, o = {}) => {
      const c = E.el(parent, "card abs", "", { left: x + "px", top: (o.top ?? 520) + "px", width: "420px", height: (o.h ?? 640) + "px", padding: "22px" });
      const tag = E.el(c, "abs badge", label, { left: "-26px", top: "-34px", width: "90px", height: "90px", borderRadius: "50%", background: col,
        font: "900 52px 'Inter Display'" });
      const img = E.el(c, "", "", { height: (o.imgH ?? 300) + "px", borderRadius: "22px", background: o.img || col, border: "4px solid #17171c", position: "relative" });
      return { c, tag, img };
    };

    // 1 — testou e não sabe quem ganhou
    const s1 = E.scene(0, N.c.t - 0.1, { exit: "whip", dolly: 0.05 });
    E.letterbox(0, true, 1, 0.01);
    E.letterbox(N.a.t + 1.2, false);
    E.cue("braam", 0.05, 0.6);
    const tq = E.text(s1, "QUAL *GANHOU*?", "t t-l", { position: "absolute", top: "330px", left: 0, right: 0, textAlign: "center" });
    E.wordsIn(tq, N.a.t + 0.2);
    const A = adCard(s1, 80, "A", "#ff5e5b", { img: "#ff8a3d" });
    const B = adCard(s1, 580, "B", "#3da5ff", { img: "#00c2a8" });
    E.el(A.c, "", "COMPRE JÁ", { font: "900 44px 'Inter Display'", marginTop: "24px" });
    E.el(A.c, "p", "Público: 18–24", { fontSize: "32px", marginTop: "8px" });
    E.el(B.c, "", "OFERTA 50%", { font: "900 44px 'Inter Display'", marginTop: "24px" });
    E.el(B.c, "p", "Público: 35–44", { fontSize: "32px", marginTop: "8px" });
    E.in([A.c, B.c], N.a.t + 0.3, { from: "up", stagger: 0.15, cue: "whoosh" });
    [A, B].forEach((p) => [...p.c.children].slice(2).forEach((n) => (n.style.position = "relative")));
    // marca cada diferença com um círculo
    const rings = [[A.img, 0], [B.img, 1], [A.c.children[2], 2], [B.c.children[2], 3], [A.c.children[3], 4], [B.c.children[3], 5]];
    rings.forEach(([node, i]) => {
      const r = E.el(node, "abs", "", { inset: "-14px", border: "7px solid #ff5e5b", borderRadius: "26px" });
      tl.fromTo(r, { scale: 1.6, opacity: 0 }, { scale: 1, opacity: 1, duration: 0.25, ease: "back.out(2)" }, N.b.t + 0.2 + i * 0.16);
      E.cue("pop", N.b.t + 0.2 + i * 0.16, 0.5);
    });
    const md = E.el(s1, "abs", "", { left: 0, right: 0, top: "1200px", textAlign: "center" });
    const mdc = E.el(md, "t", `<span class="g-red">MUDOU TUDO</span>`, { fontSize: "86px" });
    E.in(mdc, N.b.t + N.b.d * 0.6, { from: "pop", cue: "error" });
    E.punch(N.b.t + N.b.d * 0.6, { amp: 12, flash: 0.15, cue: false });

    // 2 — uma variável por vez
    const s2 = E.scene(N.c.t - 0.1, N.d.t - 0.1, { enter: "whip", exit: "whip" });
    E.bgTo(N.c.t - 0.2, "yellow");
    const k2 = E.el(s2, "abs", `<div class="kicker"><span class="dot"></span>Regra de ouro</div>`, { left: 0, right: 0, top: "330px", textAlign: "center" });
    E.in(k2, N.c.t, { from: "pop", cue: "pop" });
    const t2 = E.text(s2, "UMA COISA\nPOR *VEZ*", "t t-xl", { position: "absolute", top: "440px", left: 0, right: 0, textAlign: "center" });
    E.wordsIn(t2, N.c.t + N.c.d * 0.45, { stagger: 0.1 });
    E.punch(N.c.t + N.c.d * 0.55, { amp: 14, flash: 0.25, cue: "boom" });
    const sl = E.el(s2, "abs", "", { left: "160px", right: "160px", top: "880px", height: "380px", display: "flex", justifyContent: "space-between" });
    ["Gancho", "Oferta", "Público", "Visual"].forEach((n, i) => {
      const col = E.el(sl, "", "", { width: "150px", display: "flex", flexDirection: "column", alignItems: "center" });
      const track = E.el(col, "", "", { position: "relative", width: "26px", height: "280px", borderRadius: "20px", background: "#fff", border: "5px solid #17171c" });
      const knob = E.el(track, "abs", "", { left: "-32px", top: "110px", width: "80px", height: "50px", borderRadius: "16px", background: i === 0 ? "#ff5e5b" : "#e4e4e7",
        border: "5px solid #17171c", display: "flex", alignItems: "center", justifyContent: "center" });
      if (i > 0) knob.appendChild(E.icon("lock", 28, "#17171c", 2.8));
      E.el(col, "", n, { font: "800 32px Inter", marginTop: "14px" });
      E.in(col, N.c.t + 0.2 + i * 0.1, { from: "up", dur: 0.5 });
      if (i === 0) for (let k = 0; k < 4; k++) tl.to(knob, { top: k % 2 ? 110 : 10, duration: 0.45, ease: "power2.inOut" }, N.c.t + 0.9 + k * 0.5);
    });

    // 3 — exemplo: só o gancho muda
    const s3 = E.scene(N.d.t - 0.1, N.g.t - 0.1, { exit: "whip", dolly: 0.03 });
    E.bgTo(N.d.t - 0.2, "cream");
    const same = E.el(s3, "abs", "", { left: "60px", right: "60px", top: "320px", display: "flex", gap: "14px", justifyContent: "center", flexWrap: "wrap" });
    ["Mesmo vídeo", "Mesma oferta", "Mesmo público"].forEach((n, i) => {
      const ch = E.el(same, "chip", `${E.icon("check", 32, "#1a9e55", 3.4).outerHTML}${n}`, { fontSize: "32px", padding: "10px 20px" });
      E.in(ch, N.d.t + 0.6 + i * N.d.d * 0.18, { from: "pop", cue: "pop" });
    });
    const pa = adCard(s3, 80, "A", "#ff5e5b", { top: 520, h: 760, imgH: 420, img: "#ffd23f" });
    const pb = adCard(s3, 580, "B", "#3da5ff", { top: 520, h: 760, imgH: 420, img: "#ffd23f" });
    [pa, pb].forEach((p) => {
      p.img.innerHTML = `<div style="position:absolute;inset:0;display:flex;align-items:center;justify-content:center">${E.icon("play", 120, "#17171c", 2.4, "#fff").outerHTML}</div>`;
    });
    E.in([pa.c, pb.c], N.d.t + 0.3, { from: "up", stagger: 0.12, cue: "whoosh" });
    const hookA = E.el(pa.c, "", "", { font: "900 38px/1.15 'Inter Display'", marginTop: "24px", textTransform: "uppercase", minHeight: "150px" });
    const hookB = E.el(pb.c, "", "", { font: "900 38px/1.15 'Inter Display'", marginTop: "24px", textTransform: "uppercase", minHeight: "150px" });
    const typeIn = (node, txt, t0, d) => {
      for (let i = 1; i <= txt.length; i++) {
        tl.set(node, { textContent: txt.slice(0, i) }, t0 + (i / txt.length) * d);
        if (i % 2) E.cue("type", t0 + (i / txt.length) * d, 0.4);
      }
    };
    typeIn(hookA, "Você está jogando dinheiro fora", N.e.t + 0.5, N.e.d - 0.7);
    typeIn(hookB, "3 erros que fazem seu anúncio não vender", N.f.t + 0.5, N.f.d - 0.7);
    tl.to(pa.c, { background: "#ffe3e2", duration: 0.2 }, N.e.t + 0.3);
    tl.to(pa.c, { background: "#ffffff", duration: 0.2 }, N.f.t);
    tl.to(pb.c, { background: "#e3f2ff", duration: 0.2 }, N.f.t + 0.3);

    // 4 — deixa rodar
    const s4 = E.scene(N.g.t - 0.1, N.h.t - 0.1, { exit: "whip" });
    E.bgTo(N.g.t - 0.2, "teal");
    const t4 = E.text(s4, "DEIXA *RODAR*", "t t-l", { position: "absolute", top: "330px", left: 0, right: 0, textAlign: "center" });
    E.wordsIn(t4, N.g.t + 0.1);
    const cal = E.el(s4, "card abs", "", { left: "80px", right: "80px", top: "560px", padding: "36px", display: "grid", gridTemplateColumns: "repeat(7,1fr)", gap: "14px" });
    const days = Array.from({ length: 7 }, (_, i) => E.el(cal, "", `<div style="font:800 24px Inter;opacity:.6">DIA</div><div style="font:900 56px 'Inter Display'">${i + 1}</div>`,
      { textAlign: "center", padding: "16px 0", borderRadius: "18px", border: "4px solid #17171c", background: "#fff" }));
    E.in(cal, N.g.t + 0.3, { from: "up", cue: "swish" });
    days.forEach((d, i) => {
      const t = N.g.t + 0.8 + i * ((N.g.d - 1.2) / 7);
      tl.to(d, { background: "#b8f35a", duration: 0.15 }, t);
      E.cue("tick", t, 0.5);
    });
    const no = E.el(s4, "abs", "", { left: 0, right: 0, top: "900px", textAlign: "center" });
    const noc = E.el(no, "chip", `${E.icon("x", 40, "#ff5e5b", 3.6).outerHTML}<span>Decidir no <b>1º dia</b></span>`, { fontSize: "44px", padding: "18px 34px" });
    E.in(noc, N.g.t + N.g.d * 0.6, { from: "pop", cue: "error" });

    // 5 — resultado
    const s5 = E.scene(N.h.t - 0.1, N.i.t - 0.1, { exit: "whip", dolly: 0.04 });
    E.bgTo(N.h.t - 0.2, "orange");
    const k5 = E.el(s5, "abs", `<div class="kicker"><span class="dot"></span>Custo por venda (exemplo)</div>`, { left: 0, right: 0, top: "330px", textAlign: "center" });
    E.in(k5, N.h.t, { from: "pop" });
    const res = [["B", 22, "#b8f35a", 600], ["A", 35, "#ff5e5b", 860]];
    res.forEach(([n, v, c, y], i) => {
      const row = E.el(s5, "card abs", "", { left: "80px", right: "80px", top: y - 120 + "px", padding: "30px 36px" });
      const top = E.el(row, "", "", { display: "flex", justifyContent: "space-between", alignItems: "center" });
      E.el(top, "t", `GANCHO ${n}`, { fontSize: "56px" });
      const nv = E.el(top, "num", "", { fontSize: "80px" });
      const b = E.el(row, "bar", "<i></i>", { marginTop: "18px", height: "44px" });
      b.firstChild.style.background = c;
      const t = N.h.t + N.h.d * (i ? 0.72 : 0.38);
      E.in(row, t - 0.2, { from: i ? "right" : "left", cue: "whoosh" });
      tl.fromTo(b.firstChild, { scaleX: 0 }, { scaleX: v / 40, duration: 0.8, ease: "expo.out" }, t);
      E.counter(nv, t, 0.8, 0, v, brl);
    });
    const tip = E.el(s5, "abs p", "Menor custo por venda = vencedor", { left: 0, right: 0, top: "1110px", textAlign: "center", fontSize: "40px", color: "#17171c", fontWeight: 800 });
    E.in(tip, N.h.end - 0.4, { from: "fade" });

    // 6 — campeão e próximo teste
    const s6 = E.scene(N.i.t - 0.1, N.j.t - 0.15, { exit: "whip" });
    E.bgTo(N.i.t - 0.2, "green");
    const crown = E.el(s6, "abs badge", "B", { left: "390px", top: "330px", width: "300px", height: "300px", borderRadius: "80px", background: "#3da5ff",
      font: "900 200px 'Inter Display'" });
    const st = E.el(crown, "abs", "", { left: "100px", top: "-110px" });
    st.appendChild(E.icon("star", 110, "#17171c", 2.4, "#ffd23f"));
    E.in(crown, N.i.t + 0.05, { from: "pop", rot: -20 });
    E.punch(N.i.t + 0.2, { amp: 14, flash: 0.3, cue: "cash" });
    const t6 = E.text(s6, "CAMPEÃO", "t t-l", { position: "absolute", top: "680px", left: 0, right: 0, textAlign: "center" });
    E.wordsIn(t6, N.i.t + 0.3, { from: "pop" });
    const q = E.el(s6, "abs", "", { left: "60px", right: "60px", top: "900px", display: "flex", gap: "16px", justifyContent: "center", flexWrap: "wrap" });
    [["Gancho", true], ["Oferta", false], ["Visual", false], ["Público", false]].forEach(([n, done], i) => {
      const ch = E.el(q, "chip", (done ? E.icon("check", 32, "#1a9e55", 3.4).outerHTML : `<b>${i + 1}</b>`) + n, { fontSize: "36px",
        background: i === 1 ? "#ffd23f" : "#fff" });
      E.in(ch, N.i.t + N.i.d * 0.35 + i * 0.15, { from: "up", cue: "pop", vol: 0.5 });
    });
    const nx = E.el(s6, "abs p", "Próximo teste: <b>a oferta</b>.", { left: 0, right: 0, top: "1100px", textAlign: "center", fontSize: "44px" });
    E.in(nx, N.i.t + N.i.d * 0.45, { from: "up" });

    E.bgTo(N.j.t - 0.3, "sky");
    E.cta(N.j.t - 0.15, N.j.end + 2.2, { text: "SALVA PRO\n*PRÓXIMO TESTE*", next: "EP 13: como escalar sem quebrar" });
  },
};
