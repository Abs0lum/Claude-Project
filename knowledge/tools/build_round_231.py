#!/usr/bin/env python3
"""build_round_231.py — round 231 combined build (worker INTEGRATE, 2026-10-07). Deterministic; never overwrites.

Packs (new dir <- base dir):
  bp02  BP-02 1.3.231  _build/bp02-231  <- _build/bp02-230 (SLIM: no pw:var on ramps — asserted, never re-added)
  rp13  RP-13 1.0.2    _build/rp13-102  <- _build/rp13-101
  rp04  RP-04 1.3.160  _build/rp04-160  <- _build/rp04-159
  rp01  RP-01 1.3.126  _build/rp01-126  <- _build/rp01-125   (needs bp02-231: falling-tree copies regenerated from its trees)
  rp12  RP-12 1.0.2    _build/rp12-102  <- _build/rp12-101   (+ rp12lite 1.0.2 _build/rp12-102-lite <- rp12-101-lite with --lite)

Inputs (each staged file md5-checked against its README / MD5SUMS before use):
  CIVITAS scripts  tools/bp02_src_228/*.js (every .js that differs from bp02-230/scripts), PW_BUILD 1.3.231 +
                   `globalThis.__PW_BUILD = PW_BUILD;` (BLOCKS); the old "companion v7 LOADED" string-replace step is GONE.
  blocks231        RP-12 frames geo · RP-04 bed textures (48) + terrain_texture (+1 key) · BP-02 inn v2 structures (4 + 28) +
                   pw_civ_buildings.js (inn entries) · 5 texture-key block fixes · companion banner (= src copy).
  ramps231         t/v_ramp8 structures (void -> air) · ramp_v9 geometry (RP-13 2 files, RP-04 2 files).
  textures231/ramp-blocks  266 BP-02 pw_ramp_*.json (fill -> own '*' texture; ruling D-C1007-R231c).
  fill removal     RP-13's pw_fill* terrain keys + files removed (flag ON by default; --keep-fills turns it off).
  trees231         216 BP-02 tree structures + 54 RP-01 seamless bark files.
  acacia_230       32 BP-02 acacia structures.
  skyway230        option C: BP-02 6 blocks + skyway_test structure; RP-13 geo, 28 textures, 7 terrain keys, texts/.
  NOT included     palace231, castle231 (pending his OK). Texture tier output: hook --tier-dir DIR (DIR/<pack key>/<pack path>).

Usage:
  python3 tools/build_round_231.py --check                     # validate every input, write nothing
  python3 tools/build_round_231.py [--packs bp02,rp13,rp04,rp01,rp12] [--keep-fills] [--lite] [--tier-dir DIR]
  python3 tools/build_round_231.py --post                      # checks on the built dirs (geo refs, permutations, scripts, suites)
A pack whose new dir already exists is SKIPPED (versions are never reused); delete nothing to "rebuild" — bump instead.
Disk: before every copy, free − (size of base) must stay ≥ 400 MB, else the build stops with a note."""
import hashlib
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

HOME = Path("/home/claude")
B = HOME / "_build"
T = HOME / "tools"
S = HOME / "_staging"
JS = T / "bp02_src_228"
LOG = HOME / "_logs/build_round_231.json"
MIN_FREE = 400 * 1024 * 1024
FT_ARGS = ["--maxb=8", "--clusters=12", "--runfrom=3", "--close=3"]       # 1.3.121's meshing (build_rp01_124/125, acacia_230)
FT_INDEX_DOC = HOME / "_docs/fell/ft_tpl_index.json"

PACKS = {   # key: (base, new, version, stamp)
    "bp02": ("bp02-230", "bp02-231", [1, 3, 231],
             "v1.3.231 (2026-10-07) round 231: CIVITAS scripts (inn open round the clock, idle civs spread, land/streets work), inn v2, "
             "ramp8 top layer void->air, ramp blocks fill->own texture, dodecagon trees (one bark, clump step, no jump, full sheath, "
             "spruce cap v2), acacia limb ends, skyway rail option C, 5 texture-key fixes, PW-C2 banner from PW_BUILD. Slim ramps kept. "
             "Needs RP-01 1.3.126 + RP-04 1.3.160 + RP-13 1.0.2 + RP-12 1.0.2. Personal use. "),
    "rp13": ("rp13-101", "rp13-102", [1, 0, 2],
             "v1.0.2 (2026-10-07) round 231: ramp_v9 geometry (solid stepped sides), pw_fill textures retired (248 keys, 992 files), "
             "skyway rail option C. "),
    "rp04": ("rp04-159", "rp04-160", [1, 3, 160],
             "v1.3.160 (2026-10-07) round 231: ramp_v9 legacy ramp geometry, bed legs, pw_acacia_log_top_single key, texture variant cut "
             "(65 variation keys trimmed, 75 keys repointed, 435 unused files removed; resolutions unchanged). "),
    "rp01": ("rp01-125", "rp01-126", [1, 3, 126],
             "v1.3.126 (2026-10-07) round 231: seamless birch/oak bark, falling copies of the round-231 trees (spruce collar) + acacia_230, "
             "texture variant cut (21 variation keys trimmed, 15 keys repointed, 85 unused files removed; resolutions unchanged). "),
    "rp05": ("rp05-59", "rp05-60", [1, 3, 60],
             "v1.3.60 (2026-10-07) round 231: texture variant cut (7 variation keys trimmed, 1 key repointed, 141 unused files removed; "
             "resolutions unchanged). "),
    "rp10": ("rp10-151", "rp10-152", [1, 3, 52],
             "v1.3.52 (2026-10-07) round 231: texture variant cut (2 variation keys trimmed, 11 keys repointed, 20 unused files removed; "
             "resolutions unchanged). "),
    "rp12": ("rp12-101", "rp12-102", [1, 0, 2],
             "v1.0.2 (2026-10-07) round 231: paintings flush on all four walls (frame bones e/w). "),
    "rp12lite": ("rp12-101-lite", "rp12-102-lite", [1, 0, 2],
                 "v1.0.2 (2026-10-07) round 231: paintings flush on all four walls (frame bones e/w). "),
}
ORDER = ["bp02", "rp13", "rp04", "rp05", "rp10", "rp01", "rp12", "rp12lite"]
TIER_STAGE = S / "textures231"   # texture tier output (D-C1007-R231): applied to rp01/rp04/rp05/rp10/rp13

# staged-file md5s from the READMEs (full md5 where the README gives it; prefix otherwise)
MD5 = {
    "blocks231/BP-02/scripts/pw_civ_buildings.js": "f54228be7651e171eea04ccb00643839",
    "blocks231/BP-02/scripts/pw_companion.js": "d0c9a4b7f37b92f212b81f32ca8b840a",
    "blocks231/RP-12/models/entity/pw_frames.geo.json": "abb3fe3d",
    "blocks231/RP-12-LITE/models/entity/pw_frames.geo.json": "b7ece78b",
    "blocks231/RP-04/textures/terrain_texture.json": "24b04dc4",
    "ramps231/bp02/structures/pw/road/t_ramp8.mcstructure": "e9772f1987422afc60e51dec6a13ba94",
    "ramps231/bp02/structures/pw/road/v_ramp8.mcstructure": "afc222f7f6cc43800877c8d17feeb2ab",
    "ramps231/rp13/models/blocks/pw_ramps8.geo.json": "f22b310b27407df74a975fe1c71875bf",
    "ramps231/rp13/models/blocks/pw_snowcaps_ramps8.geo.json": "dd558d6db414f6a9e873a665f97c5528",
    "ramps231/rp04/models/blocks/pw_ramps.geo.json": "113e36ccdfee8247dfcd975a4f2620b7",
    "ramps231/rp04/models/blocks/pw_snowcaps.geo.json": "fa1f0015c1e0c7c78d8ec1dc55a42983",
    "skyway230/bp/blocks/pw_skyway_rail_spruce.json": "44b357c4",
    "skyway230/bp/blocks/pw_skyway_rail_oak.json": "73816f31",
    "skyway230/bp/blocks/pw_skyway_rail_dark_oak.json": "12e80ee8",
    "skyway230/bp/blocks/pw_skyway_bracket_oak.json": "cca3dfcb",
    "skyway230/bp/blocks/pw_skyway_bracket_spruce.json": "6b501167",
    "skyway230/bp/blocks/pw_skyway_bracket_dark_oak.json": "dc06469e",
    "skyway230/bp/structures/pw/skyway_test.mcstructure": "c3e2e6d4",
    "skyway230/rp/models/blocks/pw_skyway.geo.json": "116d31d2",
    "skyway230/rp/terrain_texture_add.json": "363f27e3",
}
BUILDINGS_SRC_MD5 = "0fb42f1930ff0e4f9bab5428fa82ad0f"     # tools/bp02_src_228/pw_civ_buildings.js == bp02-230's (no inn v2)
BLOCK_FIXES = ["blocks/pw_jib_panel.json", "blocks/pw_secret_painting.json", "blocks/roots/acacia_root.json",
               "blocks/roots/cherry_root.json", "blocks/roots/mangrove_root.json"]
BED_COLOURS = ["black", "blue", "brown", "cyan", "gray", "green", "light_blue", "lime", "magenta", "orange", "pink", "purple",
               "red", "silver", "white", "yellow"]
NEW_KEY_RP04 = "pw_acacia_log_top_single"

REPORT = {}


# ---------------------------------------------------------------- helpers
def md5(p):
    return hashlib.md5(Path(p).read_bytes()).hexdigest()


def check_md5(rel):
    p = S / rel
    assert p.is_file(), f"missing staged file {p}"
    h = md5(p)
    assert h.startswith(MD5[rel]), f"{rel}: md5 {h} != README {MD5[rel]}"
    return p


def md5sums(listing, root):
    """Parse an `md5sum` listing; return {relative path (no ./): md5} and assert every file matches."""
    out = {}
    for line in Path(listing).read_text().splitlines():
        if not line.strip():
            continue
        h, rel = line.split(None, 1)
        rel = rel.strip().lstrip("*")
        rel = rel[2:] if rel.startswith("./") else rel
        got = md5(Path(root) / rel)
        assert got == h, f"{listing}: {rel} md5 {got} != {h}"
        out[rel] = h
    return out


def du_bytes(p):
    return int(subprocess.run(["du", "-sb", str(p)], capture_output=True, text=True, check=True).stdout.split()[0])


def free_bytes():
    return shutil.disk_usage(HOME).free


def safe_copytree(src, dst):
    need = du_bytes(src)
    free = free_bytes()
    if free - need < MIN_FREE:
        raise SystemExit(f"DISK STOP: {free / 1e6:.0f} MB free, {src.name} needs {need / 1e6:.0f} MB -> would leave "
                         f"{(free - need) / 1e6:.0f} MB (< 400 MB). Nothing copied for {dst.name}.")
    shutil.copytree(src, dst, symlinks=False)


def put(src, dst, mode, changed):
    """mode 'replace' = dst must exist; 'add' = dst must not exist."""
    dst = Path(dst)
    if mode == "replace":
        assert dst.is_file(), f"replace target missing: {dst}"
        if md5(dst) == md5(src):
            changed.append(f"= {dst.name} (already identical)")
            return
    else:
        assert not dst.exists(), f"add target exists: {dst}"
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dst)
    assert md5(dst) == md5(src)
    changed.append(f"{'R' if mode == 'replace' else 'A'} {dst}")


def load_json(p):
    return json.loads(Path(p).read_text(encoding="utf-8-sig"))


def bump_manifest(root, version, stamp):
    mp = root / "manifest.json"
    m = load_json(mp)
    old = ".".join(map(str, m["header"]["version"]))
    new = ".".join(map(str, version))
    assert m["header"]["version"] < version, f"{root.name}: {old} !< {new}"
    m["header"]["version"] = version
    assert m["header"]["name"].count(old) == 1, f"{root.name}: name lacks v{old}: {m['header']['name']}"
    m["header"]["name"] = m["header"]["name"].replace(old, new)
    for mod in m["modules"]:
        mod["version"] = version
    m["header"]["description"] = (stamp + "Includes " + m["header"]["description"])[:1300]
    mp.write_text(json.dumps(m, indent=1))
    return f"manifest {old} -> {new}"


def tier_hook(key, dst, tier_dir, changed):
    """Texture-tier output (TEXTURES worker, not finished at 04:35 CT): DIR/<key>/<pack path> files replace/add."""
    if not tier_dir:
        return
    src_root = Path(tier_dir) / key
    if not src_root.is_dir():
        return
    for p in sorted(src_root.rglob("*")):
        if p.is_file():
            t = dst / p.relative_to(src_root)
            put(p, t, "replace" if t.exists() else "add", changed)


def apply_tier(key, dst, ch):
    """Texture tier overlay (README _staging/textures231, steps 3-4), merged by KEY rather than by file replace:
    re-run texture_tier_231's own transform on this pack's CURRENT terrain_texture.json (which may carry keys other workers
    added), assert every staged key comes out identical, then delete the _DELETE.txt files and prune textures_list.json
    entries whose files are gone. Returns the set of pack-relative paths deleted."""
    sys.path.insert(0, str(T))
    import texture_tier_231 as TT
    assert all(v is None for v in TT.TIER.values()), "tier resize requested — not built"
    _, _, drop, repoint = TT.load_inputs()
    tp = dst / "textures/terrain_texture.json"
    tt = load_json(tp)
    new_td = {}
    for k, entry in tt["texture_data"].items():
        if key == "rp13" and k.startswith(TT.FILL_PREFIX):
            continue
        tex = entry.get("textures")
        nt, _, _ = TT.rewrite_textures(tex, drop, repoint.get(k))
        new_td[k] = {**entry, "textures": nt} if nt is not tex else entry
    tt["texture_data"] = new_td
    staged = load_json(TIER_STAGE / key / "textures/terrain_texture.json")["texture_data"]
    missing = sorted(set(staged) - set(new_td))
    diff = sorted(k for k in staged if k in new_td and new_td[k] != staged[k])
    extra = sorted(set(new_td) - set(staged))
    assert not missing and not diff, f"{key}: tier merge disagrees with staged file: missing {missing[:5]} diff {diff[:5]}"
    allowed = {"rp04": [NEW_KEY_RP04], "rp13": sorted(load_json(S / "skyway230/rp/terrain_texture_add.json"))}.get(key, [])
    assert extra == allowed, f"{key}: unexpected extra keys {extra[:10]}"
    tp.write_text(json.dumps(tt, indent=2, ensure_ascii=False) + "\n")
    same = md5(tp) == md5(TIER_STAGE / key / "textures/terrain_texture.json")
    ch.append(f"E terrain_texture tier merge: {len(new_td)} keys, staged keys identical, extra keys {extra}, "
              f"file {'byte-identical to staged' if same else 'differs from staged only by the extra keys'}")
    deleted, already = set(), 0
    for rel in (TIER_STAGE / key / "_DELETE.txt").read_text().split():
        f = dst / rel
        if f.is_file():
            f.unlink()
            deleted.add(rel)
        else:
            already += 1
    ch.append(f"D tier: {len(deleted)} files deleted ({already} already gone)")
    tl = dst / "textures/textures_list.json"
    if tl.exists():
        lst = load_json(tl)
        gone = {r[:-len(".texture_set.json")] if r.endswith(".texture_set.json") else r.rsplit(".", 1)[0] for r in deleted}
        keep = [e for e in lst if not (isinstance(e, str) and e in gone
                                       and not any((dst / (e + x)).is_file() for x in TT.IMG_EXT))]
        if len(keep) != len(lst):
            tl.write_text(json.dumps(keep, indent=2) + "\n")
            ch.append(f"E textures_list.json: {len(lst) - len(keep)} entries of deleted files pruned ({len(lst)} -> {len(keep)})")
    REPORT[f"tier_{key}"] = {"keys": len(new_td), "extra": extra, "byte_identical": same, "deleted": len(deleted),
                             "already_gone": already}
    return deleted


def ramp_var_in_structure(path):
    sys.path.insert(0, str(T))
    import mcstructure as M
    st = M.Structure.from_bytes(Path(path).read_bytes())
    return sum(1 for name, states, _ in st.palette if "ramp" in name and "pw:var" in states)


def run_suites():
    lines = []
    for test in sorted((JS / "tests").glob("*.mjs")):
        r = subprocess.run(["node", str(test)], capture_output=True, text=True, cwd=JS)
        tail = (r.stdout.strip().splitlines() or ["(no output)"])[-1]
        lines.append(f"{'PASS' if r.returncode == 0 else 'FAIL'} {test.name}: {tail[:160]}")
        assert r.returncode == 0, f"suite {test.name} failed: {r.stdout[-800:]} {r.stderr[-400:]}"
    return lines


# ---------------------------------------------------------------- input validation (no writes)
def validate():
    for rel in MD5:
        check_md5(rel)
    assert md5(JS / "pw_civ_buildings.js") == BUILDINGS_SRC_MD5, \
        "tools/bp02_src_228/pw_civ_buildings.js changed since bp02-230: merge blocks231/civ_inn/CIV_BUILDINGS-inn.json by hand first"
    assert md5(JS / "pw_companion.js") == MD5["blocks231/BP-02/scripts/pw_companion.js"], "src companion != BLOCKS staged companion"
    assert "companion v7 LOADED (pack v1.3.2" not in (JS / "pw_companion.js").read_text(), "old hard-coded banner still present"
    trees = md5sums(S / "trees231/MD5SUMS-structures.txt", S / "trees231/structures")
    assert len(trees) == 216, len(trees)
    bark = md5sums(S / "trees231/MD5SUMS-RP-01-bark.txt", S / "trees231/RP-01")
    assert len(bark) == 54, len(bark)
    acacia = md5sums(S / "acacia_230/MD5SUMS", S / "acacia_230")
    assert len(acacia) == 32 and all(Path(k).name.startswith("acacia_") for k in acacia), len(acacia)
    assert not {Path(k).name for k in trees} & {Path(k).name for k in acacia}, "trees231 and acacia_230 overlap"
    ramps = sorted((S / "textures231/ramp-blocks").glob("pw_ramp_*.json"))
    assert len(ramps) == 266, len(ramps)
    for p in ramps:
        t = p.read_text()
        assert "pw_fill" not in t and "pw:var" not in t, f"{p.name}: pw_fill / pw:var present"
    inn = sorted((S / "blocks231/BP-02/structures/pw").glob("mvv_inn_*_r1.mcstructure"))
    stages = sorted((S / "blocks231/BP-02/structures/pw/stages").glob("mvv_inn_*.mcstructure"))
    assert len(inn) == 4 and len(stages) == 28, (len(inn), len(stages))
    for c in BED_COLOURS:
        for suf in ("", "_n", "_mers"):
            assert (S / f"blocks231/RP-04/textures/entity/bed/{c}{suf}.png").is_file(), f"bed {c}{suf}"
    for rel in BLOCK_FIXES:
        assert (S / "blocks231/BP-02" / rel).is_file(), rel
    sky_tex = sorted((S / "skyway230/rp/textures/blocks/pw_skyway").iterdir())
    assert len(sky_tex) == 28, len(sky_tex)
    for p in [S / "ramps231/bp02/structures/pw/road/t_ramp8.mcstructure", S / "ramps231/bp02/structures/pw/road/v_ramp8.mcstructure",
              S / "skyway230/bp/structures/pw/skyway_test.mcstructure"] + inn + stages + [S / "trees231/structures" / k for k in trees] \
            + [S / "acacia_230" / k for k in acacia]:
        assert ramp_var_in_structure(p) == 0, f"{p.name}: ramp palette carries pw:var (slim law)"
    return {"trees": trees, "bark": bark, "acacia": acacia, "ramps": ramps, "inn": inn, "stages": stages, "sky_tex": sky_tex}


# ---------------------------------------------------------------- packs
def build_bp02(dst, inp, tier_dir):
    ch = []
    REPORT["suites_before"] = run_suites()
    base = B / PACKS["bp02"][0]
    # scripts: every src .js that differs from the base
    for p in sorted(JS.glob("*.js")):
        ref = dst / "scripts" / p.name
        assert ref.exists(), f"new script {p.name}: not expected in round 231 — add it deliberately"
        if md5(ref) != md5(p):
            put(p, ref, "replace", ch)
    put(S / "blocks231/BP-02/scripts/pw_civ_buildings.js", dst / "scripts/pw_civ_buildings.js", "replace", ch)
    mj = dst / "scripts/main.js"
    s = mj.read_text()
    assert "globalThis.__PW_BUILD" not in s
    hits = re.findall(r'const PW_BUILD = "[0-9.]+";', s)
    assert len(hits) == 1, f"PW_BUILD lines: {hits}"
    mj.write_text(s.replace(hits[0], 'const PW_BUILD = "1.3.231";\nglobalThis.__PW_BUILD = PW_BUILD;'))
    ch.append("E scripts/main.js PW_BUILD 1.3.231 + globalThis.__PW_BUILD")
    # blocks231: block fixes, inn v2
    for rel in BLOCK_FIXES:
        put(S / "blocks231/BP-02" / rel, dst / rel, "replace", ch)
    for p in inp["inn"]:
        put(p, dst / "structures/pw" / p.name, "replace", ch)
    for p in inp["stages"]:
        put(p, dst / "structures/pw/stages" / p.name, "replace", ch)
    # ramps231 structures + textures231 ramp blocks
    for n in ("t_ramp8", "v_ramp8"):
        put(S / f"ramps231/bp02/structures/pw/road/{n}.mcstructure", dst / f"structures/pw/road/{n}.mcstructure", "replace", ch)
    for p in inp["ramps"]:
        put(p, dst / "blocks" / p.name, "replace", ch)
    # trees231 + acacia_230
    for rel in inp["trees"]:
        put(S / "trees231/structures" / rel, dst / "structures" / rel, "replace", ch)
    for rel in inp["acacia"]:
        put(S / "acacia_230" / rel, dst / "structures/pw/trees" / Path(rel).name, "replace", ch)
    names = re.search(r"FT_TPL_NAMES = (\[.*?\]);", (dst / "scripts/pw_ft_tpl_index.js").read_text(), re.S).group(1)
    assert sorted(json.loads(names)) == sorted(p.stem for p in (dst / "structures/pw/trees").glob("*.mcstructure")), "FT_TPL_NAMES drift"
    # skyway option C
    for p in sorted((S / "skyway230/bp/blocks").glob("*.json")):
        put(p, dst / "blocks" / p.name, "add", ch)
    put(S / "skyway230/bp/structures/pw/skyway_test.mcstructure", dst / "structures/pw/skyway_test.mcstructure", "add", ch)
    tier_hook("bp02", dst, tier_dir, ch)
    # slim law: no ramp block state / structure palette carries pw:var
    for f in sorted((dst / "blocks").rglob("pw_ramp_*.json")):
        assert "pw:var" not in f.read_text(), f"slim law broken: {f.name}"
    bad = [f.name for f in sorted((dst / "structures").rglob("*.mcstructure")) if ramp_var_in_structure(f)]
    assert not bad, f"slim law broken in structures: {bad[:5]}"
    # pw_fill law (slice 2 fix): the RAMP fills (RP-13's 248 retired keys) must be gone; the ROOF fills (pw_fill_45_* etc.,
    # RP-04 keys, untouched by round 231) stay and must resolve in RP-04.
    used = set()
    for f in (dst / "blocks").rglob("*.json"):
        used |= set(re.findall(r'"(pw_fill[A-Za-z0-9_]*)"', f.read_text()))
    rp13_fills = {k for k in load_json(B / "rp13-101/textures/terrain_texture.json")["texture_data"] if k.startswith("pw_fill")}
    rp04_keys = set(load_json(B / PACKS["rp04"][1] / "textures/terrain_texture.json")["texture_data"])
    assert not used & rp13_fills, f"BP-02 still names retired ramp fills: {sorted(used & rp13_fills)[:5]}"
    assert used <= rp04_keys, f"BP-02 pw_fill keys missing from RP-04 1.3.160: {sorted(used - rp04_keys)[:5]}"
    ch.append(f"N pw_fill: 0 retired ramp-fill keys referenced; {len(used)} roof-fill keys all in RP-04 1.3.160")
    ch.append(bump_manifest(dst, PACKS["bp02"][2], PACKS["bp02"][3]))
    for p in sorted((dst / "scripts").rglob("*.js")):
        r = subprocess.run(["node", "--check", str(p)], capture_output=True, text=True)
        assert r.returncode == 0, f"node --check {p.name}: {r.stderr[:300]}"
    r = subprocess.run([sys.executable, str(T / "js_dupcheck.py")] + [str(p) for p in sorted((dst / "scripts").glob("*.js"))],
                       capture_output=True, text=True)
    assert r.returncode == 0, f"js_dupcheck: {r.stdout[:600]}"
    assert base.exists()
    return ch


def build_rp13(dst, inp, tier_dir, keep_fills):
    ch = []
    for n in ("pw_ramps8", "pw_snowcaps_ramps8"):
        put(S / f"ramps231/rp13/models/blocks/{n}.geo.json", dst / f"models/blocks/{n}.geo.json", "replace", ch)
    put(S / "skyway230/rp/models/blocks/pw_skyway.geo.json", dst / "models/blocks/pw_skyway.geo.json", "add", ch)
    for p in inp["sky_tex"]:
        put(p, dst / "textures/blocks/pw_skyway" / p.name, "add", ch)
    tp = dst / "textures/terrain_texture.json"
    tt = load_json(tp)
    add = load_json(S / "skyway230/rp/terrain_texture_add.json")
    assert len(add) == 7 and not set(add) & set(tt["texture_data"]), "skyway keys clash"
    tt["texture_data"].update(add)
    ch.append(f"E terrain_texture +{len(add)} skyway keys")
    if not keep_fills:   # D-C1007-R231c: the 248 fill textures are retired
        keys = sorted(k for k in tt["texture_data"] if k.startswith("pw_fill"))
        assert len(keys) == 248, f"expected 248 pw_fill keys, found {len(keys)}"
        for k in keys:
            del tt["texture_data"][k]
        files = sorted(p for p in (dst / "textures").rglob("*") if p.is_file() and p.name.startswith("pw_fill"))
        for p in files:
            p.unlink()
        ch.append(f"D {len(keys)} pw_fill keys, {len(files)} pw_fill files")
        REPORT["rp13_fill_removed"] = {"keys": len(keys), "files": len(files)}
    tp.write_text(json.dumps(tt, indent=1))
    texts = dst / "texts"
    if texts.exists():
        lang = texts / "en_US.lang"
        have = lang.read_text(encoding="utf-8-sig") if lang.exists() else ""
        new = [ln for ln in (S / "skyway230/rp/texts/en_US.lang").read_text().splitlines() if ln and ln not in have]
        lang.write_text(have.rstrip("\n") + ("\n" if have else "") + "\n".join(new) + "\n")
        ch.append(f"E texts/en_US.lang +{len(new)} lines")
    else:
        for n in ("en_US.lang", "languages.json"):
            put(S / "skyway230/rp/texts" / n, texts / n, "add", ch)
    tier_hook("rp13", dst, tier_dir, ch)
    apply_tier("rp13", dst, ch)
    if not keep_fills:
        left = [str(p.relative_to(dst)) for p in dst.rglob("*.json") if "pw_fill" in p.read_text(encoding="utf-8", errors="ignore")]
        assert not left, f"RP-13 still names pw_fill: {left[:5]}"
    ch.append(bump_manifest(dst, PACKS["rp13"][2], PACKS["rp13"][3]))
    return ch


def build_rp04(dst, inp, tier_dir):
    ch = []
    for n in ("pw_ramps", "pw_snowcaps"):
        put(S / f"ramps231/rp04/models/blocks/{n}.geo.json", dst / f"models/blocks/{n}.geo.json", "replace", ch)
    for c in BED_COLOURS:
        for suf in ("", "_n", "_mers"):
            put(S / f"blocks231/RP-04/textures/entity/bed/{c}{suf}.png", dst / f"textures/entity/bed/{c}{suf}.png", "replace", ch)
    old = load_json(dst / "textures/terrain_texture.json")
    new = load_json(S / "blocks231/RP-04/textures/terrain_texture.json")
    od, nd = old["texture_data"], new["texture_data"]
    assert set(nd) - set(od) == {NEW_KEY_RP04} and not set(od) - set(nd), "RP-04 terrain_texture: more than the one new key"
    assert all(od[k] == nd[k] for k in od), "RP-04 terrain_texture: an existing key changed"
    assert {k: v for k, v in old.items() if k != "texture_data"} == {k: v for k, v in new.items() if k != "texture_data"}
    put(S / "blocks231/RP-04/textures/terrain_texture.json", dst / "textures/terrain_texture.json", "replace", ch)
    tier_hook("rp04", dst, tier_dir, ch)
    apply_tier("rp04", dst, ch)
    ch.append(bump_manifest(dst, PACKS["rp04"][2], PACKS["rp04"][3]))
    return ch


def tree_digests(root):
    return {str(p.relative_to(root)): md5(p) for p in sorted(root.rglob("*")) if p.is_file()}


def build_rp01(dst, inp, tier_dir, before, tier_deleted, tier_ch):
    ch = list(tier_ch)
    bp = B / PACKS["bp02"][1]
    assert (bp / "manifest.json").exists(), "RP-01 needs bp02-231 built first (its trees feed the falling copies)"
    skipped = sorted(rel for rel in inp["bark"] if rel in tier_deleted)
    for rel in inp["bark"]:
        if rel not in tier_deleted:
            put(S / "trees231/RP-01" / rel, dst / rel, "replace", ch)
    ch.append(f"N bark: {len(skipped)} seamless files not installed (variant dropped by the tier cut): {skipped}")
    tier_hook("rp01", dst, tier_dir, ch)
    doc_before = FT_INDEX_DOC.read_bytes() if FT_INDEX_DOC.exists() else None
    r = subprocess.run([sys.executable, str(T / "ft_tpl_gen_lite.py"), str(dst), str(bp)] + FT_ARGS, capture_output=True, text=True)
    assert r.returncode == 0, r.stderr[-1500:]
    REPORT["ft_tpl_gen_lite"] = r.stdout.strip().splitlines()[-1:]
    if doc_before is not None:
        FT_INDEX_DOC.with_name("ft_tpl_index.pre126.json").write_bytes(doc_before)
    after = tree_digests(dst)
    assert set(before) == set(after), f"RP-01 file set changed: {sorted(set(before) ^ set(after))[:10]}"
    changed = sorted(k for k in after if after[k] != before[k])
    want_geo = {f"models/entity/ft_tpl/{Path(k).stem}.geo.json" for k in list(inp["trees"]) + list(inp["acacia"])}
    bark = set(inp["bark"]) - set(tier_deleted)
    atl = {k for k in changed if k.startswith("textures/entity/fallingtree/leafatlas_")}
    other = [k for k in changed if k not in want_geo and k not in bark and k not in atl]
    assert not other, f"RP-01 unexpected changes: {other[:10]}"
    REPORT["rp01_changes"] = {"ft_tpl_changed": len([k for k in changed if k in want_geo]), "ft_tpl_expected_max": len(want_geo),
                              "ft_tpl_unchanged_of_248": sorted(k for k in want_geo if k not in changed),
                              "bark": len([k for k in changed if k in bark]), "leafatlas": sorted(atl)}
    ch.append(f"E ft_tpl regenerated: {REPORT['rp01_changes']['ft_tpl_changed']} of {len(want_geo)} copies changed; "
              f"{len(atl)} leaf atlases changed")
    ch.append(bump_manifest(dst, PACKS["rp01"][2], PACKS["rp01"][3]))
    return ch


def build_tier_only(dst, key):
    ch = []
    apply_tier(key, dst, ch)
    ch.append(bump_manifest(dst, PACKS[key][2], PACKS[key][3]))
    return ch


def build_rp12(dst, key, tier_dir):
    ch = []
    sub = "RP-12" if key == "rp12" else "RP-12-LITE"
    put(S / f"blocks231/{sub}/models/entity/pw_frames.geo.json", dst / "models/entity/pw_frames.geo.json", "replace", ch)
    tier_hook(key, dst, tier_dir, ch)
    ch.append(bump_manifest(dst, PACKS[key][2], PACKS[key][3]))
    return ch


# ---------------------------------------------------------------- post-build checks
def terrain_resolve(packs):
    """Every terrain key path in each pack's terrain_texture.json resolves to an image somewhere in the stack, then vanilla.
    packs: list of pack dirs (top of stack first). Returns {pack: sorted missing (key, path)}."""
    van = HOME / "_intake/bedrock-samples/resource_pack"
    ext = (".png", ".tga", ".jpg", ".jpeg")
    roots = [p for p in packs if p.is_dir()] + [van]

    def paths(t):
        if isinstance(t, str):
            return [t]
        if isinstance(t, dict):
            return paths(t["variations"]) if "variations" in t else [t.get("path")]
        if isinstance(t, list):
            return [x for e in t for x in paths(e)]
        return []
    out = {}
    for p in packs:
        f = p / "textures/terrain_texture.json"
        if not f.exists():
            continue
        td = load_json(f)["texture_data"]
        out[p.name] = sorted({(k, x) for k, v in td.items() for x in paths(v.get("textures"))
                              if not any((r / (x + e)).is_file() for r in roots for e in ext)})
    return out


def post():
    res = {}
    new = {k: B / PACKS[k][1] for k in ("bp02", "rp13", "rp04", "rp05", "rp10", "rp01", "rp12")}
    bp = new["bp02"]
    args = [sys.executable, str(T / "geo_ref_check.py"), "--bp", str(bp)]
    args += ["--bp", str(B / "markers-0.2.4-bp")]
    for k in ("rp04", "rp13", "rp01", "rp12", "rp05", "rp10"):
        if new[k].exists():
            args += ["--rp", str(new[k])]
    for n in ("rp07-1445", "rp11-140", "rp08-1414", "rp06-1429", "rp03-67", "rp02-207", "markers-0.2.3-rp"):   # rest of the stack
        args += ["--rp", str(B / n)]                                                                          # (sf_nba geos: RP-07)
    r = subprocess.run(args, capture_output=True, text=True)
    res["geo_ref_check"] = {"exit": r.returncode, "tail": r.stdout.strip().splitlines()[-4:]}
    # terrain keys across the full new stack (top first, as the verify script orders it) vs the same check on the bases
    others = [B / n for n in ("markers-0.2.3-rp", "rp11-140", "rp08-1414", "rp07-1445", "rp06-1429", "rp03-67", "rp02-207")]
    stack_new = [others[0], new["rp13"], new["rp12"], others[1], new["rp10"], others[2], others[3], others[4], new["rp05"],
                 new["rp04"], others[5], others[6], new["rp01"]]
    stack_old = [others[0], B / "rp13-101", B / "rp12-101", others[1], B / "rp10-151", others[2], others[3], others[4],
                 B / "rp05-59", B / "rp04-159", others[5], others[6], B / "rp01-125"]
    mn, mo = terrain_resolve(stack_new), terrain_resolve(stack_old)
    tr = {}
    for k in ("rp01", "rp04", "rp05", "rp10", "rp12", "rp13"):
        n, o = new[k].name, B / PACKS[k][0]
        if n not in mn:
            tr[n] = "no terrain_texture.json"
            continue
        newly = sorted(set(map(tuple, mn[n])) - set(map(tuple, mo.get(o.name, []))))
        tr[n] = {"keys": len(load_json(new[k] / "textures/terrain_texture.json")["texture_data"]), "missing": len(mn[n]),
                 "missing_in_base": len(mo.get(o.name, [])), "NEW_missing": len(newly), "new_sample": newly[:8]}
    res["terrain_resolve"] = tr
    sys.path.insert(0, str(T))
    import block_state_census as BC
    BC.PACKS = {"BP-02 1.3.231": bp, "Markers 0.2.4-bp": B / "markers-0.2.4-bp"}
    rows = BC.census()
    errs = [r for r in rows if "error" in r]
    by = {}
    for r in rows:
        if "perms" in r:
            by[r["pack"]] = by.get(r["pack"], 0) + r["perms"]
    BC.PACKS = {"BP-02 1.3.230": B / "bp02-230"}
    by_old = sum(r.get("perms", 0) for r in BC.census())
    res["permutations"] = {"by_pack": by, "total": sum(by.values()), "bp02_230": by_old, "cap": 65536, "parse_errors": errs[:5]}
    bad = []
    for p in sorted((bp / "scripts").rglob("*.js")):
        r = subprocess.run(["node", "--check", str(p)], capture_output=True, text=True)
        if r.returncode:
            bad.append(p.name)
    res["node_check"] = {"files": len(list((bp / "scripts").rglob("*.js"))), "failed": bad}
    r = subprocess.run([sys.executable, str(T / "js_dupcheck.py")] + [str(p) for p in sorted((bp / "scripts").glob("*.js"))],
                       capture_output=True, text=True)
    res["js_dupcheck"] = {"exit": r.returncode, "tail": r.stdout.strip().splitlines()[-2:]}
    try:
        res["suites"] = run_suites()
    except AssertionError as e:
        res["suites"] = [f"FAIL {e}"]
    rp13_fills = {k for k in load_json(B / "rp13-101/textures/terrain_texture.json")["texture_data"] if k.startswith("pw_fill")}
    res["retired_ramp_fill_refs"] = {d.name: sum(1 for f in d.rglob("*.json")
                                                 if set(re.findall(r'"(pw_fill[A-Za-z0-9_]*)"', f.read_text(encoding="utf-8", errors="ignore"))) & rp13_fills)
                                     for d in (bp, new["rp13"])}
    # manifests: version as planned, name carries it, uuid = base uuid, descriptions unique among new + bases
    man, descs = {}, []
    for k, d in new.items():
        if not d.exists():
            continue
        m, mb = load_json(d / "manifest.json"), load_json(B / PACKS[k][0] / "manifest.json")
        v = m["header"]["version"]
        ok = (v == PACKS[k][2] and ".".join(map(str, v)) in m["header"]["name"] and m["header"]["uuid"] == mb["header"]["uuid"]
              and all(x["version"] == v for x in m["modules"]) and m["header"]["description"] != mb["header"]["description"])
        man[d.name] = {"version": v, "name": m["header"]["name"], "ok": ok, "size_mb": round(du_bytes(d) / 1048576, 1)}
        descs += [m["header"]["description"], mb["header"]["description"]]
    res["manifests"] = man
    res["descriptions_unique"] = len(descs) == len(set(descs))
    res["rp_size_le_250MB"] = all(v["size_mb"] <= 250 for n, v in man.items() if n.startswith("rp"))
    key_files = ["scripts/main.js", "scripts/pw_civ_clock.js", "scripts/pw_civ_streets.js", "scripts/pw_civ_buildings.js",
                 "scripts/pw_companion.js", "manifest.json"]
    res["md5"] = {f"bp02-231/{k}": md5(bp / k) for k in key_files if (bp / k).exists()}
    for k, ks in (("rp13", ["textures/terrain_texture.json", "models/blocks/pw_ramps8.geo.json", "models/blocks/pw_skyway.geo.json"]),
                  ("rp04", ["textures/terrain_texture.json", "models/blocks/pw_ramps.geo.json", "textures/textures_list.json"]),
                  ("rp05", ["textures/terrain_texture.json", "textures/textures_list.json"]), ("rp10", ["textures/terrain_texture.json"]),
                  ("rp01", ["textures/terrain_texture.json"]), ("rp12", ["models/entity/pw_frames.geo.json"])):
        d = new[k]
        if d.exists():
            res["md5"].update({f"{d.name}/{f}": md5(d / f) for f in ks + ["manifest.json"] if (d / f).exists()})
    print(json.dumps(res, indent=1))
    (LOG.with_name("build_round_231_post.json")).write_text(json.dumps(res, indent=1))


# ---------------------------------------------------------------- main
def main():
    argv = sys.argv[1:]
    if "--post" in argv:
        return post()
    inp = validate()
    if "--check" in argv:
        print(f"CHECK OK: trees {len(inp['trees'])}, acacia {len(inp['acacia'])}, bark {len(inp['bark'])}, ramp blocks "
              f"{len(inp['ramps'])}, inn {len(inp['inn'])}+{len(inp['stages'])}, skyway tex {len(inp['sky_tex'])}; "
              f"free {free_bytes() / 1e6:.0f} MB; nothing written")
        return
    keys = argv[argv.index("--packs") + 1].split(",") if "--packs" in argv else [k for k in ORDER if k != "rp12lite"]
    if "--lite" in argv and "rp12lite" not in keys:
        keys.append("rp12lite")
    tier_dir = argv[argv.index("--tier-dir") + 1] if "--tier-dir" in argv else None
    keep_fills = "--keep-fills" in argv
    log = json.loads(LOG.read_text()) if LOG.exists() else {}
    for key in [k for k in ORDER if k in keys]:
        base, new, version, _ = PACKS[key]
        src, dst = B / base, B / new
        if dst.exists():
            print(f"SKIP {new}: exists (versions are never reused)")
            continue
        if key == "rp01" and not (B / PACKS["bp02"][1]).exists():
            raise SystemExit("rp01 needs bp02-231 first")
        safe_copytree(src, dst)
        try:
            tier_deleted, tier_ch = set(), []
            if key == "rp01":      # tier first: the falling-copy regen + its change audit run on the cut pack
                tier_deleted = apply_tier("rp01", dst, tier_ch)
            before = tree_digests(dst) if key == "rp01" else None
            if key == "bp02":
                ch = build_bp02(dst, inp, tier_dir)
            elif key == "rp13":
                ch = build_rp13(dst, inp, tier_dir, keep_fills)
            elif key == "rp04":
                ch = build_rp04(dst, inp, tier_dir)
            elif key == "rp01":
                ch = build_rp01(dst, inp, tier_dir, before, tier_deleted, tier_ch)
            elif key in ("rp05", "rp10"):
                ch = build_tier_only(dst, key)
            else:
                ch = build_rp12(dst, key, tier_dir)
        except BaseException:
            bad = dst.with_name(dst.name + ".FAILED")
            dst.rename(bad)        # never leave a half-built dir under the real name
            print(f"FAILED {new}: half-built dir kept as {bad.name} for inspection (delete it to retry)")
            raise
        n_r = sum(1 for c in ch if c.startswith("R "))
        n_a = sum(1 for c in ch if c.startswith("A "))
        log[new] = {"version": version, "replaced": n_r, "added": n_a, "notes": [c for c in ch if not c[:2] in ("R ", "A ")],
                    "report": {k: v for k, v in REPORT.items()}, "free_after_mb": round(free_bytes() / 1e6)}
        LOG.write_text(json.dumps(log, indent=1))
        print(f"DONE {new} {version}: replaced {n_r}, added {n_a}; " + "; ".join(log[new]["notes"]))
        REPORT.clear()


if __name__ == "__main__":
    main()
