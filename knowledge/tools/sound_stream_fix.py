#!/usr/bin/env python3
"""sound_stream_fix.py — task #169 (his PS5 witness: sounds take a LONG time to load). Mechanism found
(tools/sound_load_census.py, D-C475): RP-02's ambience set = 120 stereo Ogg files, 85.5 MB, 83 minutes of audio, NONE
marked "stream" -> the game loads every one of them whole when the packs load (about 1.5 GB if decoded to 16-bit PCM,
counting re-used files per definition). Vanilla marks long sounds (music, long ambience) "stream": true: they are read
from the file while they play. This marks every RP-02 sound of 10 s or longer "stream": true; short one-shots stay
preloaded (instant). No audio file is changed. Applied to RP-02 2.0.7 (undelivered); backup next to the report."""
import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, "/home/claude/tools")
import sound_load_census as S  # noqa: E402
import spawn_gen as G  # noqa: E402

RP = Path("/home/claude/_build/rp02-207")
DEFS = RP / "sounds/sound_definitions.json"
BACKUP = Path("/home/claude/_docs/sound/rp02-207_sound_definitions.before_stream.json")
MIN_SECONDS = 10.0

if not BACKUP.exists():
    BACKUP.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(DEFS, BACKUP)
d = G.load(BACKUP)
changed, kept, secs = 0, 0, 0.0
for name, v in d["sound_definitions"].items():
    out = []
    for s in v.get("sounds", []):
        e = {"name": s} if isinstance(s, str) else dict(s)
        f = RP / (e["name"] + ".ogg")
        dur = S.ogg_info(f.read_bytes())[2] if f.exists() else None
        if dur is not None and dur >= MIN_SECONDS:
            e["stream"] = True
            changed += 1
            secs += dur
        else:
            kept += 1
        out.append(e)
    v["sounds"] = out
DEFS.write_text(json.dumps(d, indent=1))
print(f"streamed {changed} entries ({secs / 60:.1f} min of audio); preloaded {kept} short entries")
