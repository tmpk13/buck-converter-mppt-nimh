#!/usr/bin/env python3
"""Sweep Vin and duty cycle to find 4.2V output for async buck converter.

Updated components:
  - CSD18540Q5B (Ron=2.4mΩ)
  - SS56 Schottky (60V 5A)
  - 10µH inductor (DCR ~15mΩ)
  - Input: 10µF×2 + 100µF
  - Output: 47µF×2 + 220µF
  - 50mΩ shunt between VOUT and VBAT
"""

import subprocess
import re
import json

SPICE_TEMPLATE = """\
* Async Buck Converter - Vin={vin}V, Duty={duty:.6f}
.param fsw=100k
.param period={{1/fsw}}

Vin input 0 DC {vin}

* Input caps: 10uF X7R x2 + 100uF electrolytic
Cin1 input 0 10u IC={vin}
Cin2 input 0 10u IC={vin}
Cin3 input 0 100u IC={vin}

* CSD18540Q5B: 60V N-FET, Rds_on=2.4mOhm @ Vgs=10V
.model sw_hs SW(Ron=2.4m Roff=1e6 Vt=0.5 Vh=0.1)
S1 input sw_node pwm 0 sw_hs

Vpwm pwm 0 PULSE(0 1 0 10n 10n {ton:.10e} {period:.10e})

* SS56: 60V 5A Schottky
.model schottky D(Is=1e-4 Rs=0.015 N=1.05 BV=60 IBV=1e-4 CJO=200p TT=5n)
D1 0 sw_node schottky

* 10uH inductor, DCR ~15mOhm
L1 sw_node out_l 10u IC=0
Rl out_l vout 15m

* Output caps: 47uF X5R x2 + 220uF electrolytic
Cout1 vout 0 47u IC=4.2
Cout2 vout 0 47u IC=4.2
Cout3 vout 0 220u IC=4.2

* 50mOhm current sense shunt (VOUT -> VBAT)
Rshunt vout vbat 50m

* Load ~2A (NiMH charge)
Rload vbat 0 2.1

.tran 0.1u 5m UIC
.meas tran Vout_avg AVG V(vout) FROM=4m TO=5m
.meas tran Vbat_avg AVG V(vbat) FROM=4m TO=5m
.meas tran Vout_ripple PP V(vout) FROM=4m TO=5m
.meas tran IL_avg AVG I(L1) FROM=4m TO=5m
.meas tran Ishunt_avg AVG I(Rshunt) FROM=4m TO=5m

.end
"""

FSW = 100e3
PERIOD = 1.0 / FSW
TARGET = 4.2


def run_sim(vin: float, duty: float) -> dict | None:
    ton = duty * PERIOD
    netlist = SPICE_TEMPLATE.format(vin=vin, duty=duty, ton=ton, period=PERIOD)

    with open("/tmp/buck_run.spice", "w") as f:
        f.write(netlist)

    result = subprocess.run(
        ["ngspice", "-b", "/tmp/buck_run.spice"],
        capture_output=True, text=True, timeout=60
    )

    output = result.stdout + result.stderr
    vout_match = re.search(r"vout_avg\s*=\s*([\d.eE+-]+)", output)
    vbat_match = re.search(r"vbat_avg\s*=\s*([\d.eE+-]+)", output)
    ripple_match = re.search(r"vout_ripple\s*=\s*([\d.eE+-]+)", output)
    il_match = re.search(r"il_avg\s*=\s*([\d.eE+-]+)", output)
    ishunt_match = re.search(r"ishunt_avg\s*=\s*([\d.eE+-]+)", output)

    if vout_match:
        return {
            "vout": float(vout_match.group(1)),
            "vbat": float(vbat_match.group(1)) if vbat_match else 0,
            "ripple": float(ripple_match.group(1)) if ripple_match else 0,
            "il": float(il_match.group(1)) if il_match else 0,
            "vshunt": (float(il_match.group(1)) if il_match else 0) * 0.050,
        }
    return None


def find_duty(vin: float) -> tuple[float, dict]:
    """Binary search for duty cycle that gives TARGET Vout."""
    d_est = TARGET / vin
    d_low = d_est * 0.5
    d_high = d_est * 2.0

    best_duty = d_est
    best_result = None

    for _ in range(15):
        d_mid = (d_low + d_high) / 2.0
        res = run_sim(vin, d_mid)
        if res is None:
            print(f"  Sim failed at Vin={vin}, D={d_mid:.4f}")
            d_high = d_mid
            continue

        best_duty = d_mid
        best_result = res
        err = res["vout"] - TARGET

        if abs(err) < 0.005:
            break
        elif err > 0:
            d_high = d_mid
        else:
            d_low = d_mid

    return best_duty, best_result


def main():
    vin_values = list(range(12, 33, 2))
    results = []

    print(f"{'Vin(V)':>8} {'Duty(%)':>8} {'Vout(V)':>8} {'Vbat(V)':>8} {'Ripple(mV)':>10} {'IL(A)':>8} {'Vshunt(mV)':>10}")
    print("-" * 72)

    for vin in vin_values:
        duty, res = find_duty(vin)
        if res:
            ripple_mv = res["ripple"] * 1000
            vshunt_mv = res["vshunt"] * 1000
            print(f"{vin:>8} {duty*100:>8.2f} {res['vout']:>8.4f} {res['vbat']:>8.4f} {ripple_mv:>10.2f} {res['il']:>8.3f} {vshunt_mv:>10.1f}")
            results.append({
                "vin": vin,
                "duty_pct": round(duty * 100, 3),
                "vout": round(res["vout"], 4),
                "vbat": round(res["vbat"], 4),
                "ripple_mv": round(ripple_mv, 2),
                "il_avg": round(res["il"], 3),
                "vshunt_mv": round(vshunt_mv, 1),
            })

    with open("sweep_results.json", "w") as f:
        json.dump(results, f, indent=2)

    print(f"\nResults saved to sweep_results.json")


if __name__ == "__main__":
    main()
