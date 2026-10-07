"""test_palace2_merge.py — the Part C merge tool on SYNTHETIC entries (the real 1.2 MB palace2_buildings_entries.json is
generated in the cloud workspace and is not in this session). Usage: python3 test_palace2_merge.py <pw_civ_buildings.js> <workdir>"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import palace2_merge_buildings as T  # noqa: E402

src, work = sys.argv[1], sys.argv[2]
os.makedirs(work, exist_ok=True)
ok = fail = 0


def check(c, m):
    global ok, fail
    if c:
        ok += 1
    else:
        fail += 1
        print("FAIL", m)


def entry(k):
    stem = k.split(":", 1)[1]
    return {"stem": stem, "size": [64, 50, 64], "datum_y": 15, "stages": 5, "lids": [], "door": [0, 0, 32], "work": 3,
            "dir": [[1, 15, 2, "minecraft:bed", {"direction": 1}]], "chests": [], "art": [],
            "bom": [{"stone": 10}, {"timber": 1}, {"stone": 5}, {"thatch": 1}, {"planks": 2}], "palace2": {"grid": [int(stem[12]), int(stem[13])]}}


entries = {k: entry(k) for k in T.KEYS}
ep = os.path.join(work, "entries.json")
json.dump(entries, open(ep, "w"))
out = os.path.join(work, "pw_civ_buildings.js")
head0, t0 = T.read_table(src)
r = subprocess.run([sys.executable, "-I", os.path.join(HERE, "palace2_merge_buildings.py"), src, ep, "--out", out], capture_output=True, text=True)
check(r.returncode == 0, f"merge exit {r.returncode}: {r.stdout} {r.stderr}")
head1, t1 = T.read_table(out)
check(head1 == head0, "the generator's comment line kept")
check(len(t1) == len(t0) + 16, f"{len(t0)} + 16 entries: {len(t1)}")
check(all(k in t1 for k in T.OLD), "the 4 2 x 2 palace entries kept")
check(all(json.dumps(t1[k], sort_keys=True) == json.dumps(t0[k], sort_keys=True) for k in t0), "every existing entry unchanged")
check(all(t1[k] == entries[k] for k in T.KEYS), "the 16 PALACE II entries as given")
b1 = open(out, "rb").read()
r2 = subprocess.run([sys.executable, "-I", os.path.join(HERE, "palace2_merge_buildings.py"), out, ep, "--out", out], capture_output=True, text=True)
check(r2.returncode == 0 and open(out, "rb").read() == b1, "idempotent (a second merge writes the same bytes)")
check(b1.startswith(open(src, "rb").read().split(b"\n", 1)[0]), "first line identical")
# a bad entry is refused, nothing written
bad = dict(entries)
bad[T.KEYS[5]] = dict(entry(T.KEYS[5]), size=[64, 48, 64])
bad[T.KEYS[9]] = {k: v for k, v in entry(T.KEYS[9]).items() if k != "bom"}
bp = os.path.join(work, "bad.json")
json.dump(bad, open(bp, "w"))
out2 = os.path.join(work, "bad_out.js")
r3 = subprocess.run([sys.executable, "-I", os.path.join(HERE, "palace2_merge_buildings.py"), src, bp, "--out", out2], capture_output=True, text=True)
check(r3.returncode == 1 and not os.path.exists(out2), "bad entries refused, nothing written")
check("size [64, 48, 64]" in r3.stdout and "bom missing" in r3.stdout, f"the problems are named: {r3.stdout.strip()[:200]}")
# 15 entries: refused
few = {k: v for k, v in entries.items() if k != T.KEYS[0]}
fp = os.path.join(work, "few.json")
json.dump(few, open(fp, "w"))
r4 = subprocess.run([sys.executable, "-I", os.path.join(HERE, "palace2_merge_buildings.py"), src, fp, "--check"], capture_output=True, text=True)
check(r4.returncode == 1 and "entries missing: pw:mvv_palace2_00_a_r1" in r4.stdout, "a missing piece entry is refused")
r5 = subprocess.run([sys.executable, "-I", os.path.join(HERE, "palace2_merge_buildings.py"), src, ep, "--check"], capture_output=True, text=True)
check(r5.returncode == 0 and "OK" in r5.stdout, "--check passes on a valid set")
print(f"test_palace2_merge: {ok}/{ok + fail} passed")
sys.exit(1 if fail else 0)
