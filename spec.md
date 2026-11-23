# Beam Designer

## Purpose
Shear, moment, and deflection diagrams for a beam, with a check of
whether the beam is strong and stiff enough.

## Platform
- Python desktop app using Tkinter, started with `python app.py`
- Calculations with numpy, kept in their own module, separate from
  the window code
- Diagrams drawn with matplotlib, embedded in the window

## Inputs
- Support type:
  - Control: radio buttons
  - Allowed values: simply supported or cantilever
  - Default: simply supported
- Span:
  - Unit: ft
  - Control: numeric input
  - Range: 1 to 100 ft
  - Default: 20 ft
- Point loads:
  - Control: repeatable load entries
  - Magnitude unit: kip
  - Magnitude range: 0 to 100 kip
  - Position unit: ft along the beam, measured from the left support
  - Position range: 0 to the span
  - Default: one 2-kip load at mid-span
- Uniform loads:
  - Control: repeatable start/end spans or a full-span option
  - Magnitude unit: kip/ft
  - Magnitude range: 0 to 10 kip/ft
  - Default: 1 kip/ft over the full span
- Cross-section:
  - Control: preset dropdown
  - Allowed values: steel W-shapes and lumber sizes
  - Default: W12x26
- Load direction:
  - Control: direction selector applied consistently to all entered loads
  - Allowed values: downward or upward
  - Default: downward
  - Positive sign convention: downward loads are positive; upward loads are negative

## Calculations
- Units:
  - Load magnitudes, positions, reactions, and shear use kip and ft.
  - Moments use kip-ft.
  - Section properties use inches and in³ or in⁴.
  - Deflections use inches.
- Statics:
  - Calculate reactions from equilibrium for the selected support type.
  - Calculate positive and negative shear values along the beam.
  - Calculate bending moment from shear or equilibrium at each beam position.
  - Use the left end of the beam as the position origin and signed load magnitudes, with downward positive.
  - For cantilevers, report the fixed-end vertical reaction and fixed-end moment; do not report a second support reaction.
- Diagram data:
  - Include all support locations, load boundaries, and load application points.
  - Report maximum and minimum shear and moment and their positions.
- Deflection:
  - Use the Euler-Bernoulli beam equation with E and I for the selected section.
  - Calculate deflection on a refined numerical grid that includes all load boundaries and application points.
  - Find the maximum absolute deflection from the refined curve, rather than only checking load boundaries.
  - Report maximum absolute deflection and its position.
- Bending stress:
  - Use `fb = 12M/S` with M in kip-ft and S in in³.
  - S means strong-axis section modulus, Sx.
  - Compare the maximum absolute bending stress to the allowable bending stress for the selected material.
- Deflection limit:
  - Compare maximum absolute deflection in inches to `L/30` inches, where L is the span in feet. This literal criterion is intentionally retained from the original specification; confirm whether `L/360` was intended before using it for design.
- Required section properties:
  - Every steel W-shape and lumber preset must provide Sx, I, E, and an allowable bending stress.

## Outputs
- The beam with its loads, and the three diagrams
- Pass or fail for bending and deflection

## Look and feel
Clean and professional, with an example beam loaded when it opens.
Inputs in a panel on the left, the beam and diagrams on the right, and a window that can be resized
## Validation
20 ft simply supported W12x26 with 1 kip/ft only: M = 50.0 kip-ft,
deflection approximately 0.609 in using the starter section properties below.
The opening example also includes a 2-kip mid-span point load, so its results differ from this validation case.
Simply supported, 30 ft, W18x35, uniform 2 kips/ft from 0 to 15 ft only: reactions 22.5 k (left) and 7.5 k (right); max moment 126.6 kip-ft at 11.25 ft. Add W18x35 to the preset data before treating this as an in-app preset validation.

Starter preset values (E in ksi, I in in^4, Sx in in^3, Fb in ksi) are copied from the supplied HTML example: W12x26 (29000, 204, 33.4, 24); W10x19 (29000, 96.3, 21.6, 24); W14x22 (29000, 199, 29, 24); 2x12 #2 (1400, 177.98, 31.64, 1.45). These values and allowable stresses require verification against authoritative steel and lumber references before design use.

## Out of scope
Continuous beams and buckling.

## Build stages

### Stage 1: Page mockup and default example
Create a professional desktop layout: input panel, beam/load area, three diagram areas, and pass/fail summary. Populate the opening example with W12x26, a 2-kip mid-span point load, and 1 kip/ft over the full span.

Check:
- The resizable desktop layout is readable at the minimum supported window size.
- The example beam, inputs, shear, moment, deflection, and pass/fail areas are visible.
- No real calculations or controls claim to be functional yet.

### Stage 2: Input controls and validation
Add support radio buttons, span input, repeatable point-load entries, uniform-load controls, and the steel/lumber preset dropdown. Apply the ranges and defaults in the spec.

Check:
- Defaults match the spec.
- Invalid, blank, out-of-range, and impossible load positions show clear errors.
- Adding/removing loads works and changing span does not leave loads outside the beam.

### Stage 3: Beam drawing, reactions, shear, and moment
Draw the beam and loads dynamically. Calculate reactions and piecewise shear and moment for simply supported and cantilever beams.

Check:
- A 20-ft simply supported beam with 1 kip/ft and no point load gives 10-kip reactions and 50 kip-ft maximum moment.
- Central point-load, partial uniform-load, cantilever uniform-load, and combined-load cases match hand calculations.
- Shear and moment retain the stated sign convention.

### Stage 4: Diagrams and deflection
Add the shear, moment, and deflection charts. Calculate deflection with E and I and identify maximum absolute deflection and location.

Check:
- Chart break points include supports and every load boundary/application point.
- Deflection units and sign convention are clear.
- The W12x26 20-ft uniform-only example reaches approximately 0.609 in using the listed properties.
- Cantilever and simply supported examples agree with independent hand calculations.

### Stage 5: Stress and deflection checks
Add complete section properties and allowable stress values. Calculate `fb = 12M/S`, compare deflection to `L/30`, and show numeric pass/fail results.

Check:
- Both checks display their governing values and limits.
- The uniform-only validation example reports 50.0 kip-ft moment and approximately 0.609-in deflection.
- One pass and one fail case are visible for each material type.
- Continuous beams and buckling remain unsupported.
