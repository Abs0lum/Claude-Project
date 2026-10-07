#!/usr/bin/env python3
"""flatten_sweep.py — D-C515 retro-sweep (10-03): every "minecraft:…" string literal in our install-set SCRIPTS checked against the
engine's own registries (BDS 1.26.52 dump: _bds/logs/civtest-<stamp>.json from _build/registrydump-0.0.1).
A literal that is no block, item, entity or dimension id is either a non-registry name (component, state, particle, biome, event …)
or a STALE id that code still compares typeIds against (the light_block -> light_block_N class). Silent in the content log.
Usage: flatten_sweep.py REGISTRY_JSON DIR [DIR ...]   -> prints the residue with file:line, writes _docs/recheck/W2-FLATTEN-SWEEP.json"""
import json, re, sys
from collections import defaultdict
from pathlib import Path

reg_path, dirs = Path(sys.argv[1]), [Path(d) for d in sys.argv[2:]]
reg = defaultdict(set)
for r in json.loads(reg_path.read_text())["records"]:
    if r.get("step") == "ids":
        reg[r["kind"]].update(r["ids"])
known = {k: v for k, v in reg.items()}
lit_re = re.compile(r"""["'`](minecraft:[a-z0-9_.:]+)["'`]""")
# non-registry names that are legitimately namespaced (components, states, events, particles …) — matched by shape, listed in the report
NONREG = re.compile(r"^minecraft:(?:[a-z_]+_particle|[a-z_]*particle[a-z_]*|cardinal_direction|block_face|vertical_half|facing_direction|"
                    r"[a-z_]+_component|equippable|rideable|inventory|breathable|durability|health|movement|tameable|leashable|"
                    r"projectile|is_baby|color|variant|mark_variant|skin_id|scale|cooldown|food|enchantable|potion|"
                    r"entity_spawned|entity_born|entity_transformed|on_[a-z_]+|[a-z_]+_event)$")
hits, residue = defaultdict(list), defaultdict(list)
for d in dirs:
    for f in sorted(d.rglob("*.js")):
        if "ledgerprobe" in str(f):
            continue
        for n, line in enumerate(f.read_text(errors="ignore").splitlines(), 1):
            for m in lit_re.finditer(line):
                lit = m.group(1)
                kind = next((k for k in ("block", "item", "entity", "dimension") if lit in known.get(k, set())), None)
                where = f"{f}:{n}"
                if kind:
                    hits[kind].append(lit)
                elif NONREG.match(lit):
                    hits["nonregistry-shape"].append(lit)
                else:
                    residue[lit].append((where, line.strip()[:170]))
out = {"registry": {k: len(v) for k, v in known.items()}, "counts": {k: len(v) for k, v in hits.items()},
       "residue": {k: v for k, v in sorted(residue.items())}}
Path("_docs/recheck/W2-FLATTEN-SWEEP.json").write_text(json.dumps(out, indent=1))
print("registry sizes", out["registry"])
print("literal hits", out["counts"], "· residue (not in any registry):", len(residue), "distinct")
for lit, uses in sorted(residue.items()):
    print(f"\n{lit}  ({len(uses)} use(s))")
    for w, l in uses[:4]:
        print("   ", w.replace("/home/claude/_build/", ""), "|", l)
