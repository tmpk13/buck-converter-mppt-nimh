# CH572D bring-up diagnosis - FSP V1, board 1

2026-11-03 to 2026-11-04. The first hand-built board's CH572D (U9) did not show up
on USB. It now enumerates as the WCH ROM bootloader (1a86:55e0).

## Symptom

- Nothing in `lsusb`. dmesg showed `new low-speed USB device ... error -71` with
  the first chip, and `new full-speed USB device ... device not accepting address,
  error -71 ... unable to enumerate` once a pull-up on D+ was fitted.
- Both mean the same thing: something holds a data line high, but nothing on the
  board answers.

## Causes

Two faults, each enough on its own to keep the chip silent.

1. **Y2's footprint is mirrored (design).** The buck-forest XRCGB32M000F1S1DR0
   footprint follows Murata's bottom view as if it were the top view. The part's
   two no-connect pads are joined by a strip on the package, and the footprint
   puts XI and XO on them: XI to XO measured 0.6 ohm, and the crystal sat across
   GND. The CH572 has no fast internal oscillator and runs from the crystal from
   power-on, so with no clock nothing runs, ROM bootloader included.
   - Library fixed in b402d0c. The layouts (this board and CH572D-Module) still
     need Y2 updated from the library and XI/XO rerouted.
   - Rework on a built board: turn Y2 90 degrees. The pads still overlap each
     terminal by about 70%. The crystal has no polarity, so 90 or 270 both work.
2. **U9 tilted on too much exposed-pad solder (assembly).** Some pins did not
   reach their pads, and the excess solder left a 1.5 kohm leak from XI (pin 3) to
   GND that held XI at 0 V. Reflowing U9 with a thin exposed-pad layer fixed both.

Found along the way, not the fix:

- The first U9 was replaced after VDD33 read 4.5 V, over its 4.0 V absolute
  maximum. A chip that is not running draws less than the ~1.13 mA that R41 (1.5k
  from +5V) feeds VDD33, and its internal LDO cannot sink the rest, so VDD33
  rises. That chip had no clock either and may have been fine.
- C26/C27 removed (review H2); 2.2 uF + 100 nF added on VDD33 (review H1).

## Bootloader entry

A blank chip starts in the bootloader on its own; no pull-up is needed. It
enumerates as 1a86:55e0 (bcdDevice 23.00) and leaves USB 9.9 s later if no tool
talks to it, so start the flash first (`mise run ch572-flash` in
long-range-radio-rs waits 30 s), then plug in.

Once firmware is flashed, re-entering needs a 5.1k from VDD33 (R41's U9 end) to D+,
fitted before plug-in: the same circuit as the Download button on WCH's CH572
evaluation board. Do not use +5V; PA1 is not 5 V tolerant.

## Checks

In the order that finds these faults fastest. Unpowered unless marked. Diode
mode: red probe on GND (J4 pin 2), black on the point. XI and XO are the empty
C26 and C27 pads (the pad that does not beep to GND).

| Check | Good | Bad means |
|---|---|---|
| XI to XO, ohms | open | near 0: footprint short (cause 1) or a bridge |
| Diode: D+ (J1 B6), D- (J1 A7), VDD33 | 0.35-0.6 V | OL on all: exposed pad not soldered |
| Diode: XI, XO | ~0.35 V, matching | OL: pin 2 or 3 open (tilted U9) |
| XI and XO to GND, ohms | about equal (100-300k) | one much lower: leak on that pin |
| Powered: VDD33 at R41's U9 end | 3.2-3.4 V | higher: chip not running or not grounded; unplug |
| Powered: XI and XO, DC | about equal | XI 0 V, XO 1.2 V: XI held low, no oscillation |
| Powered: 32 MHz near Y2 | line at 32.000 MHz | none: oscillator not running |

For 32 MHz: a spectrum analyzer with a near-field loop over Y2 (center 32 MHz,
span 200 kHz, RBW 1 kHz), or a 10x scope probe on the XO pad (bandwidth limit
off, 20 ns/div). A 1x probe can stop the oscillator.

## Readings that misled

- D+ at 2.5 V with the pull-up is just the 5.1k against the host's 15k pull-down.
  It says nothing about whether the bootloader runs.
- The diode check read a normal 0.35 V on XI with the 1.5 kohm leak present: a
  diode reading hides a parallel leak, so compare resistances too.

## For the next board

- Update Y2 from the library and reroute XI/XO before ordering.
- U9: a thin, even layer on the exposed pad; check that the chip sits flat. Use
  the preheater.
- Run the unpowered checks above before the first USB plug-in.
- Leave C26/C27 off and add the VDD33 caps until the layout has them (H1, H2).
