// pw_weather.js — the current weather in each dimension, for scripts pinned to STABLE @minecraft/server.
//
// Why this exists (L-API-STABLE, D-C231 audit 2026-09-22): Dimension.getWeather() is beta-only through
// @minecraft/server 2.10.0, so on a stable pin it is undefined and every weather read came back "clear".
// The stable way is the event world.afterEvents.weatherChange, which fires on EVERY change — the natural
// weather cycle and the /weather command alike — with { dimension, newWeather, previousWeather } where
// newWeather is "Clear" | "Rain" | "Thunder".
//
// The last value per dimension is saved in a world dynamic property, so it survives leaving and
// reloading the world. Until the first change after this pack is installed, it reads "Clear"
// (the API has no stable way to ask "is it raining right now?"). /weather rain | thunder | clear
// sets it immediately.
//
// Early execution (@minecraft/server 2.x): subscribing is allowed while the script loads; reading or
// writing the dynamic property is not, so the saved value is loaded lazily on first use.
import { world } from "@minecraft/server";

const KEY = "pw:weather_cache";
const cache = new Map();          // dimension key ("overworld") -> "Clear" | "Rain" | "Thunder"
let loaded = false;

// "minecraft:overworld" and "overworld" are the same dimension
export function dimKey(id) {
  return String(id ?? "").replace(/^minecraft:/, "");
}

// Anything that is not Rain or Thunder counts as Clear
export function normWeather(w) {
  const s = String(w ?? "");
  return s === "Rain" || s === "Thunder" ? s : "Clear";
}

function load() {
  if (loaded) return;
  let raw;
  try {
    raw = world.getDynamicProperty(KEY);
  } catch {
    return;                        // world not ready yet — try again on the next read
  }
  loaded = true;
  if (typeof raw !== "string" || raw === "") return;
  try {
    const saved = JSON.parse(raw);
    for (const k of Object.keys(saved)) {
      if (!cache.has(k)) cache.set(k, normWeather(saved[k]));   // a change seen this session wins
    }
  } catch { /* unreadable save: start from Clear */ }
}

function save() {
  try {
    world.setDynamicProperty(KEY, JSON.stringify(Object.fromEntries(cache)));
  } catch { /* not fatal: the in-memory value still works this session */ }
}

world.afterEvents.weatherChange.subscribe((ev) => {
  try {
    load();
    cache.set(dimKey(ev.dimension), normWeather(ev.newWeather));
    save();
  } catch { /* never let a weather event break the pack */ }
});

// "Clear" | "Rain" | "Thunder" for a dimension id ("minecraft:overworld") or a Dimension object
export function weatherIn(dimension) {
  load();
  const id = dimension && typeof dimension === "object" ? dimension.id : dimension;
  return cache.get(dimKey(id)) ?? "Clear";
}
