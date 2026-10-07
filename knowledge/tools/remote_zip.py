#!/usr/bin/env python3
"""remote_zip.py — read selected entries out of a huge zip over HTTP range requests (no full download).

Built for the Patrix Java source archives on Drive (400 MB – 1.7 GB): the confirm-page dance from
drive_pull.sh gives a usercontent URL that answers 206 to Range requests, so only the central
directory (~1 MB) and the wanted members are transferred.

Usage:
  remote_zip.py <drive-file-id> list  [substring ...]
  remote_zip.py <drive-file-id> get   <out-dir> <substring ...>
"""
import io, os, re, struct, sys, zlib, subprocess, urllib.request

def drive_url(fid):
    html = subprocess.run(["curl", "-sL", f"https://drive.google.com/uc?export=download&id={fid}"],
                          capture_output=True).stdout.decode("utf-8", "replace")
    m = re.search(r'name="uuid" value="([^"]+)"', html)
    if not m:
        return f"https://drive.google.com/uc?export=download&id={fid}"
    return f"https://drive.usercontent.google.com/download?id={fid}&export=download&confirm=t&uuid={m.group(1)}"

def fetch(url, start, end):
    req = urllib.request.Request(url, headers={"Range": f"bytes={start}-{end}"})
    with urllib.request.urlopen(req, timeout=120) as r:
        assert r.status == 206, r.status
        return r.read()

def head_len(url):
    req = urllib.request.Request(url, headers={"Range": "bytes=0-0"})
    with urllib.request.urlopen(req, timeout=60) as r:
        cr = r.headers["Content-Range"]
        return int(cr.split("/")[1])

def central_directory(url, total):
    tail = fetch(url, max(0, total - 65536), total - 1)
    i = tail.rfind(b"PK\x05\x06")
    assert i >= 0, "EOCD not found"
    eocd = tail[i:i + 22]
    n, cd_size, cd_off = struct.unpack("<HII", eocd[10:20])
    if cd_off == 0xFFFFFFFF or n == 0xFFFF:      # zip64
        j = tail.rfind(b"PK\x06\x06")
        assert j >= 0
        z64 = tail[j:j + 56]
        n = struct.unpack("<Q", z64[32:40])[0]
        cd_size, cd_off = struct.unpack("<QQ", z64[40:56])
    cd = fetch(url, cd_off, cd_off + cd_size - 1)
    entries = []
    p = 0
    while p < len(cd):
        assert cd[p:p + 4] == b"PK\x01\x02"
        (flags, method, crc, csize, usize, fnlen, exlen, cmlen) = struct.unpack("<HHIIIHHH", cd[p + 8:p + 10] + cd[p + 10:p + 12] + cd[p + 16:p + 20] + cd[p + 20:p + 24] + cd[p + 24:p + 28] + cd[p + 28:p + 30] + cd[p + 30:p + 32] + cd[p + 32:p + 34])
        lho = struct.unpack("<I", cd[p + 42:p + 46])[0]
        name = cd[p + 46:p + 46 + fnlen].decode("utf-8", "replace")
        extra = cd[p + 46 + fnlen:p + 46 + fnlen + exlen]
        if lho == 0xFFFFFFFF or csize == 0xFFFFFFFF or usize == 0xFFFFFFFF:   # zip64 extra
            q = 0
            while q + 4 <= len(extra):
                hid, hsz = struct.unpack("<HH", extra[q:q + 4])
                if hid == 1:
                    d = extra[q + 4:q + 4 + hsz]; k = 0
                    if usize == 0xFFFFFFFF: usize = struct.unpack("<Q", d[k:k + 8])[0]; k += 8
                    if csize == 0xFFFFFFFF: csize = struct.unpack("<Q", d[k:k + 8])[0]; k += 8
                    if lho == 0xFFFFFFFF: lho = struct.unpack("<Q", d[k:k + 8])[0]; k += 8
                q += 4 + hsz
        entries.append((name, method, csize, usize, lho, crc))
        p += 46 + fnlen + exlen + cmlen
    return entries

def get_member(url, e):
    name, method, csize, usize, lho, crc = e
    hdr = fetch(url, lho, lho + 29)
    assert hdr[:4] == b"PK\x03\x04"
    fnlen, exlen = struct.unpack("<HH", hdr[26:30])
    start = lho + 30 + fnlen + exlen
    data = fetch(url, start, start + csize - 1) if csize else b""
    if method == 8:
        data = zlib.decompress(data, -15)
    elif method != 0:
        raise RuntimeError(f"unsupported method {method} for {name}")
    assert (zlib.crc32(data) & 0xFFFFFFFF) == crc, f"crc mismatch {name}"
    return data

def main():
    fid, cmd = sys.argv[1], sys.argv[2]
    url = drive_url(fid)
    total = head_len(url)
    entries = central_directory(url, total)
    print(f"# {total:,} B, {len(entries)} entries", file=sys.stderr)
    if cmd == "list":
        subs = [s.lower() for s in sys.argv[3:]]
        for e in entries:
            if not subs or any(s in e[0].lower() for s in subs):
                print(f"{e[3]:>10} {e[0]}")
    elif cmd == "get":
        out = sys.argv[3]; subs = [s.lower() for s in sys.argv[4:]]
        for e in entries:
            if e[0].endswith("/") or not any(s in e[0].lower() for s in subs):
                continue
            data = get_member(url, e)
            dst = os.path.join(out, e[0]); os.makedirs(os.path.dirname(dst), exist_ok=True)
            open(dst, "wb").write(data); print(f"{len(data):>10} {e[0]}")

if __name__ == "__main__":
    main()
