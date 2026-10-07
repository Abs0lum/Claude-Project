#!/usr/bin/env python3
"""build_rp08_148.py — D-C283 (his 12:40 "yes" to the idle longbow). RP-08 Items RP v1.4.8 from v1.4.7.

The realistic longbow art (256x256) is in RP-08 as textures/items/bow.png + bow_pulling_0..2.png — Java's file names. Bedrock's
bow draws `bow_standby` when idle (item icon, held by a skeleton / stray / player) and bow_pulling_0..2 while drawing, so only the
drawing frames reached the game (same paths). Added: textures/items/bow_standby.png (byte copy of bow.png). Nothing else changes.
verify: python3 build_rp08_148.py --verify"""
import hashlib, json, shutil, sys
from pathlib import Path

ROOT = Path("/home/claude")
SRC, DST, VER = ROOT / "_build/rp08-147", ROOT / "_build/rp08-148", [1, 4, 8]
NAME = "AbsolutRealism Items RP v1.4.8"
DESC = ("v1.4.8 (2026-09-29) IDLE LONGBOW (D-C283): the realistic longbow now also shows when the bow is idle (skeletons, strays, "
        "your hand, the inventory icon) — textures/items/bow_standby.png added. Everything else identical to v1.4.7.")
ADDED = ["textures/items/bow_standby.png"]


def md5(p): return hashlib.md5(Path(p).read_bytes()).hexdigest()


def build():
    if DST.exists(): shutil.rmtree(DST)
    shutil.copytree(SRC, DST)
    assert not (DST / ADDED[0]).exists()
    shutil.copyfile(DST / "textures/items/bow.png", DST / ADDED[0])
    m = json.loads((DST / "manifest.json").read_text())
    m["header"]["version"] = VER; m["header"]["name"] = NAME; m["header"]["description"] = DESC
    for mod in m.get("modules", []): mod["version"] = VER
    (DST / "manifest.json").write_text(json.dumps(m, indent=1))
    print("built", DST)


def verify():
    fails = []
    def check(tag, ok, msg):
        print(("PASS " if ok else "FAIL ") + tag + " — " + msg)
        if not ok: fails.append(tag)
    fo = {str(p.relative_to(SRC)): md5(p) for p in SRC.rglob("*") if p.is_file()}
    fn = {str(p.relative_to(DST)): md5(p) for p in DST.rglob("*") if p.is_file()}
    changed = sorted(k for k in fo if k in fn and fo[k] != fn[k]); added = sorted(set(fn) - set(fo)); removed = sorted(set(fo) - set(fn))
    check("A1 only manifest changed, only bow_standby added, nothing removed", changed == ["manifest.json"] and added == ADDED and not removed,
          f"changed {changed} added {added} removed {removed}")
    check("B1 bow_standby.png is a byte copy of bow.png", fn[ADDED[0]] == fn["textures/items/bow.png"], fn[ADDED[0]])
    m = json.loads((DST / "manifest.json").read_text()); mo = json.loads((SRC / "manifest.json").read_text())
    check("K manifest 1.4.8, uuids kept", m["header"]["version"] == VER and m["header"]["uuid"] == mo["header"]["uuid"]
          and [x["uuid"] for x in m["modules"]] == [x["uuid"] for x in mo["modules"]], str(m["header"]["version"]))
    sys.path.insert(0, str(ROOT / "tools")); import molang_lint
    n, e = molang_lint.lint_pack(DST)
    check("MLS every Molang string parses (standing gate)", not e, f"{n} strings, {len(e)} errors")
    print(f"\n{'GATE OPEN' if not fails else 'GATE CLOSED'} {4 - len(fails)}/4")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(verify() if "--verify" in sys.argv else build())
