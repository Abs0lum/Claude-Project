#!/usr/bin/env python3
"""build_kitvillage_0037.py — the gate probe 0.0.37 for BP-02 1.3.226 (his 20:48): the LAND SURVEY is run at the site
before founding ([CIV-SURVEY]: the best three gentle sites within 192); every BEYOND record carries the core's conversions
(homes bought for businesses) and the homeless count. Usage: python3 tools/build_kitvillage_0037.py"""
import json
import shutil
from pathlib import Path

B = Path("/home/claude/_build")
SRC, DST = B / "kitvillage-0.0.36", B / "kitvillage-0.0.37"


def rep(t, old, new, n=1):
    assert t.count(old) == n, (old[:80], t.count(old))
    return t.replace(old, new)


def main():
    if DST.exists():
        raise SystemExit(f"never rebuild {DST}")
    shutil.copytree(SRC, DST)
    mp = DST / "manifest.json"
    m = json.loads(mp.read_text())
    m["header"]["name"] = "PW KitVillage probe 0.0.37 (BDS only)"
    m["header"]["version"] = [0, 0, 37]
    for mod in m["modules"]:
        mod["version"] = [0, 0, 37]
    mp.write_text(json.dumps(m, indent=1))
    p = DST / "scripts/main.js"
    t = p.read_text()
    t = rep(t, "  dim.runCommand(`scriptevent pw:clock villageat ${site.x} ${site.z} 7`);",
            "  try { dim.runCommand(`scriptevent pw:clock surveyat ${site.x} ${site.z} 192`); } catch { /* old clock */ }\n  await sleep(200);   // 0.0.37: the survey job reads ~2,300 columns\n  dim.runCommand(`scriptevent pw:clock villageat ${site.x} ${site.z} 7`);")
    t = rep(t, "winReleased: st && st.winReleased, branchesLaid: st && st.branchesLaid,",
            "winReleased: st && st.winReleased, branchesLaid: st && st.branchesLaid, conversions: st && st.conversions, homeless: st && st.census ? st.census.homeless : null,")
    p.write_text(t)
    print(f"DONE {DST}")


if __name__ == "__main__":
    main()
