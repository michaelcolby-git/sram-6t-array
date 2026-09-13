# SRAM design decisions

## Six-transistor storage

Two cross-coupled CMOS inverters form a bistable element. Two access NMOS devices
connect Q and QB to BL and BLB when WL is high. The nominal pull-down/access width
ratio is 2; the access/pull-up ratio is approximately 1.67. These are geometry ratios,
not complete strength ratios because carrier mobility and bias also matter.

## Competing read and write requirements

A read begins with high bitlines. The stored-low node must resist the access-device
pull-up while developing a bitline differential. A stronger pull-down helps this
case. A write instead requires the access path to overcome the cell's existing
state; an excessively strong cell can hinder writing. The fourth configuration
increases pull-down width from 2.0 to 2.4 µm and reruns the same functional sequence.

## Array organization

Both columns share a selected wordline and are written as a word. The other row
keeps its wordline low and is checked after neighboring activity. This tests
unselected-row retention, not column-masked half-selection. Precharge ends before
wordline assertion; ideal switches isolate the write drivers during reads.

## Measured boundary

The regression checks both Q and QB at eight times per configuration and the sign
and magnitude of each read differential. It models finite bitline/storage loads
but ideal peripherals. SNM, leakage, stochastic noise, and process Monte Carlo are
outside the measured scope of this implementation.
