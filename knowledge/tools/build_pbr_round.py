#!/usr/bin/env python3
"""build_pbr_round.py — new pack versions for the BLOCK PBR ROUND (pbr_round.py staging, D-C421/D-C422).
Each pack: copy of its last DELIVERED build + _staging/pbr/<key> laid on top, minus the files listed in DROP.json (they stay
in the source build; the new build simply does not carry them — his never-delete rule), manifest bumped.
    rp04 1.3.144 -> 1.3.145   rp05 1.3.51 -> 1.3.52   rp10 1.3.43 (snow fix, never delivered) -> 1.3.44
    rp11 1.3.35 (delivered .mcpack, extracted) -> 1.3.36   rp01 1.3.107 -> 1.3.108   rp03 1.3.60 -> 1.3.61
    rp08 1.4.9 -> 1.4.10
Never rebuilds an existing build dir. Prints per-pack file counts and sizes."""
import json
import re
import shutil
import sys
import zipfile
from pathlib import Path

ROOT = Path("/home/claude")
STAGE = ROOT / "_staging/pbr"
DATE = "2026-10-01"
NOTE = ("BLOCK PBR ROUND: every block texture this pack draws carries its own texture set (normal + MERS) — the sets used "
        "to sit in RP-03 under this pack's own copies of the pictures, so they never applied; blank (mirror-shiny) MERS maps "
        "rebuilt from Patrix (#156); maps for textures that never had any.")
PACKS = {
    "rp04": ("rp04-144", "rp04-145", [1, 3, 145], NOTE + " Vanilla grass block sides: Mojang-style tint mask (.tga), Patrix overlay."),
    "rp05": ("rp05-51", "rp05-52", [1, 3, 52], NOTE),
    "rp10": ("rp10-143", "rp10-144", [1, 3, 44], NOTE + " Includes the 1.3.43 snow-layer key fix (never delivered on its own)."),
    "rp11": ("rp11-135", "rp11-136", [1, 3, 36], NOTE),
    "rp01": ("rp01-107", "rp01-108", [1, 3, 108], NOTE),
    "rp03": ("rp03-60", "rp03-61", [1, 3, 61], NOTE),
    "rp08": ("rp08-149", "rp08-1410", [1, 4, 10], NOTE),
}
RP11_ZIP = ROOT / "_intake/stack-rps/RP-11-AbsolutRealism-Ores-RP-v1_3_35.mcpack"


def ensure_rp11():
    d = ROOT / "_build/rp11-135"
    if d.exists():
        return
    z = zipfile.ZipFile(RP11_ZIP)
    names = [n for n in z.namelist() if not n.endswith("/")]
    pre = ""
    if "manifest.json" not in names:
        tops = {n.split("/", 1)[0] for n in names}
        pre = tops.pop() + "/" if len(tops) == 1 else ""
    for n in names:
        out = d / n[len(pre):]
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(z.read(n))


def bump(d, ver, note):
    mf = d / "manifest.json"
    m = json.loads(re.sub(r"(?m)^\s*//.*$", "", mf.read_text(encoding="utf-8-sig")))
    old = ".".join(map(str, m["header"]["version"]))
    v = ".".join(map(str, ver))
    m["header"]["version"] = ver
    for mod in m["modules"]:
        mod["version"] = ver
    m["header"]["name"] = re.sub(r"v\d+\.\d+\.\d+", f"v{v}", m["header"]["name"])
    m["header"]["description"] = f"v{v} ({DATE}) {note} Includes all of v{old}."
    mf.write_text(json.dumps(m, indent=1))


def main(keys=None):
    ensure_rp11()
    drop = json.loads((STAGE / "DROP.json").read_text()) if (STAGE / "DROP.json").exists() else {}
    out = {}
    for key, (src, dst, ver, note) in PACKS.items():
        if keys and key not in keys:
            continue
        if not (STAGE / key).exists():
            continue
        S, D = ROOT / "_build" / src, ROOT / "_build" / dst
        assert not D.exists(), f"{dst} exists — never rebuild a build dir"
        shutil.copytree(S, D)
        n_new = n_rep = 0
        for f in (STAGE / key).rglob("*"):
            if f.is_file():
                t = D / f.relative_to(STAGE / key)
                if t.exists():
                    n_rep += 1
                else:
                    n_new += 1
                t.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(f, t)
        n_drop = 0
        for rel in drop.get(key, []):
            t = D / rel
            if t.exists():
                t.unlink()          # usercustomize hook: moves it to _garbage (the source build keeps its copy)
                n_drop += 1
        bump(D, ver, note)
        size = sum(p.stat().st_size for p in D.rglob("*") if p.is_file())
        out[key] = {"dir": dst, "new": n_new, "replaced": n_rep, "dropped": n_drop, "bytes": size}
        print(f"{key}: {dst} +{n_new} new, {n_rep} replaced, {n_drop} dropped, {size / 2**20:.1f} MiB")
    (ROOT / "_docs/blocks/BUILD-PBR-ROUND.json").write_text(json.dumps(out, indent=1))
    return out


if __name__ == "__main__":
    main(sys.argv[1:] or None)
