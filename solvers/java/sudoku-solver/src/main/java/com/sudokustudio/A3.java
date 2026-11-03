
package com.sudokustudio;

import java.util.ArrayList;
import java.util.List;

public class A3 {

    private static final String ALGORITHM = "A3";
    private static final int FULL_MASK = 0x3FE;

    private final Board board;
    private final SolverOptions options;
    private final List<Board> solutions = new ArrayList<>();

    private final int[] rowMask = new int[9];
    private final int[] colMask = new int[9];
    private final int[] boxMask = new int[9];

    private int solutionCount = 0;
    private long nodesVisited = 0;
    private long backtracks = 0;

    private long deadline;
    private boolean timedOut = false;

    private A3(Board board, SolverOptions options) {
        this.board = new Board(board.toArray());
        this.options = options;
        initializeMasks();
    }

    public static SolverResult solve(Board board, SolverOptions options) {
        long start = System.nanoTime();

        if (!Validator.validateBoard(board).isEmpty()) {
            return createResult(
                    SolverStatus.INVALID, 0, List.of(),
                    false, false, elapsedMs(start), 0, 0
            );
        }

        if (isCompleted(board)) {
            return createResult(
                    SolverStatus.ALREADY_SOLVED, 1,
                    List.of(new Board(board.toArray())),
                    false, false, elapsedMs(start), 0, 0
            );
        }

        A3 solver = new A3(board, options);

        solver.deadline = start + options.timeoutMs() * 1_000_000L;

        solver.search();

        double timeMs = elapsedMs(start);

        SolverStatus status;

        if (solver.solutionCount >= 2) {
            status = SolverStatus.MULTIPLE;
        } else if (solver.timedOut) {
            status = SolverStatus.TIMEOUT;
        } else if (solver.solutionCount == 0) {
            status = SolverStatus.UNSOLVABLE;
        } else {
            status = SolverStatus.UNIQUE;
        }

        return createResult(
                status,
                solver.solutionCount,
                solver.solutions,
                false,
                solver.timedOut,
                timeMs,
                solver.nodesVisited,
                solver.backtracks
        );
    }

    private void initializeMasks() {
        for (int row = 0; row < 9; row++) {
            for (int col = 0; col < 9; col++) {
                int digit = board.get(row, col);

                if (digit == 0) {
                    continue;
                }

                int bit = 1 << digit;
                int box = getBoxIndex(row, col);

                rowMask[row] |= bit;
                colMask[col] |= bit;
                boxMask[box] |= bit;
            }
        }
    }

    private void search() {
        if (timedOut) {
            return;
        }

        int[] cell = findBestEmptyCell();

        if (cell == null) {
            solutionCount++;

            if (solutions.size() < options.maxStoredSolutions()) {
                solutions.add(new Board(board.toArray()));
            }

            return;
        }

        int row = cell[0];
        int col = cell[1];
        int box = getBoxIndex(row, col);

        int usedMask = rowMask[row] | colMask[col] | boxMask[box];
        int candidates = FULL_MASK & ~usedMask;

        if (candidates == 0) {
            backtracks++;
            return;
        }

        boolean foundSolution = false;

        for (int digit = 1; digit <= 9; digit++) {
            int bit = 1 << digit;

            if ((candidates & bit) == 0) {
                continue;
            }

            nodesVisited++;

            if (nodesVisited % 1024 == 0
                    && System.nanoTime() >= deadline) {
                timedOut = true;
                return;
            }

            board.set(row, col, digit);
            rowMask[row] |= bit;
            colMask[col] |= bit;
            boxMask[box] |= bit;

            int previousCount = solutionCount;

            search();

            board.set(row, col, 0);
            rowMask[row] &= ~bit;
            colMask[col] &= ~bit;
            boxMask[box] &= ~bit;

            if (timedOut) {
                return;
            }

            if (solutionCount > previousCount) {
                foundSolution = true;
            }
        }

        if (!foundSolution) {
            backtracks++;
        }
    }

    private int[] findBestEmptyCell() {
        int bestRow = -1;
        int bestCol = -1;
        int minimumCandidates = 10;

        for (int row = 0; row < 9; row++) {
            for (int col = 0; col < 9; col++) {
                if (board.get(row, col) != 0) {
                    continue;
                }

                int box = getBoxIndex(row, col);
                int usedMask =
                        rowMask[row] | colMask[col] | boxMask[box];

                int candidates =
                        FULL_MASK & ~usedMask;

                int candidateCount = Integer.bitCount(candidates);

                if (candidateCount < minimumCandidates) {
                    minimumCandidates = candidateCount;
                    bestRow = row;
                    bestCol = col;

                    if (candidateCount == 0) {
                        return new int[]{bestRow, bestCol};
                    }
                }
            }
        }

        if (bestRow == -1) {
            return null;
        }

        return new int[]{bestRow, bestCol};
    }

    private static int getBoxIndex(int row, int col) {
        return (row / 3) * 3 + (col / 3);
    }

    private static boolean isCompleted(Board board) {
        for (int row = 0; row < 9; row++) {
            for (int col = 0; col < 9; col++) {
                if (board.get(row, col) == 0) {
                    return false;
                }
            }
        }

        return true;
    }

    private static double elapsedMs(long start) {
        return (System.nanoTime() - start) / 1_000_000.0;
    }

    private static SolverResult createResult(
            SolverStatus status,
            int count,
            List<Board> solutions,
            boolean capped,
            boolean timedOut,
            double timeMs,
            long nodes,
            long backtracks
    ) {
        return new SolverResult(
                status,
                count,
                solutions,
                capped,
                timedOut,
                timeMs,
                nodes,
                backtracks,
                ALGORITHM
        );
    }
}
