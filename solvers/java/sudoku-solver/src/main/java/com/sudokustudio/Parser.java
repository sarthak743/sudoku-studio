package com.sudokustudio;

public class Parser {

    public static boolean validateFormat(String input) {
        if (input == null || input.length() != 81) {
            return false;
        }

        for (char ch : input.toCharArray()) {
            if (ch < '0' || ch > '9') {
                if (ch != '.') {
                    return false;
                }
            }
        }

        return true;
    }

    public static Board parseGrid(String input) {
        if (!validateFormat(input)) {
            throw new IllegalArgumentException("Invalid Sudoku format");
        }

        int[][] cells = new int[9][9];

        for (int i = 0; i < 81; i++) {
            char ch = input.charAt(i);

            int value = (ch == '.' || ch == '0')
                    ? 0
                    : ch - '0';

            cells[i / 9][i % 9] = value;
        }

        return new Board(cells);
    }

    public static String serializeGrid(Board board) {
        StringBuilder result = new StringBuilder(81);

        for (int row = 0; row < 9; row++) {
            for (int col = 0; col < 9; col++) {
                int value = board.get(row, col);

                if (value < 0 || value > 9) {
                    throw new IllegalArgumentException("Invalid cell value");
                }

                result.append(value == 0 ? '.' : (char) ('0' + value));
            }
        }

        return result.toString();
    }
}