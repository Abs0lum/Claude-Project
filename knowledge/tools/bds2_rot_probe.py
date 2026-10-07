#!/usr/bin/env python3
"""bds2_rot_probe.py — engine probe (program 228 spiral integration): does /structure load ROTATE a custom block's
minecraft:cardinal_direction state (placement_direction trait) and MIRROR it? One spiral block (A_turret stone, part mid,
hand ccw, cardinal south) at (0,0,0) of a 1x1x1 structure 'pw:rotprobe' is loaded at 0 100 0 with 0/90/180/270 and
mirror x / z, and each placed state is read back with execute if block. Uses _bds/srv2 + the spiral test 0.0.3 packs."""
import json, shutil, subprocess, sys, time
from pathlib import Path
sys.path.insert(0, "/home/claude/tools")
import mcstructure as M  # noqa: E402

SRV = Path("/home/claude/_bds/srv2"); WORLD = SRV / "worlds/artest"; PRISTINE = Path("/home/claude/_bds/pristine_world")
BP = Path("/home/claude/_build/spiraltest-0.0.3-bp"); RP = Path("/home/claude/_build/spiraltest-0.0.3-rp")
NAME = "pw:spiral_stairs_A_turret_stone"


def main():
    st = M.Structure((1, 1, 1))
    st.set(0, 0, 0, NAME, {"pw:part": M.s("mid"), "pw:hand": M.s("ccw"), "minecraft:cardinal_direction": M.s("south")})
    tmp = Path("/home/claude/_staging/rotprobe-bp"); 
    if tmp.exists(): shutil.rmtree(tmp)
    shutil.copytree(BP, tmp)
    (tmp / "structures/pw/rotprobe.mcstructure").write_bytes(st.to_bytes())
    mf = json.loads((tmp / "manifest.json").read_text())
    mf["modules"].append({"type": "script", "language": "javascript", "uuid": "6c4a0f6e-2b1d-4c8e-9f3a-1d2e3f4a5b6c", "version": [0, 0, 1], "entry": "scripts/rp.js"})
    mf["dependencies"].append({"module_name": "@minecraft/server", "version": "2.10.0"})
    (tmp / "manifest.json").write_text(json.dumps(mf))
    (tmp / "scripts").mkdir(exist_ok=True)
    (tmp / "scripts/rp.js").write_text("""import { world, system } from "@minecraft/server";
system.afterEvents.scriptEventReceive.subscribe((e) => {
  if (e.id !== "pw:rp") return;
  const [x, label] = e.message.split(" ");
  const b = world.getDimension("overworld").getBlock({ x: Number(x), y: 100, z: 0 });
  console.warn(`[ROT] ${label} -> ${b ? b.typeId : "none"} ${b ? JSON.stringify(b.permutation.getAllStates()) : ""}`);
});""")
    if WORLD.exists(): shutil.rmtree(WORLD)
    shutil.copytree(PRISTINE, WORLD)
    for kind in ("behavior_packs", "resource_packs"):
        for p in (SRV / kind).glob("pw_*"): shutil.rmtree(p)
    lists = {"behavior_packs": [], "resource_packs": []}
    for d, kind in ((tmp, "behavior_packs"), (RP, "resource_packs")):
        shutil.copytree(d, SRV / kind / ("pw_" + d.name))
        m = json.loads((d / "manifest.json").read_text())
        lists[kind].append({"pack_id": m["header"]["uuid"], "version": m["header"]["version"]})
    (WORLD / "world_behavior_packs.json").write_text(json.dumps(lists["behavior_packs"]))
    (WORLD / "world_resource_packs.json").write_text(json.dumps(lists["resource_packs"]))
    out = Path(f"/home/claude/_bds/logs/rotprobe-{time.strftime('%H%M%S')}.txt")
    with open(out, "w") as f:
        p = subprocess.Popen(["./bedrock_server"], cwd=SRV, stdin=subprocess.PIPE, stdout=f, stderr=subprocess.STDOUT, env={"LD_LIBRARY_PATH": "."}, text=True)
        t0 = time.time()
        while time.time() - t0 < 90 and "Server started" not in out.read_text(errors="ignore"): time.sleep(1)
        def cmd(c, w=1.5): p.stdin.write(c + "\n"); p.stdin.flush(); time.sleep(w)
        cmd("tickingarea add 0 0 0 40 0 0 rp true", 10)
        cases = [("0_degrees", "none"), ("90_degrees", "none"), ("180_degrees", "none"), ("270_degrees", "none"), ("0_degrees", "x"), ("0_degrees", "z"), ("90_degrees", "x")]
        for i, (rot, mir) in enumerate(cases):
            x = i * 4
            cmd(f"structure load pw:rotprobe {x} 100 0 {rot} {mir}", 2)
            cmd(f"scriptevent pw:rp {x} {rot}/{mir}", 1)
        cmd("stop", 8)
        try: p.wait(30)
        except Exception: p.kill()
    for l in out.read_text(errors="ignore").splitlines():
        if "[ROT]" in l or "rror" in l: print(l[-120:])
    print(out)


if __name__ == "__main__":
    main()
