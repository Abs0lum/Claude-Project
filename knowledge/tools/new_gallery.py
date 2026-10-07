#!/usr/bin/env python3
"""new_gallery.py — D-C351: one tile per staged NEW creature (rest pose, default skin, 3/4 view) -> _docs/menagerie/new/<id>.png + a manifest."""
import json, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, "/home/claude/tools")
import menagerie_sheets as M
from bb_truth import truth_posed_faces
from equine_compare import bone_affines
from entity_tex_render import render_entity
from convb_preview3 import camera, FOV
R = Path("/home/claude/_build/menagerie-stage/RP"); OUT = Path("/home/claude/_docs/menagerie/new"); OUT.mkdir(parents=True, exist_ok=True)
rep = json.loads(Path("/home/claude/_build/menagerie-stage/PORT-REPORT.json").read_text())
cen = json.loads(Path("/home/claude/_logs/menagerie_census.json").read_text())
grp = {c["id"]: g for g, r in cen["new"].items() for c in r["candidates"]}
p = M.Pack([R]); man = []; fails = []
FB = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 13)
for c in rep["creatures"]:
    new = c["new"]
    try:
        m, why = p.model(new)
        if m is None: fails.append((new, why)); continue
        bones = [dict(b) for b in m[1]]; seen = set()
        for b in bones:
            if b.get("name") in seen: b["name"] += "_dup"
            seen.add(b.get("name"))
        import io
        tp = Path("/tmp/menag_tex") / (new.replace(":", "_") + ".png"); tp.parent.mkdir(exist_ok=True)
        Image.open(io.BytesIO(m[4])).convert("RGBA").save(tp)
        faces = truth_posed_faces(bones, m[2], m[3], bone_affines(bones))
        e, t = camera(faces, "front-east"); fl = min(0.0, min(q[1] for x in faces for q in x.pts))
        im = render_entity(faces, tp, e, t, 300, 240, fov=FOV, floor_y=fl).convert("RGB")
        d = ImageDraw.Draw(im); d.rectangle([0, 0, 300, 20], fill=(40, 60, 45)); d.text((5, 3), f"{new.split(':')[1]}  ·  {c['src']}", fill=(255, 255, 255), font=FB)
        fn = new.split(":")[1] + ".jpg"; im.save(OUT / fn, quality=82)
        man.append({"id": new, "name": new.split(":")[1].replace("_", " "), "src": c["src"], "group": grp.get(c["old"], ""), "img": f"new/{fn}",
                    "wilds": c["src"] == "JP", "dead": len(c["dead_refs"])})
    except Exception as ex:
        fails.append((new, f"{type(ex).__name__} {str(ex)[:60]}"))
(OUT / "manifest.json").write_text(json.dumps({"tiles": man, "fails": fails}, indent=1))
print(len(man), "tiles;", len(fails), "failed", fails[:6])
