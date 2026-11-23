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
- Deflection limit:
  - Control: positive numeric input in inches
  - Default: span / 30 inches, following the current deflection criterion

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
- File menu with Save and Open commands for beam design files
- Export results button that writes a CSV table with x-position, shear, moment, and deflection along the beam
- Calculation sheet button that saves a printable PDF with inputs, governing checks, and beam diagrams

## Save and Open
- Save the support type, span, section, deflection limit, load direction, point loads, and uniform loads to a human-readable JSON file.
- Open a saved JSON file and restore all saved inputs.
- Include a format version and reject unsupported versions or invalid fields with a clear error.
- Validate a complete file before applying any values; an invalid file must leave the current design unchanged.
- Save validates the current design before writing. Canceling either file dialog leaves the current design unchanged.

## Export results
- Export a comma-separated CSV file suitable for opening in Excel.
- Include columns for x-position in ft, shear V in kip, moment M in kip-ft, and deflection in inches.
- Export the same calculated beam positions used for the result diagrams, including load positions and boundaries.
- If inputs are invalid or the export is canceled, do not write a results file.

## Calculation sheet
- Export a landscape, printable PDF containing the current beam inputs at the top, including support, span, section, load direction, deflection limit, and all point and uniform loads.
- Include the governing reactions, bending stress and allowable, maximum deflection and limit, pass/fail outcomes, and beam/load, shear, moment, and deflection diagrams.
- Use the current valid analysis. If inputs are invalid or the export is canceled, do not create a calculation sheet.

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
Add support radio buttons, span input, repeatable point-load entries, uniform-load controls, the steel/lumber preset dropdown, and deflection limit input. Apply the ranges and defaults in the spec.

Check:
- Defaults match the spec.
- Invalid, blank, out-of-range, and impossible load positions show clear errors.
- Adding/removing loads works and changing span does not leave loads outside the beam.
- The deflection limit must be positive and is expressed in inches.

### Stage 2a: Save and Open
Add File menu commands to save a versioned JSON design and restore it from a validated file.

Check:
- Saving and reopening preserves both support types, span, section, deflection limit, direction, and multiple point and uniform loads.
- Malformed JSON, unsupported versions, invalid sections, and out-of-range values show an error without changing the current design.
- Canceling Save or Open leaves the current design unchanged.

### Stage 2b: Export results
Add a button that exports the calculated x, V, M, and deflection arrays to CSV.

Check:
- The CSV opens in Excel and includes unit-bearing column headings.
- Every exported row has aligned position, shear, moment, and deflection values from the current analysis.
- Invalid inputs prevent export and display a clear message.

### Stage 2c: Calculation sheet PDF
Add a button that creates a printable PDF of the current inputs, governing checks, and diagrams.

Check:
- The PDF shows all inputs and numeric pass/fail checks above the four diagrams.
- The PDF is landscape and prints on a standard page without clipping its labels.
- Invalid inputs prevent export and display a clear message.

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
