#!/usr/bin/env python3
"""Drive ngspice over the Q2 PMOS buck deck.

Each variant is a set of .param overrides. For variants that actually switch,
a bisection on duty finds the duty that delivers the requested charge current.
"""
import argparse
import json
import re
import subprocess
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
DECK = HERE / 'q2_buck.spice'

CONTROL = """
.control
set noaskquit
tran 20n {tstop} 0 20n
meas tran ibat   avg i(vb)     from={t0} to={t1}
meas tran iin    avg i(vin)    from={t0} to={t1}
meas tran pin    avg v(pin)    from={t0} to={t1}
meas tran pout   avg v(pout)   from={t0} to={t1}
meas tran vbatt  avg v(batt)   from={t0} to={t1}
meas tran il     avg i(l6)     from={t0} to={t1}
meas tran ilmax  max i(l6)     from={t0} to={t1}
meas tran ilmin  min i(l6)     from={t0} to={t1}
meas tran vgsmin min v(vgs)    from={t0} to={t1}
meas tran vgsmax max v(vgs)    from={t0} to={t1}
meas tran vswavg avg v(sw)     from={t0} to={t1}
meas tran vswmax max v(sw)     from={t0} to={t1}
meas tran id8    avg i(vad8)   from={t0} to={t1}
meas tran id8p   max i(vad8)   from={t0} to={t1}
meas tran iq3    avg i(vaq3)   from={t0} to={t1}
meas tran iq3p   max i(vaq3)   from={t0} to={t1}
meas tran vbn    avg v(a)      from={t0} to={t1}
quit
.endc
"""

MEAS_RE = re.compile(r'^\s*([a-z0-9_]+)\s*=\s*([-+0-9.eE]+|failed)', re.M)


def run(params, tstop=1.5e-3, window=0.4e-3):
    deck = DECK.read_text()
    for k, v in params.items():
        deck = re.sub(r'^\.param %s=.*$' % k, '.param %s=%s' % (k, v),
                      deck, flags=re.M)
    ctrl = CONTROL.format(tstop=tstop, t0=tstop - window, t1=tstop)
    deck = deck.replace('.end\n', ctrl + '\n.end\n')

    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / 'deck.spice'
        p.write_text(deck)
        (Path(td) / 'q2_models.inc').write_text((HERE / 'q2_models.inc').read_text())
        r = subprocess.run(['ngspice', '-b', str(p)], capture_output=True,
                           text=True, cwd=td, timeout=900)
    out = r.stdout + r.stderr
    res = {}
    for m in MEAS_RE.finditer(out):
        k, v = m.group(1), m.group(2)
        res[k] = None if v == 'failed' else float(v)
    res['_raw'] = out
    return res


def charge_current(res):
    # SPICE measures a voltage source's branch current flowing into its +
    # terminal, so charging the pack shows up as positive i(vb) directly.
    return res.get('ibat')


def bisect_duty(params, target=1.0, lo=0.01, hi=0.60, tol=5e-3, iters=16):
    best = None
    bounds = (lo, hi)
    for _ in range(iters):
        mid = 0.5 * (lo + hi)
        res = run(dict(params, duty='%.6f' % mid))
        ib = charge_current(res)
        if ib is None:
            raise RuntimeError('measurement failed at duty=%.4f' % mid)
        best = (mid, res, ib)
        if abs(ib - target) < tol:
            break
        if ib < target:
            lo = mid
        else:
            hi = mid
    if best is None:
        raise RuntimeError('bisection produced no result')
    if not (bounds[0] * 1.05 < best[0] < bounds[1] * 0.95):
        print('  WARNING: duty pinned at a search bound (%.4f), target %.3f A '
              'may be unreachable' % (best[0], target))
    return best


VARIANTS = {
    'as-drawn': dict(rd8='1m', rlrg='1m', rzen='1G'),
    'no-d8': dict(rd8='1G', rlrg='1m', rzen='1G'),
    'no-d8-zener-rail': dict(rd8='1G', rlrg='1G', rzen='1m'),
    # D8 removed, PNP collector on the Vin-10V zener rail, and a pull-up
    # fast enough to turn the follower off inside a 100kHz period.
    'fixed': dict(rd8='1G', rlrg='1G', rzen='1m', r54='2.2k'),
    # Full Option B drive from BUCK-TOPOLOGY-REPORT.md: adds the base
    # resistor the board is missing.
    'option-b': dict(rd8='1G', rlrg='1G', rzen='1m', r54='2.2k', rb='2.2k'),
    # The schematic as saved 2026-08-12 19:01: zener rail fitted (D1/R57/C24),
    # R54 now 4.7k, but no base resistor and R56 raised from 22R to 2.2k.
    'current': dict(rd8='1G', rlrg='1G', rzen='1m', r54='4.7k', rb='1m',
                    r56='2.2k'),
    # Same, with the base resistor added.
    'current-rb': dict(rd8='1G', rlrg='1G', rzen='1m', r54='4.7k', rb='2.2k',
                       r56='2.2k'),
    # Same, with the base resistor added and R56 put back to 22R.
    'current-fixed': dict(rd8='1G', rlrg='1G', rzen='1m', r54='4.7k',
                          rb='2.2k', r56='22'),
    # As above but with the SRN6045TA-330M's real 145 mohm DCR.
    'current-fixed-srn': dict(rd8='1G', rlrg='1G', rzen='1m', r54='4.7k',
                              rb='2.2k', r56='22', rl6='145m'),
    # Schematic as saved 2026-08-14 02:35: R58 2.2k added from the BJT base
    # node to GND rather than in series between Q3.D and the bases.
    'sch-0814': dict(rd8='1G', rlrg='1G', rzen='1m', r54='4.7k', rb='1m',
                     r56='22', rl6='145m', rbg='2.2k'),
    # Same, but with R58 moved into the series position it was meant for.
    'sch-0814-rb': dict(rd8='1G', rlrg='1G', rzen='1m', r54='4.7k', rb='2.2k',
                        r56='22', rl6='145m', rbg='1G'),
    # Schematic as saved 2026-08-16 16:43: R58 now in series Q3.D -> bases, but
    # R54's pull-up lands on the BASE node rather than on Q3's drain.
    'sch-0816': dict(rd8='1G', rlrg='1G', rzen='1m', r54='1G', r54b='4.7k',
                     rb='2.2k', rbg='1G', r56='22', rl6='145m'),
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--vin', default='24')
    ap.add_argument('--target', type=float, default=1.0)
    ap.add_argument('--variant', action='append', choices=list(VARIANTS))
    ap.add_argument('--duty', help='fixed duty, skip the bisection')
    ap.add_argument('--out', default=str(HERE / 'results_q2.json'))
    a = ap.parse_args()

    names = a.variant or list(VARIANTS)
    all_res = {}
    for name in names:
        params = dict(VARIANTS[name], vin=a.vin)
        print('=== %s (vin=%s)' % (name, a.vin))
        if a.duty:
            duty = float(a.duty)
            res = run(dict(params, duty=a.duty))
            ib = charge_current(res)
        else:
            try:
                duty, res, ib = bisect_duty(params, target=a.target)
            except RuntimeError as e:
                print('  %s' % e)
                continue
        eff = (res['pout'] / res['pin'] * 100
               if res.get('pin') and res['pin'] > 1e-6 else float('nan'))
        row = dict(duty=duty, ibat=ib, vbatt=res['vbatt'], iin=-res['iin'],
                   pin=res['pin'], pout=res['pout'], eff=eff,
                   il=res['il'], ilmax=res['ilmax'], ilmin=res['ilmin'],
                   vgsmin=res['vgsmin'], vgsmax=res['vgsmax'],
                   id8=res['id8'], id8p=res['id8p'],
                   iq3=res['iq3'], iq3p=res['iq3p'], vbnode=res['vbn'])
        all_res[name] = row
        print('  duty      %.4f' % duty)
        print('  I charge  %.4f A   Vbatt %.3f V' % (ib, res['vbatt']))
        print('  Pin %.3f W  Pout %.3f W  eff %.1f %%' % (res['pin'], res['pout'], eff))
        print('  Vgs       %.2f .. %.2f V' % (res['vgsmin'], res['vgsmax']))
        print('  IL        %.3f A (%.3f .. %.3f)' % (res['il'], res['ilmin'], res['ilmax']))
        print('  base node %.2f V   I(D8) avg %.4f A peak %.4f A' %
              (res['vbn'], res['id8'], res['id8p']))
        print('  I(Q3)     avg %.4f A peak %.4f A' % (res['iq3'], res['iq3p']))

    Path(a.out).write_text(json.dumps(all_res, indent=2))
    print('wrote %s' % a.out)


if __name__ == '__main__':
    main()
