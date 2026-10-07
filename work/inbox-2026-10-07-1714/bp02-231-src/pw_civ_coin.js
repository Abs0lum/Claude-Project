// pw_civ_coin.js — the CIVITAS GOLD COIN (v1.3.219, his 17:00 / 17:37 / 18:01 rulings: G1 the coin is the village money,
// exchangeable with emeralds; the coins are kept, stored and used, every one logged and tracked; G2 placeable as a pile;
// G3 stacks to 64, tracking my call; G4 a pile grows as coins are added and gives every coin back when broken).
//
// THE ITEM pw:gold_coin (stack 64) places the BLOCK pw:gold_coin_pile (state pw:count 1..16, one coin per step, its
// geometry shows one more coin per count). Using a coin on a pile adds one (sneaking: as many as fit); breaking a pile
// gives back exactly its count.
// THE MINT LEDGER (world dynamic property pw:coin_ledger): a coin exists physically only after the MINT ISSUES it from a
// settlement's treasury (a sale to a shop, an exchange) — every issue takes the next SERIAL NUMBERS (#1 onward) and is
// logged with its range, day, settlement and reason; coins paid back to a treasury are RETURNED (counted, logged);
// coins lost to the world (a pile blown up, lava) are DESTROYED when the game tells us. In circulation = issued -
// returned - destroyed. Engine limit (stated to him 17:55): a stack of 64 items cannot carry 64 serial numbers, so the
// serials live in the ledger's batches, not on the items. PILES are registered by position (count kept in sync), so a
// census can tell coins on the ground from coins carried.
import { world, system, ItemStack, Direction } from "@minecraft/server";
import { payPlan, issuePlan, COIN as PENNY_PER_GOLD } from "./pw_civ_economy.js";

export const COIN = "pw:gold_coin";
// 1.3.228 (B7 / WE10; his 12:20): the SILVER NICKEL — 1 penny (12 make a gold coin): exact prices and change. The mint logs
// nickels beside the gold (nIssued / nReturned); a nickel has no pile block (it is small change).
export const NICKEL = "pw:silver_nickel";
export const PILE = "pw:gold_coin_pile";
export const PILE_MAX = 16;
export const COIN_PER_EMERALD = 4;
const KEY = "pw:coin_ledger";
const MAX_LINES = 200;

let L = null;
export function ledger() {
  if (L) return L;
  try { const raw = world.getDynamicProperty(KEY); L = raw ? JSON.parse(raw) : null; } catch { L = null; }
  if (!L) L = { seq: 0, issued: 0, returned: 0, destroyed: 0, lines: [], piles: {} };
  return L;
}
function store() {
  const l = ledger();
  if (l.lines.length > MAX_LINES) l.lines.splice(0, l.lines.length - MAX_LINES);
  try { world.setDynamicProperty(KEY, JSON.stringify(l)); } catch (e) { console.warn(`[COIN] ledger save failed: ${e}`); }
}
const today = () => { try { return world.getDay(); } catch { return 0; } };
export const inCirculation = () => { const l = ledger(); return l.issued - l.returned - l.destroyed; };
export const nickelsInCirculation = () => { const l = ledger(); return (l.nIssued || 0) - (l.nReturned || 0); };
/** "2 gold 6 nickels" / "6 nickels" / "3 gold" */
export function fmtP(p) {
  const g = Math.floor(p / PENNY_PER_GOLD), n = p % PENNY_PER_GOLD;
  return [g ? `${g} gold` : "", n ? `${n} nickel${n === 1 ? "" : "s"}` : ""].filter(Boolean).join(" ") || "nothing";
}
export const countPennies = (player) => countCoins(player) * PENNY_PER_GOLD + countItem(player, NICKEL);
/** ISSUE p pennies: whole gold coins (serials, as before) and the rest in nickels; logged */
export function issuePennies(player, p, who, why) {
  if (p <= 0) return;
  const { gold, nick } = issuePlan(p);
  if (gold) issue(player, gold, who, why);
  if (nick) {
    const l = ledger();
    l.nIssued = (l.nIssued || 0) + nick;
    l.lines.push(`d${today()} ISSUE ${nick} nickel${nick === 1 ? "" : "s"} to ${player.name} · ${who} · ${why}`);
    giveItem(player, NICKEL, nick);
    store();
  }
}
/** PAY p pennies from a player's purse (gold first, nickels, change in nickels); logged as returned; false when short */
export function payPennies(player, p, who, why) {
  if (p <= 0) return true;
  const plan = payPlan(countCoins(player), countItem(player, NICKEL), p);
  if (!plan) return false;
  if (plan.gold && !takeCoins(player, plan.gold)) return false;
  if (plan.nick && !takeItem(player, NICKEL, plan.nick)) { if (plan.gold) giveCoins(player, plan.gold); return false; }
  const l = ledger();
  if (plan.gold) { l.returned += plan.gold; l.lines.push(`d${today()} RETURN ${plan.gold} from ${player.name} · ${who} · ${why}`); }
  if (plan.nick) l.nReturned = (l.nReturned || 0) + plan.nick;
  if (plan.change) { l.nIssued = (l.nIssued || 0) + plan.change; giveItem(player, NICKEL, plan.change); l.lines.push(`d${today()} CHANGE ${plan.change} nickel${plan.change === 1 ? "" : "s"} to ${player.name} · ${who}`); }
  store();
  return true;
}

/** ISSUE n new coins (serials seq+1 .. seq+n) to a player's inventory; logged. Returns the serial range or null. */
export function issue(player, n, who, why) {
  if (n <= 0) return null;
  const l = ledger();
  const from = l.seq + 1, to = l.seq + n;
  l.seq = to;
  l.issued += n;
  l.lines.push(`d${today()} ISSUE #${from}-#${to} (${n}) to ${player.name} · ${who} · ${why}`);
  giveCoins(player, n);
  store();
  return [from, to];
}
/** RETURN n coins taken from a player back to a treasury; logged */
export function returned(player, n, who, why) {
  if (n <= 0) return;
  const l = ledger();
  l.returned += n;
  l.lines.push(`d${today()} RETURN ${n} from ${player.name} · ${who} · ${why}`);
  store();
}
export function destroyed(n, where) {
  if (n <= 0) return;
  const l = ledger();
  l.destroyed += n;
  l.lines.push(`d${today()} LOST ${n} at ${where}`);
  store();
}

export function countCoins(player) {
  const inv = player.getComponent("minecraft:inventory")?.container;
  let n = 0;
  if (!inv) return 0;
  for (let i = 0; i < inv.size; i++) { const it = inv.getItem(i); if (it && it.typeId === COIN) n += it.amount; }
  return n;
}
/** take n coins from a player's inventory (all or nothing); true when taken */
export function takeCoins(player, n) {
  const inv = player.getComponent("minecraft:inventory")?.container;
  if (!inv || countCoins(player) < n) return false;
  let left = n;
  for (let i = 0; i < inv.size && left > 0; i++) {
    const it = inv.getItem(i);
    if (!it || it.typeId !== COIN) continue;
    const k = Math.min(left, it.amount);
    left -= k;
    if (it.amount - k > 0) { it.amount -= k; inv.setItem(i, it); } else inv.setItem(i, undefined);
  }
  return true;
}
export function giveCoins(player, n) {
  const inv = player.getComponent("minecraft:inventory")?.container;
  let left = n;
  while (left > 0) {
    const k = Math.min(64, left);
    const stack = new ItemStack(COIN, k);
    const rest = inv ? inv.addItem(stack) : stack;
    if (rest) { try { player.dimension.spawnItem(rest, player.location); } catch { /* left */ } }
    left -= k;
  }
}
export function countItem(player, id) {
  const inv = player.getComponent("minecraft:inventory")?.container;
  let n = 0;
  if (!inv) return 0;
  for (let i = 0; i < inv.size; i++) { const it = inv.getItem(i); if (it && it.typeId === id) n += it.amount; }
  return n;
}
export function takeItem(player, id, n) {
  const inv = player.getComponent("minecraft:inventory")?.container;
  if (!inv || countItem(player, id) < n) return false;
  let left = n;
  for (let i = 0; i < inv.size && left > 0; i++) {
    const it = inv.getItem(i);
    if (!it || it.typeId !== id) continue;
    const k = Math.min(left, it.amount);
    left -= k;
    if (it.amount - k > 0) { it.amount -= k; inv.setItem(i, it); } else inv.setItem(i, undefined);
  }
  return true;
}
export function giveItem(player, id, n) {
  const inv = player.getComponent("minecraft:inventory")?.container;
  let left = n;
  while (left > 0) {
    const k = Math.min(64, left);
    const stack = new ItemStack(id, k);
    const rest = inv ? inv.addItem(stack) : stack;
    if (rest) { try { player.dimension.spawnItem(rest, player.location); } catch { /* left */ } }
    left -= k;
  }
}

// ------------------------------------------------------------------------------------------------ the pile block
const pk = (dimId, l) => `${dimId}|${l.x},${l.y},${l.z}`;
function pileCount(block) { try { return Number(block.permutation.getState("pw:count")) || 1; } catch { return 1; } }

/** a pile placed from the item: registered with count 1 */
world.afterEvents.playerPlaceBlock.subscribe((ev) => {
  if (ev.block.typeId !== PILE) return;
  const l = ledger();
  l.piles[pk(ev.dimension.id, ev.block.location)] = pileCount(ev.block);
  store();
});

/** a coin used on a pile: one more coin on it (sneaking: as many as fit), instead of a new pile on top. A coin used on
 *  any other block places a pile only on a TOP face (review 19:1x: no piles hanging on walls or ceilings). Holding the
 *  button repeats the event: only the first press of a hold counts. */
world.beforeEvents.playerInteractWithBlock.subscribe((ev) => {
  const { block, player, itemStack } = ev;
  if (!itemStack || itemStack.typeId !== COIN) return;
  if (block.typeId !== PILE) { if (ev.blockFace !== Direction.Up) ev.cancel = true; return; }
  ev.cancel = true;
  if (ev.isFirstEvent === false) return;
  const loc = block.location, dimId = block.dimension.id;
  const sneaking = player.isSneaking;
  system.run(() => {
    try {
      const b = world.getDimension(dimId).getBlock(loc);
      if (!b || b.typeId !== PILE) return;
      const c = pileCount(b);
      const room = PILE_MAX - c;
      if (room <= 0) return;
      const want = sneaking ? Math.min(room, countCoins(player)) : 1;
      if (want <= 0 || !takeCoins(player, want)) return;
      b.setPermutation(b.permutation.withState("pw:count", c + want));
      ledger().piles[pk(dimId, loc)] = c + want;
      store();
    } catch (e) { console.warn(`[COIN] add to pile: ${e}`); }
  });
});

/** a pile broken by a player: every coin back as items (the block itself drops nothing) */
world.afterEvents.playerBreakBlock.subscribe((ev) => {
  const perm = ev.brokenBlockPermutation;
  if (!perm || perm.type.id !== PILE) return;
  let c = 1;
  try { c = Number(perm.getState("pw:count")) || 1; } catch { /* 1 */ }
  try {
    const at = { x: ev.block.location.x + 0.5, y: ev.block.location.y + 0.3, z: ev.block.location.z + 0.5 };
    let left = c;
    while (left > 0) { const k = Math.min(64, left); ev.dimension.spawnItem(new ItemStack(COIN, k), at); left -= k; }
  } catch (e) { console.warn(`[COIN] pile break: ${e}`); }
  const l = ledger();
  delete l.piles[pk(ev.dimension.id, ev.block.location)];
  store();
});

/** census: coins carried by the players online, coins in registered piles (re-read where loaded), in circulation */
export function census() {
  const l = ledger();
  let carried = 0, inPiles = 0, checked = 0;
  for (const p of world.getAllPlayers()) carried += countCoins(p);
  for (const [k, n] of Object.entries(l.piles)) {
    const [dimId, xyz] = k.split("|");
    const [x, y, z] = xyz.split(",").map(Number);
    try {
      const b = world.getDimension(dimId).getBlock({ x, y, z });
      if (b) { checked++; if (b.typeId === PILE) { const c = pileCount(b); l.piles[k] = c; inPiles += c; } else { destroyed(n, `${x} ${y} ${z} (pile gone)`); delete l.piles[k]; } }
      else inPiles += n;
    } catch { inPiles += n; }
  }
  store();
  let nickCarried = 0;
  for (const p of world.getAllPlayers()) nickCarried += countItem(p, NICKEL);
  return { issued: l.issued, returned: l.returned, destroyed: l.destroyed, circulation: inCirculation(), carried, inPiles, piles: Object.keys(l.piles).length, checked, seq: l.seq,
           nickels: { issued: l.nIssued || 0, returned: l.nReturned || 0, circulation: nickelsInCirculation(), carried: nickCarried } };
}
