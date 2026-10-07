#!/usr/bin/env python3
"""block_census.py — which vanilla block texture slots are HD (ours), which fall through to vanilla, and which
blocks are MIXED (some faces/states ours, some vanilla) — Abs0lum's furnace class.

Inputs: vanilla resource_pack (blobless clone, file list via git + blocks.json / terrain_texture.json /
flipbook_textures.json fetched raw) and the stack packs (zips in _packs, RP-04 from its newest build tree).
Priority = STACK-LIST order, top line = highest priority (the in-game active-packs list, top wins) — ASSUMPTION
recorded in the report.

Engine merge model (as documented / observed): per-block entry in blocks.json — highest pack wins wholesale;
per-key entry in terrain_texture.json — highest pack wins wholesale; texture file — highest pack that has the
file (png/tga/jpg).  Vanilla is the fallback for all three.
"""
import json, re, sys, zipfile, subprocess, collections
from pathlib import Path

ROOT = Path("/home/claude")
VAN = ROOT / "_intake/bedrock-samples"; VANJ = ROOT / "_intake/vanilla-bed"
PACKS = ROOT / "_packs"

def jload_text(t):
    t = t.lstrip("﻿")
    t = re.sub(r"//[^\n]*", "", t)                     # vanilla json carries // comments
    t = re.sub(r"/\*.*?\*/", "", t, flags=re.S)
    return json.loads(t)

class Pack:
    def __init__(self, name, files, reader):
        self.name = name; self.files = set(files); self.read = reader
        self.blocks = self._json("blocks.json"); self.terrain = self._json("textures/terrain_texture.json"); self.flip = self._json("textures/flipbook_textures.json")
        self.stems = {}
        for f in self.files:
            if f.startswith("textures/") and f.rsplit(".", 1)[-1] in ("png", "tga", "jpg", "jpeg"):
                self.stems.setdefault(f.rsplit(".", 1)[0], f)
    def _json(self, p):
        if p not in self.files: return None
        try: return jload_text(self.read(p))
        except Exception as e: print(f"  !! {self.name}: {p} unparsable: {e}"); return None

def zip_pack(name, path):
    z = zipfile.ZipFile(path)
    return Pack(name, z.namelist(), lambda p, z=z: z.read(p).decode("utf-8", "replace"))

def tree_pack(name, root):
    root = Path(root); fl = [str(p.relative_to(root)).replace("\\", "/") for p in root.rglob("*") if p.is_file()]
    return Pack(name, fl, lambda p, root=root: (root / p).read_text(encoding="utf-8", errors="replace"))

def vanilla_pack():
    fl = [p[len("resource_pack/"):] for p in subprocess.run(["git", "-C", str(VAN), "ls-tree", "-r", "--name-only", "HEAD"], capture_output=True, text=True).stdout.split("\n") if p.startswith("resource_pack/")]
    def rd(p):
        m = {"blocks.json": "blocks.json", "textures/terrain_texture.json": "terrain_texture.json", "textures/flipbook_textures.json": "flipbook_textures.json"}
        return (VANJ / m[p]).read_text(encoding="utf-8", errors="replace")
    return Pack("VANILLA", fl, rd)

def texture_paths(entry):
    """all texture paths an effective terrain_texture entry can resolve to (variations, index arrays)."""
    out = []
    def walk(x):
        if isinstance(x, str): out.append(x)
        elif isinstance(x, list):
            for y in x: walk(y)
        elif isinstance(x, dict):
            if "path" in x: out.append(x["path"])
            if "variations" in x: walk(x["variations"])
    walk(entry.get("textures"))
    return out

def main(stack_list, out_json, out_md, overrides=None):
    overrides = overrides or {}
    order = [l.strip() for l in Path(stack_list).read_text().split("\n") if l.strip().endswith(".mcpack") and "-RP-" in l or l.strip().startswith("RP-") ]
    packs = []
    for line in order:
        m = re.match(r"(RP-\d\d|PW-[A-Za-z]+-RP|PW-Civitas-Markers-RP)", line)
        if not m: continue
        tag = m.group(1)
        if tag in overrides: packs.append(tree_pack(f"{tag} (build {Path(overrides[tag]).name})", overrides[tag])); continue
        if tag == "RP-04": packs.append(tree_pack("RP-04 (build rp04-132)", ROOT / "_build/rp04-132")); continue
        cands = sorted(PACKS.glob(f"{tag}-*.mcpack")) + sorted(PACKS.glob(f"{tag.replace('PW-Civitas-Markers-RP','markers')}*"))
        cands = [c for c in cands if c.suffix == ".mcpack"]
        if not cands:
            mk = PACKS / "markers" / "PW-Civitas-Markers-RP-v0_1_7.mcpack"
            if tag.startswith("PW-Civitas") and mk.exists(): cands = [mk]
        if cands: packs.append(zip_pack(cands[-1].name, cands[-1]))
        else: print("  (no local copy for", line, ")")
    packs.append(vanilla_pack())
    print("priority order:", [p.name for p in packs])
    # effective blocks + terrain
    eff_blocks, eff_terrain, src_terrain, src_blocks = {}, {}, {}, {}
    for p in reversed(packs):                      # low -> high priority; higher overwrites
        if p.blocks:
            for k, v in p.blocks.items():
                if k == "format_version": continue
                eff_blocks[k] = v; src_blocks[k] = p.name
        if p.terrain and "texture_data" in p.terrain:
            for k, v in p.terrain["texture_data"].items(): eff_terrain[k] = v; src_terrain[k] = p.name
    def provider(path):
        for p in packs:
            if path in p.stems: return p.name
        return None
    report = {}
    for blk, ent in eff_blocks.items():
        tex = ent.get("textures") if isinstance(ent, dict) else None
        if tex is None: continue
        keys = [tex] if isinstance(tex, str) else list(dict.fromkeys(tex.values()))
        slots = []
        for k in keys:
            e = eff_terrain.get(k)
            if e is None: slots.append({"key": k, "path": None, "provider": "NO-KEY"}); continue
            for path in texture_paths(e): slots.append({"key": k, "path": path, "provider": provider(path) or "MISSING-EVERYWHERE"})
        provs = {s["provider"] for s in slots}
        ours = {x for x in provs if x not in ("VANILLA", "NO-KEY", "MISSING-EVERYWHERE")}
        cls = "ALL-OURS" if ours and provs <= ours else ("MIXED" if ours else ("ALL-VANILLA" if provs == {"VANILLA"} else "BROKEN"))
        report[blk] = {"class": cls, "blocks_json_from": src_blocks[blk], "slots": slots}
    # flipbooks: which atlas tiles vanilla animates, and who defines the flipbook that wins
    flips = {}
    for p in reversed(packs):
        if p.flip:
            for e in p.flip:
                if isinstance(e, dict) and "atlas_tile" in e: flips[e["atlas_tile"]] = {"pack": p.name, "texture": e.get("flipbook_texture"), "provider": provider(e.get("flipbook_texture", ""))}
    counts = collections.Counter(v["class"] for v in report.values())
    Path(out_json).write_text(json.dumps({"priority": [p.name for p in packs], "blocks": report, "flipbooks": flips, "counts": counts}, indent=1))
    # markdown
    L = [f"# BLOCK TEXTURE CENSUS — {len(report)} vanilla-registered blocks (effective blocks.json) · {dict(counts)}", "",
         f"Priority (top wins — ASSUMPTION: STACK-LIST top line = top of the in-game list): {', '.join(p.name for p in packs)}", ""]
    L.append("## MIXED blocks (some faces/variations ours, some vanilla) — the furnace class")
    for blk, v in sorted(report.items()):
        if v["class"] != "MIXED": continue
        van = sorted({s['path'] for s in v['slots'] if s['provider'] == 'VANILLA'}); our = sorted({(s['path'], s['provider']) for s in v['slots'] if s['provider'] not in ('VANILLA','NO-KEY','MISSING-EVERYWHERE')})
        L.append(f"- **{blk}** — vanilla: {', '.join(van)} · ours: {', '.join(f'{p} ({q})' for p, q in our)}")
    L.append(""); L.append("## BROKEN (a slot resolves to a key or file that exists nowhere)")
    for blk, v in sorted(report.items()):
        if v["class"] == "BROKEN": L.append(f"- {blk}: " + ", ".join(f"{s['key']}->{s['path']} [{s['provider']}]" for s in v["slots"] if s["provider"] in ("NO-KEY", "MISSING-EVERYWHERE")))
    L.append(""); L.append("## ALL-VANILLA blocks (no HD texture at all)")
    av = sorted(b for b, v in report.items() if v["class"] == "ALL-VANILLA"); L.append(f"{len(av)}: " + ", ".join(av))
    L.append(""); L.append("## Flipbooks (animated atlas tiles) — who defines the winning entry")
    for k, v in sorted(flips.items()): L.append(f"- {k}: defined by {v['pack']} -> {v['texture']} [{v['provider']}]")
    Path(out_md).write_text("\n".join(L) + "\n")
    print(dict(counts)); print("MIXED:", sum(1 for v in report.values() if v["class"] == "MIXED"))
    return report

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3])
