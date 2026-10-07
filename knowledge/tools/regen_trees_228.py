#!/usr/bin/env python3
"""regen_trees_228.py — program 228 TREES: regenerate all 544 tree templates through the build pipeline and install only
the ones that change into the BP-02 1.3.228 overlay (tools/bp02_overlay_228/structures/pw/trees/).

Changes (Abs0lum's rulings 2026-10-06, _docs/program228/DECISIONS-2026-10-06.md):
  * v4 trunk-tip rule (tree_gen.sink_tip / tree_gen_square.sink_stem) for every group in TREE-TRUNK-PLAN.md §3;
    STAG_OVER_CROWN = False (oak elder + pale oak stag limbs removed); applied to pale oak; oak old stag head removed.
  * F5 (STRUCTURE-AUDIT §5): tree_rescale no longer copies the root block up a stretched trunk (jungle_young evens).
Pipeline (TREE-TRUNK-PLAN §7): birch = tree_gen.build() written directly (as build 224); every other group =
build() -> tree_rescale.rescale(src, dst, frame=<the template's build-218 frame>) with the frames read from the FROZEN copy
_docs/trees/rescale_frames_218.json. Never calls tree_gen.main / tree_rescale.main (they write _staging / outputs / the report).

Usage:
  regen_trees_228.py OUT_DIR                 regenerate with the current tools/ generators
  regen_trees_228.py OUT_DIR --baseline DIR  regenerate with the generators in DIR (no frames: the pre-228 pipeline)
Writes OUT_DIR/<stem>.mcstructure (544) and OUT_DIR/../<basename>_stage/ (the un-rescaled builds; removed at the end)."""
import importlib.util
import json
import shutil
import sys
from pathlib import Path

TOOLS = Path("/home/claude/tools")
FRAMES = Path("/home/claude/_docs/trees/rescale_frames_218.json")


def load(gen_dir):
    """import tree_gen, tree_gen_square, tree_rescale from gen_dir under their real names (tree_gen_square's
    `import tree_gen as T` then resolves to the same module)."""
    sys.path.insert(0, str(TOOLS))                      # mcstructure
    mods = []
    for name in ("tree_gen", "tree_gen_square", "tree_rescale"):
        spec = importlib.util.spec_from_file_location(name, Path(gen_dir) / f"{name}.py")
        m = importlib.util.module_from_spec(spec)
        sys.modules[name] = m
        spec.loader.exec_module(m)
        mods.append(m)
    return mods


def main():
    out = Path(sys.argv[1])
    base = sys.argv[sys.argv.index("--baseline") + 1] if "--baseline" in sys.argv else None
    TG, TS, TR = load(base or TOOLS)
    frames = None if base else {r["template"]: r["before"] for r in json.loads(FRAMES.read_text())}
    if out.exists():
        raise SystemExit(f"{out} exists")
    stage = out.parent / f"{out.name}_stage"
    out.mkdir(parents=True)
    stage.mkdir(parents=True)
    n = 0
    for age in ("young", "mature", "old"):              # birch: direct (build 224)
        for idx in range(TG.PER_AGE):
            st = TG.build("birch", age, idx)[0]
            (out / f"birch_{age}_{idx:02d}.mcstructure").write_bytes(st.to_bytes())
            n += 1
    jobs = []
    for sp in ("oak", "spruce", "jungle"):
        for age in ("young", "mature", "old"):
            for idx in range(TG.PER_AGE):
                stem = f"{sp}_{age}_{idx:02d}"
                (stage / f"{stem}.mcstructure").write_bytes(TG.build(sp, age, idx)[0].to_bytes())
                jobs.append(stem)
    for sp in TS.SPEC:
        for idx in range(TS.PER):
            stem = f"{sp}_{idx:02d}"
            (stage / f"{stem}.mcstructure").write_bytes(TS.build(sp, idx)[0].to_bytes())
            jobs.append(stem)
    for stem in jobs:
        src = stage / f"{stem}.mcstructure"
        if frames is None:
            TR.rescale(src, out / src.name)
        else:
            TR.rescale(src, out / src.name, frame=frames[stem])
        n += 1
    shutil.rmtree(stage)
    print(f"regenerated {n} templates -> {out} ({'baseline ' + base if base else 'current generators, frames 218'})")


if __name__ == "__main__":
    main()
