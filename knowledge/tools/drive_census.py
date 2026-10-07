#!/usr/bin/env python3
"""drive_census.py — verify Abs0lum's Drive 'Packs' uploads against our delivered bytes (two-lists rule, D-C247).

For every file in the batch (a JSON list of {title, id, fileSize} from the Drive listing):
  * small files (<= 2 MB): full download over HTTP range -> md5 -> compared with the delivery ledger / local copy
  * big files: length + last 64 KB + the whole ZIP central directory (every member name/CRC32/sizes/offsets) + three
    64 KB samples at 10/50/90 % -> compared byte-for-byte with the LOCAL delivered file when we have one, else with
    the earlier Drive copy of the same name (proves 'same bytes as the earlier upload', not provenance)
Nothing is written to the Drive.  Output: a table + _logs/drive_census_<date>.json.
"""
import hashlib, json, re, sys, time
from pathlib import Path
sys.path.insert(0, "/home/claude/tools")
import remote_zip as RZ

OUT = Path("/mnt/user-data/outputs")
LEDGER = Path("/home/claude/_logs/delivery_ledger.md")


def ledger_md5s():
    m = {}
    for line in LEDGER.read_text().splitlines():
        r = re.search(r"(\S+\.mcpack) ([\d,]+) B md5 ([0-9a-f]{32})", line)
        if r: m[r.group(1)] = (int(r.group(2).replace(",", "")), r.group(3))
    return m


def local_ranges(path, total):
    """(tail64k, cd_bytes, samples) of a local file, same slices as the remote read."""
    data = path.read_bytes()
    assert len(data) == total
    tail = data[max(0, total - 65536):]
    cd_off, cd_size = cd_span(tail, total)
    cd = data[cd_off:cd_off + cd_size]
    samples = [data[o:o + 65536] for o in sample_offsets(total)]
    return tail, cd, samples


def cd_span(tail, total):
    import struct
    i = tail.rfind(b"PK\x05\x06"); assert i >= 0
    n, cd_size, cd_off = struct.unpack("<HII", tail[i + 10:i + 20])
    if cd_off == 0xFFFFFFFF or n == 0xFFFF:
        j = tail.rfind(b"PK\x06\x06"); z64 = tail[j:j + 56]
        cd_size, cd_off = struct.unpack("<QQ", z64[40:56])
    return cd_off, cd_size


def sample_offsets(total):
    return [max(0, min(total - 65536, int(total * f))) for f in (0.10, 0.50, 0.90)]


def remote_ranges(url, total):
    tail = RZ.fetch(url, max(0, total - 65536), total - 1)
    cd_off, cd_size = cd_span(tail, total)
    cd = RZ.fetch(url, cd_off, cd_off + cd_size - 1)
    samples = [RZ.fetch(url, o, o + 65535) for o in sample_offsets(total)]
    return tail, cd, samples


def check(item, earlier=None):
    name, fid, size = item["title"], item["id"], int(item["fileSize"])
    url = RZ.drive_url(fid)
    total = RZ.head_len(url)
    row = {"name": name, "id": fid, "drive_size": size, "http_len": total, "method": None, "verdict": None, "note": ""}
    if total != size:
        row["verdict"] = "SIZE-MISMATCH"; return row
    led = ledger_md5s().get(name)
    local = OUT / name
    if total <= 2_000_000:
        data = b""
        step = 1_000_000
        for o in range(0, total, step):
            data += RZ.fetch(url, o, min(total, o + step) - 1)
        md5 = hashlib.md5(data).hexdigest()
        row["method"] = "full md5"; row["md5"] = md5
        if led:
            row["verdict"] = "MATCH ledger md5" if md5 == led[1] else f"MD5-DIFF (ledger {led[1][:8]})"
        elif local.exists():
            row["verdict"] = "MATCH local md5" if md5 == hashlib.md5(local.read_bytes()).hexdigest() else "MD5-DIFF local"
        else:
            row["verdict"] = "md5 recorded (no ledger row / no local copy)"
        return row
    tail, cd, samples = remote_ranges(url, total)
    row["cd_bytes"] = len(cd); row["cd_md5"] = hashlib.md5(cd).hexdigest()
    if local.exists():
        lt, lc, ls = local_ranges(local, total)
        ok = (lt == tail) and (lc == cd) and all(a == b for a, b in zip(ls, samples))
        row["method"] = "len + tail64k + central directory + 3x64k samples vs LOCAL delivered file"
        row["verdict"] = "MATCH local (CD+tail+samples)" if ok else "DIFF vs local"
        if led: row["note"] = f"ledger md5 {led[1]} (local file)"
    elif earlier:
        eurl = RZ.drive_url(earlier["id"]); etot = RZ.head_len(eurl)
        if etot != total:
            row["verdict"] = "DIFF vs earlier Drive copy (size)"; return row
        et, ec, es = remote_ranges(eurl, etot)
        ok = (et == tail) and (ec == cd) and all(a == b for a, b in zip(es, samples))
        row["method"] = "len + tail64k + central directory + 3x64k samples vs EARLIER Drive copy " + earlier["createdTime"][:10]
        row["verdict"] = "MATCH earlier Drive copy" if ok else "DIFF vs earlier Drive copy"
    else:
        row["method"] = "central directory read only"; row["verdict"] = "no reference (recorded)"
    return row


def main():
    batch = json.load(open(sys.argv[1]))
    earlier = json.load(open(sys.argv[2])) if len(sys.argv) > 2 else {}
    rows = []
    for it in batch:
        t0 = time.time()
        try:
            r = check(it, earlier.get(it["title"]))
        except Exception as e:
            r = {"name": it["title"], "id": it["id"], "verdict": f"ERROR {type(e).__name__}: {str(e)[:120]}"}
        r["secs"] = round(time.time() - t0, 1)
        rows.append(r); print(f"{r['name']:70s} {r.get('drive_size', '?'):>12} {r['verdict']:45s} {r.get('method', '')[:40]} {r['secs']}s", flush=True)
    out = Path("/home/claude/_logs/drive_census_2026-09-27.json"); json.dump(rows, open(out, "w"), indent=1)
    print("wrote", out)


if __name__ == "__main__":
    main()
