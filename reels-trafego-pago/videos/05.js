// EP 05 — O leilão da Meta: quem paga mais não necessariamente ganha
window.VIDEO = {
  ep: 5,
  slug: "leilao-da-meta",
  title: "Quem paga mais não ganha o leilão",
  theme: { a1: "#3da5ff", a2: "#ffd23f", bg: "sky" },
  build(E) {
    const { tl } = E;

    // 1 — gancho
    const h = E.hook(0, 3.5, { kicker: "Como o leilão funciona", text: "QUEM PAGA\nMAIS [g-red:NÃO]\nGANHA O\n*LEILÃO*", cls: "t t-xl" });
    E.punch(0.75, { amp: 18 });
    E.glitch(h.tx.words[3], 0.8);

    // 2 — um leilão a cada rolagem
    const s2 = E.scene(3.5, 9.0);
    const t2 = E.text(s2, "A CADA ROLADA\nDO FEED ROLA\nUM *LEILÃO*", "t t-m", { position: "absolute", top: "320px", left: "60px", right: "60px", textAlign: "center" });
    E.wordsIn(t2, 3.6);
    const ph = E.el(s2, "abs", "", { left: "390px", top: "780px", width: "300px", height: "560px", borderRadius: "54px", padding: "12px",
      background: "#17171c", boxShadow: "12px 12px 0 rgba(23,23,28,.35)" });
    const scr = E.el(ph, "", "", { width: "100%", height: "100%", borderRadius: "44px", background: "#fff6e5", overflow: "hidden", position: "relative" });
    const slot = E.el(scr, "abs", "", { left: "18px", right: "18px", top: "150px", height: "230px", borderRadius: "22px",
      border: "4px dashed rgba(23,23,28,.45)", display: "flex", alignItems: "center", justifyContent: "center", fontFamily: "Inter", fontWeight: 800, fontSize: "26px", color: "rgba(23,23,28,.55)" });
    slot.textContent = "1 espaço";
    E.in(ph, 4.2, { from: "up", cue: "whoosh" });
    // anúncios disputando o espaço
    const colors = ["#ff5e5b", "#00c2a8", "#ffd23f", "#b8f35a", "#ff8a3d", "#ff7eb6"];
    const ads = colors.map((c, i) => {
      const a = (i / colors.length) * Math.PI * 2;
      const x = 540 + Math.cos(a) * 400 - 80, y = 1060 + Math.sin(a) * 430 - 60;
      const d = E.el(s2, "abs card", "", { left: x + "px", top: y + "px", width: "160px", height: "120px", padding: "14px", borderRadius: "22px",
        borderWidth: "4px", boxShadow: "6px 6px 0 #17171c" });
      E.el(d, "", "", { height: "52px", borderRadius: "12px", background: c, border: "3px solid #17171c" });
      E.el(d, "", "", { height: "12px", width: "80%", marginTop: "12px", borderRadius: "6px", background: "rgba(23,23,28,.35)" });
      E.el(d, "", "", { height: "12px", width: "55%", marginTop: "8px", borderRadius: "6px", background: "rgba(23,23,28,.2)" });
      return d;
    });
    E.in(ads, 4.8, { from: "pop", stagger: 0.08, cue: "pop" });
    ads.forEach((d, i) => E.float(d, 5.3, 7.4, 10 + i * 2, 1.2 + i * 0.1));
    // o vencedor entra no espaço
    const win = ads[3];
    tl.to(ads.filter((_, i) => i !== 3), { opacity: 0.15, scale: 0.8, duration: 0.4 }, 7.4);
    tl.to(win, { left: 440, top: 945, width: 200, height: 166, duration: 0.6, ease: "expo.inOut" }, 7.4);
    E.cue("whoosh", 7.4, 0.7);
    E.punch(8.0, { amp: 10, flash: 0.2, cue: "ding" });
    const qw = E.el(s2, "abs", "", { left: 0, right: 0, top: "1450px", textAlign: "center" });
    const q = E.el(qw, "chip", "Só um leva o espaço", { fontSize: "40px" });
    E.in(q, 7.9, { from: "fade", cue: false });

    // 3 — a fórmula
    const s3 = E.scene(9.0, 16.4);
    E.bgTo(8.9, "teal");
    const k3 = E.el(s3, "abs", `<div class="kicker"><span class="dot"></span>Valor total do anúncio</div>`, { left: 0, right: 0, top: "330px", textAlign: "center" });
    E.in(k3, 9.1, { from: "pop" });
    const parts = [
      ["LANCE", "quanto você topa pagar", "coin", "#ffd23f", "#ffd23f"],
      ["TAXA DE AÇÃO ESTIMADA", "a chance dessa pessoa clicar ou comprar", "target", "#ff5e5b", "#ff5e5b"],
      ["QUALIDADE DO ANÚNCIO", "o que as pessoas acham dele", "star", "#b8f35a", "#b8f35a"],
    ];
    const ops = ["", "×", "+"];
    parts.forEach(([n, d, ic, c1, c2], i) => {
      const y = 500 + i * 330;
      const t = 9.4 + i * 1.6;
      if (i > 0) {
        const op = E.el(s3, "abs t", ops[i], { left: 0, right: 0, top: y - 120 + "px", textAlign: "center", fontSize: "110px", color: "#17171c" });
        E.in(op, t - 0.1, { from: "pop", dur: 0.4 });
      }
      const card = E.el(s3, "card abs", "", { left: "80px", right: "80px", top: y + "px", padding: "30px 40px", display: "flex", gap: "30px", alignItems: "center" });
      const bd = E.el(card, "badge", "", { flex: "none", width: "110px", height: "110px", background: c1 });
      const icn = E.icon(ic, 60); bd.appendChild(icn);
      const tx = E.el(card, "", `<div class="t" style="font-size:${n.length > 12 ? 52 : 74}px">${n}</div><div class="p" style="font-size:36px;margin-top:8px">${d}</div>`);
      E.in(card, t, { from: i % 2 ? "right" : "left", cue: "whoosh" });
      E.draw(icn, t + 0.2, 0.6);
      E.cue("pop", t + 0.3, 0.6);
    });
    const note = E.el(s3, "abs p", "Modelo que a própria Meta usa pra explicar o leilão.", { left: "80px", right: "80px", top: "1500px", textAlign: "center", fontSize: "32px" });
    E.in(note, 14.6, { from: "fade" });

    // 4 — a batalha
    const s4 = E.scene(16.4, 24.0);
    E.bgTo(16.3, "orange");
    const t4 = E.text(s4, "NA PRÁTICA", "t t-m", { position: "absolute", top: "320px", left: 0, right: 0, textAlign: "center" });
    E.wordsIn(t4, 16.5);
    const P = [
      { n: "Anunciante A", bid: "Lance alto", cr: "Criativo fraco", score: 0.42, c: "#ff5e5b", y: 520 },
      { n: "Anunciante B", bid: "Lance médio", cr: "Criativo forte", score: 0.86, c: "#2bc46b", y: 920 },
    ];
    const cards = P.map((p, i) => {
      const c = E.el(s4, "card abs", "", { left: "80px", right: "80px", top: p.y + "px", padding: "36px 44px" });
      E.el(c, "t", p.n, { fontSize: "60px" });
      const chips = E.el(c, "", "", { display: "flex", gap: "16px", marginTop: "22px" });
      E.el(chips, "chip", `${E.icon("coin", 34).outerHTML}${p.bid}`, { fontSize: "32px" });
      E.el(chips, "chip", `${E.icon(i ? "check" : "x", 34, p.c, 3.2).outerHTML}${p.cr}`, { fontSize: "32px" });
      const lb = E.el(c, "", "", { display: "flex", justifyContent: "space-between", marginTop: "30px" });
      E.el(lb, "lbl", "Valor total");
      const pct = E.el(lb, "num", "0", { fontSize: "44px", color: p.c });
      const b = E.el(c, "bar", "<i></i>", { marginTop: "12px", height: "40px" });
      b.firstChild.style.background = p.c;
      const t = 16.9 + i * 0.5;
      E.in(c, t, { from: i ? "right" : "left", cue: "swish" });
      tl.fromTo(b.firstChild, { scaleX: 0 }, { scaleX: p.score, duration: 1.4, ease: "expo.out" }, 18.0);
      E.counter(pct, 18.0, 1.4, 0, p.score * 100, (v) => Math.round(v) + " pts");
      return c;
    });
    tl.to(cards[0], { opacity: 0.4, scale: 0.96, duration: 0.4 }, 19.8);
    tl.to(cards[1], { background: "#e9ffd0", duration: 0.3 }, 19.8);
    E.punch(19.8, { amp: 16, flash: 0.3, cue: "cash" });
    const ww = E.el(s4, "abs", "", { left: 0, right: 0, top: "1360px", textAlign: "center" });
    const wb = E.el(ww, "kicker", `<span class="dot"></span>B ganha com lance menor`, {
      whiteSpace: "nowrap" });
    E.in(wb, 20.0, { from: "pop", cue: "pop" });
    E.bgTo(19.8, "green");
    const disc = E.el(s4, "abs p", "Exemplo ilustrativo.", { left: 0, right: 0, top: "1500px", textAlign: "center", fontSize: "30px", opacity: 0.6 });
    E.in(disc, 20.4, { from: "fade" });

    // 5 — lição
    const s5 = E.scene(24.0, 27.6);
    E.bgTo(23.8, "yellow");
    const c5 = E.el(s5, "center");
    const a5 = E.text(c5, "CRIATIVO BOM\n=\n[g-green:CUSTO MENOR]", "t t-l");
    E.wordsIn(a5, 24.1, { stagger: 0.1, from: "pop" });
    E.punch(24.6, { amp: 16, flash: 0.3 });

    E.cta(27.6, 32.2, { next: "EP 06: criativo é a nova segmentação" });
  },
};
