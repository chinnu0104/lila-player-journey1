"""Minimal dependency-free Parquet reader (SNAPPY/UNCOMPRESSED, PLAIN + dictionary, RLE/bit-packed).
Enough for LILA's parquet-go output. Use pyarrow instead if you can install it (see build_data.py)."""
import struct

def _zz(n): return (n >> 1) ^ -(n & 1)

class Thrift:
    def __init__(s, b, p=0): s.b, s.p = b, p
    def varint(s):
        r = sh = 0
        while True:
            c = s.b[s.p]; s.p += 1; r |= (c & 0x7f) << sh; sh += 7
            if not c & 0x80: return r
    def value(s, t):
        if t in (1, 2): return t == 1
        if t == 3: v = s.b[s.p]; s.p += 1; return v
        if t in (4, 5, 6): return _zz(s.varint())
        if t == 7: v = struct.unpack('<d', s.b[s.p:s.p+8])[0]; s.p += 8; return v
        if t == 8: n = s.varint(); v = s.b[s.p:s.p+n]; s.p += n; return v
        if t in (9, 10):
            h = s.b[s.p]; s.p += 1; n = h >> 4; et = h & 15
            if n == 15: n = s.varint()
            return [s.value(et) for _ in range(n)]
        if t == 12: return s.struct()
        raise ValueError(t)
    def struct(s):
        d, last = {}, 0
        while True:
            h = s.b[s.p]; s.p += 1
            if h == 0: return d
            t, delta = h & 15, h >> 4
            last = last + delta if delta else _zz(s.varint())
            d[last] = s.value(t)

def snappy(b):
    t = Thrift(b); n = t.varint(); p = t.p; out = bytearray()
    while p < len(b):
        tag = b[p]; p += 1; k = tag & 3
        if k == 0:
            ln = tag >> 2
            if ln >= 60:
                nb = ln - 59; ln = int.from_bytes(b[p:p+nb], 'little'); p += nb
            ln += 1; out += b[p:p+ln]; p += ln
        else:
            if k == 1: ln = ((tag >> 2) & 7) + 4; off = ((tag >> 5) << 8) | b[p]; p += 1
            elif k == 2: ln = (tag >> 2) + 1; off = int.from_bytes(b[p:p+2], 'little'); p += 2
            else: ln = (tag >> 2) + 1; off = int.from_bytes(b[p:p+4], 'little'); p += 4
            for _ in range(ln): out.append(out[-off])
    assert len(out) == n
    return bytes(out)

def rle(b, p, bw, n):
    out = []
    while len(out) < n:
        t = Thrift(b, p); h = t.varint(); p = t.p
        if h & 1:
            cnt = (h >> 1) * 8; nb = (h >> 1) * bw
            v = int.from_bytes(b[p:p+nb], 'little'); p += nb
            m = (1 << bw) - 1
            out += [(v >> (i * bw)) & m for i in range(cnt)]
        else:
            cnt = h >> 1; w = (bw + 7) // 8
            out += [int.from_bytes(b[p:p+w], 'little')] * cnt; p += w
    return out[:n]

def plain(b, ptype, n):
    if ptype == 6:  # BYTE_ARRAY
        out, p = [], 0
        for _ in range(n):
            l = struct.unpack_from('<I', b, p)[0]; out.append(bytes(b[p+4:p+4+l])); p += 4 + l
        return out
    fmt = {1: 'i', 2: 'q', 4: 'f', 5: 'd'}[ptype]
    return list(struct.unpack('<%d%s' % (n, fmt), b[:n * struct.calcsize(fmt)]))

def read(path):
    """Return dict column -> list (bytes for BYTE_ARRAY, int for INT64 etc.)."""
    b = open(path, 'rb').read()
    assert b[:4] == b'PAR1'
    fl = struct.unpack('<I', b[-8:-4])[0]
    meta = Thrift(b, len(b) - 8 - fl).struct()
    schema = meta[2][1:]; cols = {}
    for rg in meta[4]:
        for cc, sc in zip(rg[1], schema):
            cm = cc[3]; name = sc[4].decode(); ptype = cm[1]; codec = cm[4]
            optional = sc.get(3, 0) == 1
            p = cm.get(11) or cm[9]; if_dict = None; vals = []; need = cm[5]
            while len(vals) < need:
                t = Thrift(b, p); ph = t.struct(); p = t.p
                raw = b[p:p+ph[3]]; p += ph[3]
                data = snappy(raw) if codec == 1 else raw
                if ph[1] == 2:
                    if_dict = plain(data, ptype, ph[7][1]); continue
                dp = ph[5]; n = dp[1]; enc = dp[2]; q = 0
                defs = None
                if optional:
                    l = struct.unpack_from('<I', data, 0)[0]; defs = rle(data, 4, 1, n); q = 4 + l
                m = n if defs is None else sum(defs)
                if enc in (2, 8):
                    bw = data[q]; idx = rle(data, q + 1, bw, m); v = [if_dict[i] for i in idx]
                else: v = plain(data[q:], ptype, m)
                if defs is not None:
                    it = iter(v); v = [next(it) if d else None for d in defs]
                vals += v
            cols.setdefault(name, []).extend(vals)
    return cols
