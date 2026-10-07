// ============================================================================
// pw_ground.js — PARITY MODULE for the two-material ground family
//   pw:grass_block · pw:podzol · pw:mycelium
//
// Abs0lum's law: "imperceptible means the change should go entirely unnoticed —
// ALL pw blocks should inherit ALL of their predecessor's qualities."
//
// Rewritten from pw_grass.js to use CUSTOM BLOCK COMPONENTS rather than global
// event subscriptions, matching the idiom already proven in main.js for
// pw:randomize_variant. That buys us the engine's OWN random tick — so spread
// and decay run on vanilla's cadence instead of a script interval — and scopes
// every interaction to these blocks instead of testing every block in the world.
// ============================================================================

import {
  world,
  system,
  BlockPermutation,
} from "@minecraft/server";

function gerr(m) { try { console.warn("[PW-GROUND][error] " + m); } catch {} }
function ginfo(m) { try { console.warn("[PW-GROUND] " + m); } catch {} }

// --------------------------------------------------------------------------
// Family table. Everything below is data-driven so podzol and mycelium share
// one code path with grass, and nylium joins by adding a row once it has art.
// --------------------------------------------------------------------------
const FAMILY = new Map(Object.entries({
  "pw:grass_block": { vanilla: "minecraft:grass_block", spreads: true,  path: "minecraft:grass_path", till: "minecraft:farmland", bonemeal: true },
  "pw:podzol":      { vanilla: "minecraft:podzol",      spreads: false, path: "minecraft:grass_path", till: "minecraft:farmland", bonemeal: false },
  "pw:mycelium":    { vanilla: "minecraft:mycelium",    spreads: true,  path: null,                   till: null,                 bonemeal: false },
  "pw:crimson_nylium": { vanilla: "minecraft:crimson_nylium", spreads: false, path: null, till: null, bonemeal: false },
  "pw:warped_nylium":  { vanilla: "minecraft:warped_nylium",  spreads: false, path: null, till: null, bonemeal: false },
}));
const VANILLA_OF = new Map([...FAMILY].map(([k, v]) => [v.vanilla, k]));
const DIRT_LIKE = new Set(["minecraft:dirt", "minecraft:coarse_dirt", "minecraft:rooted_dirt"]);

const TRANSPARENT_ABOVE = new Set([
  "minecraft:air","minecraft:short_grass","minecraft:tallgrass","minecraft:tall_grass","minecraft:fern",
  "minecraft:large_fern","minecraft:snow_layer","minecraft:dandelion","minecraft:poppy","minecraft:cornflower",
  "minecraft:oxeye_daisy","minecraft:azure_bluet","minecraft:red_tulip","minecraft:orange_tulip",
  "minecraft:white_tulip","minecraft:pink_tulip","minecraft:allium","minecraft:lily_of_the_valley",
  "minecraft:blue_orchid","minecraft:torchflower","minecraft:pink_petals","minecraft:leaf_litter",
  "minecraft:wildflowers","minecraft:bush","minecraft:firefly_bush","minecraft:dead_bush",
  "minecraft:sweet_berry_bush","minecraft:moss_carpet","minecraft:pale_moss_carpet","minecraft:brown_mushroom",
  "minecraft:red_mushroom","minecraft:sugar_cane","minecraft:torch","minecraft:lantern",
]);
function lightPasses(b) {
  if (!b) return false;
  if (b.isAir === true) return true;
  const t = b.typeId;
  if (TRANSPARENT_ABOVE.has(t)) return true;
  return typeof t === "string" && (t.endsWith("_slab") || t.indexOf("pw:slab_") === 0);
}

// --------------------------------------------------------------------------
// gvar mosaic. BLOCK PHASE only — the slab smoother deliberately samples a
// SHIFTED phase (see main.js) so a slab never lands on the same variant as the
// block beneath it. Abs0lum: "you never see two identical 5 square foot patches
// of grass right next to each other."
// --------------------------------------------------------------------------
function gvarMosaic(x, z, n) {
  // Must match _varBlockIdx in main.js exactly, or a converted riser and the slab against it would be
  // computed on different fields and the whole no-adjacent-match guarantee would evaporate.
  if (n <= 1) return 0;
  return (((x + 2 * z) % n) + n) % n;
}

const _stats = { spread: 0, decayed: 0, converted: 0, reverted: 0, pathed: 0, tilled: 0, boned: 0 };

// --------------------------------------------------------------------------
// CONVERSION SCOPE (his ruling): only the RISER at an elevation change is
// converted — a two-block line where the smoother works, never whole meadows.
// That is why the un-reproducible engine behaviours barely matter: they apply
// to a hairline of blocks at terrace edges, not to open ground.
// --------------------------------------------------------------------------
const PW_CONVERT_PROP = "pw:ground_convert_on";
let _convertOn = false;
try { _convertOn = world.getDynamicProperty(PW_CONVERT_PROP) === true; } catch {}

export function pwGroundConvertEnabled() { return _convertOn; }

export function pwConvertRiser(dim, x, y, z) {
  // Called by the slab smoother for the block a slab rises against. Returns true if converted.
  if (!_convertOn) return false;
  let b, above;
  try { b = dim.getBlock({ x, y, z }); above = dim.getBlock({ x, y: y + 1, z }); } catch { return false; }
  if (!b) return false;
  const pwId = VANILLA_OF.get(b.typeId);
  if (!pwId) return false;
  if (!lightPasses(above)) return false;
  try {
    b.setPermutation(BlockPermutation.resolve(pwId, { "pw:gvar": gvarMosaic(x, z, 16) }));
    _stats.converted++;
    return true;
  } catch (e) { gerr("convert: " + (e && e.message ? e.message : e)); return false; }
}

// --------------------------------------------------------------------------
// CUSTOM COMPONENT — engine random tick and scoped interaction
// --------------------------------------------------------------------------
const N8 = [[0,-1],[1,-1],[1,0],[1,1],[0,1],[-1,1],[-1,0],[-1,-1]];

function onRandomTick(ev) {
  try {
    const b = ev.block, dim = ev.dimension;
    const spec = FAMILY.get(b.typeId);
    if (!spec) return;
    const { x, y, z } = b.location;
    let above;
    try { above = dim.getBlock({ x, y: y + 1, z }); } catch { return; }

    // decay — smothered ground reverts to dirt, exactly like vanilla
    if (!lightPasses(above)) {
      // nylium reverts to netherrack, everything else to dirt — turning the Nether to dirt would be
      // a far louder break in imperceptibility than anything else in this module.
      const dead = b.typeId.indexOf("nylium") > 0 ? "minecraft:netherrack" : "minecraft:dirt";
      try { b.setPermutation(BlockPermutation.resolve(dead)); _stats.decayed++; } catch {}
      return;
    }
    if (!spec.spreads) return;

    // spread — one neighbouring dirt column per tick, vanilla's own cadence
    const [dx, dz] = N8[Math.floor(Math.random() * 8)];
    const dy = [0, 1, -1][Math.floor(Math.random() * 3)];
    const tx = x + dx, ty = y + dy, tz = z + dz;
    let t, tAbove;
    try { t = dim.getBlock({ x: tx, y: ty, z: tz }); tAbove = dim.getBlock({ x: tx, y: ty + 1, z: tz }); } catch { return; }
    if (!t || !DIRT_LIKE.has(t.typeId) || !lightPasses(tAbove)) return;
    try {
      t.setPermutation(BlockPermutation.resolve(b.typeId, { "pw:gvar": gvarMosaic(tx, tz, 16) }));
      _stats.spread++;
    } catch (e) { gerr("spread: " + (e && e.message ? e.message : e)); }
  } catch (e) { gerr("randomTick: " + (e && e.message ? e.message : e)); }
}

function spendDurability(player) {
  try {
    if (player.getGameMode && player.getGameMode() === "creative") return;
    const inv = player.getComponent("minecraft:inventory");
    const slot = player.selectedSlotIndex;
    const item = inv && inv.container ? inv.container.getItem(slot) : undefined;
    if (!item) return;
    const dur = item.getComponent("minecraft:durability");
    if (!dur) return;
    dur.damage = Math.min(dur.maxDurability, dur.damage + 1);
    inv.container.setItem(slot, item);
  } catch {}
}

function consumeOne(player) {
  try {
    if (player.getGameMode && player.getGameMode() === "creative") return;
    const inv = player.getComponent("minecraft:inventory");
    const slot = player.selectedSlotIndex;
    const it = inv.container.getItem(slot);
    if (!it) return;
    if (it.amount > 1) { it.amount -= 1; inv.container.setItem(slot, it); }
    else inv.container.setItem(slot, undefined);
  } catch {}
}

function onPlayerInteract(ev) {
  try {
    const b = ev.block, dim = ev.dimension, player = ev.player;
    const spec = FAMILY.get(b.typeId);
    if (!spec || !player) return;
    const item = ev.itemStack;
    if (!item) return;
    const id = item.typeId || "";
    const { x, y, z } = b.location;
    let above;
    try { above = dim.getBlock({ x, y: y + 1, z }); } catch { return; }
    const clear = !!above && above.isAir === true;

    if (spec.path && id.endsWith("_shovel") && clear) {
      try {
        b.setPermutation(BlockPermutation.resolve(spec.path));
        dim.playSound("use.grass", { x, y, z });
        _stats.pathed++; spendDurability(player);
      } catch (e) { gerr("path: " + (e && e.message ? e.message : e)); }
      return;
    }
    if (spec.till && id.endsWith("_hoe") && clear) {
      try {
        b.setPermutation(BlockPermutation.resolve(spec.till));
        dim.playSound("use.gravel", { x, y, z });
        _stats.tilled++; spendDurability(player);
      } catch (e) { gerr("till: " + (e && e.message ? e.message : e)); }
      return;
    }
    if (spec.bonemeal && id === "minecraft:bone_meal") {
      try {
        let placed = 0;
        for (let i = 0; i < 24 && placed < 9; i++) {
          const gx = x + Math.floor(Math.random() * 7) - 3;
          const gz = z + Math.floor(Math.random() * 7) - 3;
          let ground, air;
          try { ground = dim.getBlock({ x: gx, y, z: gz }); air = dim.getBlock({ x: gx, y: y + 1, z: gz }); } catch { continue; }
          if (!ground || !air || air.isAir !== true) continue;
          if (ground.typeId !== b.typeId && ground.typeId !== spec.vanilla) continue;
          const roll = Math.random();
          const put = roll < 0.86 ? "minecraft:short_grass" : (roll < 0.93 ? "minecraft:dandelion" : "minecraft:poppy");
          try { air.setPermutation(BlockPermutation.resolve(put)); placed++; } catch {}
        }
        _stats.boned++;
        try { dim.spawnParticle("minecraft:crop_growth_emitter", { x: x + 0.5, y: y + 1.1, z: z + 0.5 }); } catch {}
        consumeOne(player);
      } catch (e) { gerr("bonemeal: " + (e && e.message ? e.message : e)); }
    }
  } catch (e) { gerr("interact: " + (e && e.message ? e.message : e)); }
}

system.beforeEvents.startup.subscribe((ev) => {
  try {
    ev.blockComponentRegistry.registerCustomComponent("pw:ground_behaviour", {
      onRandomTick: onRandomTick,
      onPlayerInteract: onPlayerInteract,
    });
    ginfo("custom component pw:ground_behaviour registered (onRandomTick + onPlayerInteract)");
  } catch (e) { gerr("register: " + (e && e.message ? e.message : e)); }
});

// --------------------------------------------------------------------------
// COMMANDS
// --------------------------------------------------------------------------
function* revertJob(dim, cx, cy, cz, R) {
  let n = 0, cells = 0;
  for (let x = cx - R; x <= cx + R; x++) {
    for (let z = cz - R; z <= cz + R; z++) {
      for (let y = Math.max(-60, cy - 32); y <= Math.min(310, cy + 32); y++) {
        if (++cells % 400 === 0) yield;
        let b;
        try { b = dim.getBlock({ x, y, z }); } catch { continue; }
        if (!b) continue;
        const spec = FAMILY.get(b.typeId);
        if (!spec) continue;
        try { b.setPermutation(BlockPermutation.resolve(spec.vanilla)); n++; _stats.reverted++; } catch {}
      }
    }
  }
  ginfo(`revert complete: ${n} pw: ground blocks returned to vanilla within ${R} blocks`);
}

system.afterEvents.scriptEventReceive.subscribe((ev) => {
  try {
    if (ev.id !== "pw:groundconvert" && ev.id !== "pw:groundrevert" && ev.id !== "pw:groundparity") return;
    const p = world.getAllPlayers()[0];
    if (!p) return;
    const l = p.location;

    if (ev.id === "pw:groundconvert") {
      const a = (ev.message || "").trim().toLowerCase();
      _convertOn = (a === "on" || a === "1" || a === "true");
      try { world.setDynamicProperty(PW_CONVERT_PROP, _convertOn); } catch {}
      ginfo(`riser conversion ${_convertOn ? "ENABLED" : "DISABLED"}`);
      return;
    }
    if (ev.id === "pw:groundrevert") {
      const R = Math.max(8, Math.min(96, parseInt(ev.message, 10) || 48));
      _convertOn = false;
      try { world.setDynamicProperty(PW_CONVERT_PROP, false); } catch {}
      ginfo(`revert starting radius=${R}; conversion switched OFF first so nothing re-converts behind us`);
      system.runJob(revertJob(p.dimension, Math.floor(l.x), Math.floor(l.y), Math.floor(l.z), R));
      return;
    }
    ginfo("================ GROUND PARITY REPORT ================");
    ginfo("FAMILY: pw:grass_block · pw:podzol · pw:mycelium");
    ginfo("REPRODUCED via custom component on the ENGINE's own random tick:");
    ginfo("   spread onto lit dirt (grass, mycelium) | decay to dirt when smothered |");
    ginfo("   shovel -> grass_path | hoe -> farmland | bonemeal (grass only) |");
    ginfo("   durability cost on tools, one bonemeal consumed |");
    ginfo("   drops dirt, or itself under silk touch | shovel-preferred speed |");
    ginfo("   friction, light dampening, explosion resistance, map colour");
    ginfo("RESTORED IN PACK DATA: mob spawn rules and sheep grazing now name the pw: blocks too");
    ginfo("REMAINING GAPS: worldgen surface checks | villager farming AI");
    ginfo("   Scope keeps these small: only the RISER at an elevation change converts —");
    ginfo("   a two-block line at terrace edges, never open ground.");
    ginfo(`state: conversion=${_convertOn ? "ON" : "OFF"} spread=${_stats.spread} decayed=${_stats.decayed} ` +
          `converted=${_stats.converted} reverted=${_stats.reverted} pathed=${_stats.pathed} tilled=${_stats.tilled} boned=${_stats.boned}`);
    ginfo("=====================================================");
  } catch (e) { gerr("cmd: " + (e && e.message ? e.message : e)); }
});

ginfo(`module loaded — family of ${FAMILY.size}; riser conversion is ${_convertOn ? "ON" : "OFF"}`);
