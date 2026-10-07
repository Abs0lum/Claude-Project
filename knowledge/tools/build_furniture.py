#!/usr/bin/env python3
"""build_furniture.py — the pw:furniture family, round 1 (12 medieval pieces x oak/spruce/dark oak), per the rulings of
2026-09-22 17:19 (GO) / 18:11 / 18:55 (D-C219, D-C222, D-C223):

  BP-02 v1.3.182 -> .183   36 blocks pw:furn_<piece>_<wood> (format 1.21.80): front faces the placer (placement_direction trait,
                           y_rotation_offset 180 + the homestead rotation table); collision per ruling (bench 8 = slab, stool/barrel 10,
                           chair 12 = 3/4, table 14, storage 16, wall pieces none); seats carry the pw:seat custom component (sit);
                           tables have world-aligned pw:n/e/s/w booleans -> 16 join geometries (adjacent tables auto-join: shared legs and
                           apron rails drop); entity pw:seat (invisible rideable); scripts/pw_furniture.js (sit + cleanup + table join
                           listener) imported by main.js; ledger rows + needs-hash; lang.
  RP-04 v1.3.136 -> .137   models/blocks/pw_furniture.geo.json (11 pieces + 16 table variants, box-projected uv kept INSIDE the 16x16 tile:
                           boxes crossing y = 16 are split), pw_furn_iron (wrought iron from the Patrix anvil band) + MER + texture set,
                           terrain keys pw_furn_iron / pw_mat_stripped_dark_oak(_top), client entity pw:seat (empty geometry), lang names.
  Markers 0.1.8 -> 0.1.9   pw:station_seat — the 18th station role ("a station made for that", 18:11).
"""
import json, re, shutil, sys, datetime, hashlib, copy
from pathlib import Path
from PIL import Image, ImageDraw
sys.path.insert(0, "/home/claude/tools")
import furniture_geo as FG

ROOT = Path("/home/claude"); DATE = "2026-09-22"; LOG = ROOT / "_logs/phase_log.md"
def log(m): LOG.open("a").write(f"[{datetime.datetime.now().strftime('%H:%M')} CT 09-22] BUILD FURNITURE — {m}\n")
def jload(p): return json.loads(Path(p).read_text(encoding="utf-8-sig"))
def jdump(o, p): Path(p).write_text(json.dumps(o, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")

BP_SRC, BP_DST, BP_VER = ROOT / "_build/bp02-182", ROOT / "_build/bp02-184", "1.3.184"   # r2 rebuilds from the pre-furniture base
RP_SRC, RP_DST, RP_VER = ROOT / "_build/rp04-136", ROOT / "_build/rp04-138", "1.3.138"
MK_SRC, MK_DST, MK_VER = ROOT / "_build/markers-0.1.8", ROOT / "_build/markers-0.1.9", "0.1.9"
BUILD_MARKERS = False   # r2: Markers 0.1.9 is unchanged (already delivered)
WOODS = {"oak": ("pw_mat_oak_planks", "pw_mat_stripped_oak", "pw_mat_stripped_oak_top", "Oak"),
         "spruce": ("pw_mat_spruce_planks", "pw_mat_stripped_spruce", "pw_mat_stripped_spruce_top", "Spruce"),
         "dark_oak": ("pw_mat_dark_oak_planks", "pw_mat_stripped_dark_oak", "pw_mat_stripped_dark_oak_top", "Dark Oak")}
IRON_KEY = "pw_furn_iron"
# collision heights in cubes (ruling 18:11: low seats 1/2 .. 3/4); None = no collision (wall pieces, ruling 18:55)
COLLISION = {"table": 14, "bench": 8, "stool": 10, "chair": 12, "shelf": 16, "wall_shelf": None, "cupboard": 16, "dresser": 16,
             "trestle": 14, "barrel_seat": 10, "coat_pegs": None, "mantel": None}
SELECTION = {"wall_shelf": ([-8, 3, 2], [16, 5, 6]), "coat_pegs": ([-8, 11, 4], [16, 3, 4]), "mantel": ([-8, 0, 2], [16, 5, 6])}   # r2: both lowered (ruling 19:46)
SEAT_TOP = {"bench": 8, "stool": 10, "chair": 10, "barrel_seat": 10}          # seat surface, cubes (script table too)
NAMES = {"table": "Table", "bench": "Bench", "stool": "Stool", "chair": "Chair", "shelf": "Shelf", "wall_shelf": "Wall Shelf", "cupboard": "Cupboard",
         "dresser": "Dresser", "trestle": "Trestle", "barrel_seat": "Barrel Seat", "coat_pegs": "Coat Pegs", "mantel": "Mantel"}
ROT = [("north", [0, 0, 0]), ("west", [0, 90, 0]), ("south", [0, 180, 0]), ("east", [0, -90, 0])]   # the homestead table (front faces the placer)

# ---------------------------------------------------------------------------------------------------------------------
# geometry: in-tile uv law — a face's uv window must stay inside the 16x16 tile, so boxes crossing y = 16 are split there
# ---------------------------------------------------------------------------------------------------------------------
def split_y16(box):
    o, s = box["o"], box["s"]
    if "rot" in box or o[1] >= 16 or o[1] + s[1] <= 16: return [box]
    a = copy.deepcopy(box); b = copy.deepcopy(box)
    a["s"] = [s[0], 16 - o[1], s[2]]; b["o"] = [o[0], 16, o[2]]; b["s"] = [s[0], o[1] + s[1] - 16, s[2]]
    return [a, b]

def bedrock_geometry(ident, boxes):
    cubes = []
    for b0 in boxes:
        for b in split_y16(b0):
            o, s = b["o"], b["s"]; m = b["m"]; f = b.get("faces", {}); uv = {}
            for face in ("north", "south", "east", "west", "up", "down"):
                inst = f.get(face, m)
                if face in ("north", "south"): u, v, w, h = o[0], 16 - o[1] - s[1], s[0], s[1]
                elif face in ("east", "west"): u, v, w, h = o[2], 16 - o[1] - s[1], s[2], s[1]
                else: u, v, w, h = o[0], o[2], s[0], s[2]
                u, v = u % 16, v % 16
                if u + w > 16: u = 16 - w                      # keep the window in the tile (rotated bands / fractional cases)
                if v + h > 16: v = 16 - h
                uv[face] = {"uv": [round(u, 3), round(v, 3)], "uv_size": [round(w, 3), round(h, 3)], "material_instance": inst}
            c = {"origin": [round(o[0] - 8, 3), round(o[1], 3), round(o[2] - 8, 3)], "size": [round(x, 3) for x in s], "uv": uv}
            if "rot" in b: c["rotation"] = b["rot"]; c["pivot"] = [round(b["piv"][0] - 8, 3), round(b["piv"][1], 3), round(b["piv"][2] - 8, 3)]
            cubes.append(c)
    top = max(b["o"][1] + b["s"][1] for b in boxes) / 16
    return {"description": {"identifier": ident, "texture_width": 16, "texture_height": 16, "visible_bounds_width": 2, "visible_bounds_height": max(1.5, top + 0.5), "visible_bounds_offset": [0, top / 2, 0]},
            "bones": [{"name": "piece", "pivot": [0, 0, 0], "cubes": cubes}]}

def table_variant(mask):
    """mask = (n, e, s, w) booleans (world-aligned: n = the cell at z-1).  A joined side loses its apron rail; a corner leg
    stays only when neither adjacent side is joined (so a run of tables carries legs at its outer corners only)."""
    n, e, s, w = mask
    # r2: rails run BETWEEN the legs, 0.5 behind the leg faces (no shared planes); a rail whose end meets a joined side
    # runs on to the cell edge, so the rails of a run of tables meet end to end instead of stopping short of a missing leg
    x0, x1 = (0 if w else 2.5), (16 if e else 13.5)
    z0, z1 = (0 if n else 2.5), (16 if s else 13.5)
    boxes = [FG.B([0, 11.5, 0], [16, 2.5, 16], "board")]
    if not n: boxes.append(FG.B([x0, 9, 1.5], [x1 - x0, 3, 1]))
    if not s: boxes.append(FG.B([x0, 9, 13.5], [x1 - x0, 3, 1]))
    if not w: boxes.append(FG.B([1.5, 9, z0], [1, 3, z1 - z0]))
    if not e: boxes.append(FG.B([13.5, 9, z0], [1, 3, z1 - z0]))
    for (x, z, sides) in ((1, 1, (n, w)), (13, 1, (n, e)), (1, 13, (s, w)), (13, 13, (s, e))):
        if not any(sides): boxes.append(FG.B([x, 0, z], [2, 12.5, 2], "post", faces={"up": "end", "down": "end"}))
    return boxes

def mask_name(mask): return "".join("1" if b else "0" for b in mask)
MASKS = [(bool(i & 8), bool(i & 4), bool(i & 2), bool(i & 1)) for i in range(16)]   # bits n e s w

# ---------------------------------------------------------------------------------------------------------------------
def block_json(piece, wood):
    planks, post, end, _ = WOODS[wood]; ident = f"pw:furn_{piece}_{wood}"
    RM = "alpha_test_single_sided"   # r2: alpha_test disables backface culling (MS Learn); textures are opaque (min alpha 255)
    mats = {"*": {"texture": planks, "render_method": RM}, "board": {"texture": planks, "render_method": RM},
            "post": {"texture": post, "render_method": RM}, "end": {"texture": end, "render_method": RM},
            "iron": {"texture": IRON_KEY, "render_method": RM}}
    comps = {"minecraft:geometry": {"identifier": f"geometry.pw_furn_{piece}" + ("_0000" if piece == "table" else "")},
             "minecraft:material_instances": mats, "minecraft:light_dampening": 0,
             "minecraft:destructible_by_mining": {"seconds_to_destroy": 1.0}, "minecraft:destructible_by_explosion": {"explosion_resistance": 3},
             "minecraft:display_name": f"tile.{ident}.name", "minecraft:map_color": "#7a5a3a"}
    h = COLLISION[piece]
    if h is None:
        comps["minecraft:collision_box"] = False
        o, s = SELECTION[piece]; comps["minecraft:selection_box"] = {"origin": o, "size": s}
    else:
        comps["minecraft:collision_box"] = {"origin": [-8, 0, -8], "size": [16, h, 16]}
        comps["minecraft:selection_box"] = {"origin": [-8, 0, -8], "size": [16, h, 16]}
    if piece in SEAT_TOP: comps["minecraft:custom_components"] = ["pw:seat"]
    desc = {"identifier": ident, "menu_category": {"category": "construction", "group": "minecraft:itemGroup.name.planks"}}
    perms = []
    if piece == "table":
        desc["states"] = {"pw:n": [False, True], "pw:e": [False, True], "pw:s": [False, True], "pw:w": [False, True]}
        for mask in MASKS:
            if not any(mask): continue
            cond = " && ".join(f"q.block_state('pw:{k}') == {'true' if v else 'false'}" for k, v in zip("nesw", mask))
            perms.append({"condition": cond, "components": {"minecraft:geometry": {"identifier": f"geometry.pw_furn_table_{mask_name(mask)}"}}})
    else:
        desc["traits"] = {"minecraft:placement_direction": {"enabled_states": ["minecraft:cardinal_direction"], "y_rotation_offset": 180}}
        for d, rot in ROT:
            perms.append({"condition": f"q.block_state('minecraft:cardinal_direction') == '{d}'", "components": {"minecraft:transformation": {"rotation": rot}}})
    return {"format_version": "1.21.80", "minecraft:block": {"description": desc, "components": comps, "permutations": perms}}

SEAT_ENTITY_BP = {"format_version": "1.21.80", "minecraft:entity": {
    "description": {"identifier": "pw:seat", "is_spawnable": False, "is_summonable": True, "is_experimental": False},
    "components": {
        "minecraft:type_family": {"family": ["pw_seat", "inanimate"]},
        "minecraft:collision_box": {"width": 0.05, "height": 0.05},
        "minecraft:physics": {"has_gravity": False, "has_collision": False},
        "minecraft:pushable": {"is_pushable": False, "is_pushable_by_piston": False},
        "minecraft:knockback_resistance": {"value": 1.0},
        "minecraft:damage_sensor": {"triggers": [{"cause": "all", "deals_damage": "no"}]},
        "minecraft:health": {"value": 1, "max": 1},
        "minecraft:rideable": {"seat_count": 1, "family_types": ["player"], "interact_text": "action.interact.sit", "pull_in_entities": False,
                               "rider_can_interact": False, "seats": [{"position": [0.0, 0.0, 0.0]}]},
        "minecraft:persistent": {},
        "minecraft:conditional_bandwidth_optimization": {}}}}
SEAT_ENTITY_RP = {"format_version": "1.10.0", "minecraft:client_entity": {"description": {
    "identifier": "pw:seat", "materials": {"default": "entity_alphatest"}, "textures": {"default": "textures/entity/pw_seat"},
    "geometry": {"default": "geometry.pw_seat"}, "render_controllers": ["controller.render.default"]}}}
SEAT_GEO_RP = {"format_version": "1.12.0", "minecraft:geometry": [{"description": {"identifier": "geometry.pw_seat", "texture_width": 16, "texture_height": 16, "visible_bounds_width": 1, "visible_bounds_height": 1, "visible_bounds_offset": [0, 0.5, 0]},
                                                                    "bones": [{"name": "root", "pivot": [0, 0, 0]}]}]}

SCRIPT = r'''// pw_furniture.js — the pw:furniture family runtime (BP-02 v1.3.183): sit + table auto-join.
//
//  seats   pw:furn_{bench,stool,chair,barrel_seat}_<wood>  custom component pw:seat: interact (empty hand or any item that is
//          not a block) -> an invisible rideable pw:seat entity is spawned at the seat surface and the player mounts it;
//          sneak dismounts (vanilla); a 1 s sweeper removes riderless seat entities.  One seat entity per cell, reused.
//  tables  pw:furn_table_<wood>  states pw:n/e/s/w (world-aligned booleans, n = the cell at z-1): adjacent tables auto-join —
//          the permutation picks one of 16 geometries where joined sides drop their apron rail and shared corner legs.
//          Neighbour listener on place/break (the same pattern as the Markers frame_post resolver).
// Engine notes: block custom components are registered in system.beforeEvents.startup (@minecraft/server 2.0.0);
// the rider's pelvis sits ~0.3 below the seat entity's origin -> SEAT_Y_OFFSET (ASSUMPTION, witness item).
import { world, system, BlockPermutation } from "@minecraft/server";

const TAG = "[pw_furniture]";
const log = (m) => { try { console.warn(`${TAG} ${m}`); } catch { /* no console */ } };
const WOODS = ["oak", "spruce", "dark_oak"];
const SEAT_TOP = { bench: 8, stool: 10, chair: 10, barrel_seat: 10 };          // seat surface in cubes (1/16 block)
export const SEAT_BLOCKS = new Map();                                           // block id -> seat surface (cubes); the CIVITAS seat-station registry
for (const [piece, top] of Object.entries(SEAT_TOP)) for (const w of WOODS) SEAT_BLOCKS.set(`pw:furn_${piece}_${w}`, top);
export const TABLE_IDS = new Set(WOODS.map((w) => `pw:furn_table_${w}`));
const SEAT_ENTITY = "pw:seat";
const SEAT_Y_OFFSET = -0.30;                                                    // ASSUMPTION: rider origin vs seat surface (witness; +/-0.1 steps)
const YAW = { north: 180, south: 0, east: -90, west: 90 };                       // Bedrock yaw: 0 = +z (south), 180 = north

function seatFor(block) {
  const top = SEAT_BLOCKS.get(block.typeId); if (top === undefined) return null;
  const dim = block.dimension, l = block.location;
  const loc = { x: l.x + 0.5, y: l.y + top / 16 + SEAT_Y_OFFSET, z: l.z + 0.5 };
  const near = dim.getEntities({ type: SEAT_ENTITY, location: loc, maxDistance: 0.75 });
  let seat = near[0];
  if (seat) {
    const r = seat.getComponent("minecraft:rideable");
    if (r && r.getRiders().length > 0) return null;                             // occupied
    seat.teleport(loc);
  } else seat = dim.spawnEntity(SEAT_ENTITY, loc);
  return seat;
}

function sit(player, block) {
  const seat = seatFor(block); if (!seat) return false;
  let yaw = 0;
  try { const d = block.permutation.getState("minecraft:cardinal_direction"); if (d in YAW) yaw = YAW[d]; } catch { /* no state */ }
  try { seat.setRotation({ x: 0, y: yaw }); } catch { /* ignore */ }
  const r = seat.getComponent("minecraft:rideable"); if (!r) return false;
  const ok = r.addRider(player);
  if (ok) system.run(() => { try { player.setRotation({ x: 0, y: yaw }); } catch { /* ignore */ } });
  return ok;
}

// riderless seat entities are removed (sneak-dismount leaves them behind); 1 s cadence, cheap: a handful of entities at most
system.runInterval(() => {
  try {
    for (const dimId of ["overworld", "nether", "the_end"]) {
      const dim = world.getDimension(dimId);
      for (const e of dim.getEntities({ type: SEAT_ENTITY })) {
        const r = e.getComponent("minecraft:rideable");
        if (!r || r.getRiders().length === 0) e.remove();
      }
    }
  } catch (x) { /* dimension not ready */ }
}, 20);

// ---- table auto-join --------------------------------------------------------------------------------------------------
function joinMask(dim, l) {
  const at = (dx, dz) => { try { const b = dim.getBlock({ x: l.x + dx, y: l.y, z: l.z + dz }); return !!b && TABLE_IDS.has(b.typeId); } catch { return false; } };
  return { "pw:n": at(0, -1), "pw:e": at(1, 0), "pw:s": at(0, 1), "pw:w": at(-1, 0) };
}
function refreshTable(dim, l) {
  try {
    const b = dim.getBlock(l); if (!b || !TABLE_IDS.has(b.typeId)) return;
    const m = joinMask(dim, b.location);
    const cur = b.permutation;
    if (["pw:n", "pw:e", "pw:s", "pw:w"].every((k) => cur.getState(k) === m[k])) return;
    b.setPermutation(BlockPermutation.resolve(b.typeId, m));
  } catch (x) { log(`refreshTable: ${x}`); }
}
function refreshAround(dim, l, self) {
  if (self) refreshTable(dim, l);
  for (const [dx, dz] of [[0, -1], [1, 0], [0, 1], [-1, 0]]) refreshTable(dim, { x: l.x + dx, y: l.y, z: l.z + dz });
}
world.afterEvents.playerPlaceBlock.subscribe((ev) => {
  try { if (TABLE_IDS.has(ev.block.typeId)) refreshAround(ev.block.dimension, ev.block.location, true); } catch (x) { log(`place: ${x}`); }
});
world.afterEvents.playerBreakBlock.subscribe((ev) => {
  try { if (TABLE_IDS.has(ev.brokenBlockPermutation.type.id)) refreshAround(ev.block.dimension, ev.block.location, false); } catch (x) { log(`break: ${x}`); }
});

system.beforeEvents.startup.subscribe((ev) => {
  try {
    ev.blockComponentRegistry.registerCustomComponent("pw:seat", {
      onPlayerInteract: (e) => {
        try {
          if (!e.player) return;
          const held = e.itemStack;
          if (held && held.typeId.startsWith("pw:")) return;                 // placing our blocks against a seat stays a placement
          sit(e.player, e.block);
        } catch (x) { log(`seat onPlayerInteract: ${x}`); }
      }
    });
    log("custom component pw:seat registered; tables: " + [...TABLE_IDS].join(","));
  } catch (x) { log(`startup: ${x}`); }
});
try { console.warn(`${TAG} ready — 12 pieces x 3 woods, seats ${SEAT_BLOCKS.size}, tables auto-join`); } catch { /* no console */ }
'''

def station_icon(path):
    """a marker icon in the Markers style: the bench icon's yellow-green ground with a black 3-letter code, 16x16."""
    src = Image.open(MK_SRC / "RP/textures/blocks/pw_station_bench.png").convert("RGBA"); bg = src.getpixel((1, 1))
    im = Image.new("RGBA", (16, 16), bg); px = im.load()
    S = ["1111", "1000", "1110", "0001", "0001", "1111"]; E = ["1111", "1000", "1110", "1000", "1000", "1111"]; A = ["0110", "1001", "1111", "1001", "1001", "1001"]
    for gi, g in enumerate((S, E, A)):
        for r, row in enumerate(g):
            for c, ch in enumerate(row):
                if ch == "1": px[1 + gi * 5 + c, 5 + r] = (10, 10, 10, 255)
    im.save(path)

def main():
    for s, d in ((BP_SRC, BP_DST), (RP_SRC, RP_DST)) + (((MK_SRC, MK_DST),) if BUILD_MARKERS else ()):
        if d.exists(): shutil.rmtree(d)
        shutil.copytree(s, d)
    # ---- RP-04: geometry file
    geos = []
    for n in FG.ORDER:
        if n == "table": continue
        geos.append(bedrock_geometry(f"geometry.pw_furn_{n}", FG.PIECES[n]["boxes"]))
    for mask in MASKS: geos.append(bedrock_geometry(f"geometry.pw_furn_table_{mask_name(mask)}", table_variant(mask)))
    jdump({"format_version": "1.16.0", "minecraft:geometry": geos}, RP_DST / "models/blocks/pw_furniture.geo.json")
    log(f"RP geometry: {len(geos)} geometries ({sum(len(g['bones'][0]['cubes']) for g in geos)} cubes) -> models/blocks/pw_furniture.geo.json")
    # ---- RP-04: iron stem + terrain keys + client entity + lang
    B = RP_DST / "textures/blocks"
    shutil.copy(ROOT / "_design/furniture/pw_furn_iron.png", B / "pw_furn_iron.png"); shutil.copy(ROOT / "_design/furniture/pw_furn_iron_mer.png", B / "pw_furn_iron_mer.png")
    jdump({"format_version": "1.21.30", "minecraft:texture_set": {"color": "pw_furn_iron", "metalness_emissive_roughness": "pw_furn_iron_mer"}}, B / "pw_furn_iron.texture_set.json")
    tt = jload(RP_DST / "textures/terrain_texture.json"); td = tt["texture_data"]
    td["pw_furn_iron"] = {"textures": "textures/blocks/pw_furn_iron"}
    td["pw_mat_stripped_dark_oak"] = {"textures": "textures/blocks/stripped_dark_oak_log"}
    td["pw_mat_stripped_dark_oak_top"] = {"textures": "textures/blocks/stripped_dark_oak_log_top"}
    for k in ("pw_mat_oak_planks", "pw_mat_spruce_planks", "pw_mat_dark_oak_planks", "pw_mat_stripped_oak", "pw_mat_stripped_oak_top", "pw_mat_stripped_spruce", "pw_mat_stripped_spruce_top"):
        assert k in td, k
    jdump(tt, RP_DST / "textures/terrain_texture.json")
    (RP_DST / "entity").mkdir(exist_ok=True); (RP_DST / "models/entity").mkdir(parents=True, exist_ok=True); (RP_DST / "textures/entity").mkdir(parents=True, exist_ok=True)
    jdump(SEAT_ENTITY_RP, RP_DST / "entity/pw_seat.entity.json"); jdump(SEAT_GEO_RP, RP_DST / "models/entity/pw_seat.geo.json")
    Image.new("RGBA", (16, 16), (0, 0, 0, 0)).save(RP_DST / "textures/entity/pw_seat.png")
    lang = RP_DST / "texts/en_US.lang"; t = lang.read_text(encoding="utf-8")
    add = [f"tile.pw:furn_{p}_{w}.name={WOODS[w][3]} {NAMES[p]}" for p in FG.ORDER for w in WOODS] + ["entity.pw:seat.name=Seat", "action.interact.sit=Sit"]
    lang.write_text(t.rstrip("\n") + "\n" + "\n".join(add) + "\n", encoding="utf-8")
    tl = RP_DST / "textures/textures_list.json"
    if tl.exists():
        lst = sorted({str(q.relative_to(RP_DST)).replace("\\", "/").rsplit(".", 1)[0] for q in RP_DST.rglob("*") if q.is_file() and q.suffix.lower() in (".png", ".tga", ".jpg", ".jpeg") and str(q.relative_to(RP_DST)).startswith("textures/")})
        tl.write_text(json.dumps(lst, indent=1) + "\n", encoding="utf-8")
    log("RP wiring: pw_furn_iron (+MER, set), terrain keys, client entity pw:seat, 38 lang lines, textures_list regenerated")
    # ---- BP-02: blocks, entity, script, import, ledger
    for p in FG.ORDER:
        for w in WOODS: jdump(block_json(p, w), BP_DST / f"blocks/pw_furn_{p}_{w}.json")
    jdump(SEAT_ENTITY_BP, BP_DST / "entities/pw_seat.json")
    (BP_DST / "scripts/pw_furniture.js").write_text(SCRIPT, encoding="utf-8")
    mp = BP_DST / "scripts/main.js"; m = mp.read_text(encoding="utf-8")
    old = 'import "./pw_homestead.js"; // HOMESTEAD: hearth / flue / dual wall / rafter (v1.3.178)'
    assert old in m; m = m.replace(old, old + '\nimport "./pw_furniture.js"; // FURNITURE: 12 pieces x 3 woods, sit + table auto-join (v1.3.183)', 1)
    mp.write_text(m, encoding="utf-8")
    led = BP_DST / "PW-DEPENDENCIES.md"; text = led.read_text(encoding="utf-8")
    rows = set(re.findall(r'^\|(\w+)\|`([^`]+)`\|$', text, re.M))
    rows |= {("geometry", g["description"]["identifier"]) for g in geos}
    rows |= {("terrain_key", k) for k in (IRON_KEY, "pw_mat_stripped_dark_oak", "pw_mat_stripped_dark_oak_top", "pw_mat_oak_planks", "pw_mat_spruce_planks", "pw_mat_dark_oak_planks", "pw_mat_stripped_oak", "pw_mat_stripped_oak_top", "pw_mat_stripped_spruce", "pw_mat_stripped_spruce_top")}
    rows |= {("entity", "pw:seat")}
    h = hashlib.sha256(json.dumps(sorted([list(r) for r in rows])).encode()).hexdigest()[:16]
    body = "\n".join(f"|{t}|`{i}`|" for t, i in sorted(rows))
    led.write_text(f"# PW-DEPENDENCIES — BP-02 Tectonic BP\n\nv{BP_VER} · needs-hash `{h}`\n\n|type|identifier|\n|---|---|\n{body}\n", encoding="utf-8")
    log(f"BP: 36 blocks, entity pw:seat, scripts/pw_furniture.js (+ main.js import), ledger {len(rows)} rows hash {h}")
    # ---- Markers 0.1.9: pw:station_seat
    if not BUILD_MARKERS: return stamp()
    bench = jload(MK_DST / "BP/blocks/pw_station_bench.json")
    st = copy.deepcopy(bench); st["minecraft:block"]["description"]["identifier"] = "pw:station_seat"
    st["minecraft:block"]["components"]["minecraft:material_instances"]["*"]["texture"] = "pw_station_seat"
    jdump(st, MK_DST / "BP/blocks/pw_station_seat.json")
    station_icon(MK_DST / "RP/textures/blocks/pw_station_seat.png")
    mtt = jload(MK_DST / "RP/textures/terrain_texture.json"); mtt["texture_data"]["pw_station_seat"] = {"textures": "textures/blocks/pw_station_seat"}; jdump(mtt, MK_DST / "RP/textures/terrain_texture.json")
    for sub, name in (("BP", "PW Civitas Markers BP"), ("RP", "PW Civitas Markers RP")):
        man = jload(MK_DST / sub / "manifest.json"); man["header"]["name"] = f"{name} v{MK_VER}"; man["header"]["version"] = [0, 1, 9]
        for mod in man["modules"]: mod["version"] = [0, 1, 9]
        man["header"]["description"] = (f"v{MK_VER} ({DATE}) SEAT STATION — pw:station_seat, the 18th station role (ruling 18:11: seats are sittable and a station is made for that); "
                                        f"the pw:furniture seats (BP-02 v1.3.183) register as seat stations too. Everything else identical to v0.1.8. Pairs with {'RP' if sub == 'BP' else 'BP'} v{MK_VER}.")
        jdump(man, MK_DST / sub / "manifest.json")
    lm = MK_DST / "BP/PW-DEPENDENCIES.md"
    if lm.exists(): lm.write_text(lm.read_text(encoding="utf-8").replace("v0.1.8 ·", f"v{MK_VER} ·", 1).replace("keys pw_station_*", "keys pw_station_* (18 incl. seat)", 1), encoding="utf-8")
    log("Markers 0.1.9: pw:station_seat block + icon + terrain key; manifests stamped")
    stamp()

def stamp():
    for dst, ver, name, headline in ((BP_DST, BP_VER, "AbsolutRealism Tectonic BP v{v}",
        "FURNITURE round 2 (witness 19:46) — mantel board down 3 cubes (top 5) on 2x2 corbels; wall shelf down to top 8; every same-plane face pair removed "
        "(table rails between the legs, trestle legs half-lapped, barrel bands stepped 0.1, shelf/cupboard/dresser backs between their boards; "
        "gate tools/coplanar_audit.py = 0); render_method alpha_test_single_sided (alpha_test disabled backface culling). Round 1: 36 blocks pw:furn_<piece>_<wood> (table, bench, stool, chair, shelf, wall shelf, cupboard, dresser, trestle, barrel seat, coat pegs, mantel x oak/spruce/dark oak): "
        "front faces the placer; collision bench 8 / stool+barrel 10 / chair 12 / table+trestle 14 / storage 16, wall pieces none; SEATS are sittable (pw:seat custom component -> invisible "
        "rideable pw:seat entity, sneak to stand, riderless seats swept every second); TABLES auto-join (world-aligned pw:n/e/s/w -> 16 geometries: joined sides drop the apron rail and "
        "the shared corner legs). scripts/pw_furniture.js. Requires RP-04 v1.3.138 (geometry, iron stem, client entity). Chair tuck = crouch-interact is backlog."),
        (RP_DST, RP_VER, "AbsolutRealism Basic RP v{v}",
        "FURNITURE round 2 (witness 19:46: mantel lowered + 2x2 corbels, wall shelf lowered, zero same-plane face pairs) — round 1: models/blocks/pw_furniture.geo.json (11 pieces + 16 table join variants, box-projected uv inside the tile, tall boxes split at y=16), "
        "pw_furn_iron (wrought iron authored from the Patrix anvil's forged-iron band, + MER/texture set), keys pw_furn_iron / pw_mat_stripped_dark_oak(_top), client entity pw:seat "
        "(empty geometry), 38 lang names. Everything else byte-identical to v1.3.136. Pair with BP-02 v1.3.184 + RP-02 v2.0.4.")):
        man = jload(dst / "manifest.json"); man["header"]["name"] = name.format(v=ver); man["header"]["version"] = [int(x) for x in ver.split(".")]
        for mod in man["modules"]: mod["version"] = [int(x) for x in ver.split(".")]
        man["header"]["description"] = f"v{ver} ({DATE}) {headline}"; jdump(man, dst / "manifest.json")
    ledr = RP_DST / "PW-DEPENDENCIES.md"
    if ledr.exists():
        t2 = ledr.read_text(encoding="utf-8").replace("v1.3.136 ·", f"v{RP_VER} ·", 1); ledr.write_text(t2, encoding="utf-8")
    log(f"manifests stamped: BP-02 {BP_VER}, RP-04 {RP_VER}" + (f", Markers {MK_VER}" if BUILD_MARKERS else " (Markers unchanged)"))

if __name__ == "__main__":
    main()
