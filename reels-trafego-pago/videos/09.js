// EP 09 — Google Ads x Meta Ads: capturar demanda x criar demanda
window.VIDEO = {
  ep: 9,
  slug: "google-ou-meta-ads",
  title: "Google ou Meta Ads?",
  theme: { a1: "#3b82f6", a2: "#ff2e88", bg: { c1: "#2563eb", c2: "#db2777", c3: "#ffd400" } },
  build(E) {
    const { tl } = E;
    const G = "#3b82f6", M = "#ff2e88";

    // 1 — gancho em tela dividida
    const s1 = E.scene(0, 3.8);
    const lp = E.el(s1, "abs", "", { left: 0, top: 0, width: "1080px", height: "960px", background: `linear-gradient(160deg, ${G}cc, #1e3a8a55)`,
      clipPath: "polygon(0 0,100% 0,100% 70%,0 100%)", display: "flex", alignItems: "center", justifyContent: "center" });
    const rp = E.el(s1, "abs", "", { left: 0, top: "860px", width: "1080px", height: "1060px", background: `linear-gradient(160deg, #83184355, ${M}cc)`,
      clipPath: "polygon(0 30%,100% 0,100% 100%,0 100%)", display: "flex", alignItems: "center", justifyContent: "center" });
    E.el(lp, "t", "GOOGLE", { fontSize: "190px", marginTop: "110px" });
    E.el(rp, "t", "META", { fontSize: "220px", marginTop: "60px" });
    tl.fromTo(lp, { xPercent: -100 }, { xPercent: 0, duration: 0.5, ease: "expo.out" }, 0.05);
    tl.fromTo(rp, { xPercent: 100 }, { xPercent: 0, duration: 0.5, ease: "expo.out" }, 0.2);
    E.cue("whoosh", 0.05); E.cue("whoosh", 0.2);
    const vs = E.el(s1, "abs t", "VS", { left: "390px", top: "830px", width: "300px", height: "300px", borderRadius: "50%", display: "flex", alignItems: "center",
      justifyContent: "center", fontSize: "130px", background: "#05050b", border: "6px solid #fff", boxShadow: "0 0 80px rgba(255,255,255,.5)" });
    E.in(vs, 0.65, { from: "pop", dur: 0.5 });
    E.punch(0.7, { amp: 26, flash: 0.5 });
    const q = E.el(s1, "abs", "", { left: 0, right: 0, top: "320px", textAlign: "center" });
    E.el(q, "kicker", `<span class="dot"></span>Onde investir primeiro?`);
    E.in(q, 1.3, { from: "up", cue: "pop" });

    // 2 — Google: a pessoa procura
    const s2 = E.scene(3.8, 10.4);
    E.bgTo(3.6, { c1: G, c2: "#22d3ee" }, 0.6);
    const t2 = E.text(s2, "NO GOOGLE, A\nPESSOA *PROCURA*", "t t-m", { position: "absolute", top: "320px", left: 0, right: 0, textAlign: "center" });
    t2.style.setProperty("--a1", G); t2.style.setProperty("--a2", "#22d3ee");
    E.wordsIn(t2, 3.9);
    const sb = E.el(s2, "abs", "", { left: "80px", right: "80px", top: "640px", height: "120px", borderRadius: "70px", background: "#fff",
      display: "flex", alignItems: "center", gap: "24px", padding: "0 44px", boxShadow: "0 0 60px rgba(59,130,246,.5)" });
    sb.appendChild(E.icon("search", 54, "#64748b", 2.6));
    const typed = E.el(sb, "", "", { fontFamily: "Inter", fontWeight: 600, fontSize: "44px", color: "#111" });
    E.in(sb, 4.4, { from: "zoom", dur: 0.5, cue: "swish" });
    const query = "dentista perto de mim";
    for (let i = 1; i <= query.length; i++) {
      const tt = 5.0 + i * 0.06;
      tl.set(typed, { textContent: query.slice(0, i) }, tt);
      E.cue("type", tt, 0.6);
    }
    tl.set(typed, { textContent: "" }, 0);
    const res = E.el(s2, "card abs", "", { left: "80px", right: "80px", top: "820px", padding: "34px 40px", borderColor: G + "aa", boxShadow: `0 0 50px ${G}55` });
    E.el(res, "", `<span style="font:900 26px Inter;padding:6px 14px;border-radius:8px;background:${G};margin-right:14px">Patrocinado</span><span style="font:700 30px Inter;color:rgba(255,255,255,.7)">seusite.com.br</span>`);
    E.el(res, "", "Dentista no seu bairro — Agende Hoje", { font: "800 46px Inter", color: "#8ab4ff", marginTop: "18px" });
    E.el(res, "p", "Atendimento hoje. Avaliação gratuita.", { fontSize: "36px", marginTop: "8px" });
    E.in(res, 6.6, { from: "up", cue: "pop" });
    const cur = E.el(s2, "abs", "", { left: "720px", top: "1150px" });
    cur.appendChild(E.icon("cursor", 80, "#fff", 2.2, "#05050b"));
    tl.fromTo(cur, { opacity: 0, x: 120, y: 160 }, { opacity: 1, x: 0, y: 0, duration: 0.7, ease: "power2.inOut" }, 7.0);
    tl.to(res, { scale: 0.97, duration: 0.08, yoyo: true, repeat: 1 }, 7.75);
    E.cue("click", 7.75, 1);
    const tg = E.el(s2, "abs", "", { left: 0, right: 0, top: "1330px", textAlign: "center" });
    const tgc = E.el(tg, "kicker", `<span class="dot"></span>Captura demanda`, { "--a1": G, "--a2": "#22d3ee" });
    E.in(tgc, 8.0, { from: "pop", cue: "ding" });
    E.el(s2, "abs p", "Intenção alta: ela <b>já quer</b> o que você vende.", { left: "80px", right: "80px", top: "1460px", textAlign: "center", fontSize: "40px" });
    E.in(s2.lastChild, 8.4, { from: "fade" });

    // 3 — Meta: a pessoa descobre
    const s3 = E.scene(10.4, 17.2);
    E.bgTo(10.2, { c1: M, c2: "#8b5cf6" }, 0.6);
    const t3 = E.text(s3, "NA META, A\nPESSOA *DESCOBRE*", "t t-m", { position: "absolute", top: "320px", left: 0, right: 0, textAlign: "center" });
    E.wordsIn(t3, 10.5);
    const feed = E.el(s3, "abs", "", { left: "290px", top: "590px", width: "500px", height: "760px", borderRadius: "50px", overflow: "hidden",
      background: "#0b0b14", border: "3px solid rgba(255,255,255,.2)", boxShadow: `0 0 80px ${M}66` });
    E.in(feed, 10.9, { from: "up", cue: "whoosh" });
    const strip = E.el(feed, "abs", "", { left: "22px", right: "22px", top: "22px" });
    const posts = [["#334155", "post"], ["#475569", "post"], [M, "ad"], ["#334155", "post"]];
    posts.forEach(([c, k]) => {
      const p = E.el(strip, "", "", { height: "440px", borderRadius: "28px", marginBottom: "22px", background: k === "ad" ? `linear-gradient(160deg, ${M}, #8b5cf6)` : c,
        position: "relative", overflow: "hidden" });
      if (k === "ad") {
        E.el(p, "abs", "Patrocinado", { left: "24px", top: "22px", font: "800 24px Inter", opacity: 0.85 });
        E.el(p, "abs t", "CLAREAMENTO<br>EM 1 SESSÃO", { left: "24px", bottom: "100px", fontSize: "52px" });
        E.el(p, "abs", "Saiba mais", { left: "24px", right: "24px", bottom: "22px", height: "62px", borderRadius: "14px", background: "rgba(255,255,255,.95)", color: "#111",
          font: "800 28px/62px Inter", textAlign: "center" });
      }
    });
    tl.fromTo(strip, { y: 0 }, { y: -924, duration: 1.6, ease: "power3.inOut" }, 11.6);
    E.cue("swish", 11.6, 0.7);
    E.pulse(feed, 13.3, 1.05, 0.3);
    E.cue("pop", 13.3, 0.7);
    const heart = E.el(s3, "abs", "", { left: "470px", top: "880px" });
    const hi = E.icon("heart", 140, "#fff", 2, "#ff2e88"); heart.appendChild(hi);
    tl.fromTo(heart, { scale: 0, opacity: 0 }, { scale: 1.2, opacity: 1, duration: 0.35, ease: "back.out(3)" }, 13.6);
    tl.to(heart, { scale: 1.6, opacity: 0, y: -80, duration: 0.5 }, 14.2);
    E.cue("pop", 13.6, 0.9);
    const tg3 = E.el(s3, "abs", "", { left: 0, right: 0, top: "1390px", textAlign: "center" });
    E.el(tg3, "kicker", `<span class="dot"></span>Cria demanda`);
    E.in(tg3, 14.4, { from: "pop", cue: "ding" });
    E.el(s3, "abs p", "Ela nem sabia que queria, até <b>ver seu anúncio</b>.", { left: "80px", right: "80px", top: "1510px", textAlign: "center", fontSize: "40px" });
    E.in(s3.lastChild, 14.8, { from: "fade" });

    // 4 — comparação
    const s4 = E.scene(17.2, 24.0);
    E.bgTo(17.0, { c1: G, c2: M }, 0.6);
    const head = E.el(s4, "abs", "", { left: "80px", right: "80px", top: "330px", display: "grid", gridTemplateColumns: "1fr 1fr", gap: "20px" });
    const hg = E.el(head, "", "GOOGLE", { textAlign: "center", padding: "26px", borderRadius: "28px", background: G, font: "900 54px 'Inter Display'", letterSpacing: "-.03em", boxShadow: `0 0 40px ${G}88` });
    const hm = E.el(head, "", "META", { textAlign: "center", padding: "26px", borderRadius: "28px", background: M, font: "900 54px 'Inter Display'", letterSpacing: "-.03em", boxShadow: `0 0 40px ${M}88` });
    E.in(hg, 17.3, { from: "left", cue: "whoosh" });
    E.in(hm, 17.4, { from: "right" });
    const rows = [
      ["Intenção", "Alta: já está buscando", "Média: está rolando o feed"],
      ["Escala", "Limitada ao que é buscado", "Grande: cria o interesse"],
      ["Brilha em", "Serviço local e urgente", "Produto novo, visual, impulso"],
    ];
    rows.forEach(([lb, a, b], i) => {
      const t = 17.9 + i * 0.9;
      const y = 520 + i * 300;
      const l = E.el(s4, "abs lbl", lb, { left: 0, right: 0, top: y + "px", textAlign: "center", fontFamily: "Inter", fontWeight: 800, fontSize: "32px", letterSpacing: ".14em", textTransform: "uppercase", color: "rgba(255,255,255,.6)" });
      const g = E.el(s4, "card abs", a, { left: "80px", width: "450px", top: y + 50 + "px", padding: "28px 30px", font: "800 38px/1.2 Inter", borderColor: G + "99" });
      const m = E.el(s4, "card abs", b, { left: "550px", width: "450px", top: y + 50 + "px", padding: "28px 30px", font: "800 38px/1.2 Inter", borderColor: M + "99" });
      E.in(l, t, { from: "fade", dur: 0.4 });
      E.in(g, t + 0.05, { from: "left", dur: 0.5, cue: "swish", vol: 0.5 });
      E.in(m, t + 0.15, { from: "right", dur: 0.5 });
    });

    // 5 — resposta
    const s5 = E.scene(24.0, 27.8);
    const c5 = E.el(s5, "center");
    const a5 = E.text(c5, "A RESPOSTA?", "t t-m");
    E.wordsIn(a5, 24.1);
    const b5 = E.text(c5, "*OS DOIS*", "t t-xxl", { marginTop: "30px" });
    E.wordsIn(b5, 24.7, { from: "pop", stagger: 0.12 });
    E.punch(24.85, { amp: 22, flash: 0.4 });
    const c5b = E.el(c5, "p", "Google pra quem <b>já procura</b>. Meta pra fazer <b>mais gente querer</b>.", { marginTop: "50px", maxWidth: "880px", fontSize: "44px" });
    E.in(c5b, 25.5, { from: "up" });

    E.cta(27.8, 32.4, { next: "EP 10: 5 erros que queimam sua verba" });
  },
};
