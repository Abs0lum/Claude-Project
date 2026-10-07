// pw_flutter.js — BP-02 (his J3 = d, 2026-10-01 12:58): the non-flying fowl FLUTTER when they leave the ground:
//   "first a little bit of lift like with a jump, then slow fall, then drop".
// Per bird, once per fall: an upward push (the jump-like lift) -> slow_falling for FLUTTER_TICKS (matches the RP flutter
// animation, whose beat tires after ~1.2 s in the air) -> normal gravity (the drop). Back on the ground it re-arms.
// The RP side (animation.std.<slug>.flutter) reads q.is_on_ground only; nothing here talks to it.
import { system, world } from "@minecraft/server";

export const FLUTTER_TYPES = ["minecraft:chicken", "sf_nba:turkey", "sf_nba:peafowl", "sf_nba:kakapo",
  "pw:turkey_wa", "pw:kakapo_wwa"];
export const LIFT = 0.22;          // upward impulse (blocks / tick) — a hop, not flight
export const FLUTTER_TICKS = 24;   // slow fall for 1.2 s
export const FALL_START = -0.08;   // vertical velocity that counts as "started to fall"
const SCAN_EVERY = 2;              // ticks

// pure decision: state "ground" | "air" ; returns [newState, action] with action "lift" | null
export function flutterStep(state, onGround, vy, inWater) {
  if (onGround || inWater) return ["ground", null];
  if (state === "ground" && vy < FALL_START) return ["air", "lift"];
  return [state === "ground" ? "ground" : "air", null];
}

const states = new Map();          // entity id -> state
// 1.3.227 (profiled at city II: 18 entity queries — 6 kinds x 3 dimensions — every 2 ticks, about 7 ms a run): the birds
// are TRACKED — added as they load or spawn, re-counted by the queries once every RESYNC_EVERY ticks — and only the
// tracked birds are read every SCAN_EVERY ticks
const RESYNC_EVERY = 200;
const KINDS = new Set(FLUTTER_TYPES);
const birds = new Map();           // entity id -> entity
function track(e) { try { if (e && KINDS.has(e.typeId)) birds.set(e.id, e); } catch { /* left */ } }
world.afterEvents.entityLoad.subscribe((ev) => track(ev.entity));
world.afterEvents.entitySpawn.subscribe((ev) => track(ev.entity));
function resync() {
  birds.clear();
  for (const dimId of ["overworld", "nether", "the_end"]) {
    let dim;
    try { dim = world.getDimension(dimId); } catch { continue; }
    for (const type of FLUTTER_TYPES) {
      try { for (const e of dim.getEntities({ type })) birds.set(e.id, e); } catch { /* none */ }
    }
  }
}
system.runInterval(() => {
  if (system.currentTick % RESYNC_EVERY < SCAN_EVERY) resync();
  for (const [id, e] of birds) {
    try {
      if (!e.isValid) { birds.delete(id); states.delete(id); continue; }
      const [next, act] = flutterStep(states.get(id) ?? "ground", e.isOnGround, e.getVelocity().y, e.isInWater);
      states.set(id, next);
      if (act === "lift") {
        e.applyImpulse({ x: 0, y: LIFT, z: 0 });
        e.addEffect("slow_falling", FLUTTER_TICKS, { amplifier: 0, showParticles: false });
      }
    } catch { /* an entity unloading mid-scan: skip it */ }
  }
  for (const id of [...states.keys()]) if (!birds.has(id)) states.delete(id);
}, SCAN_EVERY);
system.runTimeout(resync, 1);
