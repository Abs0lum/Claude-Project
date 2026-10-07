#!/usr/bin/env python3
"""mcstructure.py — read AND write Bedrock .mcstructure files (little-endian NBT), with tag types preserved.

Why typed: a structure's block states must carry the engine's exact tag types (bool states are TAG_Byte, ints TAG_Int,
enum states TAG_String, the palette 'version' TAG_Int). nbt.py (the reader we had) drops types, so it cannot write.

File layout (Bedrock):
  root compound "" {
    format_version: Int 1
    size: List<Int>[3]                        (x, y, z)
    structure: Compound {
      block_indices: List<List<Int>>[2]       layer 0 = blocks, layer 1 = waterlogging (-1 = none);
                                              cell index = (x * size_y + y) * size_z + z   (z fastest)
      entities: List<Compound>
      palette: Compound { default: Compound { block_palette: List<Compound{name, states, version}>,
                                              block_position_data: Compound } }
    }
    structure_world_origin: List<Int>[3]
  }
Self-test: `python3 mcstructure.py FILE...` decodes each file and re-encodes it; PASS = byte-identical.
Complexity: O(cells + palette) for both directions."""
import struct
import sys
from pathlib import Path

END, BYTE, SHORT, INT, LONG, FLOAT, DOUBLE, BYTE_ARRAY, STRING, LIST, COMPOUND, INT_ARRAY, LONG_ARRAY = range(13)
BLOCK_VERSION = 18168865          # the palette 'version' written by 1.21+ / 1.26 engines (read back from his saves)


class Tag:
    """A typed NBT value. For LIST, value is a python list of Tag and elem is the element type."""
    __slots__ = ("type", "value", "elem")

    def __init__(self, type_, value, elem=END):
        self.type, self.value, self.elem = type_, value, elem

    def __repr__(self):
        return f"Tag({self.type},{self.value!r})"

    def plain(self):
        """Untyped python view (for reading / comparing)."""
        if self.type == COMPOUND:
            return {k: v.plain() for k, v in self.value.items()}
        if self.type == LIST:
            return [v.plain() for v in self.value]
        return self.value


def b(v):
    return Tag(BYTE, int(v))


def i(v):
    return Tag(INT, int(v))


def f(v):
    return Tag(FLOAT, float(v))


def s(v):
    return Tag(STRING, str(v))


def lst(elem, items):
    return Tag(LIST, list(items), elem)


def comp(d):
    return Tag(COMPOUND, dict(d))


# ---------------------------------------------------------------- reader
class _R:
    def __init__(self, buf):
        self.b, self.i = buf, 0

    def u(self, fmt):
        v = struct.unpack_from(fmt, self.b, self.i)[0]
        self.i += struct.calcsize(fmt)
        return v

    def string(self):
        n = self.u("<H")
        v = self.b[self.i:self.i + n].decode("utf-8")
        self.i += n
        return v

    def payload(self, t):
        if t == BYTE:
            return Tag(t, self.u("<b"))
        if t == SHORT:
            return Tag(t, self.u("<h"))
        if t == INT:
            return Tag(t, self.u("<i"))
        if t == LONG:
            return Tag(t, self.u("<q"))
        if t == FLOAT:
            return Tag(t, self.u("<f"))
        if t == DOUBLE:
            return Tag(t, self.u("<d"))
        if t == STRING:
            return Tag(t, self.string())
        if t == BYTE_ARRAY:
            n = self.u("<i")
            v = bytes(self.b[self.i:self.i + n])
            self.i += n
            return Tag(t, v)
        if t in (INT_ARRAY, LONG_ARRAY):
            n = self.u("<i")
            fmt = "<%d%s" % (n, "i" if t == INT_ARRAY else "q")
            v = list(struct.unpack_from(fmt, self.b, self.i))
            self.i += struct.calcsize(fmt)
            return Tag(t, v)
        if t == LIST:
            et = self.u("<b")
            n = self.u("<i")
            return Tag(t, [self.payload(et) for _ in range(n)], et)
        if t == COMPOUND:
            d = {}
            while True:
                tt = self.u("<b")
                if tt == END:
                    return Tag(t, d)
                name = self.string()
                d[name] = self.payload(tt)
        raise ValueError(f"unknown tag {t} at {self.i}")


def decode(buf):
    """bytes -> (root name, Tag)."""
    r = _R(buf)
    t = r.u("<b")
    name = r.string()
    return name, r.payload(t)


# ---------------------------------------------------------------- writer
def _w_string(out, v):
    e = v.encode("utf-8")
    out += struct.pack("<H", len(e)) + e


def _w_payload(out, t):
    ty, v = t.type, t.value
    if ty == BYTE:
        out += struct.pack("<b", v)
    elif ty == SHORT:
        out += struct.pack("<h", v)
    elif ty == INT:
        out += struct.pack("<i", v)
    elif ty == LONG:
        out += struct.pack("<q", v)
    elif ty == FLOAT:
        out += struct.pack("<f", v)
    elif ty == DOUBLE:
        out += struct.pack("<d", v)
    elif ty == STRING:
        _w_string(out, v)
    elif ty == BYTE_ARRAY:
        out += struct.pack("<i", len(v)) + bytes(v)
    elif ty in (INT_ARRAY, LONG_ARRAY):
        out += struct.pack("<i", len(v)) + struct.pack("<%d%s" % (len(v), "i" if ty == INT_ARRAY else "q"), *v)
    elif ty == LIST:
        et = t.elem if v == [] else v[0].type
        if any(x.type != et for x in v):
            raise ValueError("mixed list element types")
        out += struct.pack("<b", et) + struct.pack("<i", len(v))
        for x in v:
            _w_payload(out, x)
    elif ty == COMPOUND:
        for k, x in v.items():
            out += struct.pack("<b", x.type)
            _w_string(out, k)
            _w_payload(out, x)
        out += struct.pack("<b", END)
    else:
        raise ValueError(f"cannot write tag type {ty}")


def encode(tag, name=""):
    out = bytearray()
    out += struct.pack("<b", tag.type)
    _w_string(out, name)
    _w_payload(out, tag)
    return bytes(out)


# ---------------------------------------------------------------- structure model
class Structure:
    """A block box with a palette, a waterlog layer and entities. Coordinates are local (0..size-1).
    set(x, y, z, name, states) where states = {state: Tag} (use b()/i()/s()); unset cells are 'structure void' (-1)."""

    def __init__(self, size, origin=(0, 0, 0)):
        self.size = tuple(size)
        self.origin = tuple(origin)
        n = size[0] * size[1] * size[2]
        self.layer0 = [-1] * n
        self.layer1 = [-1] * n
        self.palette = []                      # list of (name, states Tag-compound dict, version)
        self._pal_index = {}
        self.entities = []                     # list of Tag compounds
        self.position_data = {}                # cell index -> Tag compound (block entity data)
        self.layer_type = LIST                 # how block_indices layers are stored (read back from his saves)

    def index(self, x, y, z):
        sx, sy, sz = self.size
        if not (0 <= x < sx and 0 <= y < sy and 0 <= z < sz):
            raise IndexError((x, y, z), self.size)
        return (x * sy + y) * sz + z

    def _pal(self, name, states, version=BLOCK_VERSION):
        key = (name, tuple(sorted((k, v.type, v.value) for k, v in states.items())), version)
        if key not in self._pal_index:
            self._pal_index[key] = len(self.palette)
            self.palette.append((name, dict(states), version))
        return self._pal_index[key]

    def set(self, x, y, z, name, states=None, waterlogged=False):
        self.layer0[self.index(x, y, z)] = self._pal(name, states or {})
        if waterlogged:
            self.layer1[self.index(x, y, z)] = self._pal("minecraft:water", {"liquid_depth": i(0)})

    def get(self, x, y, z):
        k = self.layer0[self.index(x, y, z)]
        return None if k < 0 else self.palette[k]

    def _layer(self, cells):
        if self.layer_type == INT_ARRAY:
            return Tag(INT_ARRAY, list(cells))
        return lst(INT, [i(v) for v in cells])

    def to_tag(self):
        pal = [comp({"name": s(n), "states": comp(st), "version": i(v)}) for n, st, v in self.palette]
        pos = comp({str(k): v for k, v in sorted(self.position_data.items())})
        return comp({
            "format_version": i(1),
            "size": lst(INT, [i(v) for v in self.size]),
            "structure": comp({
                "block_indices": lst(self.layer_type, [self._layer(self.layer0)] if getattr(self, "single_layer", False)
                                     else [self._layer(self.layer0), self._layer(self.layer1)]),
                "entities": lst(COMPOUND, self.entities),
                "palette": comp({"default": comp({"block_palette": lst(COMPOUND, pal), "block_position_data": pos})}),
            }),
            "structure_world_origin": lst(INT, [i(v) for v in self.origin]),
        })

    def to_bytes(self):
        return encode(self.to_tag())

    @classmethod
    def from_bytes(cls, buf):
        _, root = decode(buf)
        r = root.value
        st = cls([t.value for t in r["size"].value], [t.value for t in r["structure_world_origin"].value])
        sv = r["structure"].value
        for p in sv["palette"].value["default"].value["block_palette"].value:
            pv = p.value
            st.palette.append((pv["name"].value, dict(pv["states"].value), pv["version"].value))
        layers = sv["block_indices"].value
        st.layer_type = layers[0].type
        unpack = (lambda L: list(L.value)) if st.layer_type == INT_ARRAY else (lambda L: [t.value for t in L.value])
        st.layer0 = unpack(layers[0])
        st.layer1 = unpack(layers[1]) if len(layers) > 1 else [-1] * len(st.layer0)
        st.single_layer = len(layers) == 1     # world-database templates store one INT_ARRAY layer
        st.entities = list(sv["entities"].value)
        st.position_data = {int(k): v for k, v in sv["palette"].value["default"].value["block_position_data"].value.items()}
        return st


def _selftest(paths):
    ok = True
    for p in paths:
        buf = Path(p).read_bytes()
        name, tag = decode(buf)
        same = encode(tag, name) == buf
        st = Structure.from_bytes(buf)
        print(f"{'PASS' if same else 'FAIL'} {Path(p).name}: {len(buf):,} B, size {st.size}, palette {len(st.palette)}, "
              f"entities {len(st.entities)}, raw re-encode {'byte-identical' if same else 'DIFFERENT'}")
        ok &= same
    return ok


if __name__ == "__main__":
    sys.exit(0 if _selftest(sys.argv[1:]) else 1)
