#!/usr/bin/env python3
"""bds_load.py — D-C357 (his 00:09 ask): load our packs in Mojang's Bedrock Dedicated Server (1.26.52.3, official download) and
collect the content log ourselves. Catches every BEHAVIOUR-side load error (entities, spawn rules, items, events, scripts); a
server draws nothing, so resource-pack render errors (geometry) still need his device.
Usage: bds_load.py [--seconds N] DIR [DIR ...]      (each DIR a built pack folder with a manifest.json; type from its modules)
Output: _bds/logs/load-<stamp>.txt (full console) + a grouped summary on stdout."""
import json, re, shutil, subprocess, sys, time
from collections import Counter
from pathlib import Path

SRV = Path("/home/claude/_bds/srv"); WORLD = SRV / "worlds/artest"; LOGS = Path("/home/claude/_bds/logs")


PRISTINE = Path("/home/claude/_bds/pristine_world")
GARBAGE = Path("/home/claude/_garbage")


def discard(p):
    """his 14:41 (10-01) rule: never delete — move into _garbage/<UTC stamp>/<original path>."""
    p = Path(p)
    if not p.exists():
        return
    dst = GARBAGE / time.strftime("%Y%m%d-%H%M%S", time.gmtime()) / p.resolve().relative_to("/home/claude")
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(p), str(dst))   # an untouched vanilla world: every load starts clean (no chunks from an earlier pack set)


def install(dirs, keep_world=False):
    # one server at a time: installing while a bedrock_server runs swaps its pack dirs and world lists under it, and the
    # second server fails on the port (03:14 10-03: an inspect run tried to start under a finishing evolution run)
    import subprocess as _sp
    if _sp.run(["pgrep", "-x", "bedrock_server"], capture_output=True).returncode == 0:
        raise SystemExit("REFUSED: a bedrock_server is already running — wait for it (pgrep -x bedrock_server)")
    bps, rps = [], []
    if PRISTINE.exists() and not keep_world:        # keep_world: a two-stage experiment reads the world the previous run saved (P-4)
        discard(WORLD); shutil.copytree(PRISTINE, WORLD)
    for kind in ("behavior_packs", "resource_packs"):
        for p in list((SRV / kind).glob("pw_*")): discard(p)
    for d in map(Path, dirs):
        m = json.loads((d / "manifest.json").read_text(encoding="utf-8-sig"))
        types = {x.get("type") for x in m["modules"]}
        kind = "resource_packs" if "resources" in types else "behavior_packs"
        dst = SRV / kind / ("pw_" + d.name)
        shutil.copytree(d, dst)
        (rps if kind == "resource_packs" else bps).append({"pack_id": m["header"]["uuid"], "version": m["header"]["version"]})
    (WORLD / "world_behavior_packs.json").write_text(json.dumps(bps, indent=1))
    (WORLD / "world_resource_packs.json").write_text(json.dumps(rps, indent=1))
    return bps, rps


def run(seconds):
    LOGS.mkdir(parents=True, exist_ok=True)
    out = LOGS / f"load-{time.strftime('%Y%m%d-%H%M%S')}.txt"
    with open(out, "w") as f:
        p = subprocess.Popen(["./bedrock_server"], cwd=SRV, stdin=subprocess.PIPE, stdout=f, stderr=subprocess.STDOUT,
                             env={"LD_LIBRARY_PATH": "."}, text=True)
        t0 = time.time()
        while time.time() - t0 < seconds:
            time.sleep(1)
            if "Server started" in out.read_text(errors="ignore") and time.time() - t0 > 8: break
        time.sleep(3)
        try: p.stdin.write("stop\n"); p.stdin.flush()
        except Exception: pass
        try: p.wait(timeout=60)
        except subprocess.TimeoutExpired: p.kill()
    return out


def summarize(out):
    lines = out.read_text(errors="ignore").splitlines()
    errs = [l for l in lines if re.search(r"\b(ERROR|WARN)\b|\[(error|warning)\]", l)]
    key = Counter()
    for l in errs:
        m = re.search(r"\|\s*(pw:[a-z0-9_]+|[a-z_]+:[a-z0-9_]+)\s*\|.*?\|\s*(.+)$", l)
        msg = re.sub(r"pw:[a-z0-9_]+", "<id>", l.split("]-")[-1] if "]-" in l else l)
        msg = re.sub(r"/[^|]*behavior_packs/[^|]*\|", "", msg)
        key[re.sub(r"\s+", " ", msg)[-160:]] += 1
    started = any("Server started" in l for l in lines)
    return started, errs, key


if __name__ == "__main__":
    args = sys.argv[1:]; secs = 120
    if args[:1] == ["--seconds"]: secs = int(args[1]); args = args[2:]
    bps, rps = install(args)
    out = run(secs)
    started, errs, key = summarize(out)
    print(f"BDS 1.26.52.3 · {len(bps)} BP + {len(rps)} RP · started={started} · {len(errs)} error/warning lines · log {out}")
    for msg, n in key.most_common(40): print(f"{n:5d}  {msg}")
