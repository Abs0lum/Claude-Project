// pw_fall_physics.js — how a felled tree falls (round 1004b, D-C563; research R6-FALLING-TREE-PHYSICS-AND-ANIMATION-2026-10-04).
// PURE functions over plain data (the engine is passed in as a ground-height callback), unit-tested under Node.
//
//  * The PIVOT is the top face of the cut block at the trunk's LEADING edge (toward the fall), r = the trunk's radius.
//  * The RESTING ANGLE is found by rotating the tree's own cells (logs above the cut + its leaves) about that pivot in
//    the fall direction and stopping at the FIRST cell whose rotated bottom meets the ground's top face (R6 §5.3): flat
//    ground gives ~84-90° (the crown props the top), a downhill slope more than 90°, a bank less. Nothing goes under.
//  * The ROTATION follows physics: a 2° lean at rest, then θ(f) = 2° + 88°·f^3.85 (R6 §6.2, within 1.2° of the exact
//    hinge solution), clamped at the resting angle. The fall takes T = 1.10·sqrt(H) seconds from 2° to 90° (broadleaf),
//    after a 0.15 s hold and a 0.45 s creak ramp 0 → 2°. The impact frame is where the curve reaches the resting angle.
//  * Angles here are POSITIVE degrees of lean; the entity's properties hold them negative (the renderer's convention).
//  * DIRECTION (Phase-6 yaw sign, closed by law not by guess — D-C565): the fall animation turns the root bone by a NEGATIVE
//    z rotation; L-ROT-DIR (verified 09-27) says +rz tips the top toward file +x, so the trunk tips toward file -x = the
//    entity's RIGHT; the right of a Bedrock entity at yaw psi is (-cos psi, -sin psi) in the world. The old script used
//    (-cos psi, +sin psi) — a reflection across the x axis, exactly the "2x2 fell dead-opposite / elders a quarter turn off"
//    witness of July. FALL_Z_SIGN = -1 is the law; +1 restores the old convention in one place if the witness disagrees.
export const HOLD_S = 0.15, RAMP_S = 0.45, LEAN0 = 2, CURVE_P = 3.85, T_COEF = 1.10;
export const FALL_T_MIN = 0.8, FALL_T_MAX = 8.0;
export const FALL_Z_SIGN = -1;

/** the world unit vector a falling tree tips toward for an entity yaw (deg) */
export function fallDirOfYaw(yawDeg, zSign = FALL_Z_SIGN) {
  const r = yawDeg * Math.PI / 180;
  return { x: -Math.cos(r), z: zSign * Math.sin(r) };
}

/** the entity yaw (deg, -180..180) that makes the tree tip toward world direction (dx, dz) */
export function yawOfFallDir(dx, dz, zSign = FALL_Z_SIGN) {
  return Math.atan2(zSign * dz, -dx) * 180 / Math.PI;
}

/** a compass name for a world direction (8 points; x east, z south) */
export function compassName(dx, dz) {
  const a = Math.atan2(dz, dx) * 180 / Math.PI;                 // 0 = east, 90 = south
  const names = ["E", "SE", "S", "SW", "W", "NW", "N", "NE"];
  return names[Math.round(((a % 360) + 360) % 360 / 45) % 8];
}

/** the fall duration (s) from 2° to 90° for a tree of height H blocks (R6: T = c·sqrt(H), c = 1.10 broadleaf) */
export function fallDuration(H, coef = T_COEF) {
  const h = Math.max(2, Math.min(40, H || 8));
  return Math.max(FALL_T_MIN, Math.min(FALL_T_MAX, coef * Math.sqrt(h)));
}

/** past 90° (a downhill rest) the curve continues at its end slope 88·p degrees per unit f (the fast end of the fall) */
export const END_SLOPE = 88 * CURVE_P;   // 338.8

/** the lean (deg) at animation time t (s): hold, creak ramp, physics curve (continued past 90°), clamped at restDeg.
 *  MIRRORED in RP-01's animation.ft_falling_tree.fall (Molang, same constants) — change both or neither. */
export function thetaAt(t, T, restDeg) {
  let th;
  if (t <= HOLD_S) th = 0;
  else if (t < HOLD_S + RAMP_S) { const x = (t - HOLD_S) / RAMP_S; th = LEAN0 * (1 - Math.cos(x * Math.PI)) / 2; }
  else {
    const f = Math.max(0, (t - HOLD_S - RAMP_S) / T);
    th = f <= 1 ? LEAN0 + 88 * Math.pow(f, CURVE_P) : 90 + END_SLOPE * (f - 1);
  }
  return Math.min(th, restDeg);
}

/** the time (s) at which the curve reaches restDeg (the impact frame) */
export function impactTime(T, restDeg) {
  if (restDeg <= LEAN0) return HOLD_S + RAMP_S * (restDeg <= 0 ? 0 : Math.acos(1 - 2 * restDeg / LEAN0) / Math.PI);
  const f = restDeg <= 90 ? Math.pow((restDeg - LEAN0) / 88, 1 / CURVE_P) : 1 + (restDeg - 90) / END_SLOPE;
  return HOLD_S + RAMP_S + T * f;
}

/** the PIVOT radius (blocks): the distance from the entity's axis to the drawn trunk's leading face (file -x), so the
 *  script's hinge is the model's hinge (R6 §6.1 "one convention"). RP-01 1.3.122 sets every root bone's pivot there:
 *  legacy models (falling_tree_*.geo, log_1's x extent): young 3 px, mature + old 4, elder and every single-geometry
 *  species 8, the 2x2 "_w2" models 16 from the cluster centre; carbon copies (ft_tpl, one box per log cell, the standing
 *  block's width capped at 16): young 12 px -> 6, mature 14 -> 7, old 15 -> 7.5, elder / vanilla-log species 16 -> 8;
 *  a 2x2 TEMPLATE tree pivots on its ROOT column's face (8 px). Change the RP builds and this table together. */
export const TIERED_SPECIES = new Set(["oak", "spruce", "birch", "jungle"]);
export function pivotRadius(speciesKey, tier, trunkWidth, carbonCopy) {
  if (!carbonCopy && trunkWidth >= 2) return 1.0;
  if (!TIERED_SPECIES.has(speciesKey)) return 0.5;
  if (carbonCopy) return tier <= 0 ? 0.375 : tier === 1 ? 0.4375 : tier === 2 ? 0.47 : 0.5;
  return tier <= 0 ? 0.1875 : tier <= 2 ? 0.25 : 0.5;
}
/** @deprecated kept for the 1004b tests; use pivotRadius */
export function trunkRadius(trunkWidth, tier, dodecagon) {
  if (trunkWidth >= 2) return 1.0;
  if (dodecagon) return tier <= 0 ? 0.25 : tier <= 2 ? 0.47 : 0.81;
  return 0.5;
}

/** ids the falling trunk passes through for the purpose of RESTING (its own kind, air, water, plants); everything else is ground */
export function isFallPassable(id) {
  if (!id || id === "minecraft:air") return true;
  if (id === "minecraft:water" || id === "minecraft:flowing_water" || id === "minecraft:lava" || id === "minecraft:flowing_lava") return true;
  if (id.includes("leaves") || id.endsWith("_log") || id.endsWith("_wood") || id.endsWith("_stem") || id.endsWith("_hyphae")) return true;
  if (id === "minecraft:mangrove_roots" || id === "minecraft:muddy_mangrove_roots") return true;              // tree parts too
  if (/pw:[a-z_]+_(young|mature|old|elder)(_root)?$/.test(id) || id.includes("_wart_block")) return true;
  if (id === "minecraft:short_grass" || id === "minecraft:tall_grass" || id === "minecraft:tallgrass" || id === "minecraft:fern" || id === "minecraft:large_fern" ||
      id === "minecraft:dead_bush" || id === "minecraft:snow_layer" || id === "minecraft:vine" || id === "pw:vine" || id === "minecraft:sweet_berry_bush" ||
      id === "minecraft:bush" || id === "minecraft:moss_carpet" || id === "minecraft:pale_moss_carpet" || id === "minecraft:glow_lichen" || id === "minecraft:mangrove_propagule" ||
      id === "minecraft:wheat" || id === "minecraft:carrots" || id === "minecraft:potatoes" || id === "minecraft:beetroot" || id === "minecraft:torch" ||
      id === "minecraft:cobweb" || id === "minecraft:pink_petals" || id === "minecraft:wildflowers" || id === "minecraft:fire" || id === "minecraft:brown_mushroom" || id === "minecraft:red_mushroom") return true;
  if (/^minecraft:[a-z_]*(sapling|flower|tulip|orchid|allium|poppy|dandelion|bluet|daisy|cornflower|lily|peony|lilac|rose_bush|sunflower|torchflower|pitcher)/.test(id)) return true;
  if (id.startsWith("pw:leaf") || id.startsWith("pw:flower") || id.startsWith("pw:veg_")) return true;
  return false;
}

/** a ground reader: top face y of the first non-passable block under (x, z) scanning down from yFrom to yTo; undefined = none */
export function makeGroundReader(getId, yFrom, yTo) {
  const cache = new Map();
  return (x, z) => {
    const k = `${x},${z}`;
    if (cache.has(k)) return cache.get(k);
    let top;
    for (let y = yFrom; y >= yTo; y--) {
      const id = getId(x, y, z);
      if (id === null) { top = undefined; break; }                           // unloaded: unknown
      if (!isFallPassable(id)) { top = y + 1; break; }
    }
    cache.set(k, top);
    return top;
  };
}

/** the resting angle (deg, 2..135) of a tree whose cells (world cells [x, y, z, leaf?], the cut and everything below
 *  excluded) rotate about pivot {x, y, z} (the stump top's leading edge) in direction f = {x, z} (unit). ground(x, z) ->
 *  top face y. A cell marked leaf (4th element 1) may CRUSH `crush` blocks into the ground (a crown crumples; R6 §5.3).
 *  Returns { deg, contact: the cell that first touches, tested } — deg = the last angle BEFORE contact, so no log is
 *  ever inside the ground; with no contact by maxDeg the tree lies at maxDeg. */
export function restAngle(cells, pivot, f, ground, opts = {}) {
  const maxDeg = opts.maxDeg ?? 135, coarse = opts.coarse ?? 2, fine = opts.fine ?? 0.5, clearance = opts.clearance ?? 0.05;
  const crush = opts.crush ?? 0.6;
  const px = f.x, pz = f.z, qx = -pz, qz = px;                                 // f = along the fall, q = across it
  const rel = [];
  for (const c of cells) {
    const cx = c[0] + 0.5 - pivot.x, cz = c[2] + 0.5 - pivot.z;
    rel.push([cx * px + cz * pz, c[1] + 0.5 - pivot.y, cx * qx + cz * qz, c, c[3] === 1 ? crush : 0]);  // [d along, h up, s across, cell, give]
  }
  if (!rel.length) return { deg: 90, contact: null, tested: 0 };
  let tested = 0;
  const touches = (deg) => {
    const a = deg * Math.PI / 180, sn = Math.sin(a), cs = Math.cos(a);
    for (const [d, h, s, c, give] of rel) {
      const d2 = d * cs + h * sn, h2 = -d * sn + h * cs;                         // rotated centre
      const wx = pivot.x + px * d2 + qx * s, wz = pivot.z + pz * d2 + qz * s;
      const g = ground(Math.floor(wx), Math.floor(wz));
      tested++;
      if (g === undefined) continue;
      if (pivot.y + h2 - 0.5 + give <= g + clearance) return c;                 // the cell's bottom met the ground's top
    }
    return null;
  };
  let lo = Math.min(LEAN0, maxDeg), hit = null, hitDeg = null;
  for (let deg = lo + coarse; deg <= maxDeg; deg += coarse) { const c = touches(deg); if (c) { hit = c; hitDeg = deg; break; } lo = deg; }
  if (!hit) return { deg: maxDeg, contact: null, tested };
  for (let deg = lo + fine; deg < hitDeg; deg += fine) { const c = touches(deg); if (c) { hit = c; hitDeg = deg; break; } lo = deg; }
  return { deg: Math.max(LEAN0, lo), contact: hit, tested };
}
