#!/usr/bin/env python3
"""Extract a netlist from a KiCad v10 .kicad_sch by geometric connectivity.

kicad-cli 9.0.8 cannot load v10 (20260306) schematics, so nets are rebuilt here
from wire/pin geometry instead of from a KiCad export.

Three details are easy to get wrong, and each fails silently rather than loudly:

  * a pin's "at" IS its connection point - do not extend it by "length" toward
    the symbol body, or every pin misses its wire by one pin stub;
  * sub-symbols are named "<lib>_<unit>_<bodystyle>". Filter on BOTH. Symbols
    with a DeMorgan alternate body define a second pin set at different
    coordinates, and taking both invents phantom pins;
  * KiCad applies the symbol ROTATION first and the MIRROR second. The other
    order gives identical results unless a symbol has both, and then it swaps
    pin 1 with pin 2 - which inverts every rotated-and-mirrored diode.

Validate against the PCB's own pad net names before trusting the output; see
crosscheck() below.

    python3 kicad_netlist.py board.kicad_sch [REF ...]
    python3 kicad_netlist.py board.kicad_sch --crosscheck board.kicad_pcb
"""
import math
import sys
from collections import defaultdict


def tokenize(s):
    out, i, n = [], 0, len(s)
    while i < n:
        c = s[i]
        if c in '()':
            out.append(c)
            i += 1
        elif c == '"':
            j, buf = i + 1, []
            while j < n:
                if s[j] == '\\':
                    buf.append(s[j + 1])
                    j += 2
                elif s[j] == '"':
                    break
                else:
                    buf.append(s[j])
                    j += 1
            out.append(('str', ''.join(buf)))
            i = j + 1
        elif c.isspace():
            i += 1
        else:
            j = i
            while j < n and not s[j].isspace() and s[j] not in '()"':
                j += 1
            out.append(('sym', s[i:j]))
            i = j
    return out


def parse(tokens):
    stack = [[]]
    for t in tokens:
        if t == '(':
            stack.append([])
        elif t == ')':
            node = stack.pop()
            stack[-1].append(node)
        else:
            stack[-1].append(t)
    return stack[0]


def name(node):
    if isinstance(node, list) and node and isinstance(node[0], tuple):
        return node[0][1]
    return None


def kids(node, key):
    return [c for c in node if isinstance(c, list) and name(c) == key]


def kid(node, key):
    k = kids(node, key)
    return k[0] if k else None


def val(node, idx=1):
    v = node[idx]
    return v[1] if isinstance(v, tuple) else v


def nums(node, start=1, count=3):
    out = []
    for c in node[start:start + count]:
        if isinstance(c, tuple):
            try:
                out.append(float(c[1]))
            except ValueError:
                break
        else:
            break
    return out


def prop(sym, pname):
    for p in kids(sym, 'property'):
        if val(p, 1) == pname:
            return val(p, 2)
    return None


def place(x, y, ang, mirror):
    """Symbol-space pin coords -> schematic coords. Rotate, then mirror."""
    a = math.radians(ang)
    ca, sa = math.cos(a), math.sin(a)
    xr = x * ca - y * sa
    yr = x * sa + y * ca
    if mirror == 'x':
        yr = -yr
    elif mirror == 'y':
        xr = -xr
    return xr, -yr           # schematic y runs downward


def key(pt):
    return (round(pt[0] * 100), round(pt[1] * 100))


def load(path):
    return parse(tokenize(open(path).read()))[0]


def symbol_pins(root):
    """(ref, pin_number, pin_name, x, y) for every placed symbol pin."""
    libpins = {}
    for ls in kids(kid(root, 'lib_symbols'), 'symbol'):
        pins = []
        for unit in kids(ls, 'symbol'):
            parts = val(unit, 1).rsplit('_', 2)
            unum = int(parts[1]) if len(parts) == 3 and parts[1].isdigit() else 0
            ustyle = int(parts[2]) if len(parts) == 3 and parts[2].isdigit() else 0
            for pin in kids(unit, 'pin'):
                px, py = (nums(kid(pin, 'at'), 1, 2) + [0, 0])[:2]
                pins.append((unum, ustyle, val(kid(pin, 'number'), 1),
                             val(kid(pin, 'name'), 1), px, py))
        libpins[val(ls, 1)] = pins

    out, refs = [], {}
    for sym in kids(root, 'symbol'):
        ref = prop(sym, 'Reference')
        if ref is None:
            continue
        sx, sy, sa = (nums(kid(sym, 'at'), 1, 3) + [0, 0, 0])[:3]
        u = kid(sym, 'unit')
        sunit = int(val(u, 1)) if u else 1
        b = kid(sym, 'body_style')
        sstyle = int(val(b, 1)) if b else 1
        m = kid(sym, 'mirror')
        mirror = val(m, 1) if m else None
        refs[ref] = prop(sym, 'Value')
        for unum, ustyle, num, pname, px, py in libpins.get(
                val(kid(sym, 'lib_id'), 1), []):
            if unum not in (0, sunit) or ustyle not in (0, sstyle):
                continue
            dx, dy = place(px, py, sa, mirror)
            out.append((ref, num, pname, sx + dx, sy + dy))
    return out, refs


def build(path):
    root = load(path)
    inst_pins, refs = symbol_pins(root)

    parent = {}

    def find(a):
        parent.setdefault(a, a)
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb

    segs = []
    for w in kids(root, 'wire'):
        xy = [tuple(nums(p, 1, 2)) for p in kids(kid(w, 'pts'), 'xy')]
        for a, b in zip(xy, xy[1:]):
            union(key(a), key(b))
            segs.append((a, b))

    def on_seg(p, a, b):
        (x, y), (x1, y1), (x2, y2) = p, a, b
        if abs(x1 - x2) < 1e-6:
            return abs(x - x1) < 1e-6 and min(y1, y2) - 1e-6 <= y <= max(y1, y2) + 1e-6
        if abs(y1 - y2) < 1e-6:
            return abs(y - y1) < 1e-6 and min(x1, x2) - 1e-6 <= x <= max(x1, x2) + 1e-6
        return False

    for j in kids(root, 'junction'):
        jp = tuple(nums(kid(j, 'at'), 1, 2))
        for a, b in segs:
            if on_seg(jp, a, b):
                union(key(jp), key(a))

    for ref, num, pname, x, y in inst_pins:
        for a, b in segs:
            if on_seg((x, y), a, b):
                union(key((x, y)), key(a))

    labels = {}
    for tag in ('label', 'global_label', 'hierarchical_label'):
        for lb in kids(root, tag):
            p = tuple(nums(kid(lb, 'at'), 1, 2))
            for a, b in segs:
                if on_seg(p, a, b):
                    union(key(p), key(a))
            labels.setdefault(find(key(p)), set()).add(val(lb, 1))
    for ref, num, pname, x, y in inst_pins:
        if ref.startswith('#PWR') or ref.startswith('#FLG'):
            labels.setdefault(find(key((x, y))), set()).add(refs.get(ref, '?'))

    nets = defaultdict(list)
    for ref, num, pname, x, y in inst_pins:
        if not ref.startswith('#'):
            nets[find(key((x, y)))].append((ref, num, pname))

    named = {}
    for rk, members in nets.items():
        nm = labels.get(rk)
        label = sorted(nm)[0] if nm else 'N$%d' % (abs(hash(rk)) % 10000)
        named.setdefault(label, []).extend(members)
    return refs, named


def pcb_pin_nets(path):
    root = load(path)
    out = {}
    for fp in kids(root, 'footprint'):
        ref = None
        for pr in kids(fp, 'property'):
            if val(pr, 1) == 'Reference':
                ref = val(pr, 2)
        if not ref:
            continue
        for pad in kids(fp, 'pad'):
            net = kid(pad, 'net')
            if net:
                out[(ref, val(pad, 1))] = val(net, 1)
    return out


def crosscheck(sch, pcb):
    """Net names differ between the files, so compare the partitions."""
    _, named = build(sch)
    s = {}
    for label, members in named.items():
        for ref, num, pname in members:
            s[(ref, num)] = label
    p = pcb_pin_nets(pcb)
    common = set(p) & set(s)
    print('pins  PCB %d  sch %d  common %d' % (len(p), len(s), len(common)))
    print('PCB-only %d   sch-only %d  (nonzero => board out of sync)'
          % (len(set(p) - set(s)), len(set(s) - set(p))))

    def groups(m):
        g = defaultdict(set)
        for k, v in m.items():
            g[v].add(k)
        return g

    bad = []
    for src, dst, tag in ((p, s, 'PCB net split in schematic'),
                          (s, p, 'schematic net split in PCB')):
        for net, members in groups(src).items():
            m = [k for k in members if k in common]
            if len(m) > 1 and len({dst[k] for k in m}) > 1:
                bad.append((tag, net, sorted(m), sorted({dst[k] for k in m})))
    print('disagreements: %d' % len(bad))
    for tag, net, members, others in bad:
        print('\n%s: %s' % (tag, net))
        print('   pins  : %s' % ', '.join('%s.%s' % k for k in members))
        print('   splits: %s' % ', '.join(others))
    return bad


if __name__ == '__main__':
    if '--crosscheck' in sys.argv:
        i = sys.argv.index('--crosscheck')
        crosscheck(sys.argv[1], sys.argv[i + 1])
    else:
        refs, named = build(sys.argv[1])
        focus = sys.argv[2:]
        for label in sorted(named):
            members = named[label]
            if focus and not any(m[0] in focus for m in members):
                continue
            print('%-22s %s' % (label, '  '.join(
                '%s.%s(%s)' % m for m in sorted(members))))
