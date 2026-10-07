#!/usr/bin/env python3
"""p0_fetch_shots.py — download every P0 screenshot listed in _intake/p0-shots/manifest.py from the Drive
into _intake/p0-shots/<stem>.png (byte-size verified against the Drive listing), then write the P10 intake
ledger (_logs/intake_ledger.md: one UNVIEWED line per file) and a time->step map (p0-shots/stepmap.json).
Re-runnable: files already present with the right size are skipped."""
import json, os, sys, time, urllib.request
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, "tools"); sys.path.insert(0, "_intake/p0-shots")
import remote_zip
from manifest import FILES, VERDICTS

OUT = "_intake/p0-shots"
os.makedirs(OUT, exist_ok=True)

def fetch(item):
    stem, fid, size = item
    path = os.path.join(OUT, f"{stem}.png")
    if os.path.exists(path) and os.path.getsize(path) == size:
        return stem, "cached", size
    for attempt in range(3):
        try:
            url = f"https://drive.google.com/uc?export=download&id={fid}"
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=120) as r:
                data = r.read()
            if len(data) != size or not data.startswith(b"\x89PNG"):
                # large-file interstitial: resolve the confirm url
                url = remote_zip.drive_url(fid)
                req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req, timeout=120) as r:
                    data = r.read()
            if len(data) == size and data.startswith(b"\x89PNG"):
                with open(path, "wb") as f:
                    f.write(data)
                return stem, "ok", len(data)
            last = f"size {len(data)} != {size} png={data[:4]!r}"
        except Exception as e:
            last = repr(e)
        time.sleep(2 + attempt * 3)
    return stem, "FAIL " + last, 0

def hhmmss(stem):
    s = stem[:6]
    return f"{s[0:2]}:{s[2:4]}:{s[4:6]}"

def stepmap():
    """Assign each shot to the step whose verdict came next AFTER the shot (shots precede their verdict)."""
    out = {}
    for stem, fid, size in FILES:
        t = hhmmss(stem)
        step = None
        for sid, vt in VERDICTS:
            if t <= vt:
                step = sid
                break
        out[stem] = step or "after-q9"
    return out

if __name__ == "__main__":
    with ThreadPoolExecutor(max_workers=6) as ex:
        results = list(ex.map(fetch, FILES))
    ok = [r for r in results if r[1] in ("ok", "cached")]
    bad = [r for r in results if r[1] not in ("ok", "cached")]
    print(f"downloaded/cached {len(ok)}/{len(FILES)}; failures {len(bad)}")
    for r in bad:
        print("  ", r)
    sm = stepmap()
    json.dump(sm, open(os.path.join(OUT, "stepmap.json"), "w"), indent=1)
    counts = {}
    for stem, step in sm.items():
        counts[step] = counts.get(step, 0) + 1
    print("shots per step (by time; confirm by content):")
    for sid, vt in VERDICTS:
        print(f"  {sid:4s} {vt}  {counts.get(sid, 0)}")
    print("  after-q9", counts.get("after-q9", 0))
    if "--ledger" in sys.argv:
        now = time.strftime("%H:%M")
        lines = [f"\n## INTAKE {now} CT 09-27 — P0 run screenshots from the Drive folder 12xuiuVkNB0uHZ4pldPD1NM7NvSXH39xY "
                 f"({len(FILES)} files, Screenshot_20260927-191958..193834; step by time = hypothesis until viewed)"]
        for i, (stem, fid, size) in enumerate(FILES, 1):
            lines.append(f"- S{i:03d} {stem}.png ({size:,} B, step-by-time {sm[stem]}) — UNVIEWED")
        lines.append(f"  -> 0/{len(FILES)} VIEWED")
        with open("_logs/intake_ledger.md", "a") as f:
            f.write("\n".join(lines) + "\n")
        print("ledger written")
