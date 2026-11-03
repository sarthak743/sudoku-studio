package com.sudokustudio;

import org.junit.jupiter.api.Test;

import java.util.List;

import static org.junit.jupiter.api.Assertions.*;

class ValidatorTest {

    private Board createEmptyBoard() {
        return new Board(new int[9][9]);
    }

    @Test
    void acceptsValidIncompleteSudoku() {
        Board board = Parser.parseGrid(
                "530070000" +
                "600195000" +
                "098000060" +
                "800060003" +
                "400803001" +
                "700020006" +
                "060000280" +
                "000419005" +
                "000080079"
        );

        assertTrue(Validator.validateBoard(board).isEmpty());
        assertTrue(Validator.validateInput(
                "530070000600195000098000060800060003400803001700020006060000280000419005000080079"
        ));
    }

    @Test
    void detectsRowConflict() {
        Board board = createEmptyBoard();

        board.set(0, 0, 5);
        board.set(0, 4, 5);

        List<CellPosition> conflicts =
                Validator.findRowConflicts(board);

        assertEquals(2, conflicts.size());
        assertTrue(conflicts.contains(new CellPosition(0, 0)));
        assertTrue(conflicts.contains(new CellPosition(0, 4)));
    }

    @Test
    void detectsColumnConflict() {
        Board board = createEmptyBoard();

        board.set(0, 2, 7);
        board.set(5, 2, 7);

        List<CellPosition> conflicts =
                Validator.findColumnConflicts(board);

        assertEquals(2, conflicts.size());
        assertTrue(conflicts.contains(new CellPosition(0, 2)));
        assertTrue(conflicts.contains(new CellPosition(5, 2)));
    }

    @Test
    void detectsBoxConflict() {
        Board board = createEmptyBoard();

        board.set(0, 0, 3);
        board.set(2, 2, 3);

        List<CellPosition> conflicts =
                Validator.findBoxConflicts(board);

        assertEquals(2, conflicts.size());
        assertTrue(conflicts.contains(new CellPosition(0, 0)));
        assertTrue(conflicts.contains(new CellPosition(2, 2)));
    }

    @Test
    void detectsMultipleConflicts() {
        Board board = createEmptyBoard();

        board.set(0, 0, 5);
        board.set(0, 1, 5);
        board.set(1, 0, 5);

        List<CellPosition> conflicts =
                Validator.validateBoard(board);

        assertTrue(conflicts.contains(new CellPosition(0, 0)));
        assertTrue(conflicts.contains(new CellPosition(0, 1)));
        assertTrue(conflicts.contains(new CellPosition(1, 0)));
    }

    @Test
    void flagsValuesOutsideValidRange() {
        Board board = createEmptyBoard();

        board.set(0, 0, 10);
        board.set(1, 1, -1);

        List<CellPosition> conflicts =
                Validator.validateBoard(board);

        assertTrue(conflicts.contains(new CellPosition(0, 0)));
        assertTrue(conflicts.contains(new CellPosition(1, 1)));
    }
}