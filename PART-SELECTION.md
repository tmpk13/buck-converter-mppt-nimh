# Forest Sensor Platform - part selection

Every purchasable component on both sheets now carries `MPN`, `MANUFACTURER`,
`Digi-Key PN` and `Datasheet`. Sourcing data started from the Digi-Key list export
`Forest-2.xlsx`; the rest was searched live against the Digi-Key API.

Supersedes the "still unsourced" tables in [BOM.md](BOM.md) and the search-parameter
guide in [SOURCING.md](SOURCING.md).

| File | Parts | With MPN | Without |
| --- | ---: | ---: | --- |
| `Forest-Sensor-Platform.kicad_sch` | 70 | 62 | H1-H4, TP1-TP4 |
| `buck_converter.kicad_sch` | 33 | 30 | TP5, TP6, TP8 |
| `Forest-Sensor-Platform.kicad_pcb` | 102 | 91 | mounting holes, test points |

Mounting holes and test points are not purchased line items. `Forest-Sensor-Platform.csv`
and `buck_converter.csv` are regenerated grouped BOMs (36 and 23 lines).

## What Forest-2.xlsx already covered

Twenty-two of the 34 list items map onto a placed component. Nine of those were sitting
unclaimed because the earlier pass only looked at the main sheet - they all belong to
`buck_converter.kicad_sch`, which the `split` branch moved out:

| Ref | List MPN | Role |
| --- | --- | --- |
| D1 | BZT52B12 | Gate-drive zener clamp |
| D4 | P6SMBJ43A | Solar input TVS |
| F1 | KLM3S500RY | Input PTC |
| J14 | S4B-XH-A-1 | Solar input, JST XH 4-pos |
| L6 | SRN6045TA-330M | 33 uH buck output |
| Q1 | MBT3946DW1T2G | Dual NPN/PNP level shift |
| Q2 | MCAC054P10Y-TP | P-channel high side |
| Q3 | BSS123NH6433XTMA1 | N-channel level shift |
| R1 | MCSF2512FR050Q9 | 50 mOhm charge shunt |

Four list items have no home and were not used: `OSTVN04A150` (no 4-position screw
terminal exists), `SWT0115-020025SSA` (switch alternate), `XRCGB32M000F1S1DR0` and
`0603N180J500CT` (32 MHz crystal and its load caps - the CH32V203 they belonged to was
replaced by the CH572D module, which needs no external crystal). `103R006BB100` /
`103P006BB100`, the 6-position board-to-board pair, still has no symbol on either sheet.

Three list items were **rejected** because they do not fit what is drawn - see below.

## Parts chosen against list items

**U1: INA181A1IDBVR, not INA180A1QDBVRQ1.** The list carries the INA180, which is
SOT-23-5. U1 is drawn and laid out as SOT-23-6. Checking all six pins: IN+/IN-/OUT are
wired, V+ goes to +3.3V, and **REF is tied to GND**, which is exactly what makes an INA181
behave like an INA180. The 6-pin part is the correct buy and needs no schematic change.
Gain 20 V/V into the 50 mOhm shunt puts 3.3 A at the top of the 3.3 V ADC range.

**D5, D8: SK56A-LTP, not SS56F.** Both footprints are `Diode_SMD:D_SMA` (DO-214AC). The
listed SS56F is SMAF / DO-221AC, a flat-lead package with a smaller land pattern - it will
not solder to those pads. SK56A-LTP is the same 60 V / 5 A Schottky in true SMA, 143 k in
stock at $0.124.

**SW1: PTS647SK38SMTR2 LFS, not SWT0210-045026GSA.** SW1's footprint is
`SW_SPST_PTS647_Sx38`, which the KiCad library documents as "C&K PTS647 Series 4.5 mm Tact
Switch, 3.8 mm Height". The listed GCT part is a 4.5 x 4.5 mm gull-wing that lands nowhere
near those pads. Buying the C&K part the footprint was drawn for removes the problem
without touching the layout.

## New parts

Passives are consolidated onto two families to keep the line-item count down: **Stackpole
RMCF** thick film for every resistor (the 0805 jumper already on the list is from this
series) and a small mix of mainstream MLCC vendors chosen per rail.

| Refs | Qty | Value | MPN | Manufacturer | Digi-Key PN | Unit |
| --- | ---: | --- | --- | --- | --- | ---: |
| C9, C13, C31, C35 | 4 | 10uF 25V 0603 | GRT188R61E106ME13D | Murata | 490-12323-2-ND | $0.060 |
| C10, C15, C16, C19, C21, C32, C44 | 7 | 100nF 50V 0603 | CC0603KRX7R9BB104 | YAGEO | 311-1344-2-ND | $0.016 |
| C12, C14 | 2 | 1uF 25V 0805 | C0805C105K3RACTU | KEMET | 399-C0805C105K3RACTUTR-ND | $0.032 |
| C30, C34 | 2 | 1uF 25V 0603 | CGA3E1X7R1E105K080AC | TDK | 445-6931-2-ND | $0.030 |
| C46 | 1 | 22uF 16V 0603 | CL10A226MO7JZNC | Samsung | 1276-7076-2-ND | $0.186 |
| C11, C20 | 2 | 10uF 50V 1206 | GMT31X7R106K50NT2 | Cal-Chip | 2571-GMT31X7R106K50NT2TR-ND | $0.400 |
| C22, C23 | 2 | 47uF 10V 1206 | GRM31CR61A476ME15L | Murata | 490-5528-2-ND | $0.100 |
| C24 | 1 | 1uF 50V 0603 | CL10A105KB8NNNC | Samsung | 1276-1860-2-ND | $0.020 |
| R13, R16-R18, R29, R30, R12, R14, R15, R57 | 10 | 10K | RMCF0603FT10K0 | Stackpole | RMCF0603FT10K0TR-ND | $0.0037 |
| R21, R22, R31, R36, R37, R44 | 6 | 1M | RMCF0603FT1M00 | Stackpole | RMCF0603FT1M00TR-ND | $0.0037 |
| R25, R26 | 2 | 5.1K | RMCF0603FT5K10 | Stackpole | RMCF0603FT5K10TR-ND | $0.0037 |
| R27, R28 | 2 | 4.7K | RMCF0603FT4K70 | Stackpole | RMCF0603FT4K70TR-ND | $0.0037 |
| R38, R39, R40, R19 | 4 | 1K | RMCF0603FT1K00 | Stackpole | RMCF0603FT1K00TR-ND | $0.0035 |
| R11, R55 | 2 | 100K | RMCF0603FT100K | Stackpole | RMCF0603FT100KTR-ND | $0.0037 |
| R58 | 1 | 2.2K | RMCF0603FT2K20 | Stackpole | RMCF0603FT2K20TR-ND | $0.0035 |
| R56 | 1 | 22R | RMCF0603FT22R0 | Stackpole | RMCF0603FT22R0TR-ND | $0.0037 |
| R42, R43 | 2 | 0 (0603) | RMCF0603ZT0R00 | Stackpole | RMCF0603ZT0R00TR-ND | $0.0025 |
| R54 | 1 | 4.7K 1206 | RMCF1206FT4K70 | Stackpole | RMCF1206FT4K70TR-ND | $0.0066 |
| D2, D6, D12, D3 | 4 | LED green | LTST-C190KGKT | Lite-On | 160-1435-2-ND | $0.042 |
| D7 | 1 | TVS 5V bidir | SMAJ5.0CA | Littelfuse | SMAJ5.0CALFTR-ND | $0.081 |
| D5, D8 | 2 | Schottky 60V 5A | SK56A-LTP | MCC | SK56A-LTPMSTR-ND | $0.124 |
| J2 | 1 | JST SH 5-pos | BM05B-SRSS-TB | JST | 455-BM05B-SRSS-TBTR-ND | $0.376 |
| J8, J10 | 2 | JST SH 4-pos | BM04B-SRSS-TB | JST | 455-BM04B-SRSS-TBTR-ND | $0.315 |
| J4 | 1 | 1x02 2.54mm header | M20-9990246 | Harwin | 952-2262-ND | $0.100 |
| SMA1 | 1 | SMA edge launch | SMA-J-P-H-ST-EM1 | Samtec | SAM8857-ND | $2.650 |
| SW1 | 1 | Tact switch | PTS647SK38SMTR2 LFS | C&K | 108-PTS647SK38SMTR2LFSTR-ND | $0.168 |
| U1 | 1 | Current sense | INA181A1IDBVR | TI | 296-47656-2-ND | $0.189 |
| U3 | 1 | LoRa module | LoRa-E5-HF | Seeed | 1597-317990829TR-ND | $8.447 |
| U4 | 1 | BLE module | CH572D | WCH | - | - |

Prices are the Digi-Key unit price at the break the API returned; for most passives that
is the reel break (2000-5000 pcs). Digi-Key lists cut-tape and reel variants of the same
MPN under different part numbers, so **the MPN is the authoritative field** - the recorded
Digi-Key PN is whichever variant the search returned.

**Estimated total, one board set: $25.60**, excluding U4 and J6 (neither is a Digi-Key
part). U3 at $8.45 and SMA1 at $2.65 are 43% of that.

### Why these, specifically

**C46 moved from 10 V to 16 V rating, same 0603 case.** It is the TPS613222A boost output
bulk cap sitting at 5 V. A 22 uF 10 V part in 0603 keeps roughly a third of its rating at
5 V bias; the 16 V part keeps roughly half. That recovers most of the missing capacitance
without a layout change, which was the alternative (move to 0805). Costs $0.11 more.

**C9 and C13 dropped from 50 V to 25 V.** Confirmed by search: 10 uF in 0603 tops out at
25 V, nobody makes a 50 V part in that case. Both sit on +3.3 V, so 25 V is 7x margin.

**C11, C20 are AEC-Q200 X7R.** They are the buck input caps on the solar rail, outdoors.
Only Cal-Chip stocks 10 uF / 50 V / 1206 in X7R in any volume - the mainstream alternatives
at that size are X5R (85 C limit) or X7T. The AEC-Q200 GMT variant gets -55/+125 C for
$0.08 more than the plain one. See the derating caveat below.

**R38-R40 set to 1K.** Each is a series element from an MCU ADC pin into a sense net with
100 nF to ground, so it sets the anti-alias corner: 1 kOhm gives 1.6 kHz, roughly 40 dB
down at the buck's 160 kHz switching harmonics, and keeps the ADC source impedance far
below the STM32WLE5's limit. It also merges with R19's line item.

**LEDs: one green part for all four.** LTST-C190KGKT is the highest output (44.5 mcd at
20 mA) among the ~2.1 V forward-voltage greens, which matters because three of the four are
driven through 10 k - see below.

**U3 is the full LoRa-E5, not the Wio-E5-LE.** Digi-Key stocks the bare LoRa-E5-HF module
(Seeed 317990829) but **only in tape and reel with a 1000-piece minimum**. For prototype
quantities either order from Seeed or Mouser direct, or substitute the Wio-E5-LE
(1597-114993120-ND, $7.11, MOQ 1, 728 in stock), which is footprint-identical but caps
transmit power at +14 dBm instead of +22 dBm. For a forest deployment that range difference
is the whole point of the module, so the full part is recorded.

**U4 has no Digi-Key source.** Digi-Key does not stock WCH silicon. Order the CH572D from
LCSC or WCH direct. MPN and manufacturer are recorded; the Digi-Key PN is left blank.

**J6 has no Digi-Key source.** AMASS XT30PW-M is not in the Digi-Key catalog. Recorded with
manufacturer only.

## Corrections applied

These were needed to make the BOM self-consistent - the value string has to agree with the
part being ordered.

- **`1m` -> `1M` on R21, R22, R31, R36, R37, R44.** KiCad reads `1m` as 1 milliohm. All six
  are enable-pin pull-downs (U2 ON, U8 ON, U4/U7 GPIO_EN, the TPT482's receiver and input
  enables, 5V_EN); at 1 milliohm they are dead shorts holding those six functions off.
- **`TBD` -> `1K` on R38, R39, R40.**
- **`10uF 50V` -> `10uF 25V` on C9, C13**, and **`22uF 10V` -> `22uF 16V` on C46**, matching
  the parts above.
- **R33 is now actually DNP.** Its value read `DNP` but its `dnp` flag was `no` and
  `in_bom` was `yes`, so R33 and R34 - both 0 ohm, in parallel from +3.3 V to the +5 V pin
  of J7 - would both have been stuffed, shorting the two rails. The flag is set in the
  schematic and `(attr smd dnp)` on the footprint. R33 keeps the same 0805 jumper MPN so
  the option stays documented.
- **Value strings normalized** (`100n` -> `100nF 50V`, `10u` -> `10uF 25V`, `22` -> `22R`,
  `4.7k 1206` -> `4.7K`, and so on) so identical parts collapse to one BOM line.

## Open before ordering

**The indicator LEDs run at a tenth of a milliamp.** D2, D6 and D12 are each in series with
a 10 k resistor. D12 off the 3.3 V rail works out to about 0.12 mA, which even at
LTST-C190KGKT's efficiency is roughly a quarter of a millicandela - visible in a dark
enclosure during bring-up, not much more. Dropping those three series resistors to 1 k
would give 1-3 mA and a normal-looking indicator. D3 on the buck sheet already uses 1 k and
is fine.

**C11 and C20 lose most of their capacitance at panel voltage.** 10 uF X7R in 1206 rated
50 V, biased at a 24-36 V panel, keeps well under half its rating - the pair behaves like
roughly 6-7 uF at the top of the range. That is workable for a 1-2 A buck at 100-200 kHz
but leaves no margin. If the input ripple measures badly, the upgrade is 1210: Samsung
CL32B106KBJNNWE is 10 uF / 50 V / X7R at $0.197, cheaper *and* better, but 1210 will not
solder onto 1206 pads.

**C9 and C10 will not group with their siblings.** Both use
`Capacitor_SMD:C_0603_1608Metric` while the rest of the 0603 capacitors use the
`_Pad1.08x0.95mm_HandSolder` variant. Same part, same value - the BOM splits them only
because the grouping key includes the footprint. Harmless for purchasing; worth
normalizing the footprints if the split is annoying.

**The board-to-board link is still unplaced.** `103R006BB100` / `103P006BB100` is on the
list, and the five signals that cross between the boards - `BAT_ISENSE`, `VSENSE_OUT`,
`VSENSE_VIN`, `PWM_Buck`, `Battery_Out` - plus a ground return are exactly the six
positions it provides. Neither half has a symbol on either sheet yet.

**J7's footprint still needs a check.** OSTVN06A150 is a 6-position 2.54 mm side-entry
block matching the pitch and pin count of the Phoenix MPT footprint in use, but the body
outline and pin diameter come from a different vendor. Confirm hole size and courtyard
against the On Shore drawing before fabrication.

## Regenerating the BOMs

```
kicad-cli sch export bom \
  --fields 'Reference,${QUANTITY},Value,MPN,MANUFACTURER,Digi-Key PN,${DNP},${EXCLUDE_FROM_BOM},${EXCLUDE_FROM_BOARD},Footprint,Datasheet,Description' \
  --labels 'Reference,Qty,Value,MPN,Manufacturer,Digi-Key PN,DNP,Exclude from BOM,Exclude from Board,Footprint,Datasheet,Description' \
  --group-by 'Value,MPN,MANUFACTURER,Digi-Key PN,${DNP},${EXCLUDE_FROM_BOM},${EXCLUDE_FROM_BOARD},Footprint' \
  --sort-field Reference --ref-delimiter ',' --ref-range-delimiter '' \
  --output Forest-Sensor-Platform.csv Forest-Sensor-Platform.kicad_sch
```
