#!/usr/bin/env python3
"""verify_size_round.py — gate for the SIZE ROUND (BP-02 1.3.190 · StripMine BP 1.3.4 · RP-06 1.4.19), D-C292.
VSC (new): every behaviour entity we override differs from its source (Mojang 1.26.50 / StripMine 1.3.3) ONLY in minecraft:scale
values — each = old x the planned factor (3 dp), plus at most one inserted adult scale = the factor; text diff lines == edits.
Plus: changed-set checks, manifests, identifiers unique across his behaviour packs, the resized sizes re-measured on the curve,
and the standing RP gates (MLS · ARS · RCV · FMT · RBW · ATT · PREC) on RP-06 1.4.19."""
import difflib, hashlib, json, re, sys
from pathlib import Path
sys.path.insert(0, "/home/claude/tools")
import molang_lint as ML
import build_size_round as B
import size_law as SL

ROOT = Path("/home/claude")
fails = []; n = [0]
def check(tag, ok, msg):
    n[0] += 1; print(("PASS " if ok else "FAIL ") + tag + " — " + msg)
    if not ok: fails.append(tag)
md5 = lambda p: hashlib.md5(Path(p).read_bytes()).hexdigest()


def files(d): return {str(p.relative_to(d)): p for p in Path(d).rglob("*") if p.is_file()}


def changed_set(old, new):
    fo, fn = files(old), files(new)
    return (sorted(k for k in fo if k in fn and md5(fo[k]) != md5(fn[k])), sorted(set(fn) - set(fo)), sorted(set(fo) - set(fn)))


def scale_diff(a, b, factor, path=""):
    """-> list of problems; allowed: minecraft:scale.value == round(old*factor,3); an inserted components.minecraft:scale == factor"""
    probs = []
    if isinstance(a, dict) and isinstance(b, dict):
        for k in set(a) | set(b):
            p = f"{path}/{k}"
            if k not in a:
                if k == "minecraft:scale" and path.endswith("/components") and abs(float(b[k]["value"]) - round(factor, 3)) < 1e-9 and set(b[k]) == {"value"}: continue
                probs.append(f"added {p}"); continue
            if k not in b: probs.append(f"removed {p}"); continue
            if k == "minecraft:scale" and isinstance(a[k], dict) and isinstance(b[k], dict) and set(a[k]) == set(b[k]) == {"value"}:
                want = round(float(a[k]["value"]) * factor, 3)
                if abs(float(b[k]["value"]) - want) > 1e-9: probs.append(f"{p} {b[k]['value']} != {want}")
                continue
            probs += scale_diff(a[k], b[k], factor, p)
    elif isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b): probs.append(f"list length {path}")
        else:
            for i, (x, y) in enumerate(zip(a, b)): probs += scale_diff(x, y, factor, f"{path}[{i}]")
    elif a != b:
        probs.append(f"value {path}: {str(a)[:30]} -> {str(b)[:30]}")
    return probs


def text_diff_lines(a, b):
    return sum(1 for l in difflib.ndiff(a.splitlines(), b.splitlines()) if l.startswith(("+ ", "- ")))


# ------------------------------------------------------------------------------------------------ BP-02 1.3.190
rep = json.load(open(ROOT / "_docs/sizes/size_round_report.json"))
OLD, NEW = ROOT / "_build/bp02-189", ROOT / "_build/bp02-190"
ch, add, rem = changed_set(OLD, NEW)
exp_add = sorted(f"entities/{fn}" for fn in B.VANILLA_FILES.values())
check("B1 BP-02 changed set", ch == ["manifest.json"] and add == exp_add and not rem, f"changed {ch}; added {len(add)} (expected {len(exp_add)}); removed {rem}")
m = json.loads((NEW / "manifest.json").read_text()); mo = json.loads((OLD / "manifest.json").read_text(encoding="utf-8-sig"))
check("B2 BP-02 manifest", m["header"]["version"] == [1, 3, 190] and all(x["version"] == [1, 3, 190] for x in m["modules"]) and m["header"]["uuid"] == mo["header"]["uuid"]
      and [x["uuid"] for x in m["modules"]] == [x["uuid"] for x in mo["modules"]] and m["dependencies"] == mo["dependencies"], f"{m['header']['version']} uuids kept")
bad = []; lines_ok = []
for r in rep["bp02"]:
    fn = Path(r["file"]).name
    a_raw = (B.VAN_BP / fn).read_text(encoding="utf-8"); b_raw = (NEW / r["file"]).read_text(encoding="utf-8")
    probs = scale_diff(ML._parse_json(a_raw), ML._parse_json(b_raw), r["factor"])
    if probs: bad.append((fn, probs[:3]))
    want = r["scales_changed"] * 2 + (1 if r["base_inserted"] else 0)
    got = text_diff_lines(a_raw, b_raw)
    if got != want: lines_ok.append((fn, got, want))
check("VSC1 BP-02 overrides differ from Mojang 1.26.50 ONLY in scale values (parsed)", not bad, f"{len(rep['bp02'])} files; problems {bad[:3]}")
check("VSC2 BP-02 text diff = exactly the scale edits (comments / order / format kept)", not lines_ok, f"mismatches {lines_ok[:4]}")
ids = {}
for bp in [NEW, ROOT / "_build/stripmine-bp-134", ROOT / "_build/bp03-134", ROOT / "_build/bp01-135"]:
    for p in (bp / "entities").rglob("*.json") if (bp / "entities").exists() else []:
        mm = re.search(r'"identifier"\s*:\s*"([a-z0-9_:]+)"', p.read_text(encoding="utf-8-sig", errors="replace"))
        if mm: ids.setdefault(mm.group(1), []).append(f"{bp.name}/{p.name}")
dups = {k: v for k, v in ids.items() if len(v) > 1 and k.startswith("minecraft:")}
check("B3 each vanilla identifier defined once across his behaviour packs (BP-02 · StripMine · BP-03 · BP-01)", not dups, f"duplicates {dups}")

# ------------------------------------------------------------------------------------------------ StripMine BP 1.3.4
OLD, NEW = ROOT / "_build/stripmine-bp-133", ROOT / "_build/stripmine-bp-134"
ch, add, rem = changed_set(OLD, NEW)
files_s = sorted(r["file"] for r in rep["stripmine"] if "skipped" not in r)
check("S1 StripMine changed set", sorted(ch) == sorted(files_s + ["manifest.json"]) and not add and not rem, f"changed {len(ch)} (expected {len(files_s) + 1}); added {add}; removed {rem}")
bad = []; lines_bad = []
for r in rep["stripmine"]:
    if "skipped" in r: bad.append((r["id"], r["skipped"])); continue
    a_raw = (OLD / r["file"]).read_text(encoding="utf-8-sig"); b_raw = (NEW / r["file"]).read_text(encoding="utf-8")
    probs = scale_diff(ML._parse_json(a_raw), ML._parse_json(b_raw), r["factor"])
    if probs: bad.append((r["id"], probs[:2]))
    if text_diff_lines(a_raw, b_raw) != r["scales_changed"] * 2 + (1 if r["base_inserted"] else 0): lines_bad.append(r["id"])
check("VSC3 StripMine entities differ from 1.3.3 ONLY in scale values", not bad, f"{len(rep['stripmine'])} files; problems {bad[:3]}")
check("VSC4 StripMine text diff = exactly the scale edits", not lines_bad, f"mismatches {lines_bad[:5]}")
sharks = [r for r in rep["stripmine"] if r["id"] in B.KEEP_IMPOSING]
check("S2 sharks untouched (his 'Sharks imposing')", not sharks, f"{[r['id'] for r in sharks]}")
mf = json.loads((NEW / "manifest.json").read_text())
check("S3 StripMine manifest", mf["header"]["version"] == [1, 3, 4] and all(x["version"] == [1, 3, 4] for x in mf["modules"]), f"{mf['header']['version']}")

# ------------------------------------------------------------------------------------------------ the curve, re-measured
# every resized mob: planned drawn size = current x factor must land on the real-life target within 1 %
off = [(r["id"], r["from_blocks"], r["factor"], r["to_blocks"]) for r in rep["bp02"] + [x for x in rep["stripmine"] if "skipped" not in x]
       if abs(r["from_blocks"] * r["factor"] - r["to_blocks"]) > 0.01 * r["to_blocks"]]
check("C1 every resized mob lands on its real-life target (current x factor = target, 1 %)", not off, f"off {off[:3]}")

# ------------------------------------------------------------------------------------------------ RP-06 1.4.19
OLD, NEW = ROOT / "_build/rp06-1418", ROOT / "_build/rp06-1419"
ch, add, rem = changed_set(OLD, NEW)
check("R1 RP-06 changed set", ch == ["manifest.json"] and add == ["entity/warden.entity.json"] and not rem, f"changed {ch} added {add} removed {rem}")
a = ML._parse_json((B.VAN_RP / "warden.entity.json").read_text(encoding="utf-8")); b = ML._parse_json((NEW / "entity/warden.entity.json").read_text(encoding="utf-8"))
sa = a["minecraft:client_entity"]["description"].get("scripts", {}); sb = b["minecraft:client_entity"]["description"].pop("scripts", {})
a["minecraft:client_entity"]["description"].pop("scripts", {})
extra = {k: v for k, v in sb.items() if k not in sa}
check("R2 warden = Mojang's client entity + scripts.scale 1.2 only", a == b and extra == {"scale": "1.2"} and all(sb[k] == sa[k] for k in sa),
      f"extra script keys {extra}")
import molang_lint, anim_resolve_lint, rc_visibility_lint, entity_schema_lint, molang_rbw_lint, attachables_lint, entity_precedence
n_ml, e_ml = molang_lint.lint_pack(NEW); check("MLS Molang parses (standing)", not e_ml, f"{n_ml} strings; errors {e_ml[:2]}")
n_ar, e_ar = anim_resolve_lint.lint_pack(NEW, stack=(ROOT / "_build/rp07-1425",))
base = set(json.load(open(ROOT / "_docs/convb/ars_baseline.json")).get("RP-06", []))
new_f = sorted({f"{e[0]} | {e[2]}" for e in e_ar} - base)
check("ARS animations resolve (standing)", not new_f, f"{n_ar} entities; NEW {new_f[:3]}")
n_rc, f_rc = rc_visibility_lint.lint_pack(NEW, (ROOT / "_build/rp07-1425",)); check("RCV render controllers leave the geometry visible (standing)", not f_rc, f"{n_rc}; {f_rc[:2]}")
n_fm, e_fm, i_fm = entity_schema_lint.lint_pack(NEW); check("FMT format sections (standing)", not e_fm, f"{n_fm}; {e_fm[:2]}")
n_rb, f_rb = molang_rbw_lint.lint_pack(NEW)
rb_base = set(json.load(open(ROOT / "_docs/convb/rbw_baseline.json")).get("RP-06", []))
rb_new = sorted({f"{x[0]} | {x[2]}" for x in f_rb} - rb_base)
check("RBW read-before-write (standing)", not rb_new, f"{n_rb}; NEW {rb_new[:3]}")
n_at, f_at = attachables_lint.lint_pack(NEW); check("ATT attachables flag (standing)", not f_at, f"{n_at}; {f_at[:3]}")
rows = entity_precedence.census([("StripMine RP 3.0.1", ROOT / "_intake/stack-rps/PW-StripMine-RP-v3_0_1.mcpack"), ("RP-08", ROOT / "_build/rp08-148"),
                                 ("RP-07", ROOT / "_build/rp07-1425"), ("RP-06", NEW)])
lose = [f"{r['id']} -> {r['winner']}" for r in rows if r["ours_lose"]]
check("PREC our client entities win (standing)", not lose, f"{len(rows)} shared ids; lose {lose[:3]}")

print(f"\n{'GATE OPEN' if not fails else 'GATE CLOSED'} {n[0] - len(fails)}/{n[0]}" + (f"  FAILS: {fails}" if fails else ""))
sys.exit(1 if fails else 0)
