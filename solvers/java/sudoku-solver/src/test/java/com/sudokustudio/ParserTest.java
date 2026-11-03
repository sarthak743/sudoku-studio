package com.sudokustudio;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

class ParserTest {

    private static final String VALID_PUZZLE =
            "530070000" +
            "600195000" +
            "098000060" +
            "800060003" +
            "400803001" +
            "700020006" +
            "060000280" +
            "000419005" +
            "000080079";

    @Test
    void acceptsValid81CharacterPuzzle() {
        assertTrue(Parser.validateFormat(VALID_PUZZLE));
    }

    @Test
    void acceptsBothEmptyCellRepresentations() {
        String puzzle = ".".repeat(81);
        assertTrue(Parser.validateFormat(puzzle));

        puzzle = "0".repeat(81);
        assertTrue(Parser.validateFormat(puzzle));
    }

    @Test
    void rejectsIncorrectLength() {
        assertFalse(Parser.validateFormat("12345"));
        assertFalse(Parser.validateFormat("0".repeat(82)));
    }

    @Test
    void rejectsInvalidCharacters() {
        String puzzle = "0".repeat(80) + "X";
        assertFalse(Parser.validateFormat(puzzle));
    }

    @Test
    void parsesAndSerializesCorrectly() {
        Board board = Parser.parseGrid(VALID_PUZZLE);

        assertEquals(5, board.get(0, 0));
        assertEquals(0, board.get(0, 2));

        String serialized = Parser.serializeGrid(board);

        assertEquals(VALID_PUZZLE.replace('0', '.'), serialized);
    }

    @Test
    void rejectsInvalidInputDuringParsing() {
        assertThrows(
                IllegalArgumentException.class,
                () -> Parser.parseGrid("invalid")
        );
    }
}