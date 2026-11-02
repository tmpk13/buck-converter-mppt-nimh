# Forest Sensor Platform - BOM sourcing status

Sourcing data merged from the Digi-Key list export `Forest-2.xlsx` (34 line items,
"My Lists Worksheet") into `Forest-Sensor-Platform.kicad_sch`.

Schematic: 70 placed components (excluding power and GND flags), 13 of which now carry a
manufacturer part number.

## What changed

| File | Change |
| --- | --- |
| `Forest-Sensor-Platform.kicad_sch` | Added `MPN`, `MANUFACTURER`, `Digi-Key PN` properties (hidden) to 13 symbols; filled `Datasheet` on those symbols; filled U10's empty `Value` |
| `Forest-Sensor-Platform.kicad_pcb` | Same three fields carried onto the matching footprints |
| `Forest-Sensor-Platform.kicad_pro` | Added the new fields as BOM columns after `Value`; turned on the `Description` column |
| `Forest-Sensor-Platform.csv` | Regenerated BOM export with the new columns |

Manufacturer data goes in `MANUFACTURER`, the all-caps field this project already listed
in its BOM settings, displayed under the label "Manufacturer". Do not add a second
lowercase `Manufacturer` field - two manufacturer columns is what made the data look
missing.

Re-export the BOM from the CLI with:

```
kicad-cli sch export bom \
  --fields 'Reference,${QUANTITY},Value,MPN,MANUFACTURER,Digi-Key PN,${DNP},${EXCLUDE_FROM_BOM},${EXCLUDE_FROM_BOARD},Footprint,Datasheet,Description' \
  --labels 'Reference,Qty,Value,MPN,Manufacturer,Digi-Key PN,DNP,Exclude from BOM,Exclude from Board,Footprint,Datasheet,Description' \
  --group-by 'Value,MPN,MANUFACTURER,Digi-Key PN,${DNP},${EXCLUDE_FROM_BOM},${EXCLUDE_FROM_BOARD},Footprint' \
  --sort-field Reference --ref-delimiter ',' --ref-range-delimiter '' \
  --output Forest-Sensor-Platform.csv Forest-Sensor-Platform.kicad_sch
```

## Sourced components

Prices are the Digi-Key unit prices captured in `Forest-2.xlsx`; "On list" is the
quantity requested in that export.

| Ref | Qty | Schematic value | MPN | Manufacturer | Digi-Key PN | Unit | Ext | On list | Stock |
| --- | ---: | --- | --- | --- | --- | ---: | ---: | ---: | --- |
| U6 | 1 | TPT482-VS2R | TPT482-VS2R | 3PEAK | 5503-TPT482-VS2RCT-ND | $1.37 | $1.37 | 1 | 2,142 (non-stock) |
| U2, U8 | 2 | LM66200DRLR | LM66200DRLR | Texas Instruments | 296-LM66200DRLRCT-ND | $0.59 | $1.18 | 2 | 22,053 |
| U7, U13 | 2 | TPS22991CRAAR | TPS22991CRAAR | Texas Instruments | 296-TPS22991CRAARCT-ND | $0.30 | $0.60 | 2 | 17,631 |
| U11 | 1 | TPS613222ADBV | TPS613222ADBVR | Texas Instruments | 296-50503-1-ND | $0.55 | $0.55 | 1 | 15,911 |
| U10 | 1 | TLV75733PDRV | TLV75733PDRVR | Texas Instruments | 296-49281-1-ND | $0.48 | $0.48 | 1 | 4,983 |
| J3 | 1 | MSD-1-A | MSD-1-A | Same Sky | 2223-MSD-1-ACT-ND | $0.44 | $0.44 | 1 | 21,106 |
| J1 | 1 | USB_C_2.0_16P | UJ20-C-H-G-SMT-2A-P16-TR | Same Sky | 2223-UJ20-C-H-G-SMT-2A-P16-TRCT-ND | $0.39 | $0.39 | 1 | 4,809 |
| SW1 | 1 | WIO_RST | SWT0210-045026GSA | GCT | 2073-SWT0210-045026GSACT-ND | $0.18 | $0.18 | 2 | 4,142 |
| L5 | 1 | 2.2uH | AOTA-N252010S-2R2MT | Abracon | 535-AOTA-N252010S-2R2MTCT-ND | $0.14 | $0.14 | 1 | 5,800 |
| R34 | 1 | 0 | RMCF0805ZT0R00 | Stackpole | RMCF0805ZT0R00CT-ND | $0.01 | $0.01 | 10 | 2,606,571 |
| J7 | 1 | Conn_01x06 2.54mm Screw Terminal | OSTVN06A150 | On Shore Technology | ED10565-ND | n/q | n/q | 0 | 5,419 |

Sourced subtotal, one board: **$5.34** plus J7. J7 was on the list but never quoted
(zero requested), so no unit price came across in the export; the 4-position
OSTVN04A150 in the same list is $1.66.

## Open items on the sourced parts

**L5 value - resolved.** The schematic read 4.7 uH against the ordered 2.2 uH part;
`Value` is now 2.2uH and agrees with AOTA-N252010S-2R2MT.

**SW1 footprint does not fit.** SW1 currently uses
`Button_Switch_SMD:SW_SPST_PTS647_Sx38` - a 6.0 x 3.8 mm body with 1.55 x 1.0 mm pads at
(+/-2.625, +/-1.6) mm. The SWT0210-045026GSA is a 4.5 x 4.5 mm gull-wing part, so its
terminals will not land on those pads. GCT's spec sheet (rev A1, 4 pages) carries no
recommended-PCB-layout drawing, so the land pattern has to come from GCT's footprint
download. Either build that footprint, or pick a switch that fits PTS647. The list also
holds SWT0115-020025SSA (3.5 x 3.1 mm, nothing requested) as a second candidate; it does
not fit either.

**J1 footprint verified compatible.** The Same Sky recommended layout matches
`Connector_USB:USB_C_Receptacle_GCT_USB4105-xx-A_16P_TopMnt_Horizontal` dimension for
dimension: shield holes 8.64 mm apart (KiCad +/-4.32), outer signal pads 6.40 mm apart
(+/-3.20), 4.80 mm (+/-2.40), 3.50 mm (+/-1.75), eight 0.30 mm pads on 0.50 mm pitch,
four 0.60 mm pads, 0.65 mm alignment bosses 5.78 mm apart (+/-2.89), pad row 3.68 mm
from the board edge, shield slots 2.10/1.80 x 1.00 mm. Only difference: Same Sky draws
1.80 mm long signal pads where KiCad uses 1.15 mm, which just trims the solder fillet.

**J7 footprint needs a check.** OSTVN06A150 is a 6-position 2.54 mm side-entry block,
matching the pitch and pin count of `TerminalBlock_Phoenix_MPT-0,5-6-2.54_1x06_P2.54mm_Horizontal`,
but the body outline and pin diameter come from a different vendor. Confirm hole size and
courtyard against the On Shore drawing before fabrication.

**U10 value was blank.** The symbol had an empty `Value`, which would have grouped
oddly in the BOM. Set to `TLV75733PDRV` to match its library symbol.

**R42, R43 are 0 ohm in 0603.** The only 0 ohm jumper on the list is 0805
(RMCF0805ZT0R00, used for R34). Add an 0603 jumper, or move these to 0805.

## Schematic components still unsourced

| Ref | Qty | Value | Footprint |
| --- | ---: | --- | --- |
| C9 | 1 | 10uF 50V | C_0603_1608Metric |
| C10 | 1 | 100nF 50V | C_0603_1608Metric |
| C12, C14 | 2 | 1uF 25V | C_0805_2012Metric_HandSolder |
| C13 | 1 | 10uF 50V | C_0603_1608Metric_HandSolder |
| C15, C44 | 2 | 100nF 50V | C_0603_1608Metric_HandSolder |
| C16, C19, C21, C32 | 4 | 100n | C_0603_1608Metric_HandSolder |
| C30, C34 | 2 | 1u | C_0603_1608Metric_HandSolder |
| C31, C35 | 2 | 10u | C_0603_1608Metric_HandSolder |
| C46 | 1 | 22uF 10V | C_0603_1608Metric_HandSolder |
| D2, D6, D12 | 3 | LED | LED_0603_1608Metric_HandSolder |
| D7 | 1 | SMAJ5.0CA clamp@9.2V | D_SMA |
| J2 | 1 | Conn_01x05_Shielded | JST_SH_BM05B-SRSS-TB_1x05-1MP |
| J4 | 1 | POWER | PinHeader_1x02_P2.54mm_Vertical |
| J8, J10 | 2 | I2C1 / I2C2 | JST_SH_BM04B-SRSS-TB_1x04-1MP |
| R13, R16-R18, R29, R30 | 6 | 10K | R_0603_1608Metric_HandSolder |
| R21, R22, R31, R36, R37, R44 | 6 | 1m | R_0603_1608Metric_HandSolder |
| R25, R26 | 2 | 5.1K | R_0603_1608Metric_HandSolder |
| R27, R28 | 2 | 4.7K | R_0603_1608Metric_HandSolder |
| R33 | 1 | DNP | R_0805_2012Metric_HandSolder |
| R38, R39, R40 | 3 | TBD | R_0603_1608Metric_HandSolder |
| R42, R43 | 2 | 0 | R_0603_1608Metric_HandSolder |
| SMA1 | 1 | ANT-SMA | SMA_Samtec_SMA-J-P-H-ST-EM1_EdgeMount |
| U3 | 1 | Wio-E5, STM32WLE5 Module | buck-forest:WIO-E5 |
| U4 | 1 | (blank) | CH572D:CH572D-Module |
| H1-H4, TP1-TP4 | 8 | mounting holes / test points | - |

J2 (JST SH 5-pos) and U4 (CH572D module) were added to the schematic after this list was
exported, so neither has a candidate in `Forest-2.xlsx`. U4 also has an empty `Value`.
J9 was removed.

R21, R22, R31, R36, R37, R44 all read `1m` (1 milliohm - they are enable-pin pull-downs
and want `1M`) and R38-R40 read `TBD`; both need settling before they can be sourced.

Digi-Key search parameters for every part in this table are in [SOURCING.md](SOURCING.md).

## List parts with no home in this schematic

Bought or listed, but nothing in `Forest-Sensor-Platform.kicad_sch` matches. Most belong
to the buck/MPPT half of the design (`buck_converter.kicad_sch`).

| MPN | Description | On list | Where it likely belongs |
| --- | --- | ---: | --- |
| 103R006BB100 | Micro BTB receptacle, 0.35 mm, 6 pos | 0 | Board-to-board link for the split - no symbol placed yet |
| 103P006BB100 | Micro BTB plug, 0.35 mm, 6 pos | 0 | Mating half of the above |
| CONMHF1-SMD-T | U.FL/MHF1 jack SMD | 1 | Antenna - SMA1 is currently an SMA edge-mount |
| S4B-XH-A-1 | JST XH 4 pos, right angle, 2.5 mm | 1 | J8/J9/J10 are JST SH 1.00 mm - different family |
| OSTVN04A150 | Terminal block 4 pos 2.54 mm | 1 | No 4-position screw terminal on this sheet |
| SWT0115-020025SSA | Tactile switch 3.5 x 3.1 mm | 0 | Alternate for SW1 (also not a PTS647 fit) |
| MIC4605-2YM-TR | Half-bridge gate driver | 0 | Buck converter |
| LV2862XLVDDCR | Buck regulator, adj, 600 mA | 0 | Buck converter |
| NTTFS5C680NLTAG | N-ch MOSFET 60 V | 0 | Buck converter |
| MCAC054P10Y-TP | P-ch MOSFET DFN5060 | 1 | Buck converter (high side) |
| BSS123NH6433XTMA1 | N-ch MOSFET 100 V SOT23 | 1 | Buck converter level shift |
| MBT3946DW1T2G | Dual NPN/PNP SC70 | 1 | Buck converter |
| HCM1A1305V3-330-R | 33 uH 4.5 A | 0 | Buck converter output |
| SDCHA1V5040-220-R | 22 uH 1.5 A | 0 | Buck converter output |
| SRN6045TA-330M | 33 uH 1.8 A | 1 | Buck converter output |
| INA180A1QDBVRQ1 | Current sense amp | 1 | Charge current sense |
| MCSF2512FR050Q9 | 50 mohm 2 W 2512 | 1 | Charge current shunt |
| SS56F | Schottky 60 V 5 A SMAF | 1 | Buck converter |
| BZT52B12 | Zener 12 V SOD123 | 1 | Gate drive rail |
| P6SMBJ43A | TVS 43 V SMB | 1 | Solar input clamp |
| KLM3S500RY | PTC fuse 1206 6 V | 1 | Input protection |
| XRCGB32M000F1S1DR0 | 32 MHz crystal 2.0x1.6 | 1 | MCU (not on this sheet) |
| 0603N180J500CT | 18 pF C0G 0603 | 1 | Crystal load caps |
