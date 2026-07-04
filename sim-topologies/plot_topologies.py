#!/usr/bin/env python3
"""Plot topology comparison from results_*.json sweeps."""
import json
import os
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = sys.argv[1] if len(sys.argv) > 1 else HERE

TOPOS = [
    ("hs_nmos", "Current: HS NMOS + 78L12/LM5109", "#d62728", "o"),
    ("hs_nmos_batdrv", "Fix A: HS NMOS, driver fed from battery", "#ff7f0e", "v"),
    ("pmos_buck", "Plain buck: HS PMOS, discrete drive", "#1f77b4", "s"),
    ("lowside_buck", "Low-side buck (floating battery)", "#2ca02c", "^"),
    ("sepic", "SEPIC (GND-ref NMOS, common GND)", "#9467bd", "D"),
]

data = {}
for key, *_ in TOPOS:
    p = os.path.join(HERE, f"results_{key}.json")
    if os.path.exists(p):
        data[key] = json.load(open(p))

fig, axes = plt.subplots(3, 1, figsize=(9, 11), sharex=True)
fig.suptitle("Solar buck alternatives: NiMH 3S charge at 1A target\n"
             "(3.9V EMF + 0.15$\\Omega$ battery, 47$\\mu$H, 100kHz, ngspice)",
             fontsize=12, fontweight="bold")

ax1, ax2, ax3 = axes
for key, label, color, mark in TOPOS:
    if key not in data:
        continue
    d = data[key]
    vin = [r["vin"] for r in d]
    ichg = [r["ichg"] if r["ichg"] is not None else 0 for r in d]
    duty = [r["duty"] * 100 for r in d]
    eff = [r["eff_pct"] for r in d]
    ax1.plot(vin, ichg, mark + "-", color=color, label=label, markersize=6)
    ax2.plot(vin, duty, mark + "-", color=color, label=label, markersize=6)
    ax3.plot([v for v, e in zip(vin, eff) if e],
             [e for e in eff if e], mark + "-", color=color, label=label, markersize=6)

ax1.axhline(1.0, color="gray", ls="--", lw=1)
ax1.set_ylabel("Achieved charge current (A)")
ax1.set_ylim(-0.05, 1.3)
ax1.legend(fontsize=8, loc="lower right")
ax1.grid(alpha=0.3)

ax2.set_ylabel("Commanded duty (%)")
ax2.grid(alpha=0.3)

ax3.set_ylabel("Efficiency Pin->Pbat (%)")
ax3.set_xlabel("Solar input voltage (V)")
ax3.set_ylim(40, 100)
ax3.grid(alpha=0.3)

plt.tight_layout()
out = os.path.join(OUT, "topology_comparison.png")
plt.savefig(out, dpi=130)
print("wrote", out)
