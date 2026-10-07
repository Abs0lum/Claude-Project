#!/usr/bin/env python3
"""std_share.py — Phase 3b: species-correct animation sharing (his A1 + 12:51 rule: "species correct animations stay with
species correct animations … I don't want any species to inherit animations that don't fit the species or animal").

Groups: the SAME real animal built by more than one creator (census species tag; SF / vanilla names resolved by the
ALIAS table below — a generic SF name maps to a species only where it can only mean that animal). Inside a group, each
animation KIND (walk, run, idle, attack, sleep, sit, swim, fly, eat, jump …) has a BEST clip — the richest one (bones
driven × keyframes / Molang channels). The best clip is COPIED to every other member whose standard rig carries ≥ 80 %
of the clip's bones, as an EXTRA animation `animation.std.<slug>.shared_<kind>` (entity short name `shared_<kind>`):
nothing plays it by default — the parade (p21) shows it beside the mob's own clips so HE picks. Cross-species: never
here (candidates are only listed, with the reason, for his approval).
Writes _docs/standard/SHARING-PICKLIST.md + _docs/standard/SHARING.json."""
import copy
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path("/home/claude")
sys.path.insert(0, str(ROOT / "tools"))
import std_convert as S  # noqa: E402
import molang_carry as MC  # noqa: E402

KINDS = [("walk", r"walk|move|locomot|trot"), ("run", r"run|sprint|gallop|charge|flee"), ("idle", r"idle|ambient|base$|look"),
         ("attack", r"attack|bite|strike|punch|swipe|melee"), ("sleep", r"sleep|lay|lie|rest"), ("sit", r"sit"),
         ("swim", r"swim|float|paddle"), ("fly", r"fly|flying|flap|glide|soar|hover"), ("eat", r"eat|graze|peck|drink|feed"),
         ("jump", r"jump|hop|leap"), ("call", r"roar|call|howl|bark|sing|croak")]
# generic SF / vanilla names that can only mean one tagged species (same animal, other creator)
ALIAS = {
    "sf_nba:black_bear": "bear_american_black", "sf_nba:grizzly_bear": "bear_grizzly", "sf_nba:beaver": "beaver",
    "sf_nba:capybara": None, "sf_nba:coyote": "coyote", "sf_nba:elephant": "elephant_african_bush",
    "sf_nba:emperor_penguin": None, "sf_nba:giraffe": "giraffe_reticulated", "sf_nba:gorilla": "gorilla",
    "sf_nba:hyena": "hyena_spotted", "sf_nba:ravenous_hyena": None, "sf_nba:kakapo": "kakapo",
    "sf_nba:komodo_dragon": "komodo_dragon", "sf_nba:male_lion": "lion", "sf_nba:female_lion": "lion_female",
    "sf_nba:ostrich": "ostrich", "sf_nba:orca": "orca", "sf_nba:platypus": "platypus", "sf_nba:raccoon": "raccoon",
    "sf_nba:red_panda": "red_panda", "sf_nba:owl": None, "sf_nba:flamingo": None, "sf_nba:eagle": "bald_eagle",
    "sf_nba:secretary_bird": None, "sf_nba:shoebill": "shoebill", "sf_nba:turkey": "wild_turkey",
    "sf_nba:bluejay": "blue_jay", "sf_nba:mallard": "mallard", "sf_nba:duck": "mallard",
    "sf_nba:great_white_shark": "shark_great_white", "sf_nba:hammer_head_shark": "shark_great_hammerhead",
    "sf_nba:jellyfish": "moon_jellyfish", "sf_nba:tiger": "tiger_bengal", "sf_nba:skunk": "skunk_striped",
    "minecraft:polar_bear": None, "minecraft:panda": None, "minecraft:dolphin": None,
}


def _aliases():
    p = ROOT / "_docs/standard/FIX-HEADS.json"
    if not p.exists():
        return {}
    return {e["entity"]: set(e["renamed"].values()) for e in json.loads(p.read_text())["entities"]}


ALIASES = _aliases()


def kind_of(short):
    s = short.lower()
    for k, rx in KINDS:
        if re.search(rx, s):
            return k
    return None


def richness(a):
    n = 0
    for ch in (a.get("bones") or {}).values():
        for v in ch.values():
            if isinstance(v, dict):
                n += len(v)
            elif isinstance(v, list):
                n += sum(2 if isinstance(x, str) and ("q." in x or "query." in x or "math." in x) else 1 for x in v)
            else:
                n += 2 if isinstance(v, str) else 1
    return n


def staged(mob, rp):
    slug = S.slug_of(mob)
    for d in S.STAGE.iterdir():
        f = d / f"entity/std/{slug}.entity.json"
        if f.exists():
            ent = S.jload(f)
            geo = S.jload(d / f"models/entity/std/{slug}.geo.json")
            an = S.jload(d / f"animations/std/{slug}.animation.json")
            return d, f, ent, geo, an
    return None


def main(write=True):
    census = json.loads((ROOT / "_docs/standard/SKELETON-CENSUS.json").read_text())
    groups = defaultdict(list)
    for c in census:
        if c["body_plan"] == "object":
            continue
        sp = c.get("species") or ALIAS.get(c["id"])
        if sp:
            groups[sp].append(c)
    out_rows, shares = [], []
    for sp, members in sorted(groups.items()):
        rigs = {(m["source"], m["geometry"]) for m in members}
        if len(rigs) < 2:
            continue
        info = {}
        for m in members:
            st = staged(m["id"], m["rp"])
            if not st:
                continue
            d, f, ent, geo, an = st
            desc = ent["minecraft:client_entity"]["description"]
            names = {b["name"] for g in geo["minecraft:geometry"] for b in g["bones"]}
            clips = {}
            for short, aid in (desc.get("animations") or {}).items():
                if aid.startswith("controller.") or aid not in an["animations"] or short.startswith("shared_"):
                    continue
                k = kind_of(short)
                if k:
                    a = an["animations"][aid]
                    if all(all(v in ([0, 0, 0], 0, [0.0, 0.0, 0.0]) for v in ch.values()) for ch in (a.get("bones") or {}).values()):
                        continue   # 15:1x 10-01: an all-zero clip (e.g. a repaired empty one) moves nothing — never a candidate
                    r = richness(a)
                    if k not in clips or r > clips[k][2]:
                        clips[k] = (short, aid, r)
            info[m["id"]] = (d, f, ent, geo, an, names, clips, m["geometry"])
        kinds = sorted({k for v in info.values() for k in v[6]})
        for k in kinds:
            src = max((mid for mid in info if k in info[mid][6]), key=lambda mid: info[mid][6][k][2])
            s_short, s_aid, s_r = info[src][6][k]
            clip = info[src][4]["animations"][s_aid]
            bones = set((clip.get("bones") or {})) - ALIASES.get(src, set())   # 16:0x: a source's restored baby-head names
            #                                                                      (fix_heads) never count against a target
            for tgt, (d, f, ent, geo, an, names, clips, gid) in info.items():
                if tgt == src or gid == info[src][7]:   # same rig: the clips are already the same
                    continue
                cover = len(bones & names) / max(1, len(bones))
                row = {"species": sp, "kind": k, "from": src, "from_clip": s_short, "to": tgt,
                       "to_has_own": clips.get(k, (None,))[0], "bone_cover": round(cover, 2)}
                if cover >= 0.8 and bones:
                    slug = S.slug_of(tgt)
                    new_id = f"animation.std.{slug}.shared_{k}"
                    a2 = copy.deepcopy(clip)
                    a2["bones"] = {b: v for b, v in (a2.get("bones") or {}).items() if b in names}
                    # 15:1x 10-01 (per-entity NWR defect in p21): the clip takes the variables it reads WITH it, renamed per
                    # source so two sources can never collide; a variable nobody can provide refuses the copy
                    src_desc = info[src][2]["minecraft:client_entity"]["description"]
                    tgt_desc = ent["minecraft:client_entity"]["description"]
                    a2, c_init, c_pre, c_missing = MC.carry(a2, src_desc, tgt_desc, f"pwc_{S.slug_of(src)[:24]}_")
                    if c_missing:
                        row["applied"] = False
                        row["refused"] = f"reads {', '.join(c_missing)} — set by no script of the source"
                        out_rows.append(row)
                        continue
                    MC.apply_to_entity(tgt_desc, c_init, c_pre, ent.get("format_version", "1.10.0"))
                    row["carried"] = len(c_init) + len(c_pre)
                    an["animations"][new_id] = a2
                    tgt_desc.setdefault("animations", {})[f"shared_{k}"] = new_id
                    row["applied"] = True
                    shares.append(row)
                else:
                    row["applied"] = False
                out_rows.append(row)
        if write:
            for mid, (d, f, ent, geo, an, names, clips, gid) in info.items():
                f.write_text(json.dumps(ent, indent=1))
                (d / f"animations/std/{S.slug_of(mid)}.animation.json").write_text(json.dumps(an, indent=1))
    lines = ["# SPECIES SHARING — pick list (Phase 3b)", "",
             "Every row is a same-species copy, added as an EXTRA clip `shared_<kind>` (nothing plays it until you pick it "
             "in the parade). Bone cover = share of the clip's bones the target's standard rig has.", "",
             "| species | kind | best clip (from) | to | target's own clip | bone cover | added |", "|---|---|---|---|---|---|---|"]
    for r in out_rows:
        lines.append(f"| {r['species']} | {r['kind']} | {r['from']} `{r['from_clip']}` | {r['to']} | "
                     f"{r['to_has_own'] or '—'} | {r['bone_cover']} | {'yes' if r['applied'] else 'no (rig too different)'} |")
    (ROOT / "_docs/standard/SHARING-PICKLIST.md").write_text("\n".join(lines) + "\n")
    (ROOT / "_docs/standard/SHARING.json").write_text(json.dumps(out_rows, indent=1))
    print(len(out_rows), "rows;", len(shares), "clips added")


if __name__ == "__main__":
    main("--dry" not in sys.argv)
