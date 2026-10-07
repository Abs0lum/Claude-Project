#!/usr/bin/env python3
"""Pure-python reader for a Bedrock LevelDB: the write-ahead log (.log, uncompressed)
and the sorted tables (.ldb, block format with raw-zlib / snappy-none compression).
(Restored 2026-10-02 from project knowledge claude/tools/ldbscan.py.)

The WAL is standard leveldb log format: 32 KiB blocks, each record
  crc32c(4 LE) | length(2 LE) | type(1)   with type 1=FULL 2=FIRST 3=MIDDLE 4=LAST
whose assembled payload is a WriteBatch:
  seq(8 LE) | count(4 LE) | [ tag(1) varint-keylen key (varint-vallen value if tag==1) ]*

The .ldb table format is: [data blocks][meta][index block][footer(48)]; the footer's
last 8 bytes are the magic 0xdb4775248b80fb57, preceded by two BlockHandles
(metaindex, index) as varint pairs.  Each block is followed by 1 type byte + crc(4).
Bedrock uses compression type 0 (none), 2 (raw deflate) and 4 (zstd).
"""
import struct
import sys
import zlib

BLOCK = 32768


def varint(buf, i):
    r = s = 0
    while True:
        b = buf[i]
        i += 1
        r |= (b & 0x7F) << s
        if not b & 0x80:
            return r, i
        s += 7


def wal_entries(path):
    data = open(path, "rb").read()
    out = []
    pos = 0
    frag = b""
    while pos + 7 <= len(data):
        off = pos % BLOCK
        if BLOCK - off < 7:
            pos += BLOCK - off
            continue
        _crc, ln, typ = struct.unpack_from("<IHB", data, pos)
        pos += 7
        payload = data[pos:pos + ln]
        pos += ln
        if typ == 0:
            continue
        if typ == 1:
            batch = payload
        elif typ == 2:
            frag = payload
            continue
        elif typ == 3:
            frag += payload
            continue
        elif typ == 4:
            batch = frag + payload
            frag = b""
        else:
            continue
        if len(batch) < 12:
            continue
        count = struct.unpack_from("<I", batch, 8)[0]
        i = 12
        for _ in range(count):
            if i >= len(batch):
                break
            tag = batch[i]
            i += 1
            kl, i = varint(batch, i)
            key = batch[i:i + kl]
            i += kl
            if tag == 1:
                vl, i = varint(batch, i)
                val = batch[i:i + vl]
                i += vl
            else:
                val = None
            out.append((key, val))
    return out


def block_handle(buf, i):
    off, i = varint(buf, i)
    size, i = varint(buf, i)
    return off, size, i


def read_block(data, off, size):
    raw = data[off:off + size]
    ctype = data[off + size]
    if ctype == 0:
        return raw
    if ctype in (2, 4):
        # Mojang leveldb: 2 = zlib, 4 = raw deflate (2026-10-02: type 4 seen as raw deflate in a 1.26 world,
        # not zstd); try both decoders so either labelling works
        for wbits in ((15, -15) if ctype == 2 else (-15, 15)):
            try:
                return zlib.decompress(raw, wbits)
            except zlib.error:
                pass
    if ctype == 1:
        try:
            import snappy
            return snappy.decompress(raw)
        except Exception:
            return None
    if ctype == 4:
        try:
            import zstandard
            return zstandard.ZstdDecompressor().decompressobj().decompress(raw)  # frames may lack a content size
        except Exception:
            return None
    return None


def block_kvs(blk):
    """Walk a leveldb data/index block's restart-prefixed entries."""
    if blk is None or len(blk) < 4:
        return []
    nrestart = struct.unpack_from("<I", blk, len(blk) - 4)[0]
    end = len(blk) - 4 - 4 * nrestart
    out = []
    i = 0
    last = b""
    while i < end:
        shared, i = varint(blk, i)
        nonshared, i = varint(blk, i)
        vlen, i = varint(blk, i)
        key = last[:shared] + blk[i:i + nonshared]
        i += nonshared
        val = blk[i:i + vlen]
        i += vlen
        last = key
        out.append((key, val))
    return out


def ldb_entries(path):
    data = open(path, "rb").read()
    magic = struct.unpack_from("<Q", data, len(data) - 8)[0]
    assert magic == 0xDB4775248B80FB57, "bad table magic %x" % magic
    foot = data[len(data) - 48:len(data) - 8]
    _mo, _ms, i = block_handle(foot, 0)
    io_, is_, _ = block_handle(foot, i)
    index = read_block(data, io_, is_)
    out = []
    for _k, handle in block_kvs(index):
        off, size, _ = block_handle(handle, 0)
        blk = read_block(data, off, size)
        for k, v in block_kvs(blk):
            # internal key = user key + 8-byte (seq<<8|type) trailer
            out.append((k[:-8], v))
    return out


def label(k):
    try:
        s = k.decode("utf-8")
        if s.isprintable():
            return s
    except Exception:
        pass
    return repr(k)


if __name__ == "__main__":
    for p in sys.argv[1:]:
        ent = wal_entries(p) if p.endswith(".log") else ldb_entries(p)
        print("== %s: %d entries" % (p, len(ent)))
        seen = {}
        for k, v in ent:
            lab = label(k)
            if lab.startswith("b'") or lab.startswith('b"'):
                lab = "<binary len %d>" % len(k)
            seen.setdefault(lab if len(lab) < 80 else lab[:80], []).append(len(v) if v else -1)
        for lab in sorted(seen):
            n = seen[lab]
            if lab.startswith("<binary"):
                continue
            print("   %-60s x%-4d bytes %s" % (lab, len(n), n[:4]))
        nb = sum(1 for k, _ in ent if label(k).startswith(("b'", 'b"')))
        print("   (%d binary/chunk keys)" % nb)
