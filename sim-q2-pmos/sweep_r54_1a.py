#!/usr/bin/env python3
"""Compare R54 values at a constant 1 A charge current, not at fixed duty.

Charge current is hyper-sensitive to duty and this drive's turn-off delay is
R54-dependent, so a fixed-duty comparison puts every row at a different output
current and is not a valid efficiency comparison.
"""
import json
from pathlib import Path

from run_q2 import VARIANTS, bisect_duty

HERE = Path(__file__).resolve().parent
VIN = 24.0

rows = []
print('%-7s %-8s %-9s %-9s %-8s %-10s %-10s' %
      ('R54', 'duty', 'Ichg(A)', 'Vgsmin', 'eff(%)', 'P_R54_avg', 'P_R54_D100'))
for r in ['1k', '2.2k', '4.7k', '10k']:
    params = dict(VARIANTS['option-b'], vin=str(VIN), r54=r)
    try:
        duty, res, ib = bisect_duty(params, target=1.0)
    except RuntimeError as e:
        print('%-7s %s' % (r, e))
        continue
    ohms = float(r[:-1]) * 1e3
    p_on = (VIN - 0.2) ** 2 / ohms
    eff = res['pout'] / res['pin'] * 100
    rows.append(dict(r54=r, duty=duty, ibat=ib, vgsmin=res['vgsmin'], eff=eff,
                     pin=res['pin'], pout=res['pout'],
                     p_r54_avg=p_on * duty, p_r54_d100=p_on))
    print('%-7s %-8.4f %-9.4f %-9.2f %-8.1f %-10.3f %-10.3f' %
          (r, duty, ib, res['vgsmin'], eff, p_on * duty, p_on))

(HERE / 'sweep_r54_1a.json').write_text(json.dumps(rows, indent=2))
print('wrote sweep_r54_1a.json')
