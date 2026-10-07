// EP 10 — 5 erros que queimam sua verba
window.VIDEO = {
  ep: 10,
  slug: "5-erros-que-queimam-verba",
  title: "5 erros que queimam sua verba",
  theme: { a1: "#ff5e5b", a2: "#ffd23f", bg: "orange" },
  build(E) {
    const { tl } = E;
    const brl = (v) => "R$ " + Math.round(v).toLocaleString("pt-BR");

    // 1 — gancho com fogo
    const s1 = E.scene(0, 3.6);
    const c1 = E.el(s1, "center");
    const fw = E.el(c1, "", "", { marginBottom: "30px", });
    const fire = E.icon("fire", 230, "#17171c", 2.4, "#ffd23f"); fw.appendChild(fire);
    E.draw(fire, 0.05, 0.6);
    E.in(fw, 0.05, { from: "pop", dur: 0.6 });
    for (let i = 0; i < 6; i++) tl.to(fw, { scaleY: i % 2 ? 1 : 1.08, scaleX: i % 2 ? 1 : 0.96, duration: 0.25, ease: "sine.inOut" }, 0.7 + i * 0.25);
    const tx = E.text(c1, "5 ERROS QUE\n[g-yellow:QUEIMAM]\nSUA VERBA", "t t-xl");
    E.wordsIn(tx, 0.2, { stagger: 0.08 });
    E.punch(0.75, { amp: 20, flash: 0.35 });
    E.glitch(tx.words[3], 0.8);

    // carteira que vai esvaziando
    const sw = E.scene(3.6, 21.0, { chapter: false, exit: "none" });
    const wal = E.el(sw, "abs", "", { left: 0, right: 0, top: "310px", display: "flex", justifyContent: "center" });
    const wc = E.el(wal, "chip", "", { fontSize: "44px", padding: "18px 34px", background: "#b8f35a" });
    wc.appendChild(E.icon("wallet", 50));
    const wv = E.el(wc, "num", brl(5000), { fontSize: "56px", color: "#17171c" });
    E.in(wal, 3.7, { from: "down", cue: "pop" });
    tl.to(sw, { opacity: 0, duration: 0.3 }, 20.7);

    const ERR = [
      ["MEXER NA\nCAMPANHA\nTODO DIA", "Cada edição grande [b:reinicia a fase de aprendizado].", "sliders"],
      ["RODAR UM\nCRIATIVO SÓ", "O público cansa dele e [b:o custo sobe].", "repeat"],
      ["ANUNCIAR\nSEM PIXEL\nE CAPI", "O algoritmo otimiza [b:no escuro].", "eye"],
      ["MANDAR PRA\nPÁGINA LENTA", "Clique pago que não carrega é [b:dinheiro fora].", "clock"],
      ["OLHAR SÓ\nO CPC", "Clique barato não paga boleto. [b:Olhe CPA e lucro].", "cursor"],
    ];
    const D = 3.4;
    let money = 5000;
    ERR.forEach(([title, desc, ic], i) => {
      const t0 = 3.6 + i * D;
      const s = E.scene(t0, t0 + D);
      const num = E.el(s, "abs t", `#${i + 1}`, { left: "80px", top: "450px", fontSize: "200px", color: "#fff", WebkitTextStroke: "6px #17171c", paintOrder: "stroke fill", textShadow: "10px 10px 0 #17171c" });
      E.in(num, t0 + 0.05, { from: "left", dur: 0.5 });
      E.bgTo(t0 - 0.1, ["coral", "yellow", "sky", "teal", "pink"][i]);
      const bd = E.el(s, "abs badge", "", { right: "80px", top: "470px", width: "160px", height: "160px", borderRadius: "48px", background: "#fff" });
      const icn = E.icon(ic, 86); bd.appendChild(icn);
      const xb = E.el(bd, "abs", "", { right: "-18px", top: "-18px", width: "64px", height: "64px", borderRadius: "50%", background: "#ff5e5b",
        display: "flex", alignItems: "center", justifyContent: "center", border: "5px solid #17171c" });
      xb.appendChild(E.icon("x", 32, "#fff", 3.4));
      E.in(bd, t0 + 0.15, { from: "pop", cue: "pop" });
      E.draw(icn, t0 + 0.25, 0.6);
      E.in(xb, t0 + 0.7, { from: "pop", dur: 0.4 });
      const tt = E.text(s, title, "t t-l", { position: "absolute", left: "80px", right: "60px", top: "720px" });
      E.wordsIn(tt, t0 + 0.12, { stagger: 0.06 });
      const ds = E.text(s, desc, "p p-l", { position: "absolute", left: "80px", right: "80px", top: "1170px" });
      E.wordsIn(ds, t0 + 0.8, { stagger: 0.03, dur: 0.45, cue: false });
      E.punch(t0 + 0.7, { amp: 14, flash: 0.2, cue: "error", vol: 0.6 });
      E.cue("hit", t0 + 0.7, 0.6);
      // a carteira perde dinheiro a cada erro
      const next = money - [900, 700, 1000, 600, 800][i];
      E.counter(wv, t0 + 0.75, 0.6, money, next, brl, { cue: false });
      tl.fromTo(wc, { background: "#ff5e5b" }, { background: i === 4 ? "#ff5e5b" : "#b8f35a", duration: 0.8, immediateRender: false }, t0 + 0.75);
      E.shake(t0 + 0.75, 6, 0.3);
      money = next;
      // brasas caindo
      const r = E.rng(100 + i);
      for (let k = 0; k < 10; k++) {
        const em = E.el(s, "abs", "", { left: 140 + r() * 800 + "px", top: "1560px", width: "20px", height: "20px", borderRadius: "5px", background: "#ffd23f", border: "4px solid #17171c", opacity: 0 });
        const te = t0 + 0.8 + r() * 1.6;
        tl.fromTo(em, { opacity: 0, y: 0 }, { opacity: 1, y: -300 - r() * 400, x: (r() - 0.5) * 120, duration: 1.4, ease: "power1.out", immediateRender: false }, te);
        tl.to(em, { opacity: 0, duration: 0.4 }, te + 1.0);
      }
    });
    tl.to(wv, { color: "#fff", duration: 0.3 }, 3.6 + 4 * D + 0.75);

    // 2 — virada
    const t2 = 3.6 + 5 * D;
    const s2 = E.scene(t2, t2 + 4.0);
    E.bgTo(t2 - 0.2, "green");
    const c2 = E.el(s2, "center");
    const rk = E.el(c2, "", "", { marginBottom: "40px", });
    const rocket = E.icon("rocket", 220, "#17171c", 2.4, "#fff"); rk.appendChild(rocket);
    E.draw(rocket, t2 + 0.1, 0.7);
    tl.fromTo(rk, { y: 120, opacity: 0 }, { y: 0, opacity: 1, duration: 0.6 }, t2 + 0.1);
    tl.to(rk, { y: -30, x: 20, duration: 1.2, ease: "sine.inOut", yoyo: true, repeat: 1 }, t2 + 0.8);
    const a2 = E.text(c2, "CORRIGIU OS 5?\nAGORA SIM,\n[g-green:ESCALA].", "t t-l");
    E.wordsIn(a2, t2 + 0.2, { stagger: 0.08 });
    E.punch(t2 + 0.95, { amp: 18, flash: 0.35, cue: "cash" });
    E.cue("riser", t2 - 1.4, 0.7);

    E.bgTo(t2 + 3.8, "yellow");
    E.cta(t2 + 4.0, t2 + 8.6, { text: "SALVA E MANDA\nPRO SEU *GESTOR*", sub: "ou pra quem [b:cuida dos seus anúncios]", next: "Segue pra mais episódios" });
  },
};
