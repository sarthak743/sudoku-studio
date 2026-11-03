package com.sudokustudio;

public class Board {
    public static final int GRID_SIZE = 9;
    public static final int BOX_SIZE = 3;

    private final int[][] cells;

    public Board(int[][] cells) {
        if (cells.length != GRID_SIZE) {
            throw new IllegalArgumentException("Board must have 9 rows");
        }

        this.cells = new int[GRID_SIZE][GRID_SIZE];

        for (int row = 0; row < GRID_SIZE; row++) {
            if (cells[row].length != GRID_SIZE) {
                throw new IllegalArgumentException("Each row must have 9 columns");
            }

            this.cells[row] = cells[row].clone();
        }
    }

    public int get(int row, int col) {
        return cells[row][col];
    }

    public void set(int row, int col, int value) {
        cells[row][col] = value;
    }

    public int[][] toArray() {
        int[][] copy = new int[GRID_SIZE][GRID_SIZE];

        for (int row = 0; row < GRID_SIZE; row++) {
            copy[row] = cells[row].clone();
        }

        return copy;
    }
}