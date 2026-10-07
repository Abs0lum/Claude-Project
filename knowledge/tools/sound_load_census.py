#!/usr/bin/env python3
"""sound_load_census.py — task #169, his witness (16:47 10-02): "on PS5 sounds take a LONG time to load" (he hopes scanner
removal fixes it; investigate, don't promise). Read-only.

For a stack (stack_now PW_STACK), every sound file that sound_definitions.json names (top pack per definition name wins):
format (ogg / wav / fsb / mp3), bytes, channels + sample rate + duration (Ogg Vorbis identification header + last granule;
WAV fmt chunk), and the definition's flags: "stream" (decoded while playing instead of fully at load), "load_on_low_memory",
"is3D". Also: sound files present in a pack that NO definition names (dead weight in the download, not loaded), and
definitions that name a file no pack holds (the engine logs these at load).
Usage: PW_STACK=<name> python3 tools/sound_load_census.py <label> -> _docs/sound/SOUND-LOAD-CENSUS-<label>.json"""
import io
import json
import struct
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path("/home/claude")
sys.path.insert(0, str(ROOT / "tools"))
import stack_now as SN  # noqa: E402

EXT = (".ogg", ".wav", ".fsb", ".mp3")


def ogg_info(data):
    try:
        i = data.index(b"\x01vorbis")
        ch = data[i + 11]
        rate = struct.unpack("<I", data[i + 12:i + 16])[0]
        j = data.rindex(b"OggS")
        gran = struct.unpack("<q", data[j + 6:j + 14])[0]
        return ch, rate, round(gran / rate, 2) if rate else None
    except Exception:  # noqa: BLE001
        return None, None, None


def wav_info(data):
    try:
        i = data.index(b"fmt ")
        ch, rate = struct.unpack("<HI", data[i + 10:i + 16])
        bits = struct.unpack("<H", data[i + 22:i + 24])[0]
        j = data.index(b"data")
        n = struct.unpack("<I", data[j + 4:j + 8])[0]
        return ch, rate, round(n / (rate * ch * bits / 8), 2)
    except Exception:  # noqa: BLE001
        return None, None, None


def main():
    label = sys.argv[1] if len(sys.argv) > 1 else "final"
    P = SN.packs()[:-1]                              # vanilla's own sounds are the game's, not ours
    defs, owner = {}, {}
    for p in P:
        d = p.json("sounds/sound_definitions.json")
        for name, v in ((d or {}).get("sound_definitions") or {}).items():
            if name not in defs:
                defs[name], owner[name] = v, p
    files, missing = {}, []
    for name, v in defs.items():
        for s in v.get("sounds", []) if isinstance(v, dict) else []:
            entry = {"name": s} if isinstance(s, str) else dict(s)
            path = entry.get("name")
            if not path:
                continue
            hit = None
            for p in P:
                for e in EXT:
                    if p.has(path + e):
                        hit = (p, path + e)
                        break
                if hit:
                    break
            if not hit:
                missing.append((name, path))
                continue
            p, f = hit
            key = f"{p.name}:{f}"
            if key in files:
                files[key]["defs"] += 1
                continue
            data = p.read(f)
            ch, rate, dur = ogg_info(data) if f.endswith(".ogg") else wav_info(data) if f.endswith(".wav") else (None,) * 3
            files[key] = {"pack": p.name, "file": f, "bytes": len(data), "fmt": f.rsplit(".", 1)[1], "channels": ch,
                          "rate": rate, "seconds": dur, "stream": bool(entry.get("stream")),
                          "load_on_low_memory": bool(entry.get("load_on_low_memory")), "defs": 1}
    referenced = {(r["pack"], r["file"]) for r in files.values()}
    unreferenced = Counter()
    unref_bytes = Counter()
    for p in P:
        for f in p.files:
            if f.startswith("sounds/") and f.endswith(EXT) and (p.name, f) not in referenced:
                unreferenced[p.name] += 1
                unref_bytes[p.name] += 0
    by_pack = defaultdict(lambda: Counter())
    for r in files.values():
        b = by_pack[r["pack"]]
        b["files"] += 1
        b["bytes"] += r["bytes"]
        b["seconds"] += r["seconds"] or 0
        b["stream"] += r["stream"]
        b["stereo"] += (r["channels"] or 0) > 1
        b[f"fmt_{r['fmt']}"] += 1
        b["rate_48k+"] += (r["rate"] or 0) >= 48000
    out = {"stack": [p.name for p in P], "definitions": len(defs), "files_loaded": len(files),
           "bytes_loaded": sum(r["bytes"] for r in files.values()),
           "seconds_loaded": round(sum(r["seconds"] or 0 for r in files.values()), 1),
           "streamed": sum(r["stream"] for r in files.values()), "missing_refs": len(missing),
           "missing_examples": missing[:15], "unreferenced_files": dict(unreferenced),
           "by_pack": {k: dict(v) for k, v in by_pack.items()},
           "largest": sorted(files.values(), key=lambda r: -r["bytes"])[:25]}
    dst = ROOT / f"_docs/sound/SOUND-LOAD-CENSUS-{label}.json"
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(json.dumps(out, indent=1))
    print(json.dumps({k: v for k, v in out.items() if k not in ("largest", "missing_examples")}, indent=1))
    for r in out["largest"][:10]:
        print(" ", r["pack"], r["file"], r["bytes"], r["fmt"], r["channels"], r["rate"], r["seconds"], "stream" if r["stream"] else "")


if __name__ == "__main__":
    main()
