#!/usr/bin/env python3
"""menagerie_p3_adjust.py — D-C353: the P3-only changes applied to STAGING after the port, before the wave build.
  1. Bears (his note 'keep our size proportions'): the AnF bears are scaled so their largest visible dimension in game matches
     our bear's (the size law's 'largest dimension' rule): AnF black -> our black bear, AnF grizzly -> our grizzly.
     Visible size = visible_size.measure(everyday=True).max x the BP minecraft:scale. The baby group scales by the same factor.
  2. Shared spawn weights (his M9 'accept recommended'): when an animal is kept from P packs (OURS counts when our creature has a
     spawn rule), every spawn condition of each kept pack's versions gets weight / P (rounded, at least 1). A pack's own sub-species
     keep their balance among themselves; the animal as a whole spawns about as often as one pack's version did.
     OURS spawn files are not touched here: their new weights go to _logs/menagerie_p3_ours_spawn.json for the wave build.
Report: _logs/menagerie_p3_adjust.json"""
import glob, json, sys
from pathlib import Path
sys.path.insert(0, "/home/claude/tools")
ROOT = Path("/home/claude"); STAGE = ROOT / "_build/menagerie-stage"; BASE_BP = ROOT / "_build/stripmine-bp-137"; BASE_RP = ROOT / "_build/rp07-1432"
SP = Path("/tmp/claude-0/-home-claude/c0a4a7ef-9c52-560d-ac77-bcf688f4b3d2/scratchpad/bearm")
BEARS = {"pw:bear_black_anf": ("bear_black", "black_bear"), "pw:bear_grizzly_anf": ("bear_grizzly", "grizzly_bear")}


def jl(p): return json.loads(Path(p).read_text(encoding="utf-8-sig"))


def bp_file_of(ident, root):
    for f in glob.glob(str(root / "entities/**/*.json"), recursive=True):
        try: d = jl(f)
        except Exception: continue
        if d.get("minecraft:entity", {}).get("description", {}).get("identifier") == ident: return Path(f)


def bears(rep):
    import visible_size as V, shutil
    (SP / "entity").mkdir(parents=True, exist_ok=True); (SP / "models").mkdir(exist_ok=True)
    link = SP / "models/entity"
    if not link.exists(): link.symlink_to(STAGE / "RP/models")
    for nid, (stem, ours) in BEARS.items():
        rp = STAGE / f"RP/entity/pw_menagerie/anf/mammals/{stem}.json"
        shutil.copyfile(rp, SP / f"entity/m_{stem}.entity.json")
        bpf = bp_file_of(nid, STAGE / "BP"); d = jl(bpf); e = d["minecraft:entity"]
        anf_scale = e["components"]["minecraft:scale"]["value"]
        ours_bp = jl(bp_file_of(f"sf_nba:{ours}", BASE_BP))["minecraft:entity"]["components"]["minecraft:scale"]["value"]
        ours_max = V.measure(str(BASE_RP), ours, everyday=True)["max"] * ours_bp
        anf_max = V.measure(str(SP), f"m_{stem}", stack=(str(STAGE / "RP"),), everyday=True)["max"] * anf_scale
        k = ours_max / anf_max; new = round(anf_scale * k, 3)
        e["components"]["minecraft:scale"]["value"] = new
        for g, c in e.get("component_groups", {}).items():
            if "minecraft:scale" in c: c["minecraft:scale"]["value"] = round(c["minecraft:scale"]["value"] * k, 3)
        bpf.write_text(json.dumps(d, indent=1, ensure_ascii=False), encoding="utf-8")
        rep["bears"][nid] = {"ours": f"sf_nba:{ours}", "ours_max_blocks": round(ours_max, 3), "anf_max_before": round(anf_max, 3),
                             "scale_before": anf_scale, "scale_after": new, "factor": round(k, 3)}


SCALE_RE = None


def rescale_text(text, factor, new_abs):
    """every minecraft:scale value x factor (top level and every component group: adult / baby keep their ratio); a file with no
    scale anywhere gets one top-level scale = new_abs. Text-level, so nothing else in the file changes."""
    import re
    rx = re.compile(r'("minecraft:scale"\s*:\s*\{\s*"value"\s*:\s*)(-?[0-9.]+(?:[eE][-+]?[0-9]+)?)')
    n = len(rx.findall(text))
    if n:
        return rx.sub(lambda mm: mm.group(1) + f"{round(float(mm.group(2)) * factor, 4)}", text), n
    m = re.search(r'("minecraft:entity"\s*:\s*\{.*?"components"\s*:\s*\{)', text, re.S)
    assert m, "no components block"
    return text[:m.end()] + f'\n   "minecraft:scale": {{"value": {round(new_abs, 4)}}},' + text[m.end():], 0


def adult_scale(e):
    groups = {g: c["minecraft:scale"].get("value") for g, c in (e.get("component_groups") or {}).items()
              if isinstance(c, dict) and isinstance(c.get("minecraft:scale"), dict)}
    adult = [v for g, v in groups.items() if "adult" in g.lower() and isinstance(v, (int, float))]
    top = float(((e.get("components") or {}).get("minecraft:scale") or {}).get("value", 1.0) or 1.0)
    return float(adult[0]) if adult else top


def sizes(rep):
    """D-C363 size law v2 (his 01:51 + Z1 = A): every ported creature's adult scale = the plan's new_scale (one figure per version,
    species-normalized); the old AnF-bear step is part of it now. Rows the plan skips keep their scale."""
    plan = {r["id"]: r for r in json.loads((ROOT / "_docs/sizes/size_law_v2_plan.json").read_text()) if r.get("new_scale")}
    done = {}
    for f in glob.glob(str(STAGE / "BP/entities/**/*.json"), recursive=True):
        txt = Path(f).read_text(encoding="utf-8-sig"); e = json.loads(txt)["minecraft:entity"]; i = e["description"]["identifier"]
        r = plan.get(i)
        if not r or r["action"] == "keep": continue
        cur = adult_scale(e); fac = r["new_scale"] / cur
        new, n = rescale_text(txt, fac, r["new_scale"])
        Path(f).write_text(new, encoding="utf-8"); done[i] = {"from": cur, "to": r["new_scale"], "edits": n or "inserted"}
    rep["sizes"] = done


def borrow(rep):
    """his S1: a creature with looks only gets another creature's behaviour, spawn rule and drops (identifier swapped, nothing else)."""
    J = json.loads((ROOT / "_logs/menagerie_jobs_P3.json").read_text())
    for nid, src in (J.get("borrow") or {}).items():
        sf = bp_file_of(src, STAGE / "BP"); d = jl(sf)
        assert bp_file_of(nid, STAGE / "BP") is None, f"{nid} already has a behaviour"
        d["minecraft:entity"]["description"]["identifier"] = nid
        pack = nid.rsplit("_", 1)[1]; stem = nid.split(":")[1].rsplit("_", 1)[0]
        out = STAGE / f"BP/entities/pw_menagerie/{pack}/{stem}.json"; out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(d, indent=1, ensure_ascii=False), encoding="utf-8")
        row = {"from": src, "behaviour": str(out.relative_to(STAGE))}
        for f in glob.glob(str(STAGE / "BP/spawn_rules/**/*.json"), recursive=True):
            sr = jl(f)
            if sr["minecraft:spawn_rules"]["description"]["identifier"] == src:
                sr["minecraft:spawn_rules"]["description"]["identifier"] = nid
                so = STAGE / f"BP/spawn_rules/pw_menagerie/{pack}/{stem}.json"; so.parent.mkdir(parents=True, exist_ok=True)
                so.write_text(json.dumps(sr, indent=1, ensure_ascii=False), encoding="utf-8"); row["spawn_rule"] = str(so.relative_to(STAGE))
        rep.setdefault("borrowed", {})[nid] = row


ANF_FACTOR = 0.1   # his S3 (23:21): AnF spawn weights (100 on most rules) to the vanilla scale (cow 8, pig 10, sheep 12)


def anf_scale(rep):
    n = 0
    files = glob.glob(str(STAGE / "BP/spawn_rules/pw_menagerie/anf/**/*.json"), recursive=True)
    files += [str(STAGE / r["spawn_rule"]) for r in rep.get("borrowed", {}).values() if r["from"].endswith("_anf") and "spawn_rule" in r]   # an AnF rule worn by another
    for f in files:
        d = jl(f)
        for c in d["minecraft:spawn_rules"].get("conditions", []):
            w = c.get("minecraft:weight")
            if isinstance(w, dict) and isinstance(w.get("default"), (int, float)): w["default"] = max(1, round(w["default"] * ANF_FACTOR)); n += 1
        Path(f).write_text(json.dumps(d, indent=1, ensure_ascii=False), encoding="utf-8")
    rep["anf_weights_scaled"] = {"factor": ANF_FACTOR, "conditions": n}


def spawns(rep):
    J = json.loads((ROOT / "_logs/menagerie_jobs_P3.json").read_text())
    dec = json.loads((ROOT / "_logs/menagerie_decisions.json").read_text())
    sheets = {s["group"]: s for s in json.loads((ROOT / "_logs/menagerie_sheets.json").read_text())["sheets"]}
    src_of = {e[2]: e[0] for e in J["entities"]}
    rules = {}
    for f in glob.glob(str(STAGE / "BP/spawn_rules/**/*.json"), recursive=True):
        rules[jl(f)["minecraft:spawn_rules"]["description"]["identifier"]] = Path(f)
    ours_rules = {}
    for f in glob.glob(str(BASE_BP / "spawn_rules/**/*.json"), recursive=True):
        try: ours_rules[jl(f)["minecraft:spawn_rules"]["description"]["identifier"]] = Path(f)
        except Exception: pass
    ours_patch = {}
    for a, v in dec.items():
        if a == "_rules": continue
        mine = [n for n, an in J["animal_of"].items() if an == a and n in src_of]
        packs = {src_of[n] for n in mine if n in rules}
        ours_ids = [x["id"] for x in sheets[a]["versions"] if x["src"] == "OURS"] if "OURS" in v["keep"] else []
        ours_with = [i for i in ours_ids if i in ours_rules]
        P = len(packs) + (1 if ours_with else 0)
        if P <= 1: continue
        row = {"packs": sorted(packs) + (["OURS"] if ours_with else []), "P": P, "changed": []}
        for n in mine:
            if n not in rules: continue
            d = jl(rules[n])
            for c in d["minecraft:spawn_rules"].get("conditions", []):
                w = c.get("minecraft:weight")
                if isinstance(w, dict) and isinstance(w.get("default"), (int, float)):
                    old = w["default"]; w["default"] = max(1, round(old / P)); row["changed"].append([n, old, w["default"]])
            rules[n].write_text(json.dumps(d, indent=1, ensure_ascii=False), encoding="utf-8")
        for i in ours_with:
            d = jl(ours_rules[i]); ch = []
            for c in d["minecraft:spawn_rules"].get("conditions", []):
                w = c.get("minecraft:weight")
                if isinstance(w, dict) and isinstance(w.get("default"), (int, float)):
                    old = w["default"]; w["default"] = max(1, round(old / P)); ch.append([old, w["default"]])
            ours_patch[str(ours_rules[i].relative_to(BASE_BP))] = {"id": i, "weights": ch, "json": d}
            row["changed"].append([i, *(ch[0] if ch else [None, None])])
        rep["spawn"][a] = row
    (ROOT / "_logs/menagerie_p3_ours_spawn.json").write_text(json.dumps(ours_patch, indent=1))


if __name__ == "__main__":
    mark = STAGE / ".p3_adjusted"
    assert not mark.exists(), "staging already adjusted: re-run addon_port.py --jobs _logs/menagerie_jobs_P1P3.json first"
    rep = {"spawn": {}}
    borrow(rep); sizes(rep); spawns(rep); anf_scale(rep); mark.write_text("done\n")   # D-C363: sizes() replaces bears()
    (ROOT / "_logs/menagerie_p3_adjust.json").write_text(json.dumps(rep, indent=1))
    print("sizes applied:", len(rep.get("sizes", {}))); print("animals sharing spawn:", len(rep["spawn"]))
    for a, r in sorted(rep["spawn"].items()): print(f"  {a}: P={r['P']} {r['packs']} conditions changed {len(r['changed'])}")
