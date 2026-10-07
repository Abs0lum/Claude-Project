#!/usr/bin/env python3
"""nbt_typed.py — little-endian (Bedrock) NBT with the TAG TYPE kept on every value, so a file can be read, edited
and written back byte-for-byte (tools/nbt.py reads only and drops the types).

Model: every value is a Tag(type, value).
  compound -> value is a dict name -> Tag (insertion order = file order)
  list     -> value is (element_type, [Tag, ...])
  arrays   -> value is a Python list of ints
Helpers b()/s()/i()/l()/f()/d()/st()/cmp()/lst() build tags without spelling the type numbers.

Complexity: O(n) in the file size for both read and write."""
import struct
from dataclasses import dataclass
from typing import Any

END, BYTE, SHORT, INT, LONG, FLOAT, DOUBLE, BYTE_ARRAY, STRING, LIST, COMPOUND, INT_ARRAY, LONG_ARRAY = range(13)
_SCALAR = {BYTE: "<b", SHORT: "<h", INT: "<i", LONG: "<q", FLOAT: "<f", DOUBLE: "<d"}


@dataclass
class Tag:
    type: int
    value: Any


class _Reader:
    def __init__(self, buf):
        self.b, self.i = buf, 0

    def take(self, fmt):
        v = struct.unpack_from(fmt, self.b, self.i)[0]
        self.i += struct.calcsize(fmt)
        return v

    def string(self):
        n = self.take("<H")
        s = self.b[self.i:self.i + n].decode("utf-8")
        self.i += n
        return s

    def payload(self, t):
        if t in _SCALAR:
            return Tag(t, self.take(_SCALAR[t]))
        if t == STRING:
            return Tag(t, self.string())
        if t == BYTE_ARRAY:
            n = self.take("<i")
            v = list(struct.unpack_from("<%db" % n, self.b, self.i))
            self.i += n
            return Tag(t, v)
        if t in (INT_ARRAY, LONG_ARRAY):
            n = self.take("<i")
            fmt = "<%d%s" % (n, "i" if t == INT_ARRAY else "q")
            v = list(struct.unpack_from(fmt, self.b, self.i))
            self.i += struct.calcsize(fmt)
            return Tag(t, v)
        if t == LIST:
            et = self.take("<b")
            n = self.take("<i")
            return Tag(t, (et, [self.payload(et) for _ in range(n)]))
        if t == COMPOUND:
            d = {}
            while True:
                tt = self.take("<b")
                if tt == END:
                    return Tag(t, d)
                name = self.string()
                d[name] = self.payload(tt)
        raise ValueError(f"unknown tag {t} at {self.i}")


def load(buf):
    """bytes -> (root name, Tag)."""
    r = _Reader(buf)
    t = r.take("<b")
    name = r.string()
    return name, r.payload(t)


def _w_string(out, s):
    raw = s.encode("utf-8")
    out += struct.pack("<H", len(raw)) + raw


def _w_payload(out, tag):
    t, v = tag.type, tag.value
    if t in _SCALAR:
        out += struct.pack(_SCALAR[t], v)
    elif t == STRING:
        _w_string(out, v)
    elif t == BYTE_ARRAY:
        out += struct.pack("<i", len(v)) + struct.pack("<%db" % len(v), *v)
    elif t == INT_ARRAY:
        out += struct.pack("<i", len(v)) + struct.pack("<%di" % len(v), *v)
    elif t == LONG_ARRAY:
        out += struct.pack("<i", len(v)) + struct.pack("<%dq" % len(v), *v)
    elif t == LIST:
        et, items = v
        out += struct.pack("<bi", et if items or et else END, len(items))
        for it in items:
            assert it.type == et, f"list element type {it.type} != {et}"
            _w_payload(out, it)
    elif t == COMPOUND:
        for name, it in v.items():
            out += struct.pack("<b", it.type)
            _w_string(out, name)
            _w_payload(out, it)
        out += struct.pack("<b", END)
    else:
        raise ValueError(f"unknown tag {t}")


def dump(tag, name=""):
    """Tag -> bytes (root compound with its name)."""
    out = bytearray()
    out += struct.pack("<b", tag.type)
    _w_string(out, name)
    _w_payload(out, tag)
    return bytes(out)


def plain(tag):
    """Tag tree -> plain Python (for reading / comparing)."""
    if tag.type == COMPOUND:
        return {k: plain(v) for k, v in tag.value.items()}
    if tag.type == LIST:
        return [plain(x) for x in tag.value[1]]
    return tag.value


# --- builders
def b(v): return Tag(BYTE, int(v))
def s(v): return Tag(SHORT, int(v))
def i(v): return Tag(INT, int(v))
def l(v): return Tag(LONG, int(v))  # noqa: E741,E743
def f(v): return Tag(FLOAT, float(v))
def d(v): return Tag(DOUBLE, float(v))
def st(v): return Tag(STRING, str(v))
def cmp(**kw): return Tag(COMPOUND, dict(kw))
def cmpd(dct): return Tag(COMPOUND, dict(dct))
def lst(et, items): return Tag(LIST, (et, list(items)))
