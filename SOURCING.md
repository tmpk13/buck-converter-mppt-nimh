# Digi-Key search parameters - parts not in Forest-2.xlsx

57 of the 70 components on `Forest-Sensor-Platform.kicad_sch` have no manufacturer part
number. Grouped below into the 19 line items you would actually search for, with the
Digi-Key category, the parametric filters to set, and a keyword string to paste into the
search box.

Ratings were chosen against the rail each part sits on, taken from the netlist rather
than from the schematic value alone. Read the "Fix before ordering" section first - four
of these line items cannot be bought as drawn.

## Capacitors

### 100nF 0603 - qty 7

C10, C15, C44 (drawn 100nF 50V), C16, C19, C21, C32 (drawn 100n). All decoupling or RC
filtering; one part covers all seven.

- **Category:** Capacitors > Ceramic Capacitors
- **Capacitance:** 0.1 uF
- **Voltage - Rated:** 50V
- **Temperature Coefficient:** X7R
- **Tolerance:** +/-10%
- **Package / Case:** 0603 (1608 Metric)
- **Mounting Type:** Surface Mount MLCC
- **Keyword:** `0.1uF 50V X7R 0603`

### 1uF 0603 - qty 2

C30 (5V boost rail), C34 (battery rail).

- **Category:** Capacitors > Ceramic Capacitors
- **Capacitance:** 1 uF | **Voltage - Rated:** 25V | **Temperature Coefficient:** X7R
- **Tolerance:** +/-10% | **Package / Case:** 0603 (1608 Metric)
- **Keyword:** `1uF 25V X7R 0603`

### 1uF 0805 - qty 2

C12 (+3.3V), C14 (PWR-IN, ~5V). Drawn as 1uF 25V.

- **Category:** Capacitors > Ceramic Capacitors
- **Capacitance:** 1 uF | **Voltage - Rated:** 25V | **Temperature Coefficient:** X7R
- **Tolerance:** +/-10% | **Package / Case:** 0805 (2012 Metric)
- **Keyword:** `1uF 25V X7R 0805`

### 10uF 0603 - qty 4

C31 (VUSB), C35 (boost input), plus C9 and C13 once their 50V rating is corrected - see
"Fix before ordering". All sit on 3.3V or 5V rails, so 25V is generous.

- **Category:** Capacitors > Ceramic Capacitors
- **Capacitance:** 10 uF | **Voltage - Rated:** 25V | **Temperature Coefficient:** X5R
- **Tolerance:** +/-20% | **Package / Case:** 0603 (1608 Metric)
- **Keyword:** `10uF 25V X5R 0603`

### 22uF 0805 - qty 1

C46, the TPS613222A boost output bulk cap on the 5V rail. Buy 0805/16V rather than the
drawn 0603/10V - see "Fix before ordering".

- **Category:** Capacitors > Ceramic Capacitors
- **Capacitance:** 22 uF | **Voltage - Rated:** 16V | **Temperature Coefficient:** X5R
- **Tolerance:** +/-20% | **Package / Case:** 0805 (2012 Metric)
- **Keyword:** `22uF 16V X5R 0805`

## Resistors

Every resistor below is 0603 thick film unless noted. Common filters:

- **Category:** Resistors > Chip Resistor - Surface Mount
- **Package / Case:** 0603 (1608 Metric) | **Power (Watts):** 0.1W, 1/10W
- **Composition:** Thick Film | **Mounting Type:** Surface Mount

| Refs | Qty | Resistance | Tolerance | Role | Keyword |
| --- | ---: | --- | --- | --- | --- |
| R13, R16, R17, R18, R29, R30 | 6 | 10 kOhms | +/-1% | LED current set, SPI pull-ups, reset pull-up | `10k 1% 0603` |
| R21, R22, R31, R36, R37, R44 | 6 | 1 MOhms | +/-1% | Enable-pin pull-downs (see fix list - drawn as `1m`) | `1M 1% 0603` |
| R27, R28 | 2 | 4.7 kOhms | +/-1% | I2C bus pull-ups | `4.7k 1% 0603` |
| R25, R26 | 2 | 5.1 kOhms | +/-1% | USB-C CC1/CC2 Rd pull-downs | `5.1k 1% 0603` |
| R42, R43 | 2 | 0 Ohms | Jumper | RS-422 Y-to-B and Z-to-A straps | `0 ohm jumper 0603` |
| R38, R39, R40 | 3 | undecided | +/-1% | Series into MCU ADC, 100nF to GND | see fix list |

R33 is marked DNP (0805, +3.3V to the J7 5V pin) - nothing to buy unless you intend to
stuff that option.

## Diodes

### Indicator LEDs - qty 3

D2 (USB source active, off U2 status pin), D6 (off U8 status pin), D12 (user LED off the
Wio-E5). Each is in series with a 10k, so the drive current is a fraction of a
milliamp - D12 works out to about 0.13 mA off the 3.3V rail. Pick a high-efficiency
part, not a bulk indicator, or they will be invisible.

- **Category:** Optoelectronics > LED Indication - Discrete
- **Package / Case:** 0603 (1608 Metric) | **Mounting Type:** Surface Mount
- **Configuration:** Standard | **Color:** Green / Red as you prefer
- **Voltage - Forward (Vf) (Typ):** <= 2.2V | **Current - Test:** 2 mA
- **Millicandela Rating:** filter high, 50 mcd and up at 2 mA
- **Keyword:** `LED 0603 green high efficiency 2mA`

### D7 - TVS on the 5V output to J7 - qty 1

Drawn as SMAJ5.0CA, annotated "clamp@9.2V", protecting the +5V pin that leaves the board
on the screw terminal.

- **Category:** Circuit Protection > TVS - Diodes
- **Unidirectional / Bidirectional:** Bidirectional
- **Voltage - Reverse Standoff (Typ):** 5V
- **Voltage - Breakdown (Min):** 6.4V | **Voltage - Clamping (Max) @ Ipp:** 9.2V
- **Power - Peak Pulse:** 400W | **Package / Case:** DO-214AC (SMA)
- **Keyword:** `SMAJ5.0CA` or `TVS bidirectional 5V 400W SMA`

## Connectors

### J8, J10 - JST SH 4-pos - qty 2

I2C1 and I2C2 breakouts, footprint `JST_SH_BM04B-SRSS-TB`. This is the Qwiic / STEMMA QT
pinout, so a Qwiic-compatible cable fits.

- **Category:** Connectors > Rectangular Connectors - Headers, Receptacles, Female Sockets
- **Manufacturer Part Number:** BM04B-SRSS-TB
- **Number of Positions:** 4 | **Pitch:** 0.039" (1.00mm)
- **Connector Type:** Header, Shrouded | **Orientation:** Vertical | **Mounting:** Surface Mount
- **Keyword:** `BM04B-SRSS-TB` or `JST SH 4 position vertical SMD 1mm`

### J2 - JST SH 5-pos - qty 1

SWD/debug header (SWCLK, SWDIO, 3V3, GND, RST), footprint `JST_SH_BM05B-SRSS-TB`.

- Same category and filters as above, **Number of Positions:** 5
- **Keyword:** `BM05B-SRSS-TB` or `JST SH 5 position vertical SMD 1mm`

### J4 - 2-pin power header - qty 1

Footprint `PinHeader_1x02_P2.54mm_Vertical`, +3.3V and GND.

- **Category:** Connectors > Rectangular Connectors - Headers, Male Pins
- **Number of Positions:** 2 | **Number of Rows:** 1 | **Pitch:** 0.100" (2.54mm)
- **Orientation:** Vertical | **Mounting Type:** Through Hole
- **Keyword:** `2 position header 2.54mm vertical through hole`

### SMA1 - antenna jack - qty 1

Footprint is `SMA_Samtec_SMA-J-P-H-ST-EM1_EdgeMount`, an edge-launch SMA. Note that
`Forest-2.xlsx` already carries CONMHF1-SMD-T, a U.FL/MHF1 jack - pick one before buying.

- **Category:** Connectors > Coaxial Connectors (RF)
- **Connector Type:** SMA | **Gender:** Jack, Female Socket
- **Mounting Type:** Surface Mount, Edge Launch (End Launch)
- **Impedance:** 50 Ohm | **Frequency - Max:** 6 GHz or better
- **Keyword:** `SMA-J-P-H-ST-EM1` or `SMA jack edge launch 50 ohm end launch`

## Modules

### U3 - Wio-E5 LoRa module - qty 1

Seeed Studio LoRa-E5 (STM32WLE5JC inside), footprint `buck-forest:WIO-E5`.

- **Category:** RF/IF and RFID > RF Transceiver Modules and Modems
- **Manufacturer:** Seeed Technology Co., Ltd
- **Frequency:** 868MHz / 915MHz (HF variant) | **Protocol:** LoRaWAN
- **Keyword:** `LoRa-E5-HF` or `Seeed LoRa-E5 module`
- Confirm you get the HF (863-928 MHz) variant, not LF.

### U4 - CH572D BLE module - qty 1

WCH part, footprint `CH572D:CH572D-Module`. **Digi-Key does not stock WCH silicon.**
Order from LCSC alongside the CH32V203 that is already sourced there, or from WCH direct.

- **Keyword (LCSC):** `CH572D module`

## Mechanical

H1-H4 are M3 mounting-hole pads and TP1-TP4 are bare copper test points - neither is a
purchased line item. You will want four M3 screws and standoffs to match the
`MountingHole_3.2mm_M3_DIN965_Pad` footprint.

## Fix before ordering

**The six `1m` resistors are wrong by a factor of a billion.** R21, R22, R31, R36, R37
and R44 all read `1m`, which KiCad reads as 1 milliohm. Every one of them is a pull-down
to GND on an enable pin - U2 ON, U8 ON, U4/U7 GPIO_EN, the TPT482's receiver enable and
input enable, and 5V_EN. At 1 milliohm they are dead shorts that would hold all six
functions permanently off. These are meant to be `1M`. Fix the values, then buy 1M.

**C9 and C13 cannot be built as drawn.** Both read 10uF 50V in an 0603 package; 0603
tops out at 25V for 10uF and no manufacturer makes a 50V part in that size. Both sit on
the +3.3V rail, so drop the rating - 25V is still 7x margin. ([Yageo 0603 10uF
range](https://www.digikey.com/en/products/detail/yageo/CC0603MRX5R8BB106/7164378))

**C46 loses most of its capacitance where it sits.** 22uF 10V X5R in 0603, biased at 5V
on the boost output, keeps roughly a third of its rated value under DC bias. The
TPS613222A wants real bulk capacitance there. Move it to 0805/16V, or budget for the
derating and check the ripple.

**R38, R39, R40 have no value.** Each is a series element from an MCU pin into a sense
net - BAT_ISENSE, VSENSE_OUT, VSENSE_VIN - with 100nF (C16, C19, C21) to ground, so they
set an RC anti-alias filter for the ADC. Nothing can be ordered until you pick the corner
frequency. With 100nF, 1k gives 1.6 kHz and 10k gives 160 Hz.

## Missing from the schematic entirely

This is what the shunt observation points at. Five nets dangle with exactly one node
each, and they are all buck-board signals:

| Net | Only node | What it wants |
| --- | --- | --- |
| `BAT_ISENSE` | R38.2 | Battery current, from the shunt + INA180 |
| `VSENSE_OUT` | R39.2 | Buck output voltage divider |
| `VSENSE_VIN` | R40.2 | Solar input voltage divider |
| `PWM_Buck` | U3.20 | Gate drive PWM out to the buck |
| `/Batt_Out` | U8.6 | Battery feed into the ORing switch |

The sense chain itself - MCSF2512FR050Q9 (0.05 Ohm, 2W, 2512) and INA180A1QDBVRQ1 - is
already on `Forest-2.xlsx` and lives on the buck board, so nothing new needs sourcing
there. What is missing here is the interconnect: `103R006BB100` / `103P006BB100`, the
6-position 0.35mm micro board-to-board pair, is on the list with nothing requested and
has no symbol on this sheet. Five dangling signals plus a ground return is exactly six
positions.

**`Battery_Out` has no source.** It connects only C34 and U13's VIN, so the load switch
feeding the boost converter is unpowered. `/Batt_Out` (U8 pin 6) is a separate net that
looks like it should be the same node. Reconcile the two names when you place the
board-to-board connector.
