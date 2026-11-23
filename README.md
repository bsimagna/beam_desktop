# Beam Designer

*A compact reference for beam response and preliminary strength checks*

Beam Designer is a Tkinter application for simply supported and cantilever beams under point loads and partial uniform loads. It reports reactions, shear, bending moment, elastic deflection, and bending/deflection checks.

## Conventions and units

Positions are measured from the left end. Loads are entered as positive magnitudes; downward loading is positive and upward loading is negative. The application uses kip and ft for loads and positions, kip-ft for moment, ksi for stress and modulus, in⁴ for the second moment of area, and inches for deflection.

## Equilibrium

For a simply supported beam of span \(L\), vertical force and moment equilibrium determine the reactions:

$$
R_A + R_B = \sum_i P_i + \sum_j w_j(b_j-a_j), \qquad
R_B L = \sum_i P_i x_i + \sum_j w_j(b_j-a_j)\frac{a_j+b_j}{2}.
$$

For a cantilever, the fixed-end reactions balance the total applied force and moment:

$$
R_A = \sum_i P_i + \sum_j w_j(b_j-a_j), \qquad
M_A = \sum_i P_i x_i + \sum_j w_j(b_j-a_j)\frac{a_j+b_j}{2}.
$$

Here \(P_i\) is a signed point load at \(x_i\), and \(w_j\) is a signed uniform load over \([a_j,b_j]\).

## Shear and bending moment

At a section \(x\), the internal shear and moment follow from equilibrium of the portion of the beam to the left of the section. For a simply supported beam:

$$
V(x)=R_A-\sum_{x_i\le x}P_i-\sum_j w_j\,\ell_j(x),
$$

$$
M(x)=R_Ax-\sum_{x_i\le x}P_i(x-x_i)
-\sum_j w_j\,\ell_j(x)\left(x-a_j-\frac{\ell_j(x)}{2}\right),
$$

where \(\ell_j(x)=\max\{0,\min(x,b_j)-a_j\}\) is the loaded length to the left of the section. The cantilever diagram is obtained from the same section equilibrium, using the fixed-end reactions.

## Elastic deflection and checks

Euler–Bernoulli beam theory relates curvature to bending moment:

$$
EI\frac{d^2v}{dx^2}=M(x),
$$

with consistent units and boundary conditions for the selected supports. The app numerically integrates curvature to obtain the deflection curve.

The maximum bending stress estimate is

$$
f_b=\frac{12M_{\max}}{S_x},
$$

where \(M_{\max}\) is in kip-ft and \(S_x\) is in in³, giving \(f_b\) in ksi. The app compares \(f_b\) with the selected section's allowable bending stress. The deflection check compares maximum absolute deflection with the configured limit; its initial value follows the project specification, \(L/30\) inches for \(L\) in feet.

## Install and run

Install Python and the required packages:

```bash
python -m pip install numpy matplotlib
```

Start the application from the project directory:

```bash
python app.py
```
