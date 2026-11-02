#!/usr/bin/env python3
"""Run each variant at a representative duty and collect the comparison set."""
import json
from pathlib import Path

from run_q2 import VARIANTS, run, charge_current

HERE = Path(__file__).resolve().parent

# as-drawn and no-d8 cannot reach 1A, so they are shown at the duty the
# firmware would command for 1A; option-b is shown at its bisected 1A duty.
CASES = [('as-drawn', 0.190), ('no-d8', 0.190), ('option-b', 0.144)]

out = {}
for name, duty in CASES:
    res = run(dict(VARIANTS[name], vin='24', duty='%.6f' % duty))
    ib = charge_current(res)
    eff = (res['pout'] / res['pin'] * 100
           if res.get('pin') and res['pin'] > 1e-6 else float('nan'))
    out[name] = dict(duty=duty, ibat=ib, vbatt=res['vbatt'], eff=eff,
                     pin=res['pin'], pout=res['pout'],
                     sw_duty=res['vswavg'] / 24.0,
                     vgsmin=res['vgsmin'], vgsmax=res['vgsmax'],
                     il=res['il'], ilmax=res['ilmax'], ilmin=res['ilmin'],
                     iq3=res['iq3'], iq3p=res['iq3p'],
                     id8=res['id8'], id8p=res['id8p'], vbnode=res['vbn'])
    print('%-18s duty %.3f  SWduty %.3f  Ichg %8.4f A  Vgs %7.2f  eff %5.1f%%  '
          'Iq3pk %.3f A' % (name, duty, out[name]['sw_duty'], ib,
                            res['vgsmin'], eff, res['iq3p']))

(HERE / 'results_q2.json').write_text(json.dumps(out, indent=2))
print('wrote results_q2.json')
