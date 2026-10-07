// pw_civ.js — CIVITAS structure test commands (PW-TestRunner BP). The checks are civ_verify.js, the same code the
// workspace dedicated server runs before a building is delivered.
//   /scriptevent pw:civ list                       every building this pack knows
//   /scriptevent pw:civ verify <name>              the structure FILE, every cell, as the game reads it
//   /scriptevent pw:civ place <name> [0|90|180|270] place it beside you (street front facing you), then check every
//                                                  block and every marker; turns ladder-hatch hinges with the rotation
// <name> may be given with or without "pw:" (e.g. mvv_cottage_s_a_r1).
import { world, system } from "@minecraft/server";
import { MANIFESTS } from "./civ_manifests.js";
import { verifyFile, placeAndVerify, turnHinges } from "./civ_verify.js";

const ROT = { 0: "None", 90: "Rotate90", 180: "Rotate180", 270: "Rotate270" };

function say(p, msg) {
  try { p.sendMessage(msg); } catch { /* player left */ }
}

function find(name) {
  const id = name.includes(":") ? name : `pw:${name}`;
  return MANIFESTS[id] ? [id, MANIFESTS[id]] : [id, undefined];
}

function report(p, r) {
  if (r.err) { say(p, `§c[CIV] ${r.id} ${r.rot || ""}: ${r.err}`); return; }
  const head = r.ok ? "§a[CIV] PASS" : "§c[CIV] FAIL";
  const ents = r.entities ? ` · markers/hatches ${r.entities.found}/${r.entities.want}` : "";
  say(p, `${head} ${r.id} ${r.rot || "file"} · ${r.cells - r.bad}/${r.cells} cells${ents}`);
  for (const b of r.first || []) say(p, `§7  cell ${b[0]},${b[1]},${b[2]}: ${b[3]} -> ${b[4]}`);
  for (const m of (r.entities && r.entities.missing) || []) say(p, `§7  missing ${m}`);
}

system.afterEvents.scriptEventReceive.subscribe((ev) => {
  if (ev.id !== "pw:civ") return;
  const p = ev.sourceEntity;
  if (!p) return;
  const [cmd, name, rotArg] = (ev.message || "").trim().split(/\s+/);
  if (cmd === "list") {
    say(p, `§e[CIV] ${Object.keys(MANIFESTS).length} buildings: ${Object.keys(MANIFESTS).join(", ")}`);
    return;
  }
  if (!name) { say(p, "§e[CIV] usage: list | verify <name> | place <name> [0|90|180|270]"); return; }
  const [id, man] = find(name);
  if (!man) { say(p, `§c[CIV] unknown building ${id} (try /scriptevent pw:civ list)`); return; }
  if (cmd === "verify") { report(p, verifyFile(id, man)); return; }
  if (cmd === "place") {
    const rot = ROT[parseInt(rotArg || "0", 10)] || "None";
    const l = p.location;
    // the box starts 2 blocks east of you; its datum row sits at your feet
    const at = { x: Math.floor(l.x) + 2, y: Math.floor(l.y) - man.datum_y, z: Math.floor(l.z) };
    say(p, `§e[CIV] placing ${id} (${rot}) at ${at.x} ${at.y} ${at.z} …`);
    placeAndVerify(id, man, p.dimension, at, rot).then((r) => {
      const h = turnHinges(p.dimension, at, man, rot);
      report(p, r);
      if (h) say(p, `§7  ${h} ladder hatch hinge(s) turned with the building`);
    }).catch((e) => say(p, `§c[CIV] place failed: ${e}`));
    return;
  }
  say(p, "§e[CIV] usage: list | verify <name> | place <name> [0|90|180|270]");
});

world.afterEvents.worldLoad.subscribe(() => {
  console.warn(`[CIV] structure tests loaded — ${Object.keys(MANIFESTS).length} building(s)`);
});
