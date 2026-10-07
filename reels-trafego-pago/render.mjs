// Renderiza os Reels quadro a quadro com o Chromium (Playwright) e monta o MP4 com ffmpeg.
//
//   node render.mjs              -> renderiza os 10 vídeos
//   node render.mjs 03 07        -> só os episódios 03 e 07
//   node render.mjs 03 --stills 0.5,4,9   -> só tira prints desses segundos (para conferir)
//   node render.mjs --mute       -> sem trilha/efeitos
import { spawn, spawnSync } from "node:child_process";
import { mkdirSync, writeFileSync, readdirSync, existsSync } from "node:fs";
import { createRequire } from "node:module";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const require = createRequire(import.meta.url);
let chromium;
try { ({ chromium } = require("playwright")); }
catch { ({ chromium } = require("/opt/node22/lib/node_modules/playwright")); }

const ROOT = path.dirname(fileURLToPath(import.meta.url));
const OUT = path.join(ROOT, "saida");
const TMP = path.join(ROOT, ".tmp");
mkdirSync(OUT, { recursive: true });
mkdirSync(TMP, { recursive: true });

const args = process.argv.slice(2);
const flag = (n) => args.includes(n);
const opt = (n) => { const i = args.indexOf(n); return i >= 0 ? args[i + 1] : null; };
const stills = opt("--stills");
let ids = args.filter((a) => /^\d\d$/.test(a));
if (!ids.length) ids = readdirSync(path.join(ROOT, "videos")).filter((f) => /^\d\d\.js$/.test(f)).map((f) => f.slice(0, 2)).sort();

const browser = await chromium.launch({
  args: ["--allow-file-access-from-files", "--font-render-hinting=none", "--disable-gpu-vsync"],
});

for (const id of ids) {
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
  page.on("pageerror", (e) => console.error(`[${id}] erro na página:`, e.message));
  page.on("console", (m) => m.type() === "error" && console.error(`[${id}]`, m.text()));
  await page.goto(pathToFileURL(path.join(ROOT, "engine", "stage.html")).href + "?v=" + id);
  await page.waitForFunction(() => window.__ready === true, null, { timeout: 30000 });
  const info = await page.evaluate(() => window.__info());
  const name = `${id}-${info.slug}`;

  if (stills) {
    const dir = path.join(TMP, "stills");
    mkdirSync(dir, { recursive: true });
    for (const s of stills.split(",").map(Number)) {
      await page.evaluate((t) => window.__seek(t), s);
      await page.screenshot({ path: path.join(dir, `${id}_${s.toFixed(2)}.png`) });
    }
    console.log(`[${id}] prints em ${dir} (duração ${info.duration.toFixed(2)}s)`);
    await page.close();
    continue;
  }

  const frames = Math.round(info.duration * info.fps);
  const silent = path.join(TMP, `${name}.video.mp4`);
  const ff = spawn("ffmpeg", ["-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", String(info.fps), "-c:v", "mjpeg", "-i", "-",
    "-c:v", "libx264", "-preset", "slow", "-crf", "20", "-maxrate", "10M", "-bufsize", "20M", "-pix_fmt", "yuv420p", "-profile:v", "high", "-r", String(info.fps), silent],
    { stdio: ["pipe", "inherit", "inherit"] });
  const cdp = await page.context().newCDPSession(page);
  const t0 = Date.now();
  for (let i = 0; i < frames; i++) {
    await page.evaluate((t) => window.__seek(t), i / info.fps);
    const { data } = await cdp.send("Page.captureScreenshot", { format: "jpeg", quality: 94, optimizeForSpeed: true });
    const buf = Buffer.from(data, "base64");
    if (!ff.stdin.write(buf)) await new Promise((r) => ff.stdin.once("drain", r));
    if (i % 150 === 0) process.stdout.write(`\r[${id}] quadro ${i}/${frames}`);
  }
  ff.stdin.end();
  await new Promise((r) => ff.on("close", r));
  console.log(`\r[${id}] ${frames} quadros em ${((Date.now() - t0) / 1000).toFixed(0)}s`);
  await page.close();

  const final = path.join(OUT, `${name}.mp4`);
  if (flag("--mute")) {
    spawnSync("ffmpeg", ["-y", "-loglevel", "error", "-i", silent, "-c", "copy", "-movflags", "+faststart", final], { stdio: "inherit" });
  } else {
    const cuesFile = path.join(TMP, `${name}.json`);
    const wav = path.join(TMP, `${name}.wav`);
    writeFileSync(cuesFile, JSON.stringify(info));
    const py = spawnSync("python3", [path.join(ROOT, "audio", "trilha.py"), cuesFile, wav], { stdio: "inherit" });
    if (py.status !== 0) throw new Error("falha ao gerar a trilha");
    spawnSync("ffmpeg", ["-y", "-loglevel", "error", "-i", silent, "-i", wav, "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
      "-shortest", "-movflags", "+faststart", final], { stdio: "inherit" });
  }
  console.log(`[${id}] pronto: ${path.relative(ROOT, final)}`);
}
await browser.close();
