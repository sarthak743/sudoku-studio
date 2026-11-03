# ADR 0001: Solver Architecture

## Status
Accepted

## Context
Sudoku Studio requires four Sudoku-solving algorithms implemented in Python, C++ and Java.

The system must support independent testing, benchmarking and consistent results across all implementations.

## Decision

1. Implement four algorithms: A1, A2, A3 and A4.
2. Python, C++ and Java implementations will follow the shared `SOLVER_SPEC.md`.
3. Each language will have an independent solver library and CLI.
4. The FastAPI backend will use the Python solver package.
5. C++ and Java solvers will be used for benchmarking and comparison.
6. Java will use a CLI. JNI integration will not be implemented.
7. All implementations will share common test fixtures and conformance tests.

## Consequences

- Solver implementations can be developed independently.
- All three languages can be benchmarked fairly.
- Shared specifications and fixtures help maintain consistent behaviour.
- Additional integration work is required to maintain three implementations.