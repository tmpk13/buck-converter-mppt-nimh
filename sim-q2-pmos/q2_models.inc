* Device models for the Q2 high-side PMOS async buck stage.

* Q2 - MCAC054P10Y-TP, DFN5060 P-channel (MCC datasheet Rev.4.1-08192025)
*   VDS -100V, VGS +/-20V abs max, ID -25A
*   RDS(on) 43m typ / 54m max at VGS=-10V, ID=-20A
*   VGS(th) -1.9/-2.7/-3.5V, Rg 12.7 typ
*   Ciss 870p, Coss 205p, Crss 6p at VDS=-50V; Qg 15.3n, Qgd 3.1n
*   VSD -1.2V at IS=-20A
.model PMOS_MCAC054P10Y VDMOS(pchan
+ Vto=-2.7 Kp=10.5 Lambda=0.008 ksubthres=0.15
+ Rs=5m Rd=25m Rg=12.7
+ Cgs=864p Cgdmax=350p Cgdmin=6p a=0.3 Cjo=1.5n
+ Is=1e-11 N=1.0 Rb=25m)

* Q3 - BSS123 logic-level NMOS, SOT-23. 100V, 170mA, RDS(on) 6 ohm at VGS=10V,
* VGS(th) 0.8-1.5V, Ciss ~35pF. Gate is driven from a 3.3V MCU pin.
.model BSS123 VDMOS(
+ Vto=1.2 Kp=0.15 Lambda=0.02 ksubthres=0.1
+ Rs=0.3 Rd=3.5 Rg=8
+ Cgs=30p Cgdmax=25p Cgdmin=3p a=0.3 Cjo=20p
+ Is=1e-13 N=1.0 Rb=1)

* Q1 - MBT3946DW1T1 dual complementary BJT, SOT-363. 40V, 200mA.
* Standard 2N3904 / 2N3906 die models.
.model NPN3946 NPN(Is=6.734f Xti=3 Eg=1.11 Vaf=74.03 Bf=416.4 Ne=1.259
+ Ise=6.734f Ikf=66.78m Xtb=1.5 Br=.7371 Nc=2 Isc=0 Ikr=0 Rc=1
+ Cjc=3.638p Mjc=.3085 Vjc=.75 Fc=.5 Cje=4.493p Mje=.2593 Vje=.75
+ Tr=239.5n Tf=301.2p Itf=.4 Vtf=4 Xtf=2 Rb=10)
.model PNP3946 PNP(Is=1.41f Xti=3 Eg=1.11 Vaf=18.7 Bf=180.7 Ne=1.5
+ Ise=0 Ikf=80m Xtb=1.5 Br=4.977 Nc=2 Isc=0 Ikr=0 Rc=2.5
+ Cjc=9.728p Mjc=.5776 Vjc=.75 Fc=.5 Cje=8.063p Mje=.3677 Vje=.75
+ Tr=33.42n Tf=179.3p Itf=.4 Vtf=4 Xtf=6 Rb=10)

* D8 / freewheel - SS56 class 60V 5A Schottky
.model SS56 D(Is=3e-5 Rs=0.012 N=1.05 BV=60 IBV=1e-4 Cjo=350p Tt=8n)

* Gate-drive rail clamp zeners. D1 is fitted as a BZT52B12 (12 V, 500 mW).
.model DZ10 D(Is=1e-12 Rs=2 N=1.0 BV=10 IBV=5m Cjo=50p)
.model DZ12 D(Is=1e-12 Rs=2 N=1.0 BV=12 IBV=5m Cjo=50p)
