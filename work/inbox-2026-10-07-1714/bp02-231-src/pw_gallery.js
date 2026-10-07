// pw_gallery.js — THE GALLERY (D-C571 v2, his 22:01): thousands of public-domain paintings hang in the CIVITAS buildings and
// the palace as pw:art_<key> entities (one entity type per work, RP-08 holds the framed textures); every hung picture is a
// UNIQUE work drawn from the world's catalogue (a registry bitset in a dynamic property, never repeating until the
// catalogue is spent); the Connoisseur's Book (pw:connoisseur_book) reads any of them: artist, date, the artist's life,
// the work, a reading, a critique (educational; readings are labelled as readings).
//   API (the clock): hangBuilding(dim, b, def) -> n hung  (def.art = slots [cx, yb, cz, w, h, facing, subject] local floats)
//   commands: /scriptevent pw:gallery status | test [n] | hang <key> | unused | reset
import { world, system, ItemStack } from "@minecraft/server";
import { ActionFormData } from "@minecraft/server-ui";
import { WORKS, ARTISTS, SUBJECTS, SOURCES } from "./pw_gallery_data.js";
import { TEXT, BIOS } from "./pw_gallery_text.js";

const USED_KEY = "pw:gallery_used";                       // a string of 0/1 per catalogue index
const N = WORKS.length;
// WORKS[i] = [key, title, artistKey, date, year, medium, dims, src, subject, w, h, famous, url, palaceOk, credit]
const F = { key: 0, title: 1, artist: 2, date: 3, year: 4, medium: 5, dims: 6, src: 7, subject: 8, w: 9, h: 10, famous: 11, url: 12, palace: 13, credit: 14 };
const BY_KEY = new Map(WORKS.map((w, i) => [w[F.key], i]));
const kid = (key) => key.toLowerCase().replace(/[^a-z0-9]+/g, "_");
const typeOf = (i) => `pw:art_${kid(WORKS[i][F.key])}`;
const KID_INDEX = new Map(WORKS.map((w, i) => [kid(w[F.key]), i]));

let used = null;
function loadUsed() {
  if (used) return used;
  let s = "";
  try { s = String(world.getDynamicProperty(USED_KEY) || ""); } catch { s = ""; }
  used = new Uint8Array(N);
  for (let i = 0; i < Math.min(s.length, N); i++) used[i] = s.charCodeAt(i) === 49 ? 1 : 0;
  return used;
}
function saveUsed() {
  if (!used) return;
  let s = "";
  for (let i = 0; i < N; i++) s += used[i] ? "1" : "0";
  try { world.setDynamicProperty(USED_KEY, s); } catch (e) { console.warn(`[GALLERY] registry: ${e}`); }
}
function usedCount() { const u = loadUsed(); let n = 0; for (let i = 0; i < N; i++) n += u[i]; return n; }

// a small deterministic generator per pick (mulberry32), seeded by the world's day and the slot so a re-run differs
function rng(seed) {
  let a = seed >>> 0;
  return () => { a = (a + 0x6D2B79F5) >>> 0; let t = a; t = Math.imul(t ^ (t >>> 15), t | 1); t ^= t + Math.imul(t ^ (t >>> 7), t | 61); return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };
}

/** an unused work that fits the slot (w x h blocks), of the subject when one is asked, the palace's period when asked;
 *  among the fitting works the LARGER classes are preferred (a state room gets its canvases) with some chance */
function pick(subject, w, h, palaceOnly, pickf) {
  const u = loadUsed();
  const want = subject && subject !== "any" ? SUBJECTS.indexOf(subject) : -1;
  let best = [], bestArea = 0;
  const pool = [];
  for (let i = 0; i < N; i++) {
    if (u[i]) continue;
    const r = WORKS[i];
    if (r[F.w] > w || r[F.h] > h) continue;
    if (palaceOnly && !r[F.palace]) continue;
    if (want >= 0 && r[F.subject] !== want) continue;
    const area = r[F.w] * r[F.h];
    pool.push([i, area]);
    if (area > bestArea) bestArea = area;
  }
  if (!pool.length) return want >= 0 ? pick("any", w, h, palaceOnly, pickf) : (palaceOnly ? pick(subject, w, h, false, pickf) : -1);
  // the biggest fitting classes (>= 55 % of the best area) make the short list; the rest only when the short list is thin
  for (const [i, area] of pool) if (area >= bestArea * 0.55) best.push(i);
  if (best.length < 4) best = pool.map((p) => p[0]);
  return best[Math.floor(pickf() * best.length)];
}

function rotSlot(X, Z, sx, sz, r) {
  if (r === 1) return [sz - Z, X];
  if (r === 2) return [sx - X, sz - Z];
  if (r === 3) return [Z, sx - X];
  return [X, Z];
}

/** hang one work at a world position: the entity's feet at the picture's bottom edge, centred on (x, z) */
export function hangAt(dim, x, y, z, facing, i, tags = []) {
  const e = dim.spawnEntity(typeOf(i), { x, y, z });
  try { e.setRotation({ x: 0, y: 0 }); } catch { /* left */ }               // 1.3.224: the frame bones assume yaw 0 (RP-12 1.0.1)
  e.setProperty("pw:facing", facing);
  e.addTag("pw_art");
  for (const t of tags) e.addTag(t);
  const u = loadUsed();
  u[i] = 1;
  return e;
}

/** the clock's call at the furnished stage (and on its sweep until done): every art slot of the building gets a unique
 *  work. RESUMABLE (gallery gate run 1: a spawn in a chunk that was loaded but not ticking threw and the building kept
 *  only the pictures hung before it): progress lives in b.artNext; b.artDone marks the end (all slots, or the catalogue
 *  spent). Returns the number hung on this call; b.art accumulates the total. */
export function hangBuilding(dim, b, def, seed = 0, maxN = 8) {          // 1.3.224: at most maxN pictures per call (a palace piece's 70 in one tick was part of the slow ticks); the sweep finishes the rest
  const slots = def.art || [];
  if (!slots.length) { b.artDone = true; return 0; }
  const [sx, , sz] = def.size;
  const pickf = rng((seed || 0) * 7919 + (b.id || 0) * 104729 + 17 + (b.artNext || 0));
  const palace = !!b.palace;
  let n = 0, k = b.artNext || 0;
  for (; k < slots.length && n < maxN; k++) {
    const [cx, yb, cz, w, h, facing, subject] = slots[k];
    const [X, Z] = rotSlot(cx, cz, sx, sz, b.rot || 0);
    const f = ((facing | 0) + (b.rot || 0)) % 4;
    // the slot's chunk must be loaded AND ticking before a work is drawn (a failed spawn would still burn the work)
    let ok = false;
    try { ok = !!dim.getBlock({ x: Math.floor(b.x + X), y: Math.floor(b.y + def.datum_y + yb), z: Math.floor(b.z + Z) }); } catch { ok = false; }
    if (!ok) break;
    const i = pick(subject, w, h, palace, pickf);
    if (i < 0) { k = slots.length; break; }                               // the catalogue is spent
    const r = WORKS[i];
    const y = b.y + def.datum_y + yb + (h - r[F.h]) / 2;                // a smaller work hangs centred in its slot
    try {
      hangAt(dim, b.x + X, y, b.z + Z, f, i, [`civ:b:${b.id}`]);
      n++;
    } catch (e) {
      loadUsed()[i] = 0;                                                // the work is not hung: give it back
      console.warn(`[GALLERY] #${b.id} slot ${k} (${cx} ${yb} ${cz}): ${e}`);
      break;
    }
  }
  b.artNext = k;
  b.art = (b.art || 0) + n;
  if (k >= slots.length) b.artDone = true;
  if (n) saveUsed();
  return n;
}

// ------------------------------------------------------------------------------------------------ the book
function label(i) {
  const r = WORKS[i];
  const a = ARTISTS[r[F.artist]] || [r[F.artist], "", ""];
  return `${r[F.title]} — ${a[0]}${r[F.date] ? `, ${r[F.date]}` : ""}`;
}
function essay(i) {
  const r = WORKS[i];
  const a = ARTISTS[r[F.artist]] || [r[F.artist], "", ""];
  const t = TEXT[r[F.key]] || {};
  const bio = BIOS[r[F.artist]] || `${a[0]}${a[1] ? ` (${a[1]}${a[2] ? `, ${a[2]}` : ""})` : ""}. A life for this painter is still being written.`;
  const parts = [
    `§e${a[0]}§r${a[1] ? ` §7(${a[1]}${a[2] ? `, ${a[2]}` : ""})§r` : ""}`,
    `${r[F.date] || "undated"}${r[F.medium] ? ` · ${r[F.medium]}` : ""}${r[F.dims] ? ` · ${r[F.dims]}` : ""}`,
    `§7${SOURCES[r[F.src]]}${r[F.famous] ? " · a celebrated work" : ""}§r`,
    "",
    "§lTHE ARTIST§r", bio,
    "",
    "§lTHE WORK§r", t.d || "A description of this picture is still to be written: look at it — what is shown, how the light falls, where the eye goes first.",
    "",
    "§lREADING IT§r §7(an interpretation, not a fact)§r", t.i || "No reading has been written for this work yet.",
    "",
    "§lA CRITIQUE§r §7(one critic's view)§r", t.c || "No critique has been written for this work yet.",
    "",
    `§7${r[F.credit] || ""}${r[F.url] ? `\n${r[F.url]}` : ""}§r`,
  ];
  return parts.join("\n");
}
async function showWork(player, i, back) {
  const r = WORKS[i];
  const f = new ActionFormData().title(r[F.title].slice(0, 60)).body(essay(i));
  f.button(`More by ${(ARTISTS[r[F.artist]] || [r[F.artist]])[0]}`);
  f.button("Works hanging nearby");
  if (back) f.button("« Back");
  f.button("Close");
  const res = await f.show(player);
  if (res.canceled) return;
  if (res.selection === 0) return showArtist(player, r[F.artist], () => showWork(player, i, back));
  if (res.selection === 1) return showNearby(player, () => showWork(player, i, back));
  if (back && res.selection === 2) return back();
}
async function showArtist(player, akey, back) {
  const a = ARTISTS[akey] || [akey, "", ""];
  const mine = [];
  for (let i = 0; i < N; i++) if (WORKS[i][F.artist] === akey) mine.push(i);
  const hung = new Set();
  try { for (const e of player.dimension.getEntities({ tags: ["pw_art"], location: player.location, maxDistance: 96 })) { const k = KID_INDEX.get(e.typeId.replace("pw:art_", "")); if (k !== undefined) hung.add(k); } } catch { /* unloaded */ }
  const body = `${BIOS[akey] || `${a[0]}${a[1] ? ` (${a[1]}${a[2] ? `, ${a[2]}` : ""})` : ""}.`}\n\n§7${mine.length} work(s) in the catalogue; ${mine.filter((i) => hung.has(i)).length} hanging within 96 blocks.§r`;
  const f = new ActionFormData().title(a[0].slice(0, 60)).body(body);
  const list = mine.slice(0, 40);
  for (const i of list) f.button(`${hung.has(i) ? "§2● " : ""}${WORKS[i][F.title].slice(0, 44)}${WORKS[i][F.date] ? ` (${WORKS[i][F.date]})` : ""}`);
  f.button("« Back");
  const res = await f.show(player);
  if (res.canceled) return;
  if (res.selection < list.length) return showWork(player, list[res.selection], () => showArtist(player, akey, back));
  if (back) return back();
}
async function showNearby(player, back) {
  const near = [];
  try {
    for (const e of player.dimension.getEntities({ tags: ["pw_art"], location: player.location, maxDistance: 48 })) {
      const k = KID_INDEX.get(e.typeId.replace("pw:art_", ""));
      if (k === undefined) continue;
      const d = Math.hypot(e.location.x - player.location.x, e.location.y - player.location.y, e.location.z - player.location.z);
      near.push([d, k]);
    }
  } catch { /* unloaded */ }
  near.sort((p, q) => p[0] - q[0]);
  const f = new ActionFormData().title("Works hanging nearby").body(near.length ? `${near.length} picture(s) within 48 blocks, nearest first.` : "No pictures hang within 48 blocks of you.");
  const list = near.slice(0, 40);
  for (const [d, i] of list) f.button(`${label(i).slice(0, 52)} §7(${d.toFixed(0)} m)§r`);
  f.button(back ? "« Back" : "Close");
  const res = await f.show(player);
  if (res.canceled) return;
  if (res.selection < list.length) return showWork(player, list[res.selection][1], () => showNearby(player, back));
  if (back) return back();
}
async function showCatalogue(player) {
  const f = new ActionFormData().title("The Connoisseur's Book").body(`${N} works are known to this book; ${usedCount()} hang somewhere in this world. Browse by subject, or read what hangs nearby.`);
  f.button("Works hanging nearby");
  for (const s of SUBJECTS) f.button(`By subject: ${s.replace("_", " / ")}`);
  f.button("Close");
  const res = await f.show(player);
  if (res.canceled || res.selection === SUBJECTS.length + 1) return;
  if (res.selection === 0) return showNearby(player, () => showCatalogue(player));
  const si = res.selection - 1;
  const u = loadUsed();
  const hung = [];
  for (let i = 0; i < N && hung.length < 40; i++) if (u[i] && WORKS[i][F.subject] === si) hung.push(i);
  const g = new ActionFormData().title(SUBJECTS[si].replace("_", " / ")).body(hung.length ? `${hung.length} ${SUBJECTS[si].replace("_", " / ")} work(s) hang in this world (first 40).` : "Nothing of this subject hangs in this world yet.");
  for (const i of hung) g.button(label(i).slice(0, 56));
  g.button("« Back");
  const r2 = await g.show(player);
  if (r2.canceled) return;
  if (r2.selection < hung.length) return showWork(player, hung[r2.selection], () => showCatalogue(player));
  return showCatalogue(player);
}

const busy = new Set();
function open(player, fn) {
  if (busy.has(player.id)) return;
  busy.add(player.id);
  Promise.resolve(fn()).catch((e) => console.warn(`[GALLERY] form: ${e}`)).finally(() => busy.delete(player.id));
}

// ------------------------------------------------------------------------------------------------ the wand (1.3.224, his 16:50)
// The Curator's Wand takes a picture off the wall: the entity goes and a FRAMED PAINTING item (the same work) drops where it
// hung. The framed painting, used on the face of a solid block, hangs that work there (flush, facing out of the wall).
const WAND = "pw:curators_wand", FRAMED = "pw:framed_painting";
function framedItem(i) {
  const it = new ItemStack(FRAMED, 1);
  it.setDynamicProperty("pw:work", WORKS[i][F.key]);
  const r = WORKS[i];
  const a = ARTISTS[r[F.artist]] || [r[F.artist]];
  it.setLore([`§e${r[F.title]}`, `§7${a[0]}${r[F.date] ? `, ${r[F.date]}` : ""}`, `§8${r[F.w]} x ${r[F.h]} blocks — use on a wall to hang it`]);
  return it;
}
function takeDown(p, t) {
  if (!t || !t.isValid || !t.typeId.startsWith("pw:art_")) return;
  const i = KID_INDEX.get(t.typeId.replace("pw:art_", ""));
  if (i === undefined) return;
  const at = t.location, dim = t.dimension;
  t.remove();                                                            // the work stays 'used': it now lives in the item
  try { dim.spawnItem(framedItem(i), { x: at.x, y: at.y + 0.5, z: at.z }); } catch (e) { console.warn(`[GALLERY] wand drop: ${e}`); }
  try { p.onScreenDisplay.setActionBar(`§6Taken down:§r ${label(i)}`); } catch { /* */ }
}
const FACE_FACING = { North: 0, East: 1, South: 2, West: 3 };
const FACE_STEP = { North: [0, -1], East: [1, 0], South: [0, 1], West: [-1, 0] };
world.beforeEvents.playerInteractWithBlock.subscribe((ev) => {
  if (!ev.itemStack || ev.itemStack.typeId !== FRAMED) return;
  ev.cancel = true;
  if (ev.isFirstEvent === false) return;
  const key = ev.itemStack.getDynamicProperty("pw:work");
  const p = ev.player, blk = ev.block, face = ev.blockFace;
  system.run(() => {
    const i = BY_KEY.get(String(key));
    if (i === undefined) { try { p.onScreenDisplay.setActionBar("§cThis frame is empty"); } catch { /* */ } return; }
    if (FACE_FACING[face] === undefined) { try { p.onScreenDisplay.setActionBar("§7Hang it on the side of a wall, not a floor or ceiling"); } catch { /* */ } return; }
    const [dx, dz] = FACE_STEP[face];
    const x = blk.location.x + dx, y = blk.location.y, z = blk.location.z + dz;
    let air;
    try { air = p.dimension.getBlock({ x, y, z }); } catch { air = undefined; }
    if (!air || !(air.isAir || air.typeId === "minecraft:air")) { try { p.onScreenDisplay.setActionBar("§7No room in front of that wall"); } catch { /* */ } return; }
    try { hangAt(p.dimension, x + 0.5, y, z + 0.5, FACE_FACING[face], i, ["gallery:player"]); saveUsed(); }
    catch (e) { console.warn(`[GALLERY] hang: ${e}`); return; }
    try { const inv = p.getComponent("minecraft:inventory").container; const held = inv.getItem(p.selectedSlotIndex); if (held && held.typeId === FRAMED) inv.setItem(p.selectedSlotIndex, undefined); } catch { /* */ }
    try { p.onScreenDisplay.setActionBar(`§6Hung:§r ${label(i)}`); } catch { /* */ }
  });
});
world.afterEvents.entityHitEntity.subscribe((ev) => {
  const p = ev.damagingEntity, t = ev.hitEntity;
  if (!p || p.typeId !== "minecraft:player" || !t || !t.typeId.startsWith("pw:art_")) return;
  let held;
  try { held = p.getComponent("minecraft:inventory").container.getItem(p.selectedSlotIndex); } catch { held = undefined; }
  if (held && held.typeId === WAND) takeDown(p, t);
});

world.beforeEvents.playerInteractWithEntity.subscribe((ev) => {
  const t = ev.target;
  if (!t || !t.typeId.startsWith("pw:art_")) return;
  const i = KID_INDEX.get(t.typeId.replace("pw:art_", ""));
  if (i === undefined) return;
  ev.cancel = true;
  if (ev.itemStack && ev.itemStack.typeId === WAND) { const pw = ev.player; system.run(() => takeDown(pw, t)); return; }
  const book = ev.itemStack && ev.itemStack.typeId === "pw:connoisseur_book";
  const p = ev.player;
  system.run(() => {
    if (book) open(p, () => showWork(p, i, null));
    else { try { p.onScreenDisplay.setActionBar(`§e${label(i)}§r §7— read it with the Connoisseur's Book§r`); } catch { /* */ } }
  });
});
world.afterEvents.itemUse.subscribe((ev) => {
  if (!ev.itemStack || ev.itemStack.typeId !== "pw:connoisseur_book") return;
  const p = ev.source;
  system.run(() => open(p, () => showCatalogue(p)));
});

// ------------------------------------------------------------------------------------------------ commands
system.afterEvents.scriptEventReceive.subscribe((ev) => {
  if (ev.id !== "pw:gallery") return;
  const [cmd, ...rest] = (ev.message || "").trim().split(/\s+/);
  const p = ev.sourceEntity && ev.sourceEntity.typeId === "minecraft:player" ? ev.sourceEntity : null;
  const say = (m) => { if (p) p.sendMessage(m); else console.warn(m.replace(/§./g, "")); };
  try {
    if (!cmd || cmd === "status") { say(`§6[GALLERY]§r ${N} works in the catalogue, ${usedCount()} hung in this world, ${Object.keys(ARTISTS).length} artists, ${Object.keys(TEXT).length} with texts, ${Object.keys(BIOS).length} lives`); return; }
    if (cmd === "unused") { say(`§6[GALLERY]§r ${N - usedCount()} works still unhung`); return; }
    if (cmd === "reset") { used = new Uint8Array(N); saveUsed(); say("§6[GALLERY]§r registry cleared (pictures already hanging stay; new ones may repeat them)"); return; }
    if (cmd === "test" || cmd === "testat") {                              // n works in a ring around the player (or x y z), facing in
      let x, y, z, n, dim;
      if (cmd === "testat") { x = parseFloat(rest[0]); y = parseFloat(rest[1]); z = parseFloat(rest[2]); n = parseInt(rest[3] || "6", 10) || 6; dim = world.getDimension("overworld"); }
      else { if (!p) { say("test needs a player (the harness: testat x y z [n])"); return; } ({ x, y, z } = p.location); n = parseInt(rest[0] || "6", 10) || 6; dim = p.dimension; }
      if (!(Number.isFinite(x) && Number.isFinite(y) && Number.isFinite(z))) { say("usage: testat x y z [n]"); return; }
      n = Math.max(1, Math.min(24, n));
      const pickf = rng(system.currentTick);
      let hung = 0;
      for (let k = 0; k < n; k++) {
        const ang = k / n * Math.PI * 2;
        const i = pick(SUBJECTS[k % SUBJECTS.length], 3, 3, false, pickf);
        if (i < 0) break;
        const fx = Math.cos(ang), fz = Math.sin(ang);
        const facing = Math.abs(fx) > Math.abs(fz) ? (fx > 0 ? 3 : 1) : (fz > 0 ? 0 : 2);   // faces the player
        hangAt(dim, Math.round(x + fx * 5) + 0.5, Math.floor(y) + 1, Math.round(z + fz * 5) + 0.5, facing, i, ["gallery:test"]);
        hung++;
      }
      saveUsed();
      say(`§6[GALLERY]§r ${hung} test work(s) hung in a ring at ${Math.round(x)} ${Math.round(y)} ${Math.round(z)} (tag gallery:test; /kill @e[tag=gallery:test] removes them)`);
      return;
    }
    if (cmd === "hang") {
      if (!p) { say("hang needs a player"); return; }
      const i = BY_KEY.get(rest[0]) ?? KID_INDEX.get(rest[0]);
      if (i === undefined) { say(`§c[GALLERY]§r unknown key ${rest[0]} (nga:1236, met:437372, cma:1944_90 …)`); return; }
      const { x, y, z } = p.location;
      hangAt(p.dimension, Math.round(x) + 0.5, Math.floor(y) + 1, Math.round(z + 3) + 0.5, 0, i, ["gallery:test"]);
      saveUsed();
      say(`§6[GALLERY]§r hung ${label(i)} 3 blocks south of you, facing north`);
      return;
    }
    say(`§6[GALLERY]§r status | test [n] | hang <key> | unused | reset`);
  } catch (e) { say(`§c[GALLERY]§r ${e}`); }
});

console.warn(`[GALLERY] ${N} works, ${Object.keys(ARTISTS).length} artists, ${Object.keys(TEXT).length} texts, ${Object.keys(BIOS).length} lives loaded`);
