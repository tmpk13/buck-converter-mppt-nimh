#!/usr/bin/env python3
"""Plot duty cycle vs Vin for async buck converter NiMH charger.

Updated: CSD18540Q5B, SS56, 110µH, 150mΩ shunt
"""

import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

with open("sweep_results.json") as f:
    data = json.load(f)

vin = [d["vin"] for d in data]
duty = [d["duty_pct"] for d in data]
vout = [d["vout"] for d in data]
vbat = [d["vbat"] for d in data]
ripple = [d["ripple_mv"] for d in data]

# Ideal duty for comparison
vin_ideal = np.linspace(12, 32, 100)
duty_ideal = 4.2 / vin_ideal * 100

fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 10))
fig.suptitle("Async Buck NiMH Charger: 4.2V Output from Solar Panel\n"
             "(CSD18540Q5B, SS56, 10µH, 50mΩ shunt, 100kHz, ~2A load)",
             fontsize=13, fontweight="bold")

# Duty cycle vs Vin
ax1.plot(vin, duty, "o-", color="#d62728", linewidth=2, markersize=8, label="Simulated (ngspice)")
ax1.plot(vin_ideal, duty_ideal, "--", color="#7f7f7f", linewidth=1.5, label="Ideal (D = Vout/Vin)")
ax1.set_ylabel("Duty Cycle (%)")
ax1.set_xlabel("Input Voltage (V)")
ax1.set_title("Required PWM Duty Cycle vs Input Voltage")
ax1.legend()
ax1.grid(True, alpha=0.3)
ax1.set_ylim(0, 45)

for v, d in zip(vin, duty):
    ax1.annotate(f"{d:.1f}%", (v, d), textcoords="offset points",
                 xytext=(0, 10), ha="center", fontsize=8)

# Output voltage vs Vin (show both Vout and Vbat)
ax2.plot(vin, vout, "s-", color="#2ca02c", linewidth=2, markersize=8, label="Vout (pre-shunt)")
ax2.plot(vin, vbat, "^-", color="#1f77b4", linewidth=2, markersize=7, label="Vbat (post-shunt)")
ax2.axhline(y=4.2, color="#ff7f0e", linestyle="--", linewidth=1, label="Target 4.2V")
ax2.fill_between(vin, 4.15, 4.25, alpha=0.15, color="#2ca02c", label="±50mV band")
ax2.set_ylabel("Voltage (V)")
ax2.set_xlabel("Input Voltage (V)")
ax2.set_title("Output Voltage Regulation (Vout & Vbat)")
ax2.legend()
ax2.grid(True, alpha=0.3)
ax2.set_ylim(3.8, 4.4)

# Ripple vs Vin
ax3.bar(vin, ripple, width=1.5, color="#1f77b4", alpha=0.7, edgecolor="#1f77b4")
ax3.set_ylabel("Output Ripple (mV pk-pk)")
ax3.set_xlabel("Input Voltage (V)")
ax3.set_title("Output Voltage Ripple")
ax3.grid(True, alpha=0.3, axis="y")

plt.tight_layout()
plt.savefig("buck_4v2_sweep.png", dpi=150, bbox_inches="tight")
print("Saved buck_4v2_sweep.png")

# Summary table
print("\n╔══════════╦══════════╦══════════╦══════════╦════════════╗")
print("║  Vin (V) ║ Duty (%) ║ Vout (V) ║ Vbat (V) ║ Ripple(mV) ║")
print("╠══════════╬══════════╬══════════╬══════════╬════════════╣")
for d in data:
    vb = d.get("vbat", 0)
    print(f"║  {d['vin']:>6}  ║  {d['duty_pct']:>6.2f}  ║  {d['vout']:>6.4f}  ║  {vb:>6.4f}  ║  {d['ripple_mv']:>8.2f}  ║")
print("╚══════════╩══════════╩══════════╩══════════╩════════════╝")
