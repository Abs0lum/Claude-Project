#!/usr/bin/env python3
"""build_markers_020.py — PW-Civitas Markers BP/RP v0.2.0 (Abs0lum 2026-09-22 20:24: "Yes, approve all").

PROPOSAL Z: every marker (12 zones, 18 stations, 4 ports, the datum) becomes the ENTITY pw:marker, so it shares a cell
with any block. The old marker blocks stay registered (old saves load; /scriptevent civ:markers migrate converts them).
PROPOSAL H probe: pw:hatch_lid — a collidable entity lid over a vanilla ladder (happy-ghast adult_immobile pattern).

Source of truth for the behaviour: tools/markers_src/pw_markers.js (copied verbatim into the BP).
Schemas checked against bedrock-samples 1.26.50 (happy_ghast / armor_stand / creaking / bee / shulker) and the
@minecraft/server 2.0.0 typings (D-C227)."""
import json, re, shutil, datetime
from pathlib import Path
from PIL import Image

ROOT = Path("/home/claude"); SRC, DST = ROOT / "_build/markers-0.1.9", ROOT / "_build/markers-0.2.1"
VER = "0.2.1"; VV = [0, 2, 1]; DATE = "2026-09-22"   # 0.2.0 withdrawn before install: its 0.4x0.5 collision box could block furniture placement in a marked cell
JS_SRC = ROOT / "tools/markers_src/pw_markers.js"
TRAPDOOR = ROOT / "_build/rp03-59/textures/blocks/trapdoor.png"      # Patrix oak trapdoor (P11 census: only RP-03 carries it)

def log(m):
    print(m); open(ROOT / "_logs/phase_log.md", "a").write(f"[{datetime.datetime.now().strftime('%H:%M')} CT 09-22] BUILD MARKERS {VER} — {m}\n")
def jdump(o, p): p = Path(p); p.parent.mkdir(parents=True, exist_ok=True); p.write_text(json.dumps(o, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
def jload(p): return json.loads(Path(p).read_text(encoding="utf-8-sig"))

# the frozen icon table — MUST equal pw_markers.js (the gate compares them)
ZONES = ["threshold", "stable", "cellar", "storeroom", "kitchen", "quarters", "chamber", "workfloor", "shopfloor", "yard", "garden", "commons"]
STATIONS = ["anvil", "bed", "bench", "counter", "desk", "door", "field", "hearth", "oven", "pen", "post", "prep", "rack", "seat", "stall", "store", "table", "yard"]
PORTS = ["passage", "sewer", "stair", "well"]
ICONS = [("zone", k) for k in ZONES] + [("station", k) for k in STATIONS] + [("port", k) for k in PORTS] + [("datum", "datum")]
def stem(fam, kind): return "pw_datum" if fam == "datum" else f"pw_{fam}_{kind}"

INERT = {   # shared by both entities: no AI, no gravity, no physics push, cannot be hurt, never despawns
    "minecraft:physics": {"has_gravity": False, "has_collision": False},
    "minecraft:pushable": {"is_pushable": False, "is_pushable_by_piston": False},
    "minecraft:knockback_resistance": {"value": 1.0},
    "minecraft:damage_sensor": {"triggers": [{"cause": "all", "deals_damage": "no"}]},
    "minecraft:health": {"value": 1, "max": 1},
    "minecraft:persistent": {},
    "minecraft:fire_immune": {},
    "minecraft:breathable": {"breathes_air": True, "breathes_water": True, "breathes_lava": True, "breathes_solids": True},
    "minecraft:body_rotation_blocked": {},
    "minecraft:conditional_bandwidth_optimization": {},
}

def marker_bp():
    return {"format_version": "1.21.80", "minecraft:entity": {
        "description": {"identifier": "pw:marker", "is_spawnable": False, "is_summonable": True, "is_experimental": False,
            "properties": {
                "pw:fam": {"type": "int", "range": [0, 3], "default": 0, "client_sync": True},
                "pw:icon": {"type": "int", "range": [0, 63], "default": 0, "client_sync": True},
                "pw:n": {"type": "int", "range": [0, 63], "default": 0, "client_sync": True},
                "pw:vis": {"type": "bool", "default": True, "client_sync": True}}},
        # COLLISION box 0 x 0 on the cell floor plane: it can never overlap a block's volume, so it never refuses a block placement
        # (a mob-sized box would stop a chair going into a marked cell). HIT box separately (custom_hit_test, hoglin pattern),
        # present only while markers are shown, so hidden markers catch no tap at all.
        "component_groups": {"pw:hittable": {"minecraft:custom_hit_test": {"hitboxes": [{"width": 0.4, "height": 0.5, "pivot": [0, 0.25, 0]}]}}},
        "components": {"minecraft:type_family": {"family": ["pw_marker", "inanimate"]},
                       "minecraft:collision_box": {"width": 0.0, "height": 0.0}, **INERT},
        "events": {
            "minecraft:entity_spawned": {"add": {"component_groups": ["pw:hittable"]}},
            "pw:hide": {"remove": {"component_groups": ["pw:hittable"]}, "set_property": {"pw:vis": False}},
            "pw:show": {"add": {"component_groups": ["pw:hittable"]}, "set_property": {"pw:vis": True}}}}}

def lid_bp():
    closed = {"add": {"component_groups": ["pw:lid_closed"]}, "remove": {"component_groups": ["pw:lid_open"]}, "set_property": {"pw:open": False}}
    opened = {"add": {"component_groups": ["pw:lid_open"]}, "remove": {"component_groups": ["pw:lid_closed"]}, "set_property": {"pw:open": True}}
    return {"format_version": "1.21.80", "minecraft:entity": {
        "description": {"identifier": "pw:hatch_lid", "is_spawnable": False, "is_summonable": True, "is_experimental": False,
            "properties": {
                "pw:open": {"type": "bool", "default": False, "client_sync": True},
                "pw:hinge": {"type": "int", "range": [0, 3], "default": 0, "client_sync": True}}},
        "component_groups": {
            "pw:lid_closed": {"minecraft:is_collidable": {}},                       # walk on it; bump your head on it from the ladder
            "pw:lid_open": {"minecraft:type_family": {"family": ["pw_hatch", "pw_hatch_open", "inanimate"]}}},
        "components": {
            "minecraft:type_family": {"family": ["pw_hatch", "inanimate"]},
            "minecraft:collision_box": {"width": 1.0, "height": 0.1875},          # the whole cell, 3 cubes thick, top flush with the floor above
            **INERT,
            "minecraft:interact": {"interactions": [{
                "on_interact": {"filters": {"test": "is_family", "subject": "other", "value": "player"}, "event": "pw:toggle", "target": "self"},
                "interact_text": "action.interact.pw_hatch", "swing": True}]}},
        "events": {
            "minecraft:entity_spawned": {"add": {"component_groups": ["pw:lid_closed"]}},
            "pw:toggle": {"first_valid": [
                {"filters": {"test": "bool_property", "domain": "pw:open", "operator": "!="}, **opened},
                closed]},
            "pw:open": opened, "pw:close": closed}}}

def item_bp():
    return {"format_version": "1.21.80", "minecraft:item": {
        "description": {"identifier": "pw:hatch_lid", "menu_category": {"category": "construction"}},
        "components": {"minecraft:icon": {"textures": {"default": "pw_hatch_lid"}}, "minecraft:max_stack_size": 16,
                       "minecraft:display_name": {"value": "item.pw:hatch_lid.name"}}}}

def face(uv, size): return {"uv": list(uv), "uv_size": list(size)}
def cube(o, s, faces): return {"origin": list(o), "size": list(s), "uv": faces}
def all6(w, h, d):
    return {"north": face((0, 0), (16, 16)), "south": face((0, 0), (16, 16)), "east": face((0, 0), (16, 16)), "west": face((0, 0), (16, 16)),
            "up": face((0, 0), (16, 16)), "down": face((0, 0), (16, 16))}

def geometry_rp():
    full = face((0, 0), (16, 16))
    marker = {"description": {"identifier": "geometry.pw_marker_entity", "texture_width": 16, "texture_height": 16,
                              "visible_bounds_width": 1, "visible_bounds_height": 1, "visible_bounds_offset": [0, 0.25, 0]},
              "bones": [
                  # zone corner: kind icon on top/bottom, corner number on the four sides (two bones, disjoint faces)
                  {"name": "zone_top", "pivot": [0, 0, 0], "cubes": [cube((-3, 0, -3), (6, 6, 6), {"up": full, "down": full})]},
                  {"name": "zone_sides", "pivot": [0, 0, 0], "cubes": [cube((-3, 0, -3), (6, 6, 6), {"north": full, "south": full, "east": full, "west": full})]},
                  {"name": "station", "pivot": [0, 0, 0], "cubes": [cube((-2, 4, -2), (4, 4, 4), all6(4, 4, 4))]},
                  {"name": "port", "pivot": [0, 0, 0], "cubes": [cube((-3, 0, -3), (6, 6, 6), all6(6, 6, 6))]}]}
    plate_top = {"up": full, "down": full, "north": face((0, 0), (16, 3)), "south": face((0, 0), (16, 3)), "east": face((0, 0), (16, 3)), "west": face((0, 0), (16, 3))}
    leaf_z = {"north": full, "south": full, "up": face((0, 0), (16, 3)), "down": face((0, 0), (16, 3)), "east": face((0, 0), (3, 16)), "west": face((0, 0), (3, 16))}
    leaf_x = {"east": full, "west": full, "up": face((0, 0), (3, 16)), "down": face((0, 0), (3, 16)), "north": face((0, 0), (3, 16)), "south": face((0, 0), (3, 16))}
    # entity origin = ladder cell centre, y + 0.8125 (13 cubes up): the closed plate is y 0..3, an open leaf spans the cell, y -13..3.
    # Bones are named by MODEL side; model space is left-handed (+x = the entity's left) and yaw 0 faces south, so model
    # +z = world north, +x = world east (D-C227 correction). The render controller maps the WORLD hinge to these bones.
    lid = {"description": {"identifier": "geometry.pw_hatch_lid", "texture_width": 16, "texture_height": 16,
                           "visible_bounds_width": 2, "visible_bounds_height": 2, "visible_bounds_offset": [0, 0, 0]},
           "bones": [
               {"name": "closed", "pivot": [0, 0, 0], "cubes": [cube((-8, 0, -8), (16, 3, 16), plate_top)]},
               {"name": "leaf_pz", "pivot": [0, 0, 0], "cubes": [cube((-8, -13, 5), (16, 16, 3), leaf_z)]},
               {"name": "leaf_px", "pivot": [0, 0, 0], "cubes": [cube((5, -13, -8), (3, 16, 16), leaf_x)]},
               {"name": "leaf_nz", "pivot": [0, 0, 0], "cubes": [cube((-8, -13, -8), (16, 16, 3), leaf_z)]},
               {"name": "leaf_nx", "pivot": [0, 0, 0], "cubes": [cube((-8, -13, -8), (3, 16, 16), leaf_x)]}]}
    return {"format_version": "1.12.0", "minecraft:geometry": [marker, lid]}

HINGE_BONE = {0: "leaf_pz", 1: "leaf_px", 2: "leaf_nz", 3: "leaf_nx"}   # world N/E/S/W -> model bone (left-handed model space)

def render_rp():
    vis = "query.property('pw:vis')"
    return {"format_version": "1.10.0", "render_controllers": {
        "controller.render.pw_marker_icon": {
            "arrays": {"textures": {"Array.icons": [f"Texture.icon_{i}" for i in range(len(ICONS))]}},
            "geometry": "Geometry.default", "materials": [{"*": "Material.default"}], "ignore_lighting": True,
            "textures": ["Array.icons[query.property('pw:icon')]"],
            "part_visibility": [{"*": False},
                                {"zone_top": f"{vis} && query.property('pw:fam') == 0"},
                                {"station": f"{vis} && query.property('pw:fam') == 1"},
                                {"port": f"{vis} && query.property('pw:fam') >= 2"}]},
        "controller.render.pw_marker_num": {
            "arrays": {"textures": {"Array.nums": [f"Texture.num_{i}" for i in range(64)]}},
            "geometry": "Geometry.default", "materials": [{"*": "Material.default"}], "ignore_lighting": True,
            "textures": ["Array.nums[query.property('pw:n')]"],
            "part_visibility": [{"*": False}, {"zone_sides": f"{vis} && query.property('pw:fam') == 0"}]},
        "controller.render.pw_hatch_lid": {
            "geometry": "Geometry.default", "materials": [{"*": "Material.default"}], "textures": ["Texture.default"],
            "part_visibility": [{"*": False}, {"closed": "!query.property('pw:open')"}] +
                               [{bone: f"query.property('pw:open') && query.property('pw:hinge') == {h}"} for h, bone in HINGE_BONE.items()]}}}

def marker_client():
    tex = {f"icon_{i}": f"textures/blocks/{stem(f, k)}" for i, (f, k) in enumerate(ICONS)}
    tex.update({f"num_{i}": f"textures/blocks/pw_num_{i}" for i in range(64)})
    return {"format_version": "1.10.0", "minecraft:client_entity": {"description": {
        "identifier": "pw:marker", "materials": {"default": "entity_alphatest"}, "textures": tex,
        "geometry": {"default": "geometry.pw_marker_entity"},
        "render_controllers": ["controller.render.pw_marker_icon", "controller.render.pw_marker_num"]}}}

def lid_client():
    return {"format_version": "1.10.0", "minecraft:client_entity": {"description": {
        "identifier": "pw:hatch_lid", "materials": {"default": "entity_alphatest"}, "textures": {"default": "textures/entity/pw_hatch_lid"},
        "geometry": {"default": "geometry.pw_hatch_lid"}, "render_controllers": ["controller.render.pw_hatch_lid"]}}}

NAMES = {"zone": "Zone", "station": "Station", "port": "Port"}
def lang_lines():
    out = [f"tile.{('pw:datum' if f == 'datum' else f'pw:{f}_{k}')}.name=" + ("Datum (entrance marker)" if f == "datum" else f"{NAMES[f]}: {k.replace('_', ' ').title()}") for f, k in ICONS]
    out += ["item.pw:hatch_lid.name=Ladder Hatch (use on the top ladder)", "action.interact.pw_hatch=Open / Close",
            "entity.pw:marker.name=Marker", "entity.pw:hatch_lid.name=Ladder Hatch"]
    return out

def main():
    if DST.exists(): shutil.rmtree(DST)
    shutil.copytree(SRC, DST)
    BP, RP = DST / "BP", DST / "RP"
    # ---------------- BP
    (BP / "scripts/pw_markers.js").write_text(JS_SRC.read_text(encoding="utf-8"), encoding="utf-8")
    m = (BP / "scripts/main.js").read_text(encoding="utf-8")
    start = m.index("// PW-Civitas Markers v0.1.0 — zone listener")
    end = m.index("// ---------- THE HATCH (HATCH LAW)")
    header = ('import "./pw_markers.js"; // v0.2.1: zones / stations / ports / datum are ENTITIES (pw:marker) + the ladder hatch lid\n'
              '// v0.2.1: the v0.1.x block listeners for zone corners and station indices moved into pw_markers.js (entity markers);\n'
              '// civ:zone close|status and civ:station reset keep working there. The manhole hatch and the frame posts below are unchanged.\n')
    m = m[:start] + header + m[end:]
    assert "playerPlaceBlock.subscribe((ev) => {\n  try {\n    const id = ev.block.typeId; if (!id.startsWith(\"pw:zone_\"))" not in m
    (BP / "scripts/main.js").write_text(m, encoding="utf-8")
    jdump(marker_bp(), BP / "entities/pw_marker.json"); jdump(lid_bp(), BP / "entities/pw_hatch_lid.json"); jdump(item_bp(), BP / "items/pw_hatch_lid.json")
    log("BP: scripts/pw_markers.js (+ main.js import; v0.1.x zone/station block listeners removed), entities pw:marker + pw:hatch_lid, item pw:hatch_lid")
    # ---------------- RP
    jdump(marker_client(), RP / "entity/pw_marker.entity.json"); jdump(lid_client(), RP / "entity/pw_hatch_lid.entity.json")
    jdump(geometry_rp(), RP / "models/entity/pw_markers.geo.json"); jdump(render_rp(), RP / "render_controllers/pw_markers.render.json")
    td = Image.open(TRAPDOOR).convert("RGBA")
    (RP / "textures/entity").mkdir(parents=True, exist_ok=True); (RP / "textures/items").mkdir(parents=True, exist_ok=True)
    td.save(RP / "textures/entity/pw_hatch_lid.png")
    td.resize((32, 32), Image.LANCZOS).save(RP / "textures/items/pw_hatch_lid.png")
    jdump({"resource_pack_name": "pw_civitas_markers", "texture_name": "atlas.items", "texture_data": {"pw_hatch_lid": {"textures": "textures/items/pw_hatch_lid"}}}, RP / "textures/item_texture.json")
    (RP / "texts").mkdir(exist_ok=True)
    (RP / "texts/en_US.lang").write_text("\n".join(lang_lines()) + "\n", encoding="utf-8")
    jdump(["en_US"], RP / "texts/languages.json")
    log(f"RP: client entities pw:marker ({len(ICONS)} icons + 64 numbers, 2 controllers, ignore_lighting) + pw:hatch_lid, geometry.pw_marker_entity + geometry.pw_hatch_lid, lid texture = RP-03 Patrix trapdoor (+ 32px item icon), item_texture, en_US.lang ({len(lang_lines())} lines)")
    # ---------------- manifests + ledgers
    for sub, name, pair in (("BP", "PW Civitas Markers BP", "RP"), ("RP", "PW Civitas Markers RP", "BP")):
        man = jload(DST / sub / "manifest.json"); man["header"]["name"] = f"{name} v{VER}"; man["header"]["version"] = VV
        for mod in man["modules"]: mod["version"] = VV
        man["header"]["description"] = (f"v{VER} ({DATE}) MARKERS ARE ENTITIES (Abs0lum 20:24 'approve all'): zone corners, stations, ports and the datum are the entity "
            "pw:marker, so they share a cell with furniture, beds, doors (collision box 0 x 0 on the floor plane: a marker never refuses a block placement; hit box only while shown). Same items; tap = the cell in front of the face, SNEAK-tap = the tapped block's own cell; "
            "numbering unchanged; /scriptevent civ:markers hide|show|migrate|list|check|remove; old marker blocks convert with 'migrate'. "
            "+ LADDER HATCH probe: item pw:hatch_lid on the top ladder of an opening -> a collidable lid (walk on it closed, tap to open; hinge opposite the ladder). "
            f"Structures must now be saved with Include Entities ON. Manhole hatch + frame posts unchanged. Pairs with {pair} v{VER}.")
        jdump(man, DST / sub / "manifest.json")
    lb = BP / "PW-DEPENDENCIES.md"
    lb.write_text(f"# PW-DEPENDENCIES — PW-Civitas-Markers-BP\n\nv{VER} · needs: entity client files pw:marker / pw:hatch_lid, geometry.pw_marker_entity / pw_hatch_lid, "
                  "controllers pw_marker_icon / pw_marker_num / pw_hatch_lid, item icon pw_hatch_lid, geometry.pw_marker_station/zone, pw_frame_post_0/_n, "
                  "keys pw_station_* (18 incl. seat), pw_zone_*, pw_num_0..63, pw_frame_wood -> PW Civitas Markers RP · needs-hash `civ0200`\n", encoding="utf-8")
    lr = RP / "PW-DEPENDENCIES.md"
    lr.write_text(f"# PW-DEPENDENCIES — PW-Civitas-Markers-RP\n\nv{VER} · provider-only (lid texture copied from RP-03 textures/blocks/trapdoor.png, Patrix) · needs-hash `e3b0c44298fc1c14`\n", encoding="utf-8")
    log(f"manifests + ledgers v{VER}")

if __name__ == "__main__":
    main()
