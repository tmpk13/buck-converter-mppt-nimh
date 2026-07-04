* Common models and battery load for topology comparison
* Battery: NiMH 3S, EMF 3.9V + 0.15 ohm internal resistance
* Target charge current ~1A -> terminal voltage ~4.05V

* Power NMOS ~ CSD18540Q5B class (60V, low Rds)
.model NBUCK VDMOS(Vto=2.2 Kp=60 Lambda=0.01 Rs=1m Rd=2.5m Rg=2
+ Cgdmax=1.2n Cgdmin=0.08n a=0.3 Cgs=2.5n Cjo=0.9n Rb=4m Is=2e-10 ksubthres=0.1)

* Logic-level small power NMOS ~ AO3400/SI2302 class (30V, ~30mohm at 4.5V)
.model NLL VDMOS(Vto=1.45 Kp=18 Lambda=0.02 Rs=4m Rd=18m Rg=2
+ Cgdmax=0.35n Cgdmin=0.03n a=0.3 Cgs=0.6n Cjo=0.25n Rb=15m Is=1e-11 ksubthres=0.1)

* Power PMOS ~ 40-60V, Rds ~35mohm at Vgs=-10 (e.g. SQ/AO 60V pFET)
.model PBUCK VDMOS(pchan Vto=-1.9 Kp=22 Lambda=0.02 Rs=6m Rd=22m Rg=3
+ Cgdmax=0.7n Cgdmin=0.05n a=0.3 Cgs=1.6n Cjo=0.5n Rb=20m Is=-1e-11 ksubthres=0.1)

* Small-signal NMOS 2N7002 class
.model N7002 VDMOS(Vto=1.7 Kp=0.35 Lambda=0.05 Rs=0.3 Rd=1.2 Rg=5
+ Cgdmax=25p Cgdmin=4p Cgs=25p Cjo=15p Is=1e-12)

* Schottky SS56 class (60V 5A)
.model SS56 D(Is=3e-5 Rs=0.012 N=1.05 BV=60 IBV=1e-4 CJO=350p TT=8n)

* Small-signal diode 1N4148 class
.model D1N4148 D(Is=2.5n Rs=0.6 N=1.8 CJO=4p TT=8n BV=100)

* 10V zener for gate clamp
.model DZ10 D(Is=1e-12 Rs=2 N=1.0 BV=10 IBV=5m CJO=50p)

* Small signal BJTs
.model QNPN NPN(Is=1e-14 BF=200 VAF=100 Rb=10 Rc=1 Cje=8p Cjc=4p TF=0.4n)
.model QPNP PNP(Is=1e-14 BF=200 VAF=100 Rb=10 Rc=1 Cje=8p Cjc=4p TF=0.5n)
