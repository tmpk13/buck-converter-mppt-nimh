# MPPT Buck Converter — NiMH D-Cell Charger

![](PCB.png)

## Project Goal
Solar MPPT buck converter charging 3× NiMH D cells in series. SMD build. High-side driver topology with synchronous rectification.

## System Specs

| Parameter | Value |
|---|---|
| Source | 24V 50W solar panel (Voc ~30-32V, Isc ~2.1A) |
| Output | 3× NiMH D cells in series (~3.6-4.35V) |
| Charge current target | 1-2A (C/5 to C/3 for typical 5-10Ah D cells) |
| Output power | ~7.2W at 2A |
| Duty cycle | ~15-18% |
| PWM frequency | 100kHz |
| MCU | STM32WLE5JC (Wio-E5 module) |

## Selected Components

### Power Stage

| Function | Part | Package | Key Specs |
|---|---|---|---|
| High-side FET | **BSC093N04LS** (Infineon) | TDSON-8 (SuperSO8) | 40V, 49A, Rdson 9.3mΩ, Qg ~18nC |
| Low-side sync FET | **BSC093N04LS** (same) | TDSON-8 | Used instead of freewheeling Schottky — better efficiency |
| Gate driver | **ADP3414** (Analog Devices) | SOIC-8 | Dual high/low driver, 4.5-13.2V VCC, 2A peak drive, internal bootstrap diode |
| Inductor | **Coilcraft MSS1583-473MEB** | 15.8×15.3×8.3mm SMD | 47µH, Isat 5.4A, Irms 4.8A, DCR ~38mΩ |

### Current Sensing

| Function | Part | Notes |
|---|---|---|
| Shunt resistor | **2.25mΩ** | Low-side, between battery return and GND |
| Sense amplifier | **OPA2835** (TI) | 8-VSSOP, dual 95MHz RRO op-amp, Vos ~0.15mV |
| Config | Differential amp, gain ×100 | 4 matched resistors (1kΩ input, 100kΩ feedback) |
| At 3A | 6.75mV × 100 = 675mV → ~837 ADC counts (12-bit, 3.3V ref) |
| At 1A | 2.25mV × 100 = 225mV → ~279 ADC counts |

Second half of OPA2835 is spare — can buffer Vpanel or Vbat ADC input.

### Voltage Sensing (resistor dividers to ADC)

| Signal | Divider | Output at max | Filter cap |
|---|---|---|---|
| Vpanel (0-32V) | 100kΩ / 10kΩ | ~2.9V | 100nF |
| Vbat (0-4.5V) | 10kΩ / 10kΩ | ~2.25V | 100nF |

### NiMH Charge Termination

- **-ΔV detection**: voltage dip ~5-10mV/cell at full charge
- **dT/dt**: temperature rise rate monitoring
- **NTC thermistor**: 10kΩ, 0402/0603, thermally coupled to cells
- NiMH does NOT use voltage cutoff like Li-ion — these methods are essential, not optional

### Protection

| Function | Part | Notes |
|---|---|---|
| Input TVS | SMBJ33A | Panel transient protection |
| Input fuse | PTC 5A resettable | Overcurrent |
| Reverse polarity | P-FET or Schottky on input | Recommended |

### Capacitors

| Ref | Value | Voltage | Package | Purpose |
|---|---|---|---|---|
| C1 | 22µF | ≥50V | 1206/1210 ceramic | Input filter |
| C2 | 100µF | ≥50V | electrolytic | Input bulk |
| C3 | 470µF | ≥10V | electrolytic | Output bulk (battery side) |
| C4 | 100nF | ≥50V | 0603 | Bootstrap (ADP3414 BOOT-SW) |
| C5 | 100nF | ≥16V | 0603 | ADP3414 VCC decoupling |
| C6 | 100nF | ≥10V | 0402/0603 | STM32 decoupling |
| C7 | 10µF | ≥10V | 0603/0805 | STM32 decoupling |
| C8 | 100nF | ≥10V | 0402/0603 | OPA2835 decoupling |
| C9 | 100nF | ≥10V | 0603 | ADC Vpanel filter |
| C10 | 100nF | ≥10V | 0603 | ADC Vbat filter |

## STM32WLE5JC Pin Assignments

| Peripheral | Function | Target |
|---|---|---|
| TIM1_CH1 | PWM output | ADP3414 IN (PWM input) |
| ADC_CH1 | Analog input | Vpanel divider |
| ADC_CH2 | Analog input | Vbat divider |
| ADC_CH3 | Analog input | OPA2835 current sense output |
| ADC_CH4 | Analog input | NTC thermistor |
| GPIO | Digital output | ADP3414 enable/shutdown (if needed) |

## Design Decisions & Rationale

1. **Synchronous rectification** (2× BSC093N04LS) chosen over Schottky diode — user only had 30V Schottkys (too close to Voc), plus 54× BSC093N04LS available. Better efficiency.
2. **ADP3414 over IR2104** — stronger 2A drive (vs 200mA), internal bootstrap diode (saves BAT54), adaptive dead time. VCC max 13.2V requires regulated supply rail.
3. **OPA2835 over INA181** — user had it on hand. Configured as diff amp with gain ×100 to work with 2.25mΩ shunt. Vos 0.15mV is adequate.
4. **2.25mΩ shunt** — requires amplification (unusable raw on ADC). Paired with OPA2835 ×100 gain gives workable resolution down to ~0.5A.
6. **50W panel is oversized** for 3 cells (~7W max charge power). MPPT will sit at low duty cycle. User may want to consider larger pack later.

## Not Yet Addressed
- PCB layout
- VCC supply for ADP3414 (needs 5-12V regulated rail from panel or separate)
- MPPT algorithm implementation (perturb & observe vs incremental conductance)
- STM32 firmware (TIM1 PWM config, ADC DMA setup, control loop)
- Detailed ADP3414 pinout wiring
- Sync FET timing / dead time considerations