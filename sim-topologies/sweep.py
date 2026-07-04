#!/usr/bin/env python3
"""Sweep Vin per topology; binary-search duty for 1A charge current via ngspice MCP."""
import json
import re
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mcp_ngspice import NgspiceMCP

HERE = os.path.dirname(os.path.abspath(__file__))
TARGET_I = 1.0
TOL = 0.02

TOPOS = {
    "hs_nmos": {"file": "hs_nmos.spice", "dmax": 0.95},
    "pmos_buck": {"file": "pmos_buck.spice", "dmax": 0.99},
    "lowside_buck": {"file": "lowside_buck.spice", "dmax": 0.99},
    "sepic": {"file": "sepic.spice", "dmax": 0.85},
}

MEAS = [
    "meas tran ichg AVG i(VB) from=1.5m to=2m",
    "meas tran vterm AVG v(pbv) from=1.5m to=2m",  # placeholder, replaced below
]


def netlist(topo, vin, duty):
    t = open(os.path.join(HERE, TOPOS[topo]["file"])).read()
    return t.replace("@VIN@", f"{vin}").replace("@DUTY@", f"{duty:.5f}")


def run_point(ng, topo, vin, duty, _retry=0):
    ng.load_circuit(netlist(topo, vin, duty))
    ng.run("tran 0.05u 2m uic")
    ng.run("meas tran ichg AVG i(VB) from=1.5m to=2m")
    ng.run("meas tran pin AVG v(pinv) from=1.5m to=2m")
    ng.run("meas tran pbat AVG v(pbv) from=1.5m to=2m")
    ng.run("meas tran vgsmax MAX v(vgsv) from=1.5m to=2m")
    ng.run("meas tran vgsmin MIN v(vgsv) from=1.5m to=2m")
    out = ng.read_stdout()
    vals = {}
    for name in ("ichg", "pin", "pbat", "vgsmax", "vgsmin"):
        m = re.findall(rf"{name}\s*=\s*([-+0-9.eE]+)", out)
        vals[name] = float(m[-1]) if m else None
    ng.run("destroy all")
    # A dead sim (aborted tran) shows up as pin ~ 0 even at nonzero duty;
    # retry with a nudged duty, in a fresh session on the second attempt.
    failed = vals["ichg"] is None or (vals["pin"] is not None
                                      and abs(vals["pin"]) < 1e-3 and duty > 0.03)
    if failed and _retry < 2:
        if _retry == 1:
            ng.run("remcirc")
        return run_point(ng, topo, vin, duty + 0.0007 * (_retry + 1), _retry + 1)
    vals["failed"] = failed
    return vals


def solve_point(ng, topo, vin):
    dmax = TOPOS[topo]["dmax"]
    lo, hi = 0.02, dmax
    # check reachability at dmax
    r = run_point(ng, topo, vin, dmax)
    if r["ichg"] is None or r["ichg"] < TARGET_I - TOL:
        return {"vin": vin, "duty": dmax, "clamped": True, **r}
    best = None
    for _ in range(11):
        mid = (lo + hi) / 2
        r = run_point(ng, topo, vin, mid)
        if r.get("failed"):
            best = {"vin": vin, "duty": mid, "clamped": False, **r}
            break
        i = r["ichg"]
        best = {"vin": vin, "duty": mid, "clamped": False, **r}
        if abs(i - TARGET_I) < TOL:
            break
        if i > TARGET_I:
            hi = mid
        else:
            lo = mid
    return best


def main():
    topo = sys.argv[1]
    vins = [float(v) for v in sys.argv[2:]]
    results = []
    with NgspiceMCP(workdir=HERE) as ng:
        for vin in vins:
            r = solve_point(ng, topo, vin)
            eff = None
            if r.get("pin") and r.get("pbat"):
                eff = r["pbat"] / r["pin"] * 100
            r["eff_pct"] = eff
            results.append(r)
            print(json.dumps(r), flush=True)
    with open(os.path.join(HERE, f"results_{topo}.json"), "w") as f:
        json.dump(results, f, indent=1)


if __name__ == "__main__":
    main()
