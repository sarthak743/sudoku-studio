
package com.sudokustudio;

import org.junit.jupiter.api.Test;

import java.util.List;
import java.util.Set;
import java.util.HashSet;

import static org.junit.jupiter.api.Assertions.*;

class CrossAlgorithmTest {

    private static final List<String> ALGORITHMS =
            List.of("A1", "A2", "A3", "A4");

    private Board createBoard(String puzzle) {
        int[][] cells = new int[9][9];

        for (int i = 0; i < 81; i++) {
            char ch = puzzle.charAt(i);
            cells[i / 9][i % 9] =
                    ch == '.' || ch == '0' ? 0 : ch - '0';
        }

        return new Board(cells);
    }

    private String serialize(Board board) {
        StringBuilder result = new StringBuilder();

        for (int row = 0; row < 9; row++) {
            for (int col = 0; col < 9; col++) {
                result.append(board.get(row, col));
            }
        }

        return result.toString();
    }

    private SolverResult solve(String algorithm, Board board) {
        SolverOptions options = new SolverOptions(10000, 15);

        return switch (algorithm) {
            case "A1" -> A1.solve(board, options);
            case "A2" -> A2.solve(board, options);
            case "A3" -> A3.solve(board, options);
            case "A4" -> A4.solve(board, options);
            default -> throw new IllegalArgumentException(
                    "Unknown algorithm: " + algorithm
            );
        };
    }

    @Test
    void allAlgorithmsProduceConsistentResults() {

        List<String> puzzles = List.of(
                // Unique puzzle
                "530070000" +
                "600195000" +
                "098000060" +
                "800060003" +
                "400803001" +
                "700020006" +
                "060000280" +
                "000419005" +
                "000080079",

                // Already solved
                "534678912" +
                "672195348" +
                "198342567" +
                "859761423" +
                "426853791" +
                "713924856" +
                "961537284" +
                "287419635" +
                "345286179",

                // Invalid puzzle
                "550070000" +
                "600195000" +
                "098000060" +
                "800060003" +
                "400803001" +
                "700020006" +
                "060000280" +
                "000419005" +
                "000080079",

                // Unsolvable puzzle
                "531070000" +
                "600195000" +
                "098000060" +
                "800060003" +
                "400803001" +
                "700020006" +
                "060000280" +
                "000419005" +
                "000080079",

                // Multiple solutions
                "530070000" +
                "600195000" +
                "098000060" +
                "000000003" +
                "400803001" +
                "700020006" +
                "060000280" +
                "000409005" +
                "000000079"
        );

        int puzzleNumber = 0;

        for (String puzzle : puzzles) {
            puzzleNumber++;

            Board board = createBoard(puzzle);
            String original = serialize(board);

            SolverResult baseline = null;

            for (String algorithm : ALGORITHMS) {

                SolverResult result = solve(algorithm, board);

                assertEquals(
                        algorithm,
                        result.algorithm(),
                        "Incorrect algorithm identifier"
                );

                assertFalse(
                        result.timedOut(),
                        "Unexpected timeout on puzzle " + puzzleNumber
                                + " using " + algorithm
                );

                assertFalse(
                        result.countCapped(),
                        "Unexpected count cap"
                );

                assertTrue(
                        result.solutions().size() <= 15,
                        "Stored more than 15 solutions"
                );

                for (Board solution : result.solutions()) {
                    assertTrue(
                            Validator.validateBoard(solution).isEmpty(),
                            algorithm + " generated an invalid solution"
                    );
                }

                assertEquals(
                        original,
                        serialize(board),
                        algorithm + " modified the original board"
                );

                if (baseline == null) {
                    baseline = result;
                } else {
                    assertEquals(
                            baseline.status(),
                            result.status(),
                            "Status mismatch on puzzle " + puzzleNumber
                                    + " between algorithms"
                    );

                    assertEquals(
                            baseline.solutionCount(),
                            result.solutionCount(),
                            "Solution count mismatch on puzzle "
                                    + puzzleNumber
                    );
                }

                if (result.solutionCount() <= 15) {
                    Set<String> solutions = new HashSet<>();

                    for (Board solution : result.solutions()) {
                        solutions.add(serialize(solution));
                    }

                    if (baseline == result) {
                        continue;
                    }

                    Set<String> baselineSolutions = new HashSet<>();

                    for (Board solution : baseline.solutions()) {
                        baselineSolutions.add(serialize(solution));
                    }

                    assertEquals(
                            baselineSolutions,
                            solutions,
                            "Solution mismatch on puzzle " + puzzleNumber
                                    + " using " + algorithm
                    );
                }
            }
        }
    }
}
