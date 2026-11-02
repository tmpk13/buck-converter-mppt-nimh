#!/usr/bin/env python3
"""Find the R54 value at which the low-duty dead zone appears."""
import json
from pathlib import Path

from run_q2 import VARIANTS, run, charge_current

HERE = Path(__file__).resolve().parent
rows = []
print('%-7s %-7s %-9s' % ('R54', 'duty', 'Ichg(A)'))
for r in ['4.7k', '10k', '22k', '47k']:
    for d in [0.01, 0.03, 0.06]:
        res = run(dict(VARIANTS['option-b'], vin='24', duty='%.6f' % d, r54=r))
        ib = charge_current(res)
        rows.append(dict(r54=r, duty=d, ibat=ib))
        print('%-7s %-7.3f %-9.4f' % (r, d, ib))
(HERE / 'check_floor.json').write_text(json.dumps(rows, indent=2))
print('done')
