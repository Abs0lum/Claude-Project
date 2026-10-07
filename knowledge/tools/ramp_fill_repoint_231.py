"""Repoint every material_instances.fill (base + permutations) of the pw_ramp_* blocks
to the same component set's '*' texture. Deterministic; JSON otherwise unchanged.

Usage: python3 ramp_fill_repoint_231.py <src_blocks_dir> <out_dir>
"""
import json
import os
import sys


def repoint(components):
    """Return number of fill slots changed in one components dict."""
    mats = components.get("minecraft:material_instances")
    if not mats or "fill" not in mats:
        return 0
    star = mats.get("*", {}).get("texture")
    if star is None:
        raise ValueError("fill without '*' texture")
    if mats["fill"].get("texture") == star:
        return 0
    mats["fill"]["texture"] = star
    return 1


def main(src, out):
    os.makedirs(out, exist_ok=True)
    total_files = total_slots = 0
    for name in sorted(os.listdir(src)):
        if not (name.startswith("pw_ramp_") and name.endswith(".json")):
            continue
        raw = open(os.path.join(src, name), encoding="utf-8").read()
        doc = json.loads(raw)
        block = doc["minecraft:block"]
        changed = repoint(block["components"])
        for perm in block.get("permutations", []):
            changed += repoint(perm.get("components", {}))
        indent = 2 if raw.startswith("{\n  \"") else (4 if raw.startswith("{\n    \"") else None)
        with open(os.path.join(out, name), "w", encoding="utf-8") as fh:
            json.dump(doc, fh, indent=indent, ensure_ascii=False)
            if raw.endswith("\n"):
                fh.write("\n")
        total_files += 1
        total_slots += changed
    print(f"files={total_files} fill_slots_repointed={total_slots}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
