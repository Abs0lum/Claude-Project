#!/usr/bin/env python3
"""placement_fix_175.py — #175 fixes from the all-block placement census (tools/block_placement_census.py, D-C490).
Undelivered builds edited in place (RP-04 1.3.156, BP-02 1.3.206); backups in _docs/blocks/before_placement_fix_175/.

F1 rafter45   the beam rose toward the state side (low S / high N at state north) while a roof45 of the same state
              has its eave (low side) at the state side -> the rafter crossed the roof it was meant to follow.
              Rotation sign flipped: the beam now follows the roof45 of the same facing.
F2 Rule D     room_wall halves hug the OUTER edge of their cell at their state side (measured: panel at world z -8..0
              for state north), so the partner hugging the same boundary is the FRONT neighbour facing the opposite
              way. The rule looked at the BACK neighbour (a full cell of air between the two panels). Fixed: the
              front neighbour; the merged full block goes into the placed cell (the halves straddle that boundary).
F3 Rule E     room_wall_corner occupies the two outer edges {state, state+90 cw}: north = N+E, west = W+N,
              south = S+W, east = E+S (measured). The old map put the L in the opposite corner in all four cases.
              New map keyed by the two panel sides; the corner forms where the perpendicular run leaves from the
              BACK of the placed wall, or when the placed wall is that perpendicular run (either order).
F4 ramp snow  box-projection uv windows for the snow caps above y = 16 ran to v = -48 (outside the 128-px texture ->
              atlas bleed, the D-C223 furniture law). Every window is shifted inside the texture (size kept)."""
import json
import re
import shutil
from pathlib import Path

B = Path("/home/claude/_build")
RP = B / "rp04-156"
BP = B / "bp02-206"
BACKUP = Path("/home/claude/_docs/blocks/before_placement_fix_175")
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


def fix_rafter():
    p = RP / "models/blocks/pw_homestead.geo.json"
    d = jload(p)
    n = 0
    for g in d["minecraft:geometry"]:
        if g["description"]["identifier"] != "geometry.pw_rafter45":
            continue
        for b in g["bones"]:
            for c in b.get("cubes", []):
                r = c.get("rotation")
                if r and r[0]:
                    c["rotation"] = [-r[0], r[1], r[2]]
                    n += 1
    assert n == 1, n
    jsave(p, d)
    LOG.append("F1 rafter45: beam rotation x -45 -> +45 (now low at the state side, like roof45)")


def fix_snow_uv():
    total = 0
    for name in ("pw_snowcaps.geo.json", "pw_ramps.geo.json"):
        p = RP / "models/blocks" / name
        d = jload(p)
        n = 0
        for g in d["minecraft:geometry"]:
            tw, th = g["description"].get("texture_width", 16), g["description"].get("texture_height", 16)
            for b in g["bones"]:
                for c in b.get("cubes", []):
                    uv = c.get("uv")
                    if not isinstance(uv, dict):
                        continue
                    for face, spec in uv.items():
                        u, v = spec["uv"]
                        us, vs = spec.get("uv_size", [0, 0])
                        lo_u, hi_u = min(u, u + us), max(u, u + us)
                        lo_v, hi_v = min(v, v + vs), max(v, v + vs)
                        du = dv = 0
                        if lo_u < 0:
                            du = -lo_u
                        elif hi_u > tw:
                            du = tw - hi_u
                        if lo_v < 0:
                            dv = -lo_v
                        elif hi_v > th:
                            dv = th - hi_v
                        if du or dv:
                            spec["uv"] = [round(u + du, 3), round(v + dv, 3)]
                            n += 1
        if n:
            jsave(p, d)
        total += n
        LOG.append(f"F4 {name}: {n} uv windows shifted inside the texture")
    return total


COMPANION_PATCHES = [
    # Rule E map: corner = the two outer edges the halves occupy
    ("""const WALL_CORNER_FACE = { "north|west":"south", "west|north":"south", "north|east":"west", "east|north":"west",
                   "south|east":"north", "east|south":"north", "south|west":"east", "west|south":"east" };""",
     """// #175 (D-C490): room_wall_corner at state s occupies the outer edges {s, s+90 cw}: n = N+E, w = W+N, s = S+W, e = E+S.
const WALL_CORNER_FACE = { "north|east":"north", "east|north":"north", "north|west":"west", "west|north":"west",
                   "south|west":"south", "west|south":"south", "south|east":"east", "east|south":"east" };"""),
    # Rule D: the partner hugs the same boundary from the FRONT cell
    ("""function tryWallMerge(b) {
  const f = faceOf(b); if (!f) return false;
  const [dx,dz] = BACK[f]; const n = nb(b,dx,dz);
  if (!n || n.typeId !== RW) return false;
  const nf = faceOf(n);
  const opp = { north:"south", south:"north", east:"west", west:"east" };
  if (nf !== opp[f]) return false;                       // must hug the SAME shared face
  const mat = matStateOf(n);
  try {
    n.setType(FULL_OF(mat));
    b.setType("minecraft:air");""",
     """function tryWallMerge(b) {
  const f = faceOf(b); if (!f) return false;
  // #175: the half panel hugs the cell's edge on its state side, so the half hugging the same boundary from the other
  // side is the FRONT neighbour facing back at it (the old code looked behind: a full cell of air between the panels).
  const [dx,dz] = DV[f]; const n = nb(b,dx,dz);
  if (!n || n.typeId !== RW) return false;
  const nf = faceOf(n);
  const opp = { north:"south", south:"north", east:"west", west:"east" };
  if (nf !== opp[f]) return false;                       // must hug the SAME shared face
  const mat = matStateOf(n);
  try {
    b.setType(FULL_OF(mat));
    n.setType("minecraft:air");"""),
    # Rule E: corner forms at the placed wall when a perpendicular run leaves from its back, or at the neighbour
    ("""function tryWallCorner(b) {
  const f = faceOf(b); if (!f) return false;
  for (const [dx,dz] of N4) {
    const n = nb(b,dx,dz); if (!n || n.typeId !== RW) continue;
    const nf = faceOf(n); if (!nf || !PERP[f].includes(nf)) continue;
    const cornerFacing = WALL_CORNER_FACE[`${f}|${nf}`] || f;    // room-wall map (unchanged by #174)
    try {
      const mat = matStateOf(b);
      b.setType(RWC);
      b.setPermutation(b.permutation.withState("minecraft:cardinal_direction", cornerFacing));
      try { b.setPermutation(b.permutation.withState("pw:material", mat)); } catch {}
      say(`RULE E — L-corner resolve: half wall met a perpendicular run; became room_wall_corner facing ${cornerFacing} — §aCORNERED§r`);
      return true;
    } catch (e) { say(`RULE E FAIL: ${e}`); return false; }
  }
  return false;
}""",
     """function makeWallCorner(cell, f, nf) {
  const cornerFacing = WALL_CORNER_FACE[`${f}|${nf}`]; if (!cornerFacing) return false;
  try {
    const mat = matStateOf(cell);
    cell.setType(RWC);
    cell.setPermutation(cell.permutation.withState("minecraft:cardinal_direction", cornerFacing));
    try { cell.setPermutation(cell.permutation.withState("pw:material", mat)); } catch {}
    say(`RULE E — L-corner resolve: half wall met a perpendicular run; became room_wall_corner facing ${cornerFacing} — §aCORNERED§r`);
    return true;
  } catch (e) { say(`RULE E FAIL: ${e}`); return false; }
}
function tryWallCorner(b) {
  const f = faceOf(b); if (!f) return false;
  // #175: (1) the placed wall is the corner cell: a perpendicular half wall sits BEHIND it (its run leaves from the back)
  const back = nb(b, -DV[f][0], -DV[f][1]);
  if (back && back.typeId === RW) {
    const nf = faceOf(back);
    if (nf && PERP[f].includes(nf) && makeWallCorner(b, f, nf)) return true;
  }
  // (2) the placed wall is the perpendicular run: the corner cell is the neighbour along my panel whose back faces me
  for (const [dx,dz] of N4) {
    if (dx === DV[f][0] && dz === DV[f][1]) continue;
    if (dx === -DV[f][0] && dz === -DV[f][1]) continue;
    const n = nb(b,dx,dz); if (!n || n.typeId !== RW) continue;
    const nf = faceOf(n); if (!nf || !PERP[f].includes(nf)) continue;
    if (DV[nf][0] !== -dx || DV[nf][1] !== -dz) continue;        // n's front points away from me: I am behind n
    if (makeWallCorner(n, nf, f)) return true;
  }
  return false;
}"""),
]


def fix_companion():
    p = BP / "scripts/pw_companion.js"
    backup(p)
    s = p.read_text()
    for i, (a, b) in enumerate(COMPANION_PATCHES):
        assert s.count(a) == 1, f"companion patch {i}: {s.count(a)} matches"
        s = s.replace(a, b)
    p.write_text(s)
    LOG.append(f"F2/F3 companion: {len(COMPANION_PATCHES)} patches (Rule D front neighbour, Rule E map + both orders)")


def main():
    fix_rafter()
    fix_snow_uv()
    fix_companion()
    Path("/home/claude/_docs/blocks/PLACEMENT-FIX-175.json").write_text(json.dumps({"changes": LOG, "backup": str(BACKUP)}, indent=1))
    print("\n".join(LOG))


if __name__ == "__main__":
    main()
