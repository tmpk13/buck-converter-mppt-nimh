#!/usr/bin/env python3
"""Drive the ngspice-mcp server (~/ngspice/mcp/ngspice-mcp) over stdio JSON-RPC.

Usage as library:
    from mcp_ngspice import NgspiceMCP
    with NgspiceMCP() as ng:
        ng.load_circuit(netlist_text)
        out = ng.run("tran 0.1u 5m uic")
        out = ng.run("meas tran vout_avg AVG v(out) from=4m to=5m")
        print(ng.read_stdout())

CLI: mcp_ngspice.py <netlist-file> <command> [command ...]
"""
import json
import subprocess
import sys
import os

SERVER = os.path.expanduser("~/ngspice/mcp/ngspice-mcp/ngspice-mcp")


class NgspiceMCP:
    def __init__(self, workdir="."):
        self.proc = subprocess.Popen(
            [SERVER, "-d", workdir],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL, text=True, bufsize=1)
        self._id = 0
        self._rpc("initialize", {
            "protocolVersion": "2024-11-05", "capabilities": {},
            "clientInfo": {"name": "claude", "version": "1.0"}})
        self._notify("notifications/initialized")

    def _send(self, obj):
        self.proc.stdin.write(json.dumps(obj) + "\n")
        self.proc.stdin.flush()

    def _notify(self, method, params=None):
        msg = {"jsonrpc": "2.0", "method": method}
        if params:
            msg["params"] = params
        self._send(msg)

    def _rpc(self, method, params=None):
        self._id += 1
        msg = {"jsonrpc": "2.0", "id": self._id, "method": method}
        if params is not None:
            msg["params"] = params
        self._send(msg)
        while True:
            line = self.proc.stdout.readline()
            if not line:
                raise RuntimeError("server closed pipe")
            try:
                resp = json.loads(line)
            except json.JSONDecodeError:
                continue
            if resp.get("id") == self._id:
                if "error" in resp:
                    raise RuntimeError(resp["error"])
                return resp["result"]
            # else: notification (resource updated etc.) -> ignore

    def tool(self, name, args=None):
        res = self._rpc("tools/call", {"name": name, "arguments": args or {}})
        texts = [c.get("text", "") for c in res.get("content", [])]
        return "\n".join(t for t in texts if t)

    def load_circuit(self, netlist):
        return self.tool("loadCircuit", {"netlist": netlist})

    def run(self, command):
        return self.tool("runSimulation", {"command": command})

    def plots(self):
        return self.tool("getPlotNames")

    def vectors_info(self, plot):
        return self.tool("getVectorsInfo", {"plot": plot})

    def vector_data(self, vectors, plot, points):
        return self.tool("getVectorData",
                         {"vectors": vectors, "plot": plot, "points": points})

    def read_stdout(self):
        res = self._rpc("resources/read", {"uri": "stdout://"})
        return "\n".join(c.get("text", "") for c in res.get("contents", []))

    def close(self):
        try:
            self.proc.stdin.close()
        except Exception:
            pass
        self.proc.wait(timeout=10)

    def __enter__(self):
        return self

    def __exit__(self, *a):
        self.close()


if __name__ == "__main__":
    netlist = open(sys.argv[1]).read()
    with NgspiceMCP() as ng:
        print(ng.load_circuit(netlist))
        for cmd in sys.argv[2:]:
            r = ng.run(cmd)
            if r:
                print(r)
        print(ng.read_stdout())
