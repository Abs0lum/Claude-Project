#!/usr/bin/env python3
"""bds2_api_probe.py — program 228 B12: does BDS 1.26.52 (= PS5 v26.52) load a behaviour pack that asks for
@minecraft/server VERSION (+ server-ui UIVER)? Builds a one-script BP, loads it in _bds/srv2 (ports 19242/3, the gate keeps
_bds/srv), and reports the script's [API-PROBE] lines + any content-log error. Usage: bds2_api_probe.py 2.10.0 [2.0.0]"""
import json, shutil, subprocess, sys, time, uuid
from pathlib import Path

SRV = Path("/home/claude/_bds/srv2")
WORLD = SRV / "worlds/artest"
PRISTINE = Path("/home/claude/_bds/pristine_world")
LOGS = Path("/home/claude/_bds/logs")
SCRIPT = r'''
import * as mc from "@minecraft/server";
import * as ui from "@minecraft/server-ui";
const has = (o, k) => { try { return o && k in o; } catch { return false; } };
mc.system.run(() => {
  console.warn(`[API-PROBE] loaded server=%s ui=%s`);
  const keys = ["system", "world", "BlockPermutation", "StructureSaveMode", "LocatorBar", "ItemInventoryComponent", "EntityItemComponent"];
  console.warn(`[API-PROBE] symbols ${JSON.stringify(Object.fromEntries(keys.map((k) => [k, has(mc, k)])))}`);
  console.warn(`[API-PROBE] shutdown ${has(mc.system.beforeEvents, "shutdown")} ui.ModalFormData ${has(ui, "ModalFormData")}`);
  try { console.warn(`[API-PROBE] getDay ${mc.world.getDay()} tod ${mc.world.getTimeOfDay()}`); } catch (e) { console.warn(`[API-PROBE] read err ${e}`); }
});
'''


def main(ver, uiver="2.0.0"):
    bp = Path(f"/home/claude/_staging/apiprobe/pw_apiprobe_{ver}")
    if bp.exists(): shutil.rmtree(bp)
    (bp / "scripts").mkdir(parents=True)
    m = {"format_version": 2, "header": {"name": f"API probe {ver}", "description": "B12 probe", "uuid": str(uuid.uuid4()), "version": [0, 0, 1], "min_engine_version": [1, 21, 0]},
         "modules": [{"type": "script", "language": "javascript", "uuid": str(uuid.uuid4()), "version": [0, 0, 1], "entry": "scripts/main.js"}],
         "dependencies": [{"module_name": "@minecraft/server", "version": ver}, {"module_name": "@minecraft/server-ui", "version": uiver}]}
    (bp / "manifest.json").write_text(json.dumps(m, indent=1))
    (bp / "scripts/main.js").write_text(SCRIPT % (ver, uiver))
    if WORLD.exists(): shutil.rmtree(WORLD)
    shutil.copytree(PRISTINE, WORLD)
    for kind in ("behavior_packs", "resource_packs"):
        for p in (SRV / kind).glob("pw_*"): shutil.rmtree(p)
    shutil.copytree(bp, SRV / "behavior_packs" / bp.name)
    (WORLD / "world_behavior_packs.json").write_text(json.dumps([{"pack_id": m["header"]["uuid"], "version": [0, 0, 1]}]))
    (WORLD / "world_resource_packs.json").write_text("[]")
    LOGS.mkdir(exist_ok=True)
    out = LOGS / f"apiprobe-{ver}-{time.strftime('%H%M%S')}.txt"
    with open(out, "w") as f:
        p = subprocess.Popen(["./bedrock_server"], cwd=SRV, stdin=subprocess.PIPE, stdout=f, stderr=subprocess.STDOUT, env={"LD_LIBRARY_PATH": "."}, text=True)
        t0 = time.time()
        while time.time() - t0 < 90 and "Server started" not in out.read_text(errors="ignore"): time.sleep(1)
        time.sleep(8)
        p.stdin.write("stop\n"); p.stdin.flush()
        try: p.wait(30)
        except Exception: p.kill()
    txt = out.read_text(errors="ignore")
    for l in txt.splitlines():
        if any(k in l for k in ("API-PROBE", "ERROR", "rror", "module", "Script", "script", "version")) and "Profiler" not in l: print(l[:300])
    print(out)


if __name__ == "__main__":
    main(*sys.argv[1:])
