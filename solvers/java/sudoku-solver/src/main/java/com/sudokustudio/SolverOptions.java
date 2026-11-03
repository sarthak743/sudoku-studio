package com.sudokustudio;

public record SolverOptions(
        long timeoutMs,
        int maxStoredSolutions
) {
    public static final SolverOptions DEFAULT =
            new SolverOptions(10_000, 15);

    public SolverOptions {
        if (timeoutMs < 0) {
            throw new IllegalArgumentException("Timeout cannot be negative");
        }

        if (maxStoredSolutions < 1) {
            throw new IllegalArgumentException("Must store at least one solution");
        }
    }
}