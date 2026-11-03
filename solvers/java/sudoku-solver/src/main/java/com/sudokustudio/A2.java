
package com.sudokustudio;

import java.util.ArrayList;
import java.util.List;

public class A2 {

    private static final String ALGORITHM = "A2";
    private static final int FULL_MASK = 0x3FE; // Bits 1 through 9

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

    private A2(Board board, SolverOptions options) {
        this.board = new Board(board.toArray());
        this.options = options;
        initializeMasks();
    }

    public static SolverResult solve(
            Board board,
            SolverOptions options
    ) {
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

        A2 solver = new A2(board, options);

        solver.deadline = start +
                options.timeoutMs() * 1_000_000L;

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

        int[] emptyCell = findNextEmptyCell();

        if (emptyCell == null) {
            solutionCount++;

            if (solutions.size() < options.maxStoredSolutions()) {
                solutions.add(new Board(board.toArray()));
            }

            return;
        }

        int row = emptyCell[0];
        int col = emptyCell[1];
        int box = getBoxIndex(row, col);

        boolean foundSolution = false;

        for (int digit = 1; digit <= 9; digit++) {

            int bit = 1 << digit;

            if (((rowMask[row] |
                    colMask[col] |
                    boxMask[box]) & bit) != 0) {
                continue;
            }

            nodesVisited++;

            if (nodesVisited % 1024 == 0 &&
                    System.nanoTime() >= deadline) {
                timedOut = true;
                return;
            }

            // Place digit and update masks.
            board.set(row, col, digit);
            rowMask[row] |= bit;
            colMask[col] |= bit;
            boxMask[box] |= bit;

            int previousCount = solutionCount;

            search();

            // Undo placement and restore masks.
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

    private int[] findNextEmptyCell() {

        for (int row = 0; row < 9; row++) {
            for (int col = 0; col < 9; col++) {

                if (board.get(row, col) == 0) {
                    return new int[]{row, col};
                }
            }
        }

        return null;
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
