
package com.sudokustudio;

import java.util.ArrayList;
import java.util.List;

public final class A4 {

    private static final String ALGORITHM = "A4";
    private static final int FULL_MASK = 0x3FE;

    private A4() {
    }

    public static SolverResult solve(Board board, SolverOptions options) {
        long startTime = System.nanoTime();
        long deadline = startTime + options.timeoutMs() * 1_000_000L;

        if (!Validator.validateBoard(board).isEmpty()) {
            return createResult(
                    SolverStatus.INVALID, 0, List.of(),
                    false, false, startTime, 0, 0
            );
        }

        Board workingBoard = new Board(board.toArray());

        Solver solver = new Solver(options, deadline);
        solver.search(workingBoard);

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

        if (status == SolverStatus.UNIQUE
                && isCompleted(board)) {
            status = SolverStatus.ALREADY_SOLVED;
        }

        return createResult(
                status,
                solver.solutionCount,
                solver.solutions,
                false,
                solver.timedOut,
                startTime,
                solver.nodesVisited,
                solver.backtracks
        );
    }

    private static SolverResult createResult(
            SolverStatus status,
            int solutionCount,
            List<Board> solutions,
            boolean countCapped,
            boolean timedOut,
            long startTime,
            long nodesVisited,
            long backtracks
    ) {
        double timeMs = (System.nanoTime() - startTime) / 1_000_000.0;

        return new SolverResult(
                status,
                solutionCount,
                solutions,
                countCapped,
                timedOut,
                timeMs,
                nodesVisited,
                backtracks,
                ALGORITHM
        );
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

    private static int getCandidates(Board board, int row, int col) {
        int usedMask = 0;

        for (int i = 0; i < 9; i++) {
            int rowValue = board.get(row, i);
            int colValue = board.get(i, col);

            if (rowValue != 0) {
                usedMask |= 1 << rowValue;
            }

            if (colValue != 0) {
                usedMask |= 1 << colValue;
            }
        }

        int boxRow = (row / 3) * 3;
        int boxCol = (col / 3) * 3;

        for (int r = boxRow; r < boxRow + 3; r++) {
            for (int c = boxCol; c < boxCol + 3; c++) {
                int value = board.get(r, c);

                if (value != 0) {
                    usedMask |= 1 << value;
                }
            }
        }

        return FULL_MASK & ~usedMask;
    }

    private static int bitCount(int mask) {
        return Integer.bitCount(mask);
    }

    private static int singleDigit(int mask) {
        return Integer.numberOfTrailingZeros(mask);
    }

    private static final class Solver {

        private final SolverOptions options;
        private final long deadline;

        private final List<Board> solutions = new ArrayList<>();

        private int solutionCount = 0;
        private boolean timedOut = false;
        private long nodesVisited = 0;
        private long backtracks = 0;

        private Solver(SolverOptions options, long deadline) {
            this.options = options;
            this.deadline = deadline;
        }

        private void search(Board board) {
            if (timedOut || solutionCount >= Integer.MAX_VALUE) {
                return;
            }

            nodesVisited++;

            if ((nodesVisited & 1023) == 0
                    && System.nanoTime() >= deadline) {
                timedOut = true;
                return;
            }

            if (!propagate(board)) {
                backtracks++;
                return;
            }

            int[] bestCell = findBestEmptyCell(board);

            if (bestCell == null) {
                solutionCount++;

                if (solutions.size() < options.maxStoredSolutions()) {
                    solutions.add(new Board(board.toArray()));
                }
                return;
            }

            int row = bestCell[0];
            int col = bestCell[1];
            int candidates = getCandidates(board, row, col);

            if (candidates == 0) {
                backtracks++;
                return;
            }

            for (int digit = 1; digit <= 9; digit++) {
                int bit = 1 << digit;

                if ((candidates & bit) == 0) {
                    continue;
                }

                Board nextBoard = new Board(board.toArray());
                nextBoard.set(row, col, digit);

                search(nextBoard);

                if (timedOut) {
                    return;
                }
            }
        }

        private boolean propagate(Board board) {
            while (true) {

                // 1. Naked singles: row-major order.
                boolean assigned = false;

                for (int row = 0; row < 9 && !assigned; row++) {
                    for (int col = 0; col < 9; col++) {

                        if (board.get(row, col) != 0) {
                            continue;
                        }

                        int candidates = getCandidates(board, row, col);
                        int count = bitCount(candidates);

                        if (count == 0) {
                            return false;
                        }

                        if (count == 1) {
                            board.set(row, col, singleDigit(candidates));
                            assigned = true;
                            break;
                        }
                    }
                }

                if (assigned) {
                    continue;
                }

                // 2. Hidden singles in rows.
                for (int row = 0; row < 9 && !assigned; row++) {
                    for (int digit = 1; digit <= 9; digit++) {

                        if (isDigitPresentInRow(board, row, digit)) {
                            continue;
                        }

                        int count = 0;
                        int targetCol = -1;

                        for (int col = 0; col < 9; col++) {
                            if (board.get(row, col) == 0
                                    && (getCandidates(board, row, col)
                                    & (1 << digit)) != 0) {
                                count++;
                                targetCol = col;
                            }
                        }

                        if (count == 0) {
                            return false;
                        }

                        if (count == 1) {
                            board.set(row, targetCol, digit);
                            assigned = true;
                            break;
                        }
                    }
                }

                if (assigned) {
                    continue;
                }

                // 3. Hidden singles in columns.
                for (int col = 0; col < 9 && !assigned; col++) {
                    for (int digit = 1; digit <= 9; digit++) {

                        if (isDigitPresentInColumn(board, col, digit)) {
                            continue;
                        }

                        int count = 0;
                        int targetRow = -1;

                        for (int row = 0; row < 9; row++) {
                            if (board.get(row, col) == 0
                                    && (getCandidates(board, row, col)
                                    & (1 << digit)) != 0) {
                                count++;
                                targetRow = row;
                            }
                        }

                        if (count == 0) {
                            return false;
                        }

                        if (count == 1) {
                            board.set(targetRow, col, digit);
                            assigned = true;
                            break;
                        }
                    }
                }

                if (assigned) {
                    continue;
                }

                // 4. Hidden singles in boxes.
                for (int boxRow = 0; boxRow < 9 && !assigned;
                     boxRow += 3) {

                    for (int boxCol = 0; boxCol < 9 && !assigned;
                         boxCol += 3) {

                        for (int digit = 1; digit <= 9; digit++) {

                            if (isDigitPresentInBox(
                                    board, boxRow, boxCol, digit)) {
                                continue;
                            }

                            int count = 0;
                            int targetRow = -1;
                            int targetCol = -1;

                            for (int r = boxRow; r < boxRow + 3; r++) {
                                for (int c = boxCol; c < boxCol + 3; c++) {

                                    if (board.get(r, c) == 0
                                            && (getCandidates(board, r, c)
                                            & (1 << digit)) != 0) {
                                        count++;
                                        targetRow = r;
                                        targetCol = c;
                                    }
                                }
                            }

                            if (count == 0) {
                                return false;
                            }

                            if (count == 1) {
                                board.set(targetRow, targetCol, digit);
                                assigned = true;
                                break;
                            }
                        }
                    }
                }

                if (assigned) {
                    continue;
                }

                // No more forced assignments.
                return true;
            }
        }

        private boolean isDigitPresentInRow(
                Board board, int row, int digit) {
            for (int col = 0; col < 9; col++) {
                if (board.get(row, col) == digit) {
                    return true;
                }
            }
            return false;
        }

        private boolean isDigitPresentInColumn(
                Board board, int col, int digit) {
            for (int row = 0; row < 9; row++) {
                if (board.get(row, col) == digit) {
                    return true;
                }
            }
            return false;
        }

        private boolean isDigitPresentInBox(
                Board board, int boxRow, int boxCol, int digit) {
            for (int row = boxRow; row < boxRow + 3; row++) {
                for (int col = boxCol; col < boxCol + 3; col++) {
                    if (board.get(row, col) == digit) {
                        return true;
                    }
                }
            }
            return false;
        }

        private int[] findBestEmptyCell(Board board) {
            int minCandidates = 10;
            int bestRow = -1;
            int bestCol = -1;

            for (int row = 0; row < 9; row++) {
                for (int col = 0; col < 9; col++) {

                    if (board.get(row, col) != 0) {
                        continue;
                    }

                    int candidates = getCandidates(board, row, col);
                    int count = bitCount(candidates);

                    if (count == 0) {
                        return new int[]{row, col};
                    }

                    if (count < minCandidates) {
                        minCandidates = count;
                        bestRow = row;
                        bestCol = col;

                        if (count == 1) {
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
    }
}
