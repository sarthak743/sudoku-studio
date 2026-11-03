package com.sudokustudio;

import java.util.ArrayList;
import java.util.List;

public class A1 {

    private static final String ALGORITHM = "A1";

    private final Board board;
    private final SolverOptions options;
    private final List<Board> solutions = new ArrayList<>();

    private int solutionCount = 0;
    private long nodesVisited = 0;
    private long backtracks = 0;

    private long startTime;
    private long deadline;

    private boolean timedOut = false;

    private A1(Board board, SolverOptions options) {
        this.board = new Board(board.toArray());
        this.options = options;
    }

    public static SolverResult solve(
            Board board,
            SolverOptions options
    ) {
        long start = System.nanoTime();

        if (!Validator.validateBoard(board).isEmpty()) {
            return createResult(
                    SolverStatus.INVALID,
                    0,
                    List.of(),
                    false,
                    false,
                    elapsedMs(start),
                    0,
                    0
            );
        }

        if (isCompleted(board)) {
            return createResult(
                    SolverStatus.ALREADY_SOLVED,
                    1,
                    List.of(new Board(board.toArray())),
                    false,
                    false,
                    elapsedMs(start),
                    0,
                    0
            );
        }

        A1 solver = new A1(board, options);

        solver.startTime = start;
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

        boolean foundSolution = false;

        for (int digit = 1; digit <= 9; digit++) {

            if (!isValidPlacement(row, col, digit)) {
                continue;
            }

            nodesVisited++;

            if (nodesVisited % 1024 == 0 &&
                    System.nanoTime() >= deadline) {
                timedOut = true;
                return;
            }

            board.set(row, col, digit);

            int previousCount = solutionCount;

            search();

            board.set(row, col, 0);

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

    private boolean isValidPlacement(
            int row,
            int col,
            int digit
    ) {

        for (int i = 0; i < 9; i++) {

            if (board.get(row, i) == digit) {
                return false;
            }

            if (board.get(i, col) == digit) {
                return false;
            }
        }

        int boxRow = (row / 3) * 3;
        int boxCol = (col / 3) * 3;

        for (int r = boxRow; r < boxRow + 3; r++) {
            for (int c = boxCol; c < boxCol + 3; c++) {

                if (board.get(r, c) == digit) {
                    return false;
                }
            }
        }

        return true;
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