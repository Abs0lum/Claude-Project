#!/usr/bin/env python3
"""roof_fix_174.py — task #174, his 19:02 ruling: "I want them to work and appear correctly oriented and positioned"
(fix all six: gusset lower/upper, hip, pyramidion, ridge end, crown ring, roof63). Every change is backed by the numbers
in D-C487 (measured transformation law) and D-C489 (audit + true-law top surfaces). Undelivered builds, edited in place:
RP-04 1.3.156 (models + 4 textures) and BP-02 1.3.206 (blocks, companion script, test structures).

FRONT-STATE LAW used throughout (the witnessed roof45 convention): a piece's model is authored for state "north" at
rotation 0; states map n 0 / w 90 / s 180 / e -90 (world right-handed, D-C487); a slope's state = its DOWNHILL side;
a corner piece's state = the corner it sits at, n -> NW, w -> SW, s -> SE, e -> NE (s3 pyramid + HIP_FACE notes).

G1 hip       the 7 Z-boards carried rz +45: they rose to file -x while the stepped body rises to file +x (inverted, the
             pyramid's jagged look) -> rz -45. Then the whole model is mirrored in x so rotation 0 is the NW corner
             (it was NE, a quarter turn from every state's meaning). Hair-thin eave faces with v 16.2 on a 16 px texture
             -> v 15.9.
G2 pyramidion the 2 Z-boards had the same inverted sign (rose outward) -> sign flipped.
G3 gussets   the side-triangle faces flipped with uv [64,0] size [-16,16] on a 16 px texture (4 tiles out) -> [16,0].
             The 4 pw_fill_tri* textures: 1,272 soft-alpha texels each -> hard (cut at 128, what alpha_test draws).
G4 crown ring straight lip sat on the inner side; the corner's two legs sat on the inner (S) and outer (W) side, with a
             notch -> both forms carry the lip on the OUTER edge(s) (state = outward, the side the builder faces
             when standing outside; corners n->NW), flush and continuous with their neighbours.
B1 roof63_upper permutation map was the reverse of lower's (n 180 ...) -> the auto-placed upper sloped the wrong way;
             now the same map as lower (the model at rotation 0 already continues lower's plane: 2z+3 both).
S1 companion Rule A corner fold -> only at OUTER corners, new corner map; Rule B ridge end -> fires where a hipped end
             really is (along-axis neighbour air with a roof45 below it facing away), also when that roof45 comes
             second; Rule C pyramidion -> one level ABOVE the centre of the four hips; Rule G -> corner facings from
             neighbours, every facing re-set outward on closure; Rule E (room walls) keeps its old map under its own
             name (walls not in this task; logged for audit).
T1 structures s1 gusset fold, s2 hipped roof 7x5 (hips + ridge ends + ridge), s4 plain gable run, s3 / s6 unchanged
             states (already the law), and the roof kit rebuilt with a 63 gable."""
import json
import shutil
import sys
import time
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, "/home/claude/tools")
import mcstructure as M  # noqa: E402

B = Path("/home/claude/_build")
RP = B / "rp04-156"
BP = B / "bp02-206"
MODELS = RP / "models/blocks"
BACKUP = Path("/home/claude/_docs/blocks/before_roof_fix_174")
LOG = []


def backup(p):
    dst = BACKUP / p.relative_to(B)
    if not dst.exists():
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(p, dst)


def jload(p):
    return json.loads(p.read_text(encoding="utf-8-sig"))


def jsave(p, d):
    backup(p)
    p.write_text(json.dumps(d, indent=1))


def cubes(g):
    for b in g["bones"]:
        for c in b.get("cubes", []):
            yield b, c


def mirror_x(g):
    """file-x mirror of every cube: origin x -> -(x+sx), pivot x -> -px, rotation (rx, -ry, -rz), east<->west uv keys."""
    for b in g["bones"]:
        if "pivot" in b:
            b["pivot"][0] = -b["pivot"][0]
        if "rotation" in b:
            b["rotation"] = [b["rotation"][0], -b["rotation"][1], -b["rotation"][2]]
        for c in b.get("cubes", []):
            c["origin"][0] = round(-(c["origin"][0] + c["size"][0]), 4)
            if "pivot" in c:
                c["pivot"][0] = round(-c["pivot"][0], 4)
            if "rotation" in c:
                r = c["rotation"]
                c["rotation"] = [r[0], -r[1] if r[1] else 0, -r[2] if r[2] else 0]
            uv = c.get("uv")
            if isinstance(uv, dict):
                e, w = uv.pop("east", None), uv.pop("west", None)
                if e is not None:
                    uv["west"] = e
                if w is not None:
                    uv["east"] = w


def fix_hip():
    p = MODELS / "roof_hip.geo.json"
    d = jload(p)
    g = d["minecraft:geometry"][0]
    n_z = n_uv = 0
    for _b, c in cubes(g):
        if c.get("rotation") == [0, 0, 45]:
            c["rotation"] = [0, 0, -45]
            n_z += 1
        for spec in (c.get("uv") or {}).values():
            if isinstance(spec, dict) and spec["uv"][1] > 16 - abs(spec.get("uv_size", [0, 0])[1]):
                spec["uv"][1] = 15.9
                n_uv += 1
    assert n_z == 7, n_z
    mirror_x(g)
    jsave(p, d)
    LOG.append(f"G1 roof_hip: {n_z} Z-boards rz +45 -> -45; model mirrored in x (rotation 0 = NW corner); {n_uv} hair faces v -> 15.9")


def fix_pyramidion():
    p = MODELS / "roof_pyramidion.geo.json"
    d = jload(p)
    g = d["minecraft:geometry"][0]
    n = 0
    for _b, c in cubes(g):
        r = c.get("rotation")
        if r and r[2] and not r[0] and not r[1]:
            c["rotation"] = [0, 0, -r[2]]
            n += 1
    assert n == 2, n
    jsave(p, d)
    LOG.append(f"G2 roof_pyramidion: {n} Z-boards sign flipped (now rise toward the apex like the X-boards)")


def fix_gussets():
    n = 0
    for name in ("roof_gusset_lower", "roof_gusset_upper"):
        p = MODELS / f"{name}.geo.json"
        d = jload(p)
        g = d["minecraft:geometry"][0]
        tw = g["description"]["texture_width"]
        for _b, c in cubes(g):
            for spec in (c.get("uv") or {}).values():
                if isinstance(spec, dict) and spec["uv"][0] > tw:
                    spec["uv"][0] = tw
                    n += 1
        jsave(p, d)
    assert n == 2, n
    hard = []
    for f in sorted((RP / "textures/blocks").glob("pw_fill_tri*.png")):
        if f.stem.endswith(("_mer", "_mers", "_n", "_normal")):
            continue
        backup(f)
        a = np.asarray(Image.open(f).convert("RGBA")).copy()
        soft = int(((a[..., 3] > 0) & (a[..., 3] < 255)).sum())
        a[..., 3] = np.where(a[..., 3] >= 128, 255, 0).astype(np.uint8)
        Image.fromarray(a, "RGBA").save(f)
        hard.append(f"{f.name} {soft}->0")
    LOG.append(f"G3 gussets: {n} flipped side-triangle uvs 64 -> 16 (texture is 16 wide); alpha hardened: {hard}")


def lip(o, s):
    x, y, z = s
    return {"origin": o, "size": s, "uv": {
        "north": {"uv": [0, 0], "uv_size": [x, y]}, "south": {"uv": [0, 0], "uv_size": [x, y]},
        "east": {"uv": [0, 0], "uv_size": [z, y]}, "west": {"uv": [0, 0], "uv_size": [z, y]},
        "up": {"uv": [0, 0], "uv_size": [x, z]}, "down": {"uv": [0, 0], "uv_size": [x, z]}}}


def fix_crown():
    p = MODELS / "crown_ring.geo.json"
    d = jload(p)
    g = d["minecraft:geometry"][0]
    by = {b["name"]: b for b in g["bones"]}
    # outer lip: world north edge (file z -7.6..-5.4, 0.4 in from the edge, 1.6 tall on the 10 px body)
    by["trim_straight"]["cubes"] = [lip([-8, 10, -7.6], [16, 1.6, 2.2])]
    # NW corner: north leg across the cell (flush with the west leg's outer face), west leg (world west = file +x)
    by["trim_corner"]["cubes"] = [lip([-8, 10, -7.6], [15.6, 1.6, 2.2]),
                                  lip([5.4, 10, -5.4], [2.2, 1.6, 13.4])]
    jsave(p, d)
    LOG.append("G4 crown_ring: straight lip -> outer (north) edge; corner -> north + west legs meeting flush at NW (no notch)")


def fix_bp_blocks():
    n = 0
    for mat in ("oak", "spruce"):
        p = BP / f"blocks/roof63_upper_{mat}.json"
        d = jload(p)
        lower = jload(BP / f"blocks/roof63_lower_{mat}.json")["minecraft:block"]["permutations"]
        rot = {}
        for perm in lower:
            for s in ("north", "south", "east", "west"):
                if f"== '{s}'" in perm["condition"] and "minecraft:transformation" in perm["components"]:
                    rot[s] = perm["components"]["minecraft:transformation"]["rotation"]
        for perm in d["minecraft:block"]["permutations"]:
            for s, r in rot.items():
                if f"== '{s}'" in perm["condition"] and "minecraft:transformation" in perm["components"]:
                    perm["components"]["minecraft:transformation"]["rotation"] = list(r)
                    n += 1
        jsave(p, d)
    assert n == 8, n
    LOG.append(f"B1 roof63_upper (oak, spruce): {n} permutation rotations set equal to roof63_lower's map")


COMPANION_PATCHES = [
    # Rule A map (hips) and Rule E map (room walls) split
    ("""const HIP_FACE = { "north|west":"south", "west|north":"south", "north|east":"west", "east|north":"west",
                   "south|east":"north", "east|south":"north", "south|west":"east", "west|south":"east" };""",
     """const HIP_FACE = { "north|west":"north", "west|north":"north", "north|east":"east", "east|north":"east",
                   "south|east":"south", "east|south":"south", "south|west":"west", "west|south":"west" };
// #174 (D-C489): hip corner = the corner it sits at, n->NW w->SW s->SE e->NE, under the MEASURED transformation law
// (D-C487). Room-wall corners keep their own (old) map until the walls get their own audit.
const WALL_CORNER_FACE = { "north|west":"south", "west|north":"south", "north|east":"west", "east|north":"west",
                   "south|east":"north", "east|south":"north", "south|west":"east", "west|south":"east" };
const DV = { north:[0,-1], south:[0,1], east:[1,0], west:[-1,0] };"""),
    ("""    const cornerFacing = HIP_FACE[`${f}|${nf}`] || f;    // quadrant map shared with hips (witness item)""",
     """    const cornerFacing = WALL_CORNER_FACE[`${f}|${nf}`] || f;    // room-wall map (unchanged by #174)"""),
    # Rule A: outer corners only
    ("""  let runMate = null;
  for (const [dx,dz] of along) { const n = nb(b,dx,dz); if (n && R45.has(n.typeId) && faceOf(n) === f) { runMate = f; break; } }
  if (!runMate) return false;
  for (const [dx,dz] of across) {
    const n = nb(b,dx,dz); if (!n || !R45.has(n.typeId)) continue;
    const pf = faceOf(n); if (!pf || !PERP[f].includes(pf)) continue;
    const hf = HIP_FACE[`${f}|${pf}`]; if (!hf) continue;""",
     """  for (const pf of PERP[f]) {
    // OUTER corner only (#174): the f-run continues AWAY from the pf side, the pf-run continues away from the f side.
    const run = nb(b, -DV[pf][0], -DV[pf][1]);
    const per = nb(b, -DV[f][0], -DV[f][1]);
    if (!run || !R45.has(run.typeId) || faceOf(run) !== f) continue;
    if (!per || !R45.has(per.typeId) || faceOf(per) !== pf) continue;
    const hf = HIP_FACE[`${f}|${pf}`]; if (!hf) continue;"""),
    ("""    say(`RULE A — corner self-fold: 45 at run-meet became roof_hip_${m} facing ${hf} — §aFOLDED§r`);
    return true;""",
     """    say(`RULE A — corner self-fold: 45 at run-meet became roof_hip_${m} facing ${hf} — §aFOLDED§r`);
    try { tryPyramidion(b); } catch {}
    return true;"""),
    # Rule B: real hipped-end geometry
    ("""  const axis = (f === "north" || f === "south") ? [[1,0],[-1,0]] : [[0,1],[0,-1]];
  const DIRNAME = (dx,dz) => dx===1?"east":dx===-1?"west":dz===1?"south":"north";
  for (const [dx,dz] of axis) {
    const n = nb(b,dx,dz);
    if (n && HIP.has(n.typeId)) {
      const endFacing = DIRNAME(-dx,-dz); // terminus points away from the hip, along the axis (front-state law)""",
     """  const axis = (f === "north" || f === "south") ? [[1,0],[-1,0]] : [[0,1],[0,-1]];
  const DIRNAME = (dx,dz) => dx===1?"east":dx===-1?"west":dz===1?"south":"north";
  for (const [dx,dz] of axis) {
    // #174: a hipped end = along the ridge axis the next cell is open and, one level DOWN, a 45 slopes away from the
    // ridge (its downhill side = the axis direction). The ridge_end's state = the side its hip end points to.
    const n = nb(b,dx,dz);
    let below = null; try { below = b.offset({ x: dx, y: -1, z: dz }); } catch {}
    if (n && n.isAir && below && R45.has(below.typeId) && faceOf(below) === DIRNAME(dx,dz)) {
      const endFacing = DIRNAME(dx,dz);"""),
    # Rule C: one level above the centre
    ("""    const c = nb(b,cx,cz); if (!c || !c.isAir) continue;
    let hips = 0, m = null;
    for (const [dx,dz] of D4) { const h = nb(c,dx,dz); if (h && HIP.has(h.typeId)) { hips++; m = m || matOf(h.typeId); } }
    if (hips === 4 && m) {
      setBlockWithStates(c, `pw:roof_pyramidion_${m}`, "north", "bottom");""",
     """    const c = nb(b,cx,cz); if (!c) continue;
    let hips = 0, m = null;
    for (const [dx,dz] of D4) { const h = nb(c,dx,dz); if (h && HIP.has(h.typeId)) { hips++; m = m || matOf(h.typeId); } }
    let top = null; try { top = c.above(); } catch {}
    if (hips === 4 && m && top && top.isAir) {
      // #174: the four hips' inner edges stand a full block above the centre cell -> the cap goes one level UP
      setBlockWithStates(top, `pw:roof_pyramidion_${m}`, "north", "bottom");"""),
    # Rule G: corner facings + outward on closure
    ("""    const form = (ax >= 1 && az >= 1) ? "corner" : "straight";
    try { c.setPermutation(c.permutation.withState("pw:ring_form", form)); } catch {}""",
     """    const form = (ax >= 1 && az >= 1) ? "corner" : "straight";
    try { c.setPermutation(c.permutation.withState("pw:ring_form", form)); } catch {}
    if (form === "corner") {                         // #174: the corner's outer lip = the two sides WITHOUT neighbours
      const ex = ns.some((t) => t[0] === 1), sz = ns.some((t) => t[1] === 1);
      const cf = ex && sz ? "north" : !ex && sz ? "east" : !ex && !sz ? "south" : "west";
      try { c.setPermutation(c.permutation.withState("minecraft:cardinal_direction", cf)); } catch {}
    }"""),
    ("""    if (degTwo && seen.size >= 8) {""",
     """    if (degTwo && seen.size >= 8) {
      try {                                          // #174: closed ring -> every straight faces outward
        const cells = [...seen].map((k) => k.split(",").map(Number));
        const cx = cells.reduce((a, c) => a + c[0], 0) / cells.length, cz = cells.reduce((a, c) => a + c[2], 0) / cells.length;
        for (const [x, y, z] of cells) {
          const c = b.dimension.getBlock({ x, y, z }); if (!c || !RING.has(c.typeId)) continue;
          const ns = ringNeighbors(c);
          if (ns.length === 2 && ns[0][0] === -ns[1][0] && ns[0][1] === -ns[1][1]) {
            const alongX = ns[0][0] !== 0;
            const of = alongX ? (z < cz ? "north" : "south") : (x < cx ? "west" : "east");
            c.setPermutation(c.permutation.withState("minecraft:cardinal_direction", of));
          }
        }
      } catch (e) { say(`RULE G orient err: ${e}`); }"""),
    # Rule B second direction: a 45 placed under the open end of a ridge
    ("""    if (R45.has(id)) { tryCornerFold(b, id); return; }""",
     """    if (R45.has(id)) {
      if (tryCornerFold(b, id)) return;
      try {                                          // #174: a 45 laid under the open end of a ridge caps that ridge
        const f = faceOf(b); const d = DV[f];
        const r = b.offset({ x: -d[0], y: 1, z: -d[1] });
        if (r && RIDGE.has(r.typeId)) tryRidgeEnd(r, r.typeId);
      } catch {}
      return;
    }"""),
]


def fix_companion():
    p = BP / "scripts/pw_companion.js"
    backup(p)
    s = p.read_text()
    for i, (a, b) in enumerate(COMPANION_PATCHES):
        assert s.count(a) == 1, f"companion patch {i}: {s.count(a)} matches"
        s = s.replace(a, b)
    s = s.replace("// SEMANTICS v3: front-state law; Rules maps RE-DERIVED (Fix-Wave 1 / D-1, 2026-08-09)",
                  "// SEMANTICS v4 (#174, 2026-10-02): corner/hip/ring maps re-derived under the MEASURED transformation law (D-C487)")
    p.write_text(s)
    LOG.append(f"S1 companion: {len(COMPANION_PATCHES)} patches (Rule A outer corners + map, Rule B hipped end both orders, Rule C level, Rule G corners + closure, Rule E own map)")


# ---------------------------------------------------------------- structures
def setb(st, x, y, z, name, face=None, half="bottom", **extra):
    states = {}
    if face:
        states["minecraft:cardinal_direction"] = M.s(face)
    if name.split(":")[1].startswith(("roof45", "roof_hip", "roof_gusset", "roof_pyramidion", "roof_ridge_end")):
        states["minecraft:vertical_half"] = M.s(half)
    for k, v in extra.items():
        states[k.replace("__", ":")] = M.s(v)
    st.set(x, y, z, name, states)


def s2_hipped_roof(m="oak"):
    W, D = 7, 5                                        # x 0..6, z 0..4
    st = M.Structure((W, 3, D))
    R, H, RG, RE = f"pw:roof45_{m}", f"pw:roof_hip_{m}", f"pw:roof45_ridge_{m}", f"pw:roof_ridge_end_{m}"
    for lv, (x0, x1, z0, z1) in enumerate([(0, 6, 0, 4), (1, 5, 1, 3)]):
        for x in range(x0 + 1, x1):
            setb(st, x, lv, z0, R, "north")
            setb(st, x, lv, z1, R, "south")
        for z in range(z0 + 1, z1):
            setb(st, x0, lv, z, R, "west")
            setb(st, x1, lv, z, R, "east")
        setb(st, x0, lv, z0, H, "north")
        setb(st, x1, lv, z0, H, "east")
        setb(st, x1, lv, z1, H, "south")
        setb(st, x0, lv, z1, H, "west")
    setb(st, 2, 2, 2, RE, "west")
    setb(st, 3, 2, 2, RG, "north")
    setb(st, 4, 2, 2, RE, "east")
    return st


def s4_gable(m="oak"):
    st = M.Structure((3, 2, 3))
    for x in range(3):
        setb(st, x, 0, 0, f"pw:roof45_{m}", "north")
        setb(st, x, 0, 2, f"pw:roof45_{m}", "south")
        setb(st, x, 1, 1, f"pw:roof45_ridge_{m}", "north")
    st.set(0, 0, 1, f"minecraft:{m}_planks")         # gable walls under the ridge ends
    st.set(2, 0, 1, f"minecraft:{m}_planks")
    return st


def s1_gusset_fold(m="oak"):
    """the gusset pair in its junction: plane y = x + (16 - z) rising to the NE corner (state north).
    Neighbours that share its edges: west roof45 S (level 0), south roof45 W (level 0), north roof45 W (level 1),
    east roof45 S (level 1)."""
    st = M.Structure((3, 2, 3))
    setb(st, 1, 0, 1, f"pw:roof_gusset_lower_{m}", "north")
    setb(st, 1, 1, 1, f"pw:roof_gusset_upper_{m}", "north")
    setb(st, 0, 0, 1, f"pw:roof45_{m}", "south")
    setb(st, 1, 0, 2, f"pw:roof45_{m}", "west")
    setb(st, 1, 1, 0, f"pw:roof45_{m}", "west")
    setb(st, 2, 1, 1, f"pw:roof45_{m}", "south")
    return st


def write_structs():
    SP = BP / "structures/pw"
    for name, st in (("s1_gusset_column", s1_gusset_fold()), ("s2_hip_junction", s2_hipped_roof()), ("s4_ridge_run", s4_gable())):
        p = SP / f"{name}.mcstructure"
        backup(p)
        p.write_bytes(st.to_bytes())
    LOG.append("T1 structures: s1 -> gusset fold (gusset pair + its 4 edge neighbours), s2 -> hipped roof 7x5 (8 hips, 2 ridge ends, "
               "ridge), s4 -> plain gable run (3 ridges + gable planks); s3 pyramid + s6 ring states already match the law")


def main():
    t = time.strftime("%H:%M:%S")
    fix_hip()
    fix_pyramidion()
    fix_gussets()
    fix_crown()
    fix_bp_blocks()
    fix_companion()
    write_structs()
    out = Path("/home/claude/_docs/blocks/ROOF-FIX-174.json")
    out.write_text(json.dumps({"time": t, "changes": LOG, "backup": str(BACKUP)}, indent=1))
    print("\n".join(LOG))


if __name__ == "__main__" and "--pyramidion" not in sys.argv:
    main()


# ---------------------------------------------------------------- G2b (added 19:4x): pointed pyramidion from hip quarters
def mirror_z(g):
    """file-z mirror: origin z -> -(z+sz), pivot z -> -pz, rotation (-rx, -ry, rz), north<->south uv keys."""
    for b in g["bones"]:
        for c in b.get("cubes", []):
            c["origin"][2] = round(-(c["origin"][2] + c["size"][2]), 4)
            if "pivot" in c:
                c["pivot"][2] = round(-c["pivot"][2], 4)
            if "rotation" in c:
                r = c["rotation"]
                c["rotation"] = [-r[0] if r[0] else 0, -r[1] if r[1] else 0, r[2]]
            uv = c.get("uv")
            if isinstance(uv, dict):
                n, s = uv.pop("north", None), uv.pop("south", None)
                if n is not None:
                    uv["south"] = n
                if s is not None:
                    uv["north"] = s


def pyramidion_from_hip():
    """The apex cell of a 45-degree pyramid is four hips at half scale meeting at the centre: the NW quarter is the
    (fixed) NW hip scaled by 0.5 and moved to the NW quadrant; NE / SW / SE are its mirrors. Every face then continues
    the 45-degree planes of the ring below exactly (edge height = hip eave height / 2 + ring top) and rises to a point."""
    import copy
    hip = jload(MODELS / "roof_hip.geo.json")["minecraft:geometry"][0]
    q = copy.deepcopy(hip)
    k = 0.5
    for b in q["bones"]:
        for c in b.get("cubes", []):
            c["origin"] = [round(v * k, 4) for v in c["origin"]]
            c["size"] = [round(v * k, 4) for v in c["size"]]
            if "pivot" in c:
                c["pivot"] = [round(v * k, 4) for v in c["pivot"]]
            for spec in (c.get("uv") or {}).values():
                if isinstance(spec, dict) and "uv_size" in spec:
                    spec["uv_size"] = [round(v * k, 4) for v in spec["uv_size"]]
            # NW quadrant = world x -8..0, z -8..0 = file x 0..8: shift by file (+4, 0, -4)
            c["origin"][0] += 4
            c["origin"][2] -= 4
            if "pivot" in c:
                c["pivot"][0] += 4
                c["pivot"][2] -= 4
    quarters = [copy.deepcopy(q)]
    ne = copy.deepcopy(q); mirror_x(ne); quarters.append(ne)
    sw = copy.deepcopy(q); mirror_z(sw); quarters.append(sw)
    se = copy.deepcopy(q); mirror_x(se); mirror_z(se); quarters.append(se)
    p = MODELS / "roof_pyramidion.geo.json"
    d = jload(p)
    g = d["minecraft:geometry"][0]
    cap = [c for _b, c in cubes(g) if c["origin"] == [-1.2, 8, -1.2]]
    allc = [c for qq in quarters for _b, c in cubes(qq)]
    g["bones"] = [{"name": "root", "pivot": [0, 0, 0], "cubes": allc + cap}]
    jsave(p, d)
    LOG.append(f"G2b roof_pyramidion rebuilt as four half-scale NW hips (mirrored to NE/SW/SE) + the apex cap: {len(allc) + len(cap)} cubes; "
               "a pointed 45-degree cap that continues the ring's planes (was a flat-topped frustum with short boards)")


if __name__ == "__main__" and "--pyramidion" in sys.argv:
    pyramidion_from_hip()
    out = Path("/home/claude/_docs/blocks/ROOF-FIX-174.json")
    d = json.loads(out.read_text())
    d["changes"] += LOG
    out.write_text(json.dumps(d, indent=1))
    print("\n".join(LOG))
