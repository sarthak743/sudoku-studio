package com.sudokustudio;

import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

public class Validator {

    public static List<CellPosition> findRowConflicts(Board board) {
        Set<CellPosition> conflicts = new HashSet<>();

        for (int row = 0; row < 9; row++) {
            int[] firstPosition = new int[10];
            java.util.Arrays.fill(firstPosition, -1);

            for (int col = 0; col < 9; col++) {
                int value = board.get(row, col);

                if (value == 0) continue;

                if (value < 1 || value > 9) {
                    conflicts.add(new CellPosition(row, col));
                    continue;
                }

                if (firstPosition[value] != -1) {
                    conflicts.add(new CellPosition(row, firstPosition[value]));
                    conflicts.add(new CellPosition(row, col));
                } else {
                    firstPosition[value] = col;
                }
            }
        }

        return new ArrayList<>(conflicts);
    }

    public static List<CellPosition> findColumnConflicts(Board board) {
        Set<CellPosition> conflicts = new HashSet<>();

        for (int col = 0; col < 9; col++) {
            int[] firstPosition = new int[10];
            java.util.Arrays.fill(firstPosition, -1);

            for (int row = 0; row < 9; row++) {
                int value = board.get(row, col);

                if (value == 0) continue;

                if (value < 1 || value > 9) {
                    conflicts.add(new CellPosition(row, col));
                    continue;
                }

                if (firstPosition[value] != -1) {
                    conflicts.add(new CellPosition(firstPosition[value], col));
                    conflicts.add(new CellPosition(row, col));
                } else {
                    firstPosition[value] = row;
                }
            }
        }

        return new ArrayList<>(conflicts);
    }

    public static List<CellPosition> findBoxConflicts(Board board) {
        Set<CellPosition> conflicts = new HashSet<>();

        for (int boxRow = 0; boxRow < 9; boxRow += 3) {
            for (int boxCol = 0; boxCol < 9; boxCol += 3) {
                int[] firstPosition = new int[10];
                java.util.Arrays.fill(firstPosition, -1);

                for (int row = boxRow; row < boxRow + 3; row++) {
                    for (int col = boxCol; col < boxCol + 3; col++) {
                        int value = board.get(row, col);

                        if (value == 0) continue;

                        if (value < 1 || value > 9) {
                            conflicts.add(new CellPosition(row, col));
                            continue;
                        }

                        if (firstPosition[value] != -1) {
                            int firstIndex = firstPosition[value];

                            conflicts.add(new CellPosition(
                                    boxRow + firstIndex / 3,
                                    boxCol + firstIndex % 3
                            ));

                            conflicts.add(new CellPosition(row, col));
                        } else {
                            firstPosition[value] =
                                    (row - boxRow) * 3 + (col - boxCol);
                        }
                    }
                }
            }
        }

        return new ArrayList<>(conflicts);
    }

    public static List<CellPosition> validateBoard(Board board) {
        Set<CellPosition> conflicts = new HashSet<>();

        conflicts.addAll(findRowConflicts(board));
        conflicts.addAll(findColumnConflicts(board));
        conflicts.addAll(findBoxConflicts(board));

        return new ArrayList<>(conflicts);
    }

    public static boolean validateInput(String input) {
        if (!Parser.validateFormat(input)) {
            return false;
        }

        Board board = Parser.parseGrid(input);
        return validateBoard(board).isEmpty();
    }
}