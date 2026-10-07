#!/usr/bin/env python3
"""stack_now.py — his INSTALLED resource-pack stack (top first, as of his log 4, 10-01 16:49) + a resolver:
terrain key -> (pack, definition) and texture path -> (pack, file) through the stack (top pack wins).
Sources: built dirs for our packs; the delivered .mcpack zips for packs not built here (LeafProbe, StripMine RP, RP-11)."""
import io
import json
import re
import zipfile
from pathlib import Path

ROOT = Path("/home/claude")
ORDER = [("Markers RP 0.2.1", ROOT / "_build/markers-0.2.1/RP"),
         ("LeafProbe RP 0.3.1", ROOT / "_intake/stack-rps/PW-LeafProbe-RP-v0_3_1.mcpack"),
         ("StripMine RP 3.0.1", ROOT / "_intake/stack-rps/PW-StripMine-RP-v3_0_1.mcpack"),
         ("RP-11 1.3.35", ROOT / "_intake/stack-rps/RP-11-AbsolutRealism-Ores-RP-v1_3_35.mcpack"),
         ("RP-10 1.3.42", ROOT / "_build/rp10-142"), ("RP-08 1.4.9", ROOT / "_build/rp08-149"),
         ("RP-07 1.4.43", ROOT / "_build/rp07-1443"), ("RP-06 1.4.28", ROOT / "_build/rp06-1428"),
         ("RP-05 1.3.51", ROOT / "_build/rp05-51"), ("RP-04 1.3.144", ROOT / "_build/rp04-144"),
         ("RP-03 1.3.60", ROOT / "_build/rp03-60"), ("RP-02 2.0.5", ROOT / "_build/rp02-205"),
         ("RP-01 1.3.107", ROOT / "_build/rp01-107"),
         ("vanilla (bedrock-samples)", ROOT / "_intake/bedrock-samples/resource_pack")]


import os
if os.environ.get("PW_STACK") == "pbr":     # the block PBR round's new builds in place of the installed ones (verification)
    _NEW = {"RP-11 1.3.35": ("RP-11 1.3.36", ROOT / "_build/rp11-136"), "RP-10 1.3.42": ("RP-10 1.3.44", ROOT / "_build/rp10-144"),
            "RP-08 1.4.9": ("RP-08 1.4.10", ROOT / "_build/rp08-1410"), "RP-05 1.3.51": ("RP-05 1.3.52", ROOT / "_build/rp05-52"),
            "RP-04 1.3.144": ("RP-04 1.3.146", ROOT / "_build/rp04-146"), "RP-03 1.3.60": ("RP-03 1.3.61", ROOT / "_build/rp03-61"),
            "RP-01 1.3.107": ("RP-01 1.3.108", ROOT / "_build/rp01-108")}
    ORDER = [_NEW.get(n, (n, s)) for n, s in ORDER]
if os.environ.get("PW_STACK") == "tier":    # the resolution tier round on top of the delivered block PBR round
    _NEW = {"RP-11 1.3.35": ("RP-11 1.3.36", ROOT / "_build/rp11-136"), "RP-10 1.3.42": ("RP-10 1.3.45", ROOT / "_build/rp10-145"),
            "RP-08 1.4.9": ("RP-08 1.4.10", ROOT / "_build/rp08-1410"), "RP-05 1.3.51": ("RP-05 1.3.53", ROOT / "_build/rp05-53"),
            "RP-04 1.3.144": ("RP-04 1.3.147", ROOT / "_build/rp04-147"), "RP-03 1.3.60": ("RP-03 1.3.62", ROOT / "_build/rp03-62"),
            "RP-01 1.3.107": ("RP-01 1.3.109", ROOT / "_build/rp01-109")}
    ORDER = [_NEW.get(n, (n, s)) for n, s in ORDER]

if os.environ.get("PW_STACK") == "r1002a":  # round 1002a (bark ownership + sand B+G2 + vines 256) on the tier stack
    _NEW = {"RP-11 1.3.35": ("RP-11 1.3.37", ROOT / "_build/rp11-137"), "RP-10 1.3.42": ("RP-10 1.3.46", ROOT / "_build/rp10-146"),
            "RP-08 1.4.9": ("RP-08 1.4.10", ROOT / "_build/rp08-1410"), "RP-05 1.3.51": ("RP-05 1.3.54", ROOT / "_build/rp05-54"),
            "RP-04 1.3.144": ("RP-04 1.3.148", ROOT / "_build/rp04-148"), "RP-03 1.3.60": ("RP-03 1.3.63", ROOT / "_build/rp03-63"),
            "RP-01 1.3.107": ("RP-01 1.3.110", ROOT / "_build/rp01-110"), "RP-02 2.0.5": ("RP-02 2.0.6", ROOT / "_build/rp02-206")}
    ORDER = [_NEW.get(n, (n, s)) for n, s in ORDER]

if os.environ.get("PW_STACK") == "r1002b":  # round 1002b (plant flipbooks) on top of 1002a
    _NEW = {"RP-11 1.3.35": ("RP-11 1.3.37", ROOT / "_build/rp11-137"), "RP-10 1.3.42": ("RP-10 1.3.47", ROOT / "_build/rp10-147"),
            "RP-08 1.4.9": ("RP-08 1.4.10", ROOT / "_build/rp08-1410"), "RP-05 1.3.51": ("RP-05 1.3.55", ROOT / "_build/rp05-55"),
            "RP-04 1.3.144": ("RP-04 1.3.148", ROOT / "_build/rp04-148"), "RP-03 1.3.60": ("RP-03 1.3.64", ROOT / "_build/rp03-64"),
            "RP-01 1.3.107": ("RP-01 1.3.111", ROOT / "_build/rp01-111"), "RP-02 2.0.5": ("RP-02 2.0.6", ROOT / "_build/rp02-206")}
    ORDER = [_NEW.get(n, (n, s)) for n, s in ORDER]

if os.environ.get("PW_STACK") == "r1002c":  # round 1002c (plank grids) on top of 1002b
    _NEW = {"RP-11 1.3.35": ("RP-11 1.3.37", ROOT / "_build/rp11-137"), "RP-10 1.3.42": ("RP-10 1.3.47", ROOT / "_build/rp10-147"),
            "RP-08 1.4.9": ("RP-08 1.4.10", ROOT / "_build/rp08-1410"), "RP-05 1.3.51": ("RP-05 1.3.55", ROOT / "_build/rp05-55"),
            "RP-04 1.3.144": ("RP-04 1.3.149", ROOT / "_build/rp04-149"), "RP-03 1.3.60": ("RP-03 1.3.64", ROOT / "_build/rp03-64"),
            "RP-01 1.3.107": ("RP-01 1.3.111", ROOT / "_build/rp01-111"), "RP-02 2.0.5": ("RP-02 2.0.6", ROOT / "_build/rp02-206")}
    ORDER = [_NEW.get(n, (n, s)) for n, s in ORDER]

if os.environ.get("PW_STACK") == "r1002d":  # size-cap fix (planks -> RP-01, dirt -> RP-10)
    _NEW = {"RP-11 1.3.35": ("RP-11 1.3.37", ROOT / "_build/rp11-137"), "RP-10 1.3.42": ("RP-10 1.3.48", ROOT / "_build/rp10-148"),
            "RP-08 1.4.9": ("RP-08 1.4.10", ROOT / "_build/rp08-1410"), "RP-05 1.3.51": ("RP-05 1.3.55", ROOT / "_build/rp05-55"),
            "RP-04 1.3.144": ("RP-04 1.3.150", ROOT / "_build/rp04-150"), "RP-03 1.3.60": ("RP-03 1.3.64", ROOT / "_build/rp03-64"),
            "RP-01 1.3.107": ("RP-01 1.3.112", ROOT / "_build/rp01-112"), "RP-02 2.0.5": ("RP-02 2.0.6", ROOT / "_build/rp02-206")}
    ORDER = [_NEW.get(n, (n, s)) for n, s in ORDER]

if os.environ.get("PW_STACK") == "r1002e":  # 3D vines on top of the final set
    _NEW = {"RP-11 1.3.35": ("RP-11 1.3.37", ROOT / "_build/rp11-137"), "RP-10 1.3.42": ("RP-10 1.3.48", ROOT / "_build/rp10-148"),
            "RP-08 1.4.9": ("RP-08 1.4.10", ROOT / "_build/rp08-1410"), "RP-05 1.3.51": ("RP-05 1.3.55", ROOT / "_build/rp05-55"),
            "RP-04 1.3.144": ("RP-04 1.3.150", ROOT / "_build/rp04-150"), "RP-03 1.3.60": ("RP-03 1.3.64", ROOT / "_build/rp03-64"),
            "RP-01 1.3.107": ("RP-01 1.3.113", ROOT / "_build/rp01-113"), "RP-02 2.0.5": ("RP-02 2.0.6", ROOT / "_build/rp02-206")}
    ORDER = [_NEW.get(n, (n, s)) for n, s in ORDER]

if os.environ.get("PW_STACK") == "r1002f":  # atlas budget (256->192 except leaves + sand)
    _NEW = {"RP-11 1.3.35": ("RP-11 1.3.38", ROOT / "_build/rp11-138"), "RP-10 1.3.42": ("RP-10 1.3.49", ROOT / "_build/rp10-149"),
            "RP-08 1.4.9": ("RP-08 1.4.11", ROOT / "_build/rp08-1411"), "RP-05 1.3.51": ("RP-05 1.3.56", ROOT / "_build/rp05-56"),
            "RP-04 1.3.144": ("RP-04 1.3.151", ROOT / "_build/rp04-151"), "RP-03 1.3.60": ("RP-03 1.3.65", ROOT / "_build/rp03-65"),
            "RP-01 1.3.107": ("RP-01 1.3.114", ROOT / "_build/rp01-114"), "RP-02 2.0.5": ("RP-02 2.0.6", ROOT / "_build/rp02-206")}
    ORDER = [_NEW.get(n, (n, s)) for n, s in ORDER]

if os.environ.get("PW_STACK") in ("r1002g", "r1002h", "r1002i", "r1002l", "r1002m"):  # dirt family -> 128 on top of 1002f
    _NEW = {"RP-11 1.3.35": ("RP-11 1.3.38", ROOT / "_build/rp11-138"), "RP-10 1.3.42": ("RP-10 1.3.50", ROOT / "_build/rp10-150"),
            "RP-08 1.4.9": ("RP-08 1.4.11", ROOT / "_build/rp08-1411"), "RP-05 1.3.51": ("RP-05 1.3.57", ROOT / "_build/rp05-57"),
            "RP-04 1.3.144": ("RP-04 1.3.152", ROOT / "_build/rp04-152"), "RP-03 1.3.60": ("RP-03 1.3.65", ROOT / "_build/rp03-65"),
            "RP-01 1.3.107": ("RP-01 1.3.114", ROOT / "_build/rp01-114"), "RP-02 2.0.5": ("RP-02 2.0.6", ROOT / "_build/rp02-206")}
    ORDER = [_NEW.get(n, (n, s)) for n, s in ORDER]

if os.environ.get("PW_STACK") in ("r1002h", "r1002i", "r1002l", "r1002m"):  # vine wind + rustle (RP-01 1.3.115), RP-04 vine copies dropped (1.3.153)
    ORDER = [{"RP-04 1.3.152": ("RP-04 1.3.153", ROOT / "_build/rp04-153"),
              "RP-01 1.3.114": ("RP-01 1.3.115", ROOT / "_build/rp01-115")}.get(n, (n, s)) for n, s in ORDER]

if os.environ.get("PW_STACK") in ("r1002i", "r1002l", "r1002m"):  # 128 round (rows 1,2,3,4,7,9,10) + sand grains non-metal, on top of r1002h
    ORDER = [{"RP-04 1.3.153": ("RP-04 1.3.154", ROOT / "_build/rp04-154"), "RP-01 1.3.115": ("RP-01 1.3.116", ROOT / "_build/rp01-116"),
              "RP-03 1.3.65": ("RP-03 1.3.66", ROOT / "_build/rp03-66"), "RP-05 1.3.57": ("RP-05 1.3.58", ROOT / "_build/rp05-58"),
              "RP-08 1.4.11": ("RP-08 1.4.12", ROOT / "_build/rp08-1412"), "RP-10 1.3.50": ("RP-10 1.3.51", ROOT / "_build/rp10-151")}.get(n, (n, s)) for n, s in ORDER]

if os.environ.get("PW_STACK") == "r1002l":  # ores rebuilt in RP-11 1.3.39, RP-04 1.3.155 without ore copies, on top of r1002i
    ORDER = [{"RP-11 1.3.38": ("RP-11 1.3.39", ROOT / "_build/rp11-139"), "RP-04 1.3.154": ("RP-04 1.3.155", ROOT / "_build/rp04-155")}.get(n, (n, s)) for n, s in ORDER]

if os.environ.get("PW_STACK") == "r1002m":  # ore round 1.3.40 (RP-11 1.3.40, RP-04 1.3.156 + roof cut-outs back at 256, RP-03 1.3.67)
    ORDER = [{"RP-11 1.3.38": ("RP-11 1.3.40", ROOT / "_build/rp11-140"), "RP-04 1.3.154": ("RP-04 1.3.156", ROOT / "_build/rp04-156"),
              "RP-03 1.3.66": ("RP-03 1.3.67", ROOT / "_build/rp03-67")}.get(n, (n, s)) for n, s in ORDER]

if os.environ.get("PW_STACK") == "ship1002":   # the recheck fix round on top of the delivered set: RP-07 1.4.45, RP-08 1.4.14 (10-02 23:1x)
    ORDER = [{"RP-11 1.3.35": ("RP-11 1.3.40", ROOT / "_build/rp11-140"), "RP-10 1.3.42": ("RP-10 1.3.51", ROOT / "_build/rp10-151"),
              "RP-08 1.4.9": ("RP-08 1.4.14", ROOT / "_build/rp08-1414"), "RP-07 1.4.43": ("RP-07 1.4.45", ROOT / "_build/rp07-1445"),
              "RP-05 1.3.51": ("RP-05 1.3.58", ROOT / "_build/rp05-58"), "RP-04 1.3.144": ("RP-04 1.3.156", ROOT / "_build/rp04-156"),
              "RP-06 1.4.28": ("RP-06 1.4.29", ROOT / "_build/rp06-1429"),
              "RP-03 1.3.60": ("RP-03 1.3.67", ROOT / "_build/rp03-67"), "RP-02 2.0.5": ("RP-02 2.0.7", ROOT / "_build/rp02-207"),
              "RP-01 1.3.107": ("RP-01 1.3.117", ROOT / "_build/rp01-117")}.get(n, (n, s)) for n, s in ORDER
             if not n.startswith("StripMine")]

if os.environ.get("PW_STACK") == "w2":   # the 10-03 install set: final + RP-01 1.3.118 (root sounds), RP-07 1.4.45, RP-08 1.4.14 (V6 recheck fixes)
    ORDER = [{"RP-11 1.3.35": ("RP-11 1.3.40", ROOT / "_build/rp11-140"), "RP-10 1.3.42": ("RP-10 1.3.51", ROOT / "_build/rp10-151"),
              "RP-08 1.4.9": ("RP-08 1.4.14", ROOT / "_build/rp08-1414"), "RP-07 1.4.43": ("RP-07 1.4.45", ROOT / "_build/rp07-1445"),
              "RP-05 1.3.51": ("RP-05 1.3.58", ROOT / "_build/rp05-58"), "RP-04 1.3.144": ("RP-04 1.3.156", ROOT / "_build/rp04-156"),
              "RP-06 1.4.28": ("RP-06 1.4.29", ROOT / "_build/rp06-1429"),
              "RP-03 1.3.60": ("RP-03 1.3.67", ROOT / "_build/rp03-67"), "RP-02 2.0.5": ("RP-02 2.0.7", ROOT / "_build/rp02-207"),
              "RP-01 1.3.107": ("RP-01 1.3.118", ROOT / "_build/rp01-118")}.get(n, (n, s)) for n, s in ORDER
             if not n.startswith("StripMine")]

if os.environ.get("PW_STACK") == "final":   # the complete set being prepared: r1002m + StripMine dissolved (RP-07 1.4.44, RP-08 1.4.13, RP-02 2.0.7), StripMine RP removed
    ORDER = [{"RP-11 1.3.35": ("RP-11 1.3.40", ROOT / "_build/rp11-140"), "RP-10 1.3.42": ("RP-10 1.3.51", ROOT / "_build/rp10-151"),
              "RP-08 1.4.9": ("RP-08 1.4.13", ROOT / "_build/rp08-1413"), "RP-07 1.4.43": ("RP-07 1.4.44", ROOT / "_build/rp07-1444"),
              "RP-05 1.3.51": ("RP-05 1.3.58", ROOT / "_build/rp05-58"), "RP-04 1.3.144": ("RP-04 1.3.156", ROOT / "_build/rp04-156"),
              "RP-06 1.4.28": ("RP-06 1.4.29", ROOT / "_build/rp06-1429"),
              "RP-03 1.3.60": ("RP-03 1.3.67", ROOT / "_build/rp03-67"), "RP-02 2.0.5": ("RP-02 2.0.7", ROOT / "_build/rp02-207"),
              "RP-01 1.3.107": ("RP-01 1.3.117", ROOT / "_build/rp01-117")}.get(n, (n, s)) for n, s in ORDER
             if not n.startswith("StripMine")]


def jl(b):
    s = b.decode("utf-8-sig") if isinstance(b, bytes) else b
    s = re.sub(r"(?m)^\s*//.*$", "", s)
    return json.loads(s)


class PackFS:
    def __init__(self, name, src):
        self.name, self.src = name, Path(src)
        self.zip = zipfile.ZipFile(self.src) if self.src.suffix == ".mcpack" else None
        if self.zip:
            names = [n for n in self.zip.namelist() if not n.endswith("/")]
            pre = ""
            if not any(n == "manifest.json" for n in names):            # a zip with one top folder
                tops = {n.split("/", 1)[0] for n in names}
                if len(tops) == 1:
                    pre = tops.pop() + "/"
            self.pre = pre
            self.files = {n[len(pre):] for n in names if n.startswith(pre)}
        else:
            self.files = {str(p.relative_to(self.src)).replace("\\", "/") for p in self.src.rglob("*") if p.is_file()}
        self.lower = {f.lower(): f for f in self.files}

    def read(self, rel):
        rel = self.lower.get(rel.lower(), rel)
        return self.zip.read(self.pre + rel) if self.zip else (self.src / rel).read_bytes()

    def has(self, rel):
        return rel.lower() in self.lower

    def json(self, rel):
        return jl(self.read(rel)) if self.has(rel) else None


def packs():
    return [PackFS(n, s) for n, s in ORDER]


def terrain(P):
    """key -> (pack name, definition, pack index) — top pack wins."""
    out = {}
    for i, p in enumerate(P):
        d = p.json("textures/terrain_texture.json")
        for k, v in ((d or {}).get("texture_data") or {}).items():
            out.setdefault(k, (p.name, v, i))
    return out


def find_image(P, path, from_index=0):
    """texture path (no extension) -> (pack, file) — the first pack (top first) holding .png / .tga / .jpg."""
    for p in P[from_index:]:
        for ext in (".png", ".tga", ".jpg"):
            if p.has(path + ext):
                return p, path + ext
    return None, None


def paths_of(defn):
    t = defn.get("textures") if isinstance(defn, dict) else defn
    out = []
    if isinstance(t, str):
        out.append(t)
    elif isinstance(t, dict):
        if "path" in t:
            out.append(t["path"])
        for v in t.get("variations") or []:
            out.append(v["path"] if isinstance(v, dict) else v)
    elif isinstance(t, list):
        for v in t:
            if isinstance(v, str):
                out.append(v)
            elif isinstance(v, dict):
                if "path" in v:
                    out.append(v["path"])
                for w in v.get("variations") or []:
                    out.append(w["path"] if isinstance(w, dict) else w)
    return out
