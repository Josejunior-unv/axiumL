// EP 06 — Criativo é a nova segmentação (Meta Andromeda e diversidade de ângulos)
window.VIDEO = {
  ep: 6,
  slug: "criativo-e-a-nova-segmentacao",
  title: "Criativo é a nova segmentação",
  theme: { a1: "#ff7eb6", a2: "#ffd23f", bg: "pink" },
  build(E) {
    const { tl } = E;

    // 1 — gancho
    const h = E.hook(0, 3.5, { kicker: "Meta Ads em 2026", text: "SEU PÚBLICO\nAGORA É O\n*CRIATIVO*", cls: "t t-xl" });
    E.punch(0.75, { amp: 20 });

    // 2 — antes x agora
    const s2 = E.scene(3.5, 11.6);
    const k1 = E.el(s2, "abs", `<div class="kicker" style="--a2:#b9bec7"><span class="dot"></span>Antes</div>`, { left: "80px", top: "320px" });
    E.in(k1, 3.6, { from: "left" });
    const box = E.el(s2, "card abs", "", { left: "80px", right: "80px", top: "430px", padding: "34px 40px" });
    E.el(box, "lbl", "Você escolhia o público na mão");
    const opts = ["Mulheres, 25–34", "Interesse: academia", "Interesse: moda fitness", "Cidade: São Paulo"];
    const rows = opts.map((o) => {
      const r = E.el(box, "", "", { display: "flex", alignItems: "center", gap: "22px", marginTop: "22px", fontFamily: "Inter", fontWeight: 700, fontSize: "40px" });
      const cb = E.el(r, "", "", { width: "50px", height: "50px", borderRadius: "14px", border: "4px solid #17171c", background: "#fff", display: "flex", alignItems: "center", justifyContent: "center" });
      const ck = E.icon("check", 36, "#17171c", 3.4); cb.appendChild(ck);
      E.el(r, "", o);
      return { r, cb, ck };
    });
    E.in(box, 3.8, { from: "up", cue: "swish" });
    rows.forEach(({ cb, ck }, i) => {
      const t = 4.3 + i * 0.35;
      tl.fromTo(ck.querySelector("path"), { drawSVG: "0%" }, { drawSVG: "100%", duration: 0.25 }, t);
      tl.to(cb, { background: "#ffd23f", duration: 0.15 }, t);
      E.cue("click", t, 0.8);
    });
    tl.to(box, { opacity: 0.35, scale: 0.94, duration: 0.5 }, 6.2);
    const x = E.el(s2, "abs", "", { left: "80px", right: "80px", top: "640px", height: "8px", borderRadius: "9px", background: "#ff5e5b", border: "3px solid #17171c", transformOrigin: "left", rotate: "-8deg" });
    tl.fromTo(x, { scaleX: 0 }, { scaleX: 1, duration: 0.35, ease: "expo.out" }, 6.2);
    E.cue("swish", 6.2, 0.8);

    const k2 = E.el(s2, "abs", `<div class="kicker"><span class="dot"></span>Agora</div>`, { left: "80px", top: "1000px" });
    E.in(k2, 6.6, { from: "left", cue: "whoosh" });
    const ai = E.el(s2, "card glow abs", "", { left: "80px", right: "80px", top: "1110px", padding: "36px 40px", display: "flex", gap: "32px", alignItems: "center" });
    const bd = E.el(ai, "badge", "", { flex: "none", width: "140px", height: "140px", borderRadius: "40px" });
    const br = E.icon("brain", 80); bd.appendChild(br);
    E.el(ai, "", `<div class="t" style="font-size:56px">A IA LÊ SEU<br>ANÚNCIO</div><div class="p" style="font-size:36px;margin-top:10px">e entrega pra quem tem mais chance de reagir a ele.</div>`);
    E.in(ai, 6.9, { from: "up", cue: "swish" });
    E.draw(br, 7.1, 0.9);
    E.pulse(bd, 8.1, 1.15, 0.4);
    E.cue("ding", 8.1, 0.6);
    const nm = E.el(s2, "abs p", "O nome do sistema: <b>Andromeda</b>.", { left: "80px", right: "80px", top: "1470px", textAlign: "center", fontSize: "38px" });
    E.in(nm, 8.6, { from: "fade" });

    // 3 — parecido demais = mesmo anúncio
    const s3 = E.scene(11.6, 17.4);
    E.bgTo(11.5, "yellow");
    const t3 = E.text(s3, "MUDAR SÓ A\n[g-white:COR] NÃO É\nCRIATIVO NOVO", "t t-m", { position: "absolute", top: "320px", left: "60px", right: "60px", textAlign: "center" });
    E.wordsIn(t3, 11.7);
    const cc = ["#ff5e5b", "#3da5ff", "#b8f35a"];
    const mini = cc.map((c, i) => {
      const d = E.el(s3, "abs card", "", { left: 110 + i * 300 + "px", top: "800px", width: "260px", height: "400px", padding: "18px", borderRadius: "28px" });
      E.el(d, "", "", { height: "200px", borderRadius: "18px", background: c, border: "4px solid #17171c" });
      E.el(d, "", "MESMA OFERTA", { fontFamily: "Inter", fontWeight: 900, fontSize: "26px", marginTop: "20px" });
      E.el(d, "", "", { height: "14px", width: "85%", marginTop: "14px", borderRadius: "7px", background: "rgba(23,23,28,.3)" });
      E.el(d, "", "", { height: "14px", width: "60%", marginTop: "10px", borderRadius: "7px", background: "rgba(23,23,28,.18)" });
      return d;
    });
    E.in(mini, 12.4, { from: "up", stagger: 0.12, cue: "pop" });
    tl.to(mini, { left: 410, rotate: (i) => (i - 1) * 6, duration: 0.7, ease: "expo.inOut" }, 13.9);
    E.cue("whoosh", 13.9, 0.8);
    E.punch(14.6, { amp: 12, flash: 0.2, cue: "hit" });
    const eq = E.el(s3, "abs", "", { left: 0, right: 0, top: "1290px", textAlign: "center" });
    const eqc = E.el(eq, "chip", `${E.icon("alert", 36, "#17171c", 2.8, "#ffd23f").outerHTML}<span>Pro algoritmo, é <b>o mesmo anúncio</b></span>`, { fontSize: "38px" });
    E.in(eqc, 14.7, { from: "pop", cue: "pop" });

    // 4 — ângulos
    const s4 = E.scene(17.4, 24.4);
    E.bgTo(17.3, "cream");
    const t4 = E.text(s4, "TESTE *ÂNGULOS*", "t t-l", { position: "absolute", top: "320px", left: 0, right: 0, textAlign: "center" });
    E.wordsIn(t4, 17.5);
    const cx = 540, cy = 1000;
    const core = E.el(s4, "abs badge", "", { left: cx - 100 + "px", top: cy - 100 + "px", width: "200px", height: "200px", borderRadius: "60px" });
    core.appendChild(E.icon("target", 110));
    E.in(core, 17.8, { from: "pop", cue: "pop" });
    const A = [["DOR", "o problema que incomoda", "#ff5e5b"], ["DESEJO", "o resultado sonhado", "#ff7eb6"], ["PROVA", "depoimento, antes/depois", "#b8f35a"],
      ["OBJEÇÃO", "o \"mas e se...\" respondido", "#ffd23f"], ["COMPARAÇÃO", "você x alternativa", "#3da5ff"]];
    A.forEach(([n, d, c], i) => {
      const a = -Math.PI / 2 + (i * 2 * Math.PI) / 5;
      const rx = 330, ry = 380;
      const x = cx + Math.cos(a) * rx, y = cy + Math.sin(a) * ry;
      const ln = E.el(s4, "abs", "", { left: cx + "px", top: cy + "px", width: Math.hypot(x - cx, y - cy) - 60 + "px", height: "8px", background: "#17171c",
        transformOrigin: "0 50%", rotate: (Math.atan2(y - cy, x - cx) * 180) / Math.PI + "deg", opacity: 1 });
      tl.fromTo(ln, { scaleX: 0 }, { scaleX: 1, duration: 0.4, ease: "expo.out" }, 18.3 + i * 0.3);
      const b = E.el(s4, "abs", "", { left: x - 170 + "px", top: y - 70 + "px", width: "340px", textAlign: "center" });
      const ch = E.el(b, "chip", n, { fontSize: "40px", fontWeight: 900, background: c, padding: "16px 30px" });
      E.el(b, "p", d, { fontSize: "30px", marginTop: "14px", color: "#17171c", fontWeight: 700 });
      E.in(b, 18.4 + i * 0.3, { from: "pop", cue: "pop", vol: 0.6 });
    });
    E.punch(20.0, { amp: 10, flash: 0.2 });
    tl.to(core, { rotate: 360, duration: 4, ease: "none" }, 18.0);

    // 5 — fechamento
    const s5 = E.scene(24.4, 27.8);
    E.bgTo(24.3, "teal");
    const c5 = E.el(s5, "center");
    const a5 = E.text(c5, "MAIS IDEIAS\nDIFERENTES,\nNÃO MAIS\n[g-yellow:CÓPIAS].", "t t-l");
    E.wordsIn(a5, 24.5, { stagger: 0.08 });
    E.punch(25.3, { amp: 16, flash: 0.3 });

    E.cta(27.8, 32.4, { next: "EP 07: anatomia de um anúncio que vende" });
  },
};
