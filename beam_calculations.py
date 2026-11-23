"""Beam statics and elastic deflection calculations (kip, ft, ksi, inches)."""
from __future__ import annotations

from dataclasses import dataclass
import numpy as np


@dataclass(frozen=True)
class Section:
    name: str
    material: str
    E: float       # ksi
    I: float       # in^4
    Sx: float      # in^3
    Fb: float      # ksi (allowable bending stress)


# Starter values are the values used by the supplied HTML example.
SECTIONS = {
    "W12x26": Section("W12x26", "Steel", 29000, 204, 33.4, 24),
    "W10x19": Section("W10x19", "Steel", 29000, 96.3, 21.6, 24),
    "W14x22": Section("W14x22", "Steel", 29000, 199, 29, 24),
    "2x12 #2": Section("2x12 #2", "Lumber", 1400, 177.98, 31.64, 1.45),
}


def analyze(span, support, point_loads, uniform_loads, section_name, direction="Downward", samples=1201):
    """Return equilibrium, sampled diagrams and checks. Loads are entered as positive magnitudes."""
    if span <= 0 or support not in ("Simply supported", "Cantilever"):
        raise ValueError("Invalid span or support type")
    sign = -1.0 if direction == "Upward" else 1.0
    points_in = [(float(p), sign * float(m)) for m, p in point_loads]
    loads_in = [(float(a), float(b), sign * float(w)) for w, a, b in uniform_loads]
    sec = SECTIONS[section_name]
    total = sum(p for _, p in points_in) + sum(w * (b-a) for a, b, w in loads_in)
    first_moment = sum(p*x for x, p in points_in) + sum(w*(b-a)*(a+b)/2 for a, b, w in loads_in)
    if support == "Cantilever":
        ra, rb, fixed_moment = total, 0.0, first_moment
    else:
        rb = first_moment / span
        ra, fixed_moment = total-rb, 0.0

    # Include every discontinuity/boundary and a regular mesh for smooth plots.
    x = np.unique(np.r_[np.linspace(0, span, samples), 0, span,
                        [p for p, _ in points_in], [v for a, b, _ in loads_in for v in (a,b)]])
    shear = np.full_like(x, ra, dtype=float)
    moment = ra*x
    if support == "Cantilever":
        moment = np.full_like(x, -fixed_moment, dtype=float) + ra*x
    for px, load in points_in:
        active = x >= px
        shear[active] -= load
        if support == "Simply supported":
            moment[active] -= load*(x[active]-px)
        else:
            moment[active] -= load*(x[active]-px)
    for a, b, w in loads_in:
        covered = np.clip(x-a, 0, b-a)
        active = x >= a
        shear -= w*covered
        moment[active] -= w*covered[active]*(x[active]-a-covered[active]/2)
    # Cantilever moment expressed from the fixed end; this is equivalent to the left-cut form.
    # With the root at x=0, internal M(0) balances the applied load first moment.
    if support == "Cantilever":
        moment = -fixed_moment + ra*x
        for px, load in points_in:
            moment -= load*np.maximum(x-px, 0)
        for a, b, w in loads_in:
            c = np.clip(x-a, 0, b-a)
            moment -= w*c*(x-a-c/2)

    # Integrate curvature M/EI (M kip-ft -> kip-in) twice by trapezoids.
    xin = x*12
    curvature = moment*12/(sec.E*sec.I)
    slope = np.r_[0.0, np.cumsum((curvature[:-1]+curvature[1:])*np.diff(xin)/2)]
    ybase = np.r_[0.0, np.cumsum((slope[:-1]+slope[1:])*np.diff(xin)/2)]
    if support == "Simply supported":
        slope0 = -ybase[-1]/xin[-1]
        deflection = ybase + slope0*xin
    else:
        deflection = ybase
    imax = int(np.argmax(np.abs(deflection)))
    imom = int(np.argmax(np.abs(moment)))
    ishear = int(np.argmax(np.abs(shear)))
    max_moment = abs(float(moment[imom]))
    stress = max_moment*12/sec.Sx
    limit = span/30 # Per spec: L/30 in inches, L expressed in feet.
    return {
        "x": x, "shear": shear, "moment": moment, "deflection": deflection,
        "RA": ra, "RB": rb, "fixed_moment": fixed_moment, "section": sec,
        "max_shear": float(shear[ishear]), "max_shear_x": float(x[ishear]),
        "max_moment": max_moment, "max_moment_x": float(x[imom]),
        "max_deflection": float(deflection[imax]), "max_deflection_x": float(x[imax]),
        "stress": stress, "deflection_limit": limit,
        "bending_pass": stress <= sec.Fb, "deflection_pass": abs(deflection[imax]) <= limit,
    }
