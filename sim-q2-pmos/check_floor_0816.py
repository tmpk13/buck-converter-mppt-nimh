#!/usr/bin/env python3
"""Low-duty controllability of the 2026-08-16 drive arrangement."""
import json
from pathlib import Path
from run_q2 import VARIANTS, run, charge_current

HERE = Path(__file__).resolve().parent
rows = []
print('%-7s %-9s' % ('duty', 'Ichg(A)'))
for d in [0.01, 0.03, 0.06, 0.10]:
    res = run(dict(VARIANTS['sch-0816'], vin='24', duty='%.6f' % d))
    ib = charge_current(res)
    rows.append(dict(duty=d, ibat=ib, vgsmin=res['vgsmin']))
    print('%-7.3f %-9.4f' % (d, ib))
(HERE / 'check_floor_0816.json').write_text(json.dumps(rows, indent=2))
print('done')
