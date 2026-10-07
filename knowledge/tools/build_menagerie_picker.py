#!/usr/bin/env python3
"""build_menagerie_picker.py — D-C349: the 'Menagerie Picker' artifact page (his 20:10 CT 09-30: a test to choose which version of each
animal we keep). One card per COMPARE animal: its comparison sheet (from menagerie_sheets.py) + one button per version + a note.
Picks are stored in the artifact's db (collection 'picks', doc id = animal) so Claude reads them back with ArtifactData.
Output: _build/menagerie-picker/index.html + sheets/*.jpg (JPEG copies of the PNG sheets, for phone loading)."""
import json, html, shutil
from pathlib import Path
from PIL import Image

ROOT = Path("/home/claude"); OUT = ROOT / "_build/menagerie-picker"; SRC = ROOT / "_docs/menagerie/compare"
NAMES = {"AnF": "Animals & Fauna", "WA": "World Animals", "WS": "Wildlife Sanctuary", "WWA": "World Wild Animals", "IFS": "Immersive Fauna",
         "YSav": "yCreatures Savanna", "YTri": "yCreatures", "JP": "Jurassic Project", "OURS": "Ours now (StripMine)"}


def main():
    man = json.loads((ROOT / "_logs/menagerie_sheets.json").read_text())
    (OUT / "sheets").mkdir(parents=True, exist_ok=True)
    cards = []
    for s in man["sheets"]:
        jpg = s["sheet"].replace(".png", ".jpg")
        im = Image.open(SRC / s["sheet"]).convert("RGB")
        if im.width > 1400: im = im.resize((1400, round(im.height * 1400 / im.width)), Image.LANCZOS)
        im.save(OUT / "sheets" / jpg, quality=80, optimize=True)
        cards.append({"n": s["n"], "g": s["group"], "kind": s["kind"], "img": f"sheets/{jpg}",
                      "v": [{"id": f"{v['src']}|{v['key']}", "src": NAMES.get(v["src"], v["src"]), "key": v["key"], "px": v["px"],
                             "cubes": v["cubes"], "bones": v["bones"], "anims": v["anims"][:6], "also": len(v["also"])} for v in s["versions"]]})
    data = json.dumps(cards, separators=(",", ":"))
    nm = json.loads((ROOT / "_docs/menagerie/new/manifest.json").read_text())["tiles"]
    (OUT / "new").mkdir(exist_ok=True)
    for x in nm: shutil.copyfile(ROOT / "_docs/menagerie" / x["img"], OUT / x["img"])
    newdata = json.dumps([{"id": x["id"], "name": x["name"], "src": NAMES.get(x["src"], x["src"]), "img": x["img"], "wilds": x["wilds"]} for x in nm], separators=(",", ":"))
    page = TEMPLATE.replace("__DATA__", data.replace("</", "<\\/")).replace("__NEWDATA__", newdata.replace("</", "<\\/")).replace("__COUNT__", str(len(cards))).replace("__NEWCOUNT__", str(len(nm)))
    (OUT / "index.html").write_text(page, encoding="utf-8")
    size = sum(p.stat().st_size for p in OUT.rglob("*") if p.is_file())
    print(f"{len(cards)} cards, {size / 1e6:.1f} MB -> {OUT}")


TEMPLATE = r"""<title>Menagerie Picker</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bitter:wght@600;700&family=Source+Sans+3:wght@400;600&family=JetBrains+Mono:wght@400;600&display=swap">
<style>
/* Field-guide ledger: one card per animal, the sheet on top, version buttons below; a sticky tally bar. */
:root{
  --bg:#f3f1ea; --card:#fffdf8; --fg:#23271f; --muted:#5d6457; --line:#d9d5c6; --accent:#2f6b3f; --accent-ink:#ffffff; --pick:#e3efe2; --warn:#8a5a12;
  --display:"Bitter",Georgia,serif; --body:"Source Sans 3",system-ui,sans-serif; --mono:"JetBrains Mono",ui-monospace,monospace;
}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--bg:#171a15;--card:#20241d;--fg:#e8e9e1;--muted:#a3aa9a;--line:#3a4034;--accent:#7fbf8c;--accent-ink:#10140f;--pick:#26372a;--warn:#e0b45c;color-scheme:dark}}
:root[data-theme="dark"]{--bg:#171a15;--card:#20241d;--fg:#e8e9e1;--muted:#a3aa9a;--line:#3a4034;--accent:#7fbf8c;--accent-ink:#10140f;--pick:#26372a;--warn:#e0b45c;color-scheme:dark}
body{background:var(--bg);color:var(--fg);font-family:var(--body);font-size:15px;line-height:1.45}
.wrap{max-width:1100px;margin:0 auto;padding-inline:16px;padding-block:12px 64px}
header h1{font-family:var(--display);font-size:1.7rem;margin:.4rem 0 .2rem;text-wrap:balance}
header p{color:var(--muted);margin:0 0 .6rem;max-width:68ch}
.bar{position:sticky;top:env(safe-area-inset-top,0px);z-index:5;background:var(--bg);border-bottom:1px solid var(--line);padding-block:8px;display:flex;flex-wrap:wrap;gap:8px;align-items:center}
.tally{font-family:var(--mono);font-variant-numeric:tabular-nums;font-size:.9rem;margin-right:auto}
.chip{border:1px solid var(--line);background:var(--card);color:var(--fg);border-radius:999px;padding:5px 12px;font:inherit;font-size:.9rem;cursor:pointer}
.chip[aria-pressed="true"]{background:var(--accent);color:var(--accent-ink);border-color:var(--accent)}
#q{flex:1 1 160px;min-width:0;border:1px solid var(--line);background:var(--card);color:var(--fg);border-radius:8px;padding:6px 10px;font:inherit}
.status{font-size:.85rem;color:var(--warn);width:100%}
.list{display:grid;gap:18px;margin-top:14px}
.card{background:var(--card);border:1px solid var(--line);border-radius:10px;overflow:hidden}
.card.done{border-color:var(--accent)}
.head{display:flex;gap:10px;align-items:baseline;padding:10px 14px;flex-wrap:wrap}
.head h2{font-family:var(--display);font-size:1.2rem;margin:0;text-transform:capitalize}
.num{font-family:var(--mono);color:var(--muted);font-size:.85rem}
.kind{font-size:.75rem;letter-spacing:.06em;text-transform:uppercase;color:var(--muted);border:1px solid var(--line);border-radius:4px;padding:1px 6px}
.chosen{margin-left:auto;font-size:.9rem;color:var(--accent);font-weight:600}
.sheet{display:block;background:#fff}
.sheet img{display:block;width:100%;height:auto}
.vs{display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:8px;padding:12px 14px}
.v{text-align:left;border:1px solid var(--line);background:var(--bg);color:var(--fg);border-radius:8px;padding:8px 10px;font:inherit;cursor:pointer;min-width:0}
.v b{display:block;font-size:.95rem}
.v span{display:block;font-family:var(--mono);font-size:.75rem;color:var(--muted);overflow-wrap:anywhere}
.v[aria-pressed="true"]{background:var(--pick);border-color:var(--accent);box-shadow:inset 0 0 0 1px var(--accent)}
.v:focus-visible,.chip:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
.note{padding:0 14px 14px;display:flex;gap:8px;flex-wrap:wrap}
.note textarea{flex:1 1 240px;min-width:0;min-height:2.4em;border:1px solid var(--line);background:var(--bg);color:var(--fg);border-radius:8px;padding:6px 10px;font:inherit;resize:vertical}
.note button{border:1px solid var(--line);background:var(--card);color:var(--fg);border-radius:8px;padding:6px 12px;font:inherit;cursor:pointer}
.empty{color:var(--muted);padding:20px 0}
.tabs{display:flex;gap:6px;flex-wrap:wrap;margin:6px 0 4px}
.tab{border:1px solid var(--line);background:var(--card);color:var(--fg);border-radius:8px 8px 0 0;padding:7px 14px;font:inherit;font-weight:600;cursor:pointer}
.tab[aria-selected="true"]{background:var(--accent);color:var(--accent-ink);border-color:var(--accent)}
.lede{color:var(--muted);max-width:68ch;margin:.4rem 0}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(160px,1fr));gap:10px;margin-top:12px}
.tile{background:var(--card);border:1px solid var(--line);border-radius:8px;overflow:hidden;display:flex;flex-direction:column;min-width:0}
.tile img{display:block;width:100%;height:auto;background:#fff}
.tile .meta{padding:6px 8px;display:flex;flex-direction:column;gap:4px;min-width:0}
.tile .nm{font-weight:600;text-transform:capitalize;overflow-wrap:anywhere}
.tile .src{font-family:var(--mono);font-size:.72rem;color:var(--muted)}
.tile button{border:1px solid var(--line);background:var(--bg);color:var(--fg);border-radius:6px;padding:4px 8px;font:inherit;font-size:.85rem;cursor:pointer}
.tile.skip{opacity:.45}
.tile.skip button{background:var(--pick);border-color:var(--accent)}
</style>
<div class="wrap">
<header>
  <h1>Menagerie Picker</h1>
  <p>Two jobs: choose the version to keep for each of the __COUNT__ animals that more than one pack draws, and skip any of the __NEWCOUNT__ new animals you don't want (second tab). Each comparison picture shows every version side by side (rest pose, default skin, front three-quarter and side; parts the game hides, like chests or food, still show). Tap the version to keep; add a note for a mix ("World Animals model, our skin"). Picks save as you tap and Claude reads them back.</p>
</header>
<nav class="tabs" role="tablist">
  <button class="tab" id="tab-compare" role="tab" aria-selected="true">Choose a version · __COUNT__</button>
  <button class="tab" id="tab-new" role="tab" aria-selected="false">New animals · __NEWCOUNT__</button>
</nav>
<section id="pane-new" hidden>
  <p class="lede">Animals only one pack has and we don't yet. All of them get ported unless you tap <b>Skip</b>. Jurassic ones go to the separate Wilds pack. Pictures: rest pose, default skin.</p>
  <div class="bar"><span class="tally" id="ntally"></span><input id="nq" type="search" placeholder="Find an animal" aria-label="Find a new animal"></div>
  <div class="grid" id="ngrid"></div>
</section>
<section id="pane-compare">
<div class="bar">
  <span class="tally" id="tally">0 / __COUNT__ picked</span>
  <button class="chip" data-f="all" aria-pressed="true">All</button>
  <button class="chip" data-f="open" aria-pressed="false">Still to pick</button>
  <button class="chip" data-f="done" aria-pressed="false">Picked</button>
  <button class="chip" data-f="A" aria-pressed="false">2+ add-ons</button>
  <button class="chip" data-f="B" aria-pressed="false">Add-on vs ours</button>
  <input id="q" type="search" placeholder="Find an animal" aria-label="Find an animal">
  <div class="status" id="status" hidden></div>
</div>
<div class="list" id="list"></div>
</section>
</div>
<script>
const CARDS = __DATA__;
const NEW = __NEWDATA__;
const skips = {};             // pw id -> true when he skips it (collection 'newpicks')
const picks = {};             // animal -> {choice, note}
let db = null, filter = "all", query = "";
const $ = (s, r = document) => r.querySelector(s);
const list = $("#list"), statusEl = $("#status");
function say(t){ statusEl.textContent = t; statusEl.hidden = !t; }
function label(c, id){ const v = c.v.find(x => x.id === id); return v ? `${v.src} · ${v.key}` : id; }
const drafts = {};            // unsaved note text, kept across re-draws
function visible(c){
  const done = !!(picks[c.g] || {}).choice;
  if (filter === "open" && done) return false; if (filter === "done" && !done) return false;
  if ((filter === "A" || filter === "B") && c.kind !== filter) return false;
  return !query || c.g.replace(/_/g, " ").includes(query);
}
function buildCard(c){
  const p = picks[c.g] || {}; const done = !!p.choice;
  const card = document.createElement("article"); card.className = "card" + (done ? " done" : ""); card.id = "a-" + c.g;
  card.innerHTML = `<div class="head"><span class="num">${String(c.n).padStart(3, "0")}</span><h2></h2><span class="kind">${c.kind === "A" ? "2+ add-ons" : "add-on vs ours"}</span><span class="chosen"></span></div>
    <a class="sheet" target="_blank" rel="noopener"><img loading="lazy" alt=""></a><div class="vs"></div>
    <div class="note"><textarea placeholder="Note (optional): a mix, a skin swap, anything off" aria-label="Note"></textarea><button type="button">Save note</button></div>`;
  $("h2", card).textContent = c.g.replace(/_/g, " ");
  $(".chosen", card).textContent = done ? "Keep: " + label(c, p.choice) : "";
  $("a", card).href = c.img; $("img", card).src = c.img; $("img", card).alt = `${c.g} — every version side by side`;
  const vs = $(".vs", card);
  for (const v of c.v){
    const b = document.createElement("button"); b.type = "button"; b.className = "v"; b.setAttribute("aria-pressed", String(p.choice === v.id));
    const t = document.createElement("b"); t.textContent = v.src + (v.also ? `  (+${v.also} alike)` : "");
    const s = document.createElement("span"); s.textContent = `${v.key} · ${v.px ?? "?"} px · ${v.cubes}/${v.bones} cubes/bones${v.anims.length ? " · " + v.anims.join(", ") : ""}`;
    b.append(t, s); b.addEventListener("click", () => choose(c, v.id)); vs.append(b);
  }
  const ta = $("textarea", card); ta.id = "note-" + c.g; ta.value = drafts[c.g] ?? (p.note || "");
  ta.addEventListener("input", () => { drafts[c.g] = ta.value; });
  $(".note button", card).addEventListener("click", () => saveNote(c, ta.value));
  return card;
}
function tally(){ $("#tally").textContent = `${Object.values(picks).filter(p => p.choice).length} / ${CARDS.length} picked`; }
function render(){
  list.textContent = ""; let shown = 0;
  for (const c of CARDS){ if (!visible(c)) continue; shown++; list.append(buildCard(c)); }
  if (!shown){ const e = document.createElement("p"); e.className = "empty"; e.textContent = "Nothing here for this filter."; list.append(e); }
  tally();
}
function redraw(g){             // one card in place (keeps the scroll position)
  const c = CARDS.find(x => x.g === g); const old = document.getElementById("a-" + g);
  if (c && old) old.replaceWith(buildCard(c)); tally();
}
async function write(c, patch){
  const next = { ...(picks[c.g] || {}), ...patch, label: patch.choice ? label(c, patch.choice) : (picks[c.g] || {}).label || "", at: new Date().toISOString() };
  picks[c.g] = next; if (patch.note !== undefined) delete drafts[c.g]; redraw(c.g);
  if (!db){ say("Not saved: storage isn't available in this view. Open the page in the Claude app or claude.ai while signed in."); return; }
  try { await db.doc("picks/" + c.g).set(next); say(""); }
  catch (e){ say("Not saved (" + (e && e.code || "error") + "). Try again in a moment."); }
}
function choose(c, id){ write(c, { choice: (picks[c.g] || {}).choice === id ? "" : id }); }
function saveNote(c, text){ write(c, { note: text.slice(0, 600) }); }
document.querySelectorAll(".chip").forEach(ch => ch.addEventListener("click", () => {
  filter = ch.dataset.f; document.querySelectorAll(".chip").forEach(x => x.setAttribute("aria-pressed", String(x === ch))); render();
}));
$("#q").addEventListener("input", e => { query = e.target.value.trim().toLowerCase(); render(); });
let nquery = "";
function renderNew(){
  const g = $("#ngrid"); g.textContent = "";
  for (const x of NEW){
    if (nquery && !x.name.includes(nquery)) continue;
    const el = document.createElement("div"); el.className = "tile" + (skips[x.id] ? " skip" : "");
    el.innerHTML = `<a target="_blank" rel="noopener"><img loading="lazy" alt=""></a><div class="meta"><span class="nm"></span><span class="src"></span><button type="button"></button></div>`;
    $("a", el).href = x.img; $("img", el).src = x.img; $("img", el).alt = x.name;
    $(".nm", el).textContent = x.name; $(".src", el).textContent = x.src + (x.wilds ? " · Wilds pack" : "");
    const b = $("button", el); b.textContent = skips[x.id] ? "Skipped · undo" : "Skip"; b.setAttribute("aria-pressed", String(!!skips[x.id]));
    b.addEventListener("click", () => toggleSkip(x));
    g.append(el);
  }
  $("#ntally").textContent = `${NEW.length - Object.values(skips).filter(Boolean).length} of ${NEW.length} will be ported`;
}
async function toggleSkip(x){
  skips[x.id] = !skips[x.id]; renderNew();
  if (!db){ say("Not saved: storage isn't available in this view."); return; }
  try { await db.doc("newpicks/" + x.id.replace(":", "_")).set({ id: x.id, skip: !!skips[x.id], at: new Date().toISOString() }); }
  catch (e){ say("Not saved (" + (e && e.code || "error") + ")."); }
}
$("#nq").addEventListener("input", e => { nquery = e.target.value.trim().toLowerCase(); renderNew(); });
function showTab(which){
  $("#tab-compare").setAttribute("aria-selected", String(which === "compare")); $("#tab-new").setAttribute("aria-selected", String(which === "new"));
  $("#pane-compare").hidden = which !== "compare"; $("#pane-new").hidden = which !== "new";
}
$("#tab-compare").addEventListener("click", () => showTab("compare"));
$("#tab-new").addEventListener("click", () => showTab("new"));
render(); renderNew();
(async () => {
  try { db = window.claude ? await window.claude.use("db") : null; } catch { db = null; }
  if (!db){ say("Picks can't be saved in this view (signed out or preview)."); return; }
  let first = true;
  db.collection("picks").onSnapshot(snap => {
    for (const ch of snap.docChanges()){ if (ch.type === "removed") delete picks[ch.doc.id]; else picks[ch.doc.id] = { ...ch.doc.data() }; if (!first) redraw(ch.doc.id); }
    if (first){ first = false; render(); }
  }, () => say("Couldn't load saved picks."));
  db.collection("newpicks").onSnapshot(snap => {
    for (const d of snap.docs){ const v = d.data(); if (v && v.id) skips[v.id] = !!v.skip; }
    renderNew();
  }, () => say("Couldn't load saved skips."));
})();
</script>
"""

if __name__ == "__main__":
    main()
