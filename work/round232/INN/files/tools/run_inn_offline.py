#!/usr/bin/env python3
"""run_inn_offline.py — 1.3.232 (#INN): run tools/inn_v2.py OFFLINE (this repo session has no /home/claude tree).

inn_v2.py and its imports hard-code the cloud workspace paths (/home/claude/_staging/..., /home/claude/tools/...). This
runner imports the copies in TOOLS_DIR and re-points only the module globals that hold paths, then calls inn_v2.main():
  civgen.TEMPLATES    the engine entity probe (tools/civ_templates/engine_entities_probe.nbt) is NOT in the mirror.
                      civgen only reads it to deep-copy one pw:marker and one pw:hatch_lid compound and then overwrites
                      Pos / UniqueID / Tags / definitions / properties on every copy. Any structure that holds both entity
                      kinds as civgen wrote them serves: the 1.3.230 inn (mvv_inn_a_r1.mcstructure, cloned from that probe).
                      Proof: the UNMODIFIED round-231 inn_v2.py run this way reproduces the 4 shipped 231 table entries
                      byte for byte (all 11 fields).
  civ_roster.OUT      unused by inn_v2 (kept inside STAGE_ROOT so nothing writes outside it).
  inn_v2.STAGE_ROOT / BP / CIV   the outputs (inn_v2.main re-points civ_village_data and weather_overlays from these).
--sewer-port (TOOLS_DIR must hold build_bp02_219.py): afterwards apply the 1.3.219 law to every written template and stage
  ("the shaft's street-side opening reaches down to the gallery floor (local x0, y3-y4 opened) in every template and
  stage"; build_bp02_219.fix_structure, which also hinges double doors). Every 1.3.230 building file carries it; round
  231 copied the inn v2 files from staging without it (build_round_231.py l.333-336 'put' only).
Usage: python3 run_inn_offline.py TOOLS_DIR STAGE_ROOT TEMPLATE_MCSTRUCTURE [--sewer-port]"""
import sys
from pathlib import Path

tools_dir, stage_root, template = (Path(a).resolve() for a in sys.argv[1:4])
sys.path.insert(0, str(tools_dir))
import civgen as G          # noqa: E402
G.TEMPLATES = template
import civ_roster as R      # noqa: E402
R.OUT = stage_root / "civ"
import inn_v2 as I          # noqa: E402
I.STAGE_ROOT = stage_root
I.BP = stage_root / "BP-02/structures/pw"
I.CIV = stage_root / "civ_inn"
I.main()

if "--sewer-port" in sys.argv[4:]:
    import build_bp02_219 as B219   # noqa: E402  (module level holds only path constants; nothing runs on import)
    report = {"files": 0, "door_cells": 0, "port_cells": 0}
    for tpl in sorted(I.BP.glob("mvv_inn_*.mcstructure")):
        shaft = B219.shaft_of(tpl)
        files = [tpl] + [I.BP / "stages" / f"{tpl.stem}_s{k}.mcstructure" for k in range(5)]
        for p in files:
            if B219.fix_structure(p, report, shaft):
                report["files"] += 1
        print(f"sewer port {tpl.stem}: shaft z {shaft}")
    print("1.3.219 law applied:", report)
