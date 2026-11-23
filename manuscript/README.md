# Bala's inverse-function period conjectures

An elementary proof of Su's theorem on Bala's inverse-function period conjectures, with odd-exponent extensions.

Haobo Ma (ChronoAI Pte Ltd, Singapore), then Wenlin Zhang (National University of Singapore; ChronoAI Pte Ltd, Singapore). Revision 2, 14 November 2026. Note and verification code: CC BY 4.0.

## Mathematical content

For the integer sequence `A281440(n) = (2n)! [x^(2n)] C(x)` with `C(x) = cosh(integral_0^x C(t)^7 dt)`, every modulus `m >= 3` has the eventual period `phi(m)^2/2`. Moduli 1 and 2 have eventual period one. The prime-five branch is eventually zero. The proof covers every integer exponent `a >= 2` in the integral quadratic derivation `D(s)=c^a, D(c)=s*c^(a-1), c^2-s^2=1`, including the four companion conjectures A281180, A281181, A281183 and A281184.

The twelve sequence identifications include the odd-exponent flows A281427, A281428, A281436, A281443 and A281444. The columns with exponents 5, 7 and 9 eventually vanish modulo any integer coprime to 6, 30 and 70, respectively. These are consequences of the general theorem, not additional conjectures posed in those entries. The source derivative question in A281436 is answered yes; its algebraic formula and the A281427 algebraic equations follow from an explicit polynomial for `T=S/C`. A displayed A281181 factorial is corrected from `13*x^5/6!` to `13*x^5/5!`. Composite row relations and the two A281428 examples are also proved.

These period theorems were proved by Lien-Hung Su, *Quadratic Derivations and Uniform Modular Periods for Six Inverse-Function Sequences*, version 1, 31 October 2026, Theorem 3.2 and Corollary 3.3: https://doi.org/10.5281/zenodo.23835577. This note gives an alternative proof with an elementary endomorphism lifting lemma and explicit source coverage. The source conjecture is Peter Bala's COMMENT of 19 February 2026 in https://oeis.org/A281440, revision 17 of 6 November 2026.

## Contents

- `note.tex`: complete mathematical argument, bibliography, source coverage and verification scope.
- `note.pdf`: typeset note, distributed alongside the source archive.
- `verify.py`: Python 3 exact-arithmetic coefficient comparisons and finite-dimensional congruence certificates; standard library only.
- `checks.json`: deterministic output of `verify.py`.
- `metadata.json`: title, creators, license, covered problem identifiers and scientific evidence link.
- `SHA256SUMS.txt`: member hashes for the source package.

## Build

Use Tectonic 0.17.0:

```sh
tectonic --untrusted note.tex
```

Alternatively, use a standard LaTeX installation with `amsmath`, `amssymb`, `amsthm`, `geometry`, `booktabs`, `array`, `longtable`, `fontenc`, `lmodern`, `xurl` and `hyperref`:

```sh
pdflatex -interaction=nonstopmode -halt-on-error note.tex
pdflatex -interaction=nonstopmode -halt-on-error note.tex
```

The bibliography is embedded in `note.tex`, so BibTeX is unnecessary. There are no external figures, bibliography databases or mathematical input files.

## Reproduce the exact arithmetic

```sh
python3 verify.py --output checks-rebuilt.json
cmp checks.json checks-rebuilt.json
```

The program returns `PASS`, with 396 coefficient comparisons, 192 uniform-period certificates, 420 additional odd-exponent certificates, 60 composite row certificates and eight least-period certificates. It also verifies five scalar-layout certificates, the displayed prefixes of all twelve families, the two algebraic polynomial identities, the A281181 factorial correction and constant-one identity modulo 12, and the zero tail modulo 385 of A281428. The coefficient comparisons cover column indices 0 through 32 for twelve families; the A281180, A281427, A281439 and A281443 OEIS indices are one greater than their column indices.

The congruence certificates use the quotient of dimension `ceil(m/2)` specified in the note. Cayley-Hamilton turns that many consecutive zero differences into an all-subsequent-index conclusion for each listed modulus, shift and initial column. The universal theorem for all positive moduli has the written proof in the note; it is not inferred from the finite list of examples.

## Lean statements

At revision `92de86888730265f84e24d28bdb67546c543a966`,

https://github.com/the-omega-institute/trureturing/blob/92de86888730265f84e24d28bdb67546c543a966/D5/S1/Recurrence/Periodic/BalaA281440TotientSquarePeriod.lean

contains `BalaA281440TotientSquarePeriod.result`, which proves the rational series and integer coefficient witnesses and the eventual `phi(m)^2` shift for A281440. The general `phi(m)^2` column statement for exponents 4 and 8 is `BalaPolynomialSystem.even_sequence_period` in

https://github.com/the-omega-institute/trureturing/blob/92de86888730265f84e24d28bdb67546c543a966/D5/S1/Recurrence/Periodic/BalaA281181TotientSquarePeriod.lean.

Three further pinned files at that revision contain `result` for A281180 (odd coefficients of the exponent-four flow), A281183 (`C^2`) and A281184 (`C^3` and the logarithmic derivative identity). Each proves the full-square shift with its rational-series and integer-coefficient witnesses; all five file links and their mathematical scope are given in the PDF.

The half-square period, explicit onsets, all-integer-exponent result, composite rows and derivative/algebraic identities have written proofs; the listed residue identities have finite-dimensional certificates. The odd-exponent extension and half-square bound are distinct from the full-square statements of the pinned Lean declarations. Su's stronger totient bound for A281428 is cited as Theorem 4.1, not inferred from the half-square bound.
