#!/usr/bin/env python3
"""version_banner_audit.py — W2-V2 (10-03, D-C506 retro hit): every place a pack states ITS OWN version must equal its manifest.
Per pack: manifest header + module versions · manifest name ("… vX.Y.Z") · description lead ("vX.Y.Z (date)") · the PW-DEPENDENCIES.md
stamp (first version on its first stamp line) · script banners (PW_BUILD, RUNNER_VERSION, "[PW-VERSION] … vX") · texts/*.lang lines
that name the pack version. A mismatch is a LAG (cosmetic unless a brief tells him to expect a log line). Writes
_docs/recheck/W2-V2-BANNERS.json and prints one line per pack."""
import json, re
from pathlib import Path
B = Path("/home/claude/_build")
SET = ["bp01-135", "bp02-214", "bp03-134", "markers-0.2.1/BP", "testrunner-0.5.20", "rp01-118", "rp02-207", "rp03-67", "rp04-156",
       "rp05-58", "rp06-1429", "rp07-1445", "rp08-1414", "rp10-151", "rp11-140", "markers-0.2.2-rp/RP"]
V = r"(\d+\.\d+\.\d+)"
out, bad = {}, 0
for d in SET:
    p = B / d
    m = json.loads((p / "manifest.json").read_text(encoding="utf-8-sig"))
    ver = ".".join(map(str, m["header"]["version"]))
    found = []
    for mod in m.get("modules", []):
        found.append(("module", ".".join(map(str, mod["version"]))))
    mm = re.search(r"v" + V + r"\s*$", m["header"].get("name", ""))
    if mm: found.append(("name", mm.group(1)))
    md = re.match(r"\s*v" + V, m["header"].get("description", ""))
    if md: found.append(("description", md.group(1)))
    dep = p / "PW-DEPENDENCIES.md"
    if dep.exists():
        for line in dep.read_text(errors="ignore").splitlines()[1:6]:
            ms = re.match(r"\s*v" + V, line)
            if ms: found.append(("PW-DEPENDENCIES", ms.group(1))); break
    for f in list(p.rglob("*.js")):
        t = f.read_text(errors="ignore")
        for rx, tag in [(r'const PW_BUILD = "' + V + '"', "PW_BUILD"), (r'RUNNER_VERSION = "' + V + '"', "RUNNER_VERSION"),
                        (r"\[PW-VERSION\][^\n`'\"]{0,80}? v" + V, "PW-VERSION banner")]:
            for x in re.finditer(rx, t):
                found.append((f"{tag} ({f.name})", x.group(1)))
    for f in list(p.rglob("*.lang")):
        for line in f.read_text(errors="ignore").splitlines():
            if re.search(r"pack\.(name|description)", line):
                for x in re.finditer(r"v" + V, line): found.append((f"lang {f.name}", x.group(1)))
    lags = [(k, v) for k, v in found if v != ver]
    bad += bool(lags)
    out[d] = {"manifest": ver, "checked": found, "lags": lags}
    print(f"{'LAG ' if lags else 'OK  '} {d:22s} {ver:9s} {len(found):3d} statement(s)" + (f"  -> {lags}" if lags else ""))
Path("/home/claude/_docs/recheck/W2-V2-BANNERS.json").write_text(json.dumps(out, indent=1))
print(f"{len(SET) - bad}/{len(SET)} packs state one version everywhere")
