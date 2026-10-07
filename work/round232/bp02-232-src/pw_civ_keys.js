// pw_civ_keys.js — CIVITAS KEYS (F4; his 22:08 / 22:18 rulings D-C538 / D-C539): the sewer keys are TRACKED VALUABLE ASSETS,
// never crafted, never sold. Every key is a record in its settlement's register { id, holder, issued, custody[] } — holder =
// "person:<census id>" | "player:<name>" | "treasury" | "lost". A key is minted only when a sewer post is filled (one per post)
// and returns to the treasury when its holder dies, leaves or loses the post; the register gives it to the next holder of the
// post, never to kin. The ITEM (pw:sewer_key, stack 1) exists only in a player's hands, carrying its id in a dynamic property
// and in its lore; the hatch law accepts it only when the register says that player holds that key of that settlement.
// THE HATCH LAW (from above): a pw:manhole_cover opens only for a registered key in hand ("The lock doesn't know this key."
// for any other key, "It won't budge." without one — the Markers pack's own message); from below as every hatch; an open
// cover closes itself after AUTO_CLOSE ticks when nobody is in its shaft. Utopia-First: no picking, no copying.
import { world, system, ItemStack, Direction, BlockPermutation } from "@minecraft/server";
import * as HB from "./pw_civ_beat.js";                 // 1.3.228 (B1 / BF1): the auto-close is a heartbeat slot

let API = null;
export function initKeys(api) { API = api; }
export const POSTS = ["sewer_keeper", "watch"];           // the posts that carry a key (F5: the watch goes below on its rounds)
const AUTO_CLOSE = 300;

/** the register of a settlement (created on first use) */
export function register(st) { return (st.keys = st.keys || { next: 1, list: [] }); }
/** mint a key for a post holder (once per post holder); returns the record */
export function mint(st, personId, post, day, why = "post") {
  const R = register(st);
  let k = R.list.find((x) => x.post === post && (x.holder === "treasury" || x.holder === `person:${personId}`));
  if (!k) { k = { id: `${st.id}-K${R.next++}`, post, holder: "treasury", issued: day, custody: [] }; R.list.push(k); }
  if (k.holder !== `person:${personId}`) { k.custody.push([day, k.holder, `person:${personId}`, why]); k.holder = `person:${personId}`; }
  return k;
}
/** a holder is gone (death, departure, the post lost): the key goes back to the treasury */
export function recall(st, personId, day, why) {
  for (const k of register(st).list) if (k.holder === `person:${personId}`) { k.custody.push([day, k.holder, "treasury", why]); k.holder = "treasury"; }
}
/** the daily reconciliation with the census: every post holder has their key, every key of a gone holder returns */
export function reconcile(st, people, day, log) {
  const alive = new Map(people.filter((p) => p.alive).map((p) => [p.id, p]));
  for (const k of register(st).list) {
    const m = /^person:(\d+)$/.exec(k.holder);
    if (!m) continue;
    const p = alive.get(Number(m[1]));
    if (!p || p.job !== k.post) { recall(st, Number(m[1]), day, p ? "left the post" : "gone"); log(`the ${k.post.replace("_", " ")}'s key (${k.id}) went back to the town's strongbox`); }
  }
  for (const p of alive.values()) {
    if (!POSTS.includes(p.job)) continue;
    if (register(st).list.some((k) => k.holder === `person:${p.id}`)) continue;
    const k = mint(st, p.id, p.job, day);
    log(`the ${p.job.replace("_", " ")}'s key (${k.id}) was given to ${p.name}`);
  }
}
/** the settlement's valuable assets (keys first), for the status and the notice board */
export function assets(st) { return register(st).list.map((k) => [k.id, k.post, k.holder, k.custody.length]); }

// ------------------------------------------------------------------------------------------------ the item and the lock
function keyIdOf(item) { try { return item && item.typeId === "pw:sewer_key" ? item.getDynamicProperty("pw:key") : undefined; } catch { return undefined; } }
/** the test path (a player tagged civ:tester only): a key minted to the player, for witnessing the lock */
export function giveTestKey(player, st, day) {
  const R = register(st);
  const k = { id: `${st.id}-K${R.next++}`, post: "test", holder: `player:${player.name}`, issued: day, custody: [[day, "mint", `player:${player.name}`, "tester"]] };
  R.list.push(k);
  const it = new ItemStack("pw:sewer_key", 1);
  it.setDynamicProperty("pw:key", k.id);
  it.setLore([`§7Key ${k.id}`, `§7${st.name}`]);
  player.getComponent("minecraft:inventory").container.addItem(it);
  return k;
}
function slide(block, from, to) {
  const id = block.typeId, skin = block.permutation.getState("pw:skin"), loc = block.location, dim = block.dimension;
  const step = to > from ? 1 : -1;
  let ph = from;
  const tick = () => {
    try {
      ph += step;
      const b = dim.getBlock(loc);
      if (!b || b.typeId !== id) return;
      b.setPermutation(BlockPermutation.resolve(id, { "pw:skin": skin, "pw:phase": ph }));
      if (ph !== to) system.runTimeout(tick, 2);
    } catch { /* left */ }
  };
  system.runTimeout(tick, 1);
}
/** F5: a patrol's key turns the lock — the cover slides from its phase to `to` (0 shut, 5 open) */
export function slideCover(block, to) { const ph = block.permutation.getState("pw:phase"); if (ph !== to) slide(block, ph, to); }
/** the key a census person holds in a settlement's register (or undefined) */
export function keyOf(st, personId) { return register(st).list.find((k) => k.holder === `person:${personId}`); }
const openCovers = new Map();                             // "x,y,z" -> { dim, since }
world.beforeEvents.playerInteractWithBlock.subscribe((ev) => {
  const b = ev.block;
  if (!b || b.typeId !== "pw:manhole_cover" || ev.blockFace !== Direction.Up) return;
  const kid = keyIdOf(ev.itemStack);
  if (kid === undefined) return;                          // no key in hand: the Markers hatch says "It won't budge."
  ev.cancel = true;
  const player = ev.player, loc = b.location;
  system.run(() => {
    try {
      const s = API.load();
      const st = s.settlements.find((x) => register(x).list.some((k) => k.id === kid));
      const k = st && register(st).list.find((x) => x.id === kid);
      const blk = player.dimension.getBlock(loc);
      if (!blk || blk.typeId !== "pw:manhole_cover") return;
      if (!k || k.holder !== `player:${player.name}`) { player.onScreenDisplay.setActionBar("The lock doesn't know this key."); return; }
      const ph = blk.permutation.getState("pw:phase");
      if (ph === 0) { slide(blk, 0, 5); openCovers.set(`${loc.x},${loc.y},${loc.z}`, { dim: player.dimension.id, since: system.currentTick }); player.onScreenDisplay.setActionBar(`§7${st.name}: the cover lifts`); }
      else if (ph === 5) slide(blk, 5, 0);
    } catch (e) { console.warn(`[CIV-KEYS] ${e}`); }
  });
});
/** open covers close themselves when nobody is in the shaft (monsters stay out) — 1.3.228 (B1 / BF1): heartbeat slot 17 of 40 */
HB.register("keys", { fn: () => {
  const now = system.currentTick;
  for (const [key, o] of [...openCovers]) {
    if (now - o.since < AUTO_CLOSE) continue;
    const [x, y, z] = key.split(",").map(Number);
    try {
      const dim = world.getDimension(o.dim);
      const inShaft = dim.getPlayers({ location: { x: x + 0.5, y: y - 6, z: z + 0.5 }, maxDistance: 7 }).some((p) => Math.abs(p.location.x - (x + 0.5)) < 1.2 && Math.abs(p.location.z - (z + 0.5)) < 1.2);
      if (inShaft) { o.since = now; continue; }
      const blk = API && API.blockAt ? API.blockAt(dim, x, y, z) : undefined;                // 1.3.228: guarded
      if (blk === null) continue;                                                             // asleep: try later (was the thrown read)
      if (blk && blk.typeId === "pw:manhole_cover" && blk.permutation.getState("pw:phase") === 5) slide(blk, 5, 0);
    } catch { /* unloaded: try later */ continue; }
    openCovers.delete(key);
  }
} });
