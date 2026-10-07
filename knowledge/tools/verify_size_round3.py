#!/usr/bin/env python3
"""verify_size_round3.py — the gate for build_size_round3.py.
  P1  BP-02 1.3.193 / StripMine 1.3.6: every changed file differs from its source ONLY in minecraft:scale values (parsed JSON,
      scale values masked), each new value = old x factor (3-decimal rounding); nothing else changed but the manifests
  P2  the endermite = Mojang's 1.26.50 endermite.json + one base minecraft:scale 0.75 (nothing else)
  P3  the factors reproduce the targets: to_blocks / from_blocks, targets = size_law.target(metres)
  P4  manifests: versions 1.3.193 / 1.3.6, uuids kept
Static checks only rule OUT (P1); his in-game witness rules IN."""
import hashlib, json, sys
from pathlib import Path
sys.path.insert(0, "/home/claude/tools")
import molang_lint as ML
import size_law as S
import build_size_round as R1

ROOT = Path("/home/claude")
REP = json.load(open(ROOT / "_docs/sizes/size_round3_report.json"))
fails, n = [], [0]


def check(tag, ok, msg=""):
    n[0] += 1; print(("PASS " if ok else "FAIL ") + tag + (f" — {msg}" if msg else ""))
    if not ok: fails.append(tag)


def scales(o, path=""):
    out = []
    if isinstance(o, dict):
        for k, v in o.items():
            if k == "minecraft:scale" and isinstance(v, dict) and "value" in v: out.append((path + "/" + k, float(v["value"])))
            else: out += scales(v, path + "/" + k)
    elif isinstance(o, list):
        for i, v in enumerate(o): out += scales(v, f"{path}[{i}]")
    return out


def masked(o):
    if isinstance(o, dict): return {k: ("<scale>" if k == "minecraft:scale" else masked(v)) for k, v in o.items()}
    if isinstance(o, list): return [masked(v) for v in o]
    return o


def diff_tree(old, new):
    md5 = lambda p: hashlib.md5(p.read_bytes()).hexdigest()
    fo = {str(p.relative_to(old)): p for p in old.rglob("*") if p.is_file()}; fn = {str(p.relative_to(new)): p for p in new.rglob("*") if p.is_file()}
    return sorted(k for k in fo if k in fn and md5(fo[k]) != md5(fn[k])), sorted(set(fn) - set(fo)), sorted(set(fo) - set(fn))


for label, old, new, rows, ver in (("BP-02", ROOT / "_build/bp02-192", ROOT / "_build/bp02-193", REP["bp02"], [1, 3, 193]),
                                    ("StripMine", ROOT / "_build/stripmine-bp-135", ROOT / "_build/stripmine-bp-136", REP["stripmine"], [1, 3, 6])):
    ch, add, rem = diff_tree(old, new)
    want_ch = sorted({r["file"] for r in rows if not r.get("new_file")} | {"manifest.json"})
    want_add = sorted(r["file"] for r in rows if r.get("new_file"))
    check(f"P1 {label} changed set = the resized files + manifest", ch == want_ch and add == want_add and not rem, f"changed {ch} added {add} removed {rem}")
    for r in rows:
        if r.get("new_file"): continue
        a = ML._parse_json((old / r["file"]).read_text(encoding="utf-8-sig")); b = ML._parse_json((new / r["file"]).read_text(encoding="utf-8-sig"))
        sa, sb = scales(a), scales(b)
        ok = masked(a) == masked(b) and [p for p, _ in sa] == [p for p, _ in sb] and all(abs(vb - float(R1.fmt(va * r["factor"]))) < 1e-9 for (_, va), (_, vb) in zip(sa, sb))
        check(f"P1 {label} {r['id']}: only scale values, each x{r['factor']}", ok, str([(round(va, 3), vb) for (_, va), (_, vb) in zip(sa, sb)]))
    m_old = json.loads((old / "manifest.json").read_text(encoding="utf-8-sig")); m_new = json.loads((new / "manifest.json").read_text(encoding="utf-8-sig"))
    check(f"P4 {label} manifest {ver}, uuid kept", m_new["header"]["version"] == ver and m_new["header"]["uuid"] == m_old["header"]["uuid"]
          and all(x["version"] == ver and x["uuid"] == y["uuid"] for x, y in zip(m_new["modules"], m_old["modules"])), "")

van = ML._parse_json((R1.VAN_BP / "endermite.json").read_text(encoding="utf-8")); ours = ML._parse_json((ROOT / "_build/bp02-193/entities/endermite.json").read_text(encoding="utf-8"))
base = ours["minecraft:entity"]["components"].get("minecraft:scale")
rest = json.loads(json.dumps(ours)); rest["minecraft:entity"]["components"].pop("minecraft:scale", None)
check("P2 endermite = Mojang's file + base minecraft:scale 0.75 only", base == {"value": 0.75} and rest == van and not scales(van), str(base))
for r in REP["rows"]:
    if r["id"] == "minecraft:polar_bear":
        ok = abs(r["factor"] - round(r["model_l_old"] / r["model_l_new"], 4)) < 1e-9 and r["to_blocks"] == r["from_blocks"]
        check(f"P3 polar bear keeps {r['to_blocks']} blocks head-body on the new model (x{r['factor']} = {r['model_l_old']} / {r['model_l_new']})", ok, "")
    else:
        ok = abs(r["to_blocks"] - round(S.target(r["real_m"]), 3)) < 1e-9 and abs(r["factor"] - round(S.target(r["real_m"]) / r["from_blocks"], 4)) < 2e-4
        check(f"P3 {r['id']} {r['real_m_old']} -> {r['real_m']} m = {r['to_blocks']} blocks (x{r['factor']})", ok, "")
print(f"\n{'GATE OPEN' if not fails else 'GATE SHUT'} {n[0] - len(fails)}/{n[0]}")
sys.exit(1 if fails else 0)
