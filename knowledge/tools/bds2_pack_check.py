#!/usr/bin/env python3
"""bds2_pack_check.py — load any BP + RP in a SECOND BDS install (_bds/srv2, ports 19242/19243; the
gate keeps _bds/srv), place pw:spiral_pad through a ticking area, and collect every content-log line about our blocks.
srv2 is a hard-link copy of srv (binary + vanilla packs shared read-only); its world, packs, properties are its own.
Usage: bds2_spiral_check.py BP_DIR RP_DIR"""
import json, shutil, subprocess, sys, time
from pathlib import Path

SRV = Path("/home/claude/_bds/srv2")
WORLD = SRV / "worlds/artest"
PRISTINE = Path("/home/claude/_bds/pristine_world")
LOGS = Path("/home/claude/_bds/logs")


def main(bp, rp):
    if WORLD.exists(): shutil.rmtree(WORLD)
    shutil.copytree(PRISTINE, WORLD)
    for kind in ("behavior_packs", "resource_packs"):
        for p in (SRV / kind).glob("pw_*"): shutil.rmtree(p)
    lists = {"behavior_packs": [], "resource_packs": []}
    for d, kind in ((Path(bp), "behavior_packs"), (Path(rp), "resource_packs")):
        shutil.copytree(d, SRV / kind / ("pw_" + d.name))
        m = json.loads((d / "manifest.json").read_text())
        lists[kind].append({"pack_id": m["header"]["uuid"], "version": m["header"]["version"]})
    (WORLD / "world_behavior_packs.json").write_text(json.dumps(lists["behavior_packs"]))
    (WORLD / "world_resource_packs.json").write_text(json.dumps(lists["resource_packs"]))
    LOGS.mkdir(exist_ok=True)
    out = LOGS / f"packcheck-{time.strftime('%Y%m%d-%H%M%S')}.txt"
    with open(out, "w") as f:
        p = subprocess.Popen(["./bedrock_server"], cwd=SRV, stdin=subprocess.PIPE, stdout=f, stderr=subprocess.STDOUT,
                             env={"LD_LIBRARY_PATH": "."}, text=True)
        t0 = time.time()
        while time.time() - t0 < 90 and "Server started" not in out.read_text(errors="ignore"): time.sleep(1)
        def cmd(c, wait=4):
            p.stdin.write(c + "\n"); p.stdin.flush(); time.sleep(wait)
        cmd("tickingarea add 0 0 0 100 0 40 spiralpad true", 12)
        cmd("structure load pw:spiral_pad 0 100 0", 6)
        cmd("structure load pw:mvv_palace_sw_a_r1 40 80 0", 10)
        # read back a few cells: the first stair's foot block and its head block (testforblock is gone; use 'fill ... keep' dry
        # tests via 'execute if block' which reports success/failure)
        cmd("execute if block 0 100 0 minecraft:smooth_stone run say PAD-FLOOR-OK", 2)
        cmd("stop", 8)
        try: p.wait(30)
        except Exception: p.kill()
    txt = out.read_text(errors="ignore")
    keys = ("spiral", "pw:", "ERROR", "error", "collision", "geometry", "block", "Structure", "structure", "PAD-")
    lines = [l for l in txt.splitlines() if any(k in l for k in keys) and "Profiler" not in l]
    print(out)
    for l in lines[:80]: print(l[:300])


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
