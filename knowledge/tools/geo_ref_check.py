#!/usr/bin/env python3
"""geo_ref_check.py — every geometry a BEHAVIOUR pack's blocks reference must exist in the RESOURCE packs of the stack,
with the exact identifier (D-C1006-GEO: the 1.3.228 spiral blocks referenced 104 mixed-case geometries that the PS5
client never registered; the earlier 228 check only covered TEXTURES).

Usage: geo_ref_check.py --bp BP_DIR [--bp BP_DIR ...] --rp RP_DIR [--rp RP_DIR ...]

Checks (exit 1 on any failure):
  missing    a referenced geometry id that no RP defines (exact string)
  uppercase  a referenced or defined block geometry id with an uppercase letter (none of our 4,618 working ones has one)
  format     a block geometry file whose format_version is not one our working packs use (1.12.0 / 1.16.0)
"""
import argparse
import json
import re
import sys
from pathlib import Path

WORKING_GEO_FORMATS = {"1.12.0", "1.16.0"}


def load_json(path):
    """Parse a pack JSON file (tolerates a UTF-8 BOM); None when it is not valid JSON."""
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, ValueError):
        return None


def referenced_geometries(bp_dir):
    """{geometry id: [block file, ...]} for every minecraft:geometry identifier in the BP's blocks (base + permutations)."""
    refs = {}
    for f in sorted((bp_dir / "blocks").rglob("*.json")):
        text = f.read_text(encoding="utf-8-sig", errors="ignore")
        for gid in re.findall(r'"identifier"\s*:\s*"(geometry\.[^"]+)"', text):
            refs.setdefault(gid, []).append(f.name)
    return refs


def defined_geometries(rp_dir):
    """{geometry id: (file, format_version)} for every geometry in the RP's models/ tree."""
    out = {}
    for f in sorted((rp_dir / "models").rglob("*.json")):
        j = load_json(f)
        if not isinstance(j, dict):
            continue
        geos = j.get("minecraft:geometry")
        if not isinstance(geos, list):
            continue
        for g in geos:
            gid = (g.get("description") or {}).get("identifier")
            if gid:
                out[gid] = (f, j.get("format_version"))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bp", action="append", default=[], type=Path)
    ap.add_argument("--rp", action="append", default=[], type=Path)
    a = ap.parse_args()
    refs = {}
    for bp in a.bp:
        for gid, files in referenced_geometries(bp).items():
            refs.setdefault(gid, []).extend(files)
    defined = {}
    for rp in a.rp:
        defined.update(defined_geometries(rp))
    missing = sorted(g for g in refs if g not in defined)
    upper = sorted(g for g in refs if re.search(r"[A-Z]", g))
    bad_fmt = sorted({(str(defined[g][0]), defined[g][1]) for g in refs if g in defined and defined[g][1] not in WORKING_GEO_FORMATS})
    print(f"referenced {len(refs)} · defined {len(defined)} · missing {len(missing)} · uppercase {len(upper)} · odd format files {len(bad_fmt)}")
    for g in missing[:20]:
        print(f"  MISSING   {g}  (used by {refs[g][0]})")
    for g in upper[:20]:
        print(f"  UPPERCASE {g}")
    for f, fv in bad_fmt[:20]:
        print(f"  FORMAT    {fv}  {f}")
    sys.exit(1 if (missing or upper or bad_fmt) else 0)


if __name__ == "__main__":
    main()
