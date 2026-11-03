# ADR 0003: Benchmarking Architecture

## Status
Accepted

## Context
Sudoku Studio needs to compare four solving algorithms across Python, C++ and Java using consistent performance measurements.

## Decision

1. Benchmark all four algorithms across all three languages.
2. Use the same shared puzzle dataset for every implementation.
3. Execute benchmark combinations independently, not concurrently.
4. Perform five measured runs per puzzle, algorithm and language combination.
5. Perform a Java warm-up run before measured runs, excluding it from results.
6. Use median execution time as the primary performance metric.
7. Measure solver execution time separately from process startup, parsing and serialization.
8. Build C++ and Java implementations in Release mode.
9. Store raw benchmark results as JSON in `benchmarks/results/`.

## Consequences

- Performance comparisons use consistent conditions.
- Median measurements reduce the impact of outliers.
- Java warm-up reduces JVM startup and JIT compilation effects.
- Benchmarking takes longer but produces more reliable comparisons.