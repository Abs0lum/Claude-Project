#!/usr/bin/env python3
"""report_merge.py — 10-01 tool hygiene (P8 lesson, twice in one day: a one-mob run of std_quad at 13:58 and of
std_flight_batch at 16:55 overwrote the whole report with its single row).

write_table(path, text, partial): writes `text` (a markdown report) to `path`. When `partial` is true (the run covered only
some mobs) and the file exists, every table row of the OLD file whose mob id is not in the new text is kept, in its old
place; rows for the re-run mobs are replaced by the new ones; anything else in the new text (header, notes) is used as is.
A row's key = its first cell that looks like a mob id (namespace:name). The old file goes to _garbage first (never delete)."""
import datetime
import re
import shutil
from pathlib import Path

ROOT = Path("/home/claude")
ID = re.compile(r"^[a-z0-9_]+:[a-z0-9_.]+$")


def row_key(line):
    if not line.startswith("|"):
        return None
    for cell in line.strip().strip("|").split("|"):
        c = cell.strip()
        if ID.match(c):
            return c
    return None


def merge(old_text, new_text):
    new_lines = new_text.rstrip("\n").split("\n")
    new_rows = {row_key(x): x for x in new_lines if row_key(x)}
    out, used = [], set()
    old_rows = [x for x in old_text.rstrip("\n").split("\n") if row_key(x)]
    first_row = next((i for i, x in enumerate(new_lines) if row_key(x)), None)
    if first_row is None:      # the new run produced no rows: keep the old table under the new header
        hdr_end = next((i for i, x in enumerate(new_lines) if x.startswith("|---")), len(new_lines) - 1)
        return "\n".join(new_lines[:hdr_end + 1] + old_rows + new_lines[hdr_end + 1:]) + "\n"
    head, tail = new_lines[:first_row], [x for x in new_lines[first_row:] if not row_key(x)]
    for x in old_rows:
        k = row_key(x)
        if k in new_rows:
            out.append(new_rows[k])
            used.add(k)
        else:
            out.append(x)
    out += [v for k, v in new_rows.items() if k not in used]
    return "\n".join(head + out + tail) + "\n"


def write_table(path, text, partial):
    path = Path(path)
    if path.exists():
        dst = ROOT / "_garbage" / datetime.datetime.utcnow().strftime("%Y%m%d-%H%M%S") / "reports" / path.name
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, dst)
        if partial:
            text = merge(path.read_text(), text)
    path.write_text(text)
    return path


if __name__ == "__main__":
    old = "# T\n\n| mob | a |\n|---|---|\n| pw:x | 1 |\n| pw:y | 2 |\n| pw:z | 3 |\n"
    new = "# T\n\n| mob | a |\n|---|---|\n| pw:y | 9 |\n| pw:w | 4 |\n"
    got = merge(old, new)
    want = "# T\n\n| mob | a |\n|---|---|\n| pw:x | 1 |\n| pw:y | 9 |\n| pw:z | 3 |\n| pw:w | 4 |\n"
    assert got == want, got
    # a plans-style row: the mob id is the SECOND cell
    old2 = "| plan | mob | g |\n|---|---|---|\n| cetacean | pw:whale_wa | 1 |\n| cetacean | pw:whale_wwa | NOT |\n"
    new2 = "| plan | mob | g |\n|---|---|---|\n| cetacean | pw:whale_wwa | 36 / 0 |\n"
    assert merge(old2, new2) == "| plan | mob | g |\n|---|---|---|\n| cetacean | pw:whale_wa | 1 |\n| cetacean | pw:whale_wwa | 36 / 0 |\n"
    print("report_merge tests OK")
