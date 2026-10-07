"""Print floor plans (seen from above) of the CIVITAS starter cottages, built IN MEMORY by the repo's own generators
(knowledge/tools/civgen.py + civ_roster.py; read-only; markers/hatches stubbed: they need the cloud template file).
x = depth from the street (row 0 = the front wall, the door), z = frontage (column 0 = the clearance column)."""
import sys
sys.path.insert(0, "/home/user/Claude-Project/knowledge/tools")
import civgen as G  # noqa: E402
G._entity_templates = lambda: (None, None)
G.Building.marker = lambda self, *a, **k: None
G.Building.zone = lambda self, *a, **k: None
G.Building.hatch = lambda self, *a, **k: None
import civ_roster as R  # noqa: E402

SYM = {"minecraft:air": ".", "minecraft:bed": "B", "minecraft:ladder": "H", "minecraft:chest": "c", "minecraft:barrel": "c",
       "minecraft:light_block_14": ".", "minecraft:glass_pane": "w", "minecraft:spruce_log": "#", "minecraft:oak_planks": "#",
       "minecraft:oak_fence": "f", "minecraft:wooden_door": "D", "minecraft:spruce_door": "D"}


def sym(n):
    if n is None:
        return " "
    if n in SYM:
        return SYM[n]
    if "roof" in n:
        return "^"
    if "furn" in n or "hearth" in n or "flue" in n or "mantel" in n:
        return "f"
    return "#"


def plan(b, feet, extra=()):
    X, W = b.size[0], b.size[2]
    rows = []
    for x in range(X):
        rows.append("".join(sym(b.get(x, feet, z)) for z in range(W)))
    return rows


def show(b, feets):
    print(b.name, "size", b.size)
    cols = [plan(b, f) for f in feets]
    print("   " + "   ".join(f"feet {f:<2}".ljust(len(cols[0][0])) for f in feets))
    for i in range(len(cols[0])):
        print(f"x{i:<2}" + "   ".join(c[i].ljust(max(7, len(c[i]))) for c in cols))
    print()


if __name__ == "__main__":
    for b in (G.cottage(), R.cottage_m(), R.cottage_l()):
        show(b, [0, 1, 3, 4, 5, 6])
