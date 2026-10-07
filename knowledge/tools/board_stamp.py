#!/usr/bin/env python3
"""board_stamp.py "note" — set the STATUS-BOARD 'Updated HH:MM CT MM-DD (note).' line from the CLOCK at write time (no typed stamps)."""
import re, sys, datetime
from pathlib import Path
from zoneinfo import ZoneInfo
b = Path("/home/claude/_docs/recheck/STATUS-BOARD.md"); t = b.read_text()
now = datetime.datetime.now(ZoneInfo("America/Chicago")).strftime("%H:%M CT %m-%d")
m = re.search(r"Updated \d\d:\d\d CT \d\d-\d\d \(.*?\)\.(?= \*\*HIS)", t)   # the note may hold parentheses
assert m, "stamp line not found"
b.write_text(t.replace(m.group(0), f"Updated {now} ({' '.join(sys.argv[1:])})."))
print(f"board stamped {now}")
