package com.sudokustudio;

import java.util.List;

public record SolverResult(
        SolverStatus status,
        int solutionCount,
        List<Board> solutions,
        boolean countCapped,
        boolean timedOut,
        double timeMs,
        long nodesVisited,
        long backtracks,
        String algorithm
) {
    public SolverResult {
        solutions = List.copyOf(solutions);
    }
}