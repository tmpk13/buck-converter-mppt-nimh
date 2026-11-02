#!/usr/bin/env python3
"""Sweep commanded duty and report what the gate drive actually delivers.

The emitter follower is turned off through R54 (47k), so the SW-node duty can
be far larger than the duty commanded on PWM_HI. This sweep quantifies that.
"""
import argparse
import json
from pathlib import Path

from run_q2 import VARIANTS, run, charge_current

HERE = Path(__file__).resolve().parent


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--variant', default='no-d8', choices=list(VARIANTS))
    ap.add_argument('--vin', default='24')
    ap.add_argument('--duties', default='0.01,0.03,0.05,0.10,0.19,0.30,0.50')
    a = ap.parse_args()

    rows = []
    print('%-8s %-10s %-10s %-9s %-9s %-8s' %
          ('duty', 'Ichg(A)', 'SWduty', 'Vbatt(V)', 'Vgsmin', 'eff(%)'))
    for d in [float(x) for x in a.duties.split(',')]:
        res = run(dict(VARIANTS[a.variant], vin=a.vin, duty='%.6f' % d))
        ib = charge_current(res)
        swd = res['vswavg'] / float(a.vin)
        eff = (res['pout'] / res['pin'] * 100
               if res.get('pin') and res['pin'] > 1e-6 else float('nan'))
        print('%-8.3f %-10.4f %-10.4f %-9.3f %-9.2f %-8.1f' %
              (d, ib, swd, res['vbatt'], res['vgsmin'], eff))
        rows.append(dict(duty=d, ibat=ib, sw_duty=swd, vbatt=res['vbatt'],
                         vgsmin=res['vgsmin'], eff=eff, pin=res['pin'],
                         pout=res['pout']))

    out = HERE / ('sweep_%s_%sv.json' % (a.variant, a.vin))
    out.write_text(json.dumps(rows, indent=2))
    print('wrote %s' % out)


if __name__ == '__main__':
    main()
