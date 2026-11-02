#!/usr/bin/env python3
"""Emit markdown tables from results_*.json."""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
TOPOS = [
    ("hs_nmos", "Current design (HS NMOS, 78L12+LM5109 from solar)"),
    ("hs_nmos_batdrv", "Fix A: same HS NMOS, driver rail boosted from battery"),
    ("pmos_buck", "Plain buck: HS PMOS + discrete level shift"),
    ("lowside_buck", "Low-side buck: GND-ref NMOS, floating battery"),
    ("sepic", "SEPIC: GND-ref NMOS, common ground"),
]

for key, title in TOPOS:
    p = os.path.join(HERE, f"results_{key}.json")
    if not os.path.exists(p):
        continue
    d = json.load(open(p))
    print(f"\n### {title}\n")
    print("| Vin (V) | Duty (%) | Ichg (A) | Pin (W) | Pbat (W) | Eff (%) | Vgs drive (V) |")
    print("|---|---|---|---|---|---|---|")
    for r in d:
        vgs = r["vgsmax"] if abs(r["vgsmax"]) > abs(r["vgsmin"] or 0) else r["vgsmin"]
        dead = r["ichg"] is not None and r["ichg"] < 0.05
        duty = f"{r['duty']*100:.1f}" + (" (max)" if r.get("clamped") else "")
        if dead:
            print(f"| {r['vin']:.0f} | - | **0 (dead)** | - | - | - | {vgs:.1f} |")
        else:
            print(f"| {r['vin']:.0f} | {duty} | {r['ichg']:.2f} | {r['pin']:.2f} | "
                  f"{r['pbat']:.2f} | {r['eff_pct']:.1f} | {vgs:.1f} |")
