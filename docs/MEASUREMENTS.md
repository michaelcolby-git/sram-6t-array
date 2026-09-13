# What the simulations establish

## Sequence

| Time (ns) | Activity |
|---|---|
| 5-20 | Drive row-0 data; WL0 asserted 10-18; write 10 |
| 25-40 | Drive row-1 data; WL1 asserted 30-38; write 01 |
| 42-48, 50-58 | Precharge then read row 0 |
| 62-68, 70-78 | Precharge then read row 1 |
| 85-100 | Overwrite row 0 with 01, WL0 90-98 |
| 102-108, 110-118 | Precharge then read row 0 |
| 122-128, 130-138 | Precharge then read row 1 |
| 140-150 | Hold with wordlines off |

Controls transition over 0.1 ns. Bitline drivers connect both columns during writes;
this is a word-wide array, not a column-masked half-select implementation. The unselected
row is checked after writes to establish retention for this particular sequence.
Initial conditions deterministically initialize all cells to zero; writes then exercise
both states. This does not model power-up randomness.

Cell Q/QB levels must be below 20% or above 80% VDD at the documented sample times.
Read differential is sampled about 2 ns after wordline assertion, must have the correct
sign, and must exceed 10% VDD. This threshold is an explicit test criterion, not a
measured sense-amplifier sensitivity. Voltage/temperature sweeps are not process corners.

## Original evidence needed for stronger claims

Static noise margin: use a documented hold/read butterfly method, including read
bitline/wordline biases, extract the largest inscribed square with a checked numerical
method, and report both lobes and the smaller margin. Do not call a successful read SNM.

Write margin: define the convention (bitline write-trip, wordline write-trip, or static
write noise margin), sweep the relevant bias, check the stored-state transition, and
report sweep direction and hysteresis. These metrics are not interchangeable.

Leakage: use calibrated process models with the relevant leakage mechanisms, specify
stored value and all terminal biases, and separate cell current from ideal peripheral
current. Generic Level-1 cutoff behavior does not substantiate a realistic leakage claim.

Noise/variability: deterministic voltage perturbation is not stochastic device noise.
Use a justified noise/Monte Carlo model, seed, distribution, sample size, and operating
conditions. No such fabricated results are included here.

Reference: [ngspice documentation](https://ngspice.sourceforge.io/docs.html).
