// pw_prof.js — BDS-only script profiler for BP-02 (never shipped). Imported FIRST by main.js in a diag copy.
// Wraps system.run / runTimeout / runInterval / runJob and every world/system event subscribe, so each callback's
// run time is charged to the place that registered it (file:line from the registration stack). Logs:
//   [PROF-CB]   any single callback over CB_MS
//   [PROF-TICK] any tick whose wrapped script time totals over TICK_MS, with its top contributors
//   [PROF-SUM]  every SUM_EVERY ticks: the top 12 registration sites by total time since the last summary
import { system, world } from "@minecraft/server";

const CB_MS = 100, TICK_MS = 250, SUM_EVERY = 1200;
let tick = -1, tickTotal = 0, tickParts = new Map();
const sums = new Map();
const W = (s) => console.warn(s);

function site() {
  const st = String(new Error().stack || "").split("\n").map((l) => l.trim()).filter((l) => l && !l.includes("pw_prof.js") && l.startsWith("at"));
  const l = st[0] || "?";
  const m = l.match(/\(([^)]+)\)/);
  return (m ? m[1] : l).replace(/^.*scripts\//, "");
}
function flushTick() {
  if (tick >= 0 && tickTotal > TICK_MS) {
    const top = [...tickParts.entries()].sort((a, b) => b[1] - a[1]).slice(0, 8).map(([k, v]) => `${k} ${v}ms`).join(" | ");
    W(`[PROF-TICK] tick ${tick}: ${tickTotal} ms · ${top}`);
  }
  tickTotal = 0; tickParts = new Map();
}
function charge(label, ms) {
  const t = system.currentTick;
  if (t !== tick) { flushTick(); tick = t; }
  tickTotal += ms;
  tickParts.set(label, (tickParts.get(label) || 0) + ms);
  const s = sums.get(label) || [0, 0, 0]; s[0] += ms; s[1]++; if (ms > s[2]) s[2] = ms; sums.set(label, s);
  if (ms > CB_MS) W(`[PROF-CB] ${ms} ms in ${label} (tick ${t})`);
}
function wrapFn(fn, label) {
  return function (...a) {
    const t0 = Date.now();
    try { return fn.apply(this, a); } finally { charge(label, Date.now() - t0); }
  };
}

for (const name of ["run", "runTimeout", "runInterval"]) {
  const orig = system[name].bind(system);
  try {
    system[name] = function (cb, ...rest) { return orig(wrapFn(cb, `${name}@${site()}`), ...rest); };
  } catch (e) { W(`[PROF] cannot wrap system.${name}: ${e}`); }
}
{
  const orig = system.runJob.bind(system);
  try {
    system.runJob = function (gen) {
      const label = `job@${site()}`;
      function* w() {
        while (true) {
          const t0 = Date.now();
          let r;
          try { r = gen.next(); } finally { charge(label, Date.now() - t0); }
          if (r.done) return r.value;
          yield r.value;
        }
      }
      return orig(w());
    };
  } catch (e) { W(`[PROF] cannot wrap system.runJob: ${e}`); }
}
function wrapSignals(holder, prefix) {
  if (!holder) return;
  let n = 0;
  const proto = Object.getPrototypeOf(holder);
  const keys = new Set([...Object.getOwnPropertyNames(holder), ...(proto ? Object.getOwnPropertyNames(proto) : [])]);
  for (const k of keys) {
    let sig;
    try { sig = holder[k]; } catch { continue; }
    if (!sig || typeof sig.subscribe !== "function") continue;
    const sub = sig.subscribe.bind(sig), unsub = sig.unsubscribe ? sig.unsubscribe.bind(sig) : null;
    const map = new Map();
    try {
      sig.subscribe = function (cb, ...rest) {
        const w = wrapFn(cb, `${prefix}.${k}@${site()}`);
        map.set(cb, w);
        sub(w, ...rest);
        return cb;                                   // callers unsubscribe with what they passed (or what came back)
      };
      if (unsub) sig.unsubscribe = function (cb) { const w = map.get(cb) || cb; map.delete(cb); return unsub(w); };
      n++;
    } catch (e) { W(`[PROF] cannot wrap ${prefix}.${k}: ${e}`); }
  }
  return n;
}
const nA = wrapSignals(world.afterEvents, "after"), nB = wrapSignals(world.beforeEvents, "before");
const nS = wrapSignals(system.afterEvents, "sys"), nSB = wrapSignals(system.beforeEvents, "sysb");
W(`[PROF] loaded — wrapped run/runTimeout/runInterval/runJob + ${nA}/${nB}/${nS}/${nSB} signals; CB ${CB_MS} ms, TICK ${TICK_MS} ms`);
system.runInterval(() => {
  const top = [...sums.entries()].sort((a, b) => b[1][0] - a[1][0]).slice(0, 12)
    .map(([k, [ms, n, mx]]) => `${k} ${ms}ms/${n} max ${mx}`).join(" | ");
  W(`[PROF-SUM] tick ${system.currentTick}: ${top}`);
  sums.clear();
}, SUM_EVERY);
