#!/usr/bin/env python3
"""Little-endian (Bedrock) NBT reader, enough for structure templates."""
import struct

TAG_END, TAG_BYTE, TAG_SHORT, TAG_INT, TAG_LONG, TAG_FLOAT, TAG_DOUBLE = range(7)
TAG_BYTE_ARRAY, TAG_STRING, TAG_LIST, TAG_COMPOUND, TAG_INT_ARRAY, TAG_LONG_ARRAY = range(7, 13)


class Reader:
    def __init__(self, buf):
        self.b = buf
        self.i = 0

    def u(self, fmt, n):
        v = struct.unpack_from(fmt, self.b, self.i)[0]
        self.i += n
        return v

    def string(self):
        n = self.u("<H", 2)
        s = self.b[self.i:self.i + n]
        self.i += n
        return s.decode("utf-8", "replace")

    def payload(self, t):
        if t == TAG_BYTE:
            return self.u("<b", 1)
        if t == TAG_SHORT:
            return self.u("<h", 2)
        if t == TAG_INT:
            return self.u("<i", 4)
        if t == TAG_LONG:
            return self.u("<q", 8)
        if t == TAG_FLOAT:
            return self.u("<f", 4)
        if t == TAG_DOUBLE:
            return self.u("<d", 8)
        if t == TAG_BYTE_ARRAY:
            n = self.u("<i", 4)
            v = list(self.b[self.i:self.i + n])
            self.i += n
            return v
        if t == TAG_STRING:
            return self.string()
        if t == TAG_LIST:
            et = self.u("<b", 1)
            n = self.u("<i", 4)
            return [self.payload(et) for _ in range(n)] if et != TAG_END else []
        if t == TAG_COMPOUND:
            d = {}
            while True:
                tt = self.u("<b", 1)
                if tt == TAG_END:
                    return d
                name = self.string()
                d[name] = self.payload(tt)
        if t == TAG_INT_ARRAY:
            n = self.u("<i", 4)
            v = list(struct.unpack_from("<%di" % n, self.b, self.i))
            self.i += 4 * n
            return v
        if t == TAG_LONG_ARRAY:
            n = self.u("<i", 4)
            v = list(struct.unpack_from("<%dq" % n, self.b, self.i))
            self.i += 8 * n
            return v
        raise ValueError("unknown tag %d at %d" % (t, self.i))


def load(buf):
    r = Reader(buf)
    t = r.u("<b", 1)
    name = r.string()
    return name, r.payload(t)
