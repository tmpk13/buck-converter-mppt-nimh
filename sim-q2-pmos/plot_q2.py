#!/usr/bin/env python3
"""Dump and plot switching waveforms for each Q2 buck variant.

Run with the pixi environment: pixi run python sim-q2-pmos/plot_q2.py
"""
import json
import re
import subprocess
import tempfile
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

HERE = Path(__file__).resolve().parent
DECK = HERE / 'q2_buck.spice'

from run_q2 import VARIANTS  # noqa: E402

CONTROL = """
.control
set noaskquit
tran 5n {tstop} 0 5n
wrdata {out} v(pwm) v(bnode) v(g) v(vgs) v(sw) i(l6) i(vb) i(vaq3)
quit
.endc
"""

COLS = ['pwm', 'bnode', 'g', 'vgs', 'sw', 'il', 'ivb', 'iq3']


def dump(params, tstop=3e-3):
    deck = DECK.read_text()
    for k, v in params.items():
        deck = re.sub(r'^\.param %s=.*$' % k, '.param %s=%s' % (k, v),
                      deck, flags=re.M)
    with tempfile.TemporaryDirectory() as td:
        out = Path(td) / 'wave.dat'
        d = deck.replace('.end\n', CONTROL.format(tstop=tstop, out=out) + '\n.end\n')
        p = Path(td) / 'deck.spice'
        p.write_text(d)
        (Path(td) / 'q2_models.inc').write_text((HERE / 'q2_models.inc').read_text())
        subprocess.run(['ngspice', '-b', str(p)], capture_output=True,
                       text=True, cwd=td, timeout=900)
        raw = np.loadtxt(out)
    # wrdata interleaves a time column ahead of every vector
    t = raw[:, 0]
    data = {name: raw[:, 2 * i + 1] for i, name in enumerate(COLS)}
    return t, data


def main():
    res = json.loads((HERE / 'results_current.json').read_text())
    names = [n for n in ('current', 'current-rb', 'current-fixed') if n in res]

    fig, axes = plt.subplots(4, len(names), figsize=(5.2 * len(names), 10.5),
                             sharex='col', squeeze=False)
    for col, name in enumerate(names):
        duty = res.get(name, {}).get('duty', 0.19)
        t, d = dump(dict(VARIANTS[name], duty='%.6f' % duty))
        # last 3 switching periods
        m = t >= t[-1] - 30e-6
        tu = (t[m] - t[m][0]) * 1e6

        ax = axes[0][col]
        ax.plot(tu, d['pwm'][m], label='PWM (PB10)')
        ax.plot(tu, d['bnode'][m], label='BJT base node')
        ax.set_title('%s  (duty %.3f)' % (name, duty))
        ax.set_ylabel('V')
        ax.legend(fontsize=7)

        ax = axes[1][col]
        ax.plot(tu, d['vgs'][m], color='tab:red', label='Vgs(Q2)')
        ax.axhline(-20, ls='--', lw=0.8, color='k')
        ax.axhline(20, ls='--', lw=0.8, color='k')
        ax.set_ylabel('Vgs (V)')
        ax.legend(fontsize=7)

        ax = axes[2][col]
        ax.plot(tu, d['sw'][m], color='tab:green', label='SW node')
        ax.set_ylabel('V')
        ax.legend(fontsize=7)

        ax = axes[3][col]
        ax.plot(tu, d['il'][m], color='tab:blue', label='I(L6)')
        ax.plot(tu, d['ivb'][m], color='tab:orange', label='I charge')
        ax.plot(tu, d['iq3'][m], color='tab:purple', lw=0.8, label='I(Q3)')
        ax.set_ylabel('A')
        ax.set_xlabel('time (us)')
        ax.legend(fontsize=7)

    for row in axes:
        for ax in row:
            ax.grid(alpha=0.3)
    fig.suptitle('Q2 PMOS async buck as drawn 2026-08-12, 24V in, 100kHz, 3S NiMH')
    fig.tight_layout()
    fig.savefig(HERE / 'q2_waveforms.png', dpi=130)
    print('wrote', HERE / 'q2_waveforms.png')


if __name__ == '__main__':
    main()
