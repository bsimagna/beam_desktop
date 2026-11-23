# Beam Designer

Tkinter desktop beam-analysis app. Install the dependencies with `python -m pip install -r requirements.txt`, then start it with `python app.py`.

Loads are entered as positive magnitudes; the direction selector applies downward-positive or upward-negative signs consistently. Positions are measured from the left end. The supported cases are simply supported and fixed-free cantilever beams with point loads and partial uniform loads. Section data is kept in `beam_calculations.py` and currently mirrors the starter values in the supplied HTML example; verify properties and allowable stresses against the governing design references before relying on the checks for design.

Deflection is found by numerical integration of Euler-Bernoulli curvature. Values are displayed in inches. The current spec's `L/30` limit is implemented literally with span in feet, producing a limit in inches; change this criterion to `L/360` if that was the intended engineering limit.
