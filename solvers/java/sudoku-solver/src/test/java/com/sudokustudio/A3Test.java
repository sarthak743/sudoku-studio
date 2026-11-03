
package com.sudokustudio;
import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;

import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Locale;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

class A3Test {

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

    @Test
    void solvesUniquePuzzle() {
        Board board = createBoard(
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

        SolverResult result = A3.solve(board, new SolverOptions(10000, 15));

        assertEquals(SolverStatus.UNIQUE, result.status());
        assertEquals(1, result.solutionCount());
        assertEquals("A3", result.algorithm());
        assertEquals(1, result.solutions().size());
        assertFalse(result.timedOut());
    }

    @Test
    void detectsInvalidPuzzle() {
        Board board = createBoard(
                "550070000" +
                "600195000" +
                "098000060" +
                "800060003" +
                "400803001" +
                "700020006" +
                "060000280" +
                "000419005" +
                "000080079"
        );

        SolverResult result = A3.solve(board, new SolverOptions(10000,15));

        assertEquals(SolverStatus.INVALID, result.status());
        assertEquals(0, result.solutionCount());
    }

    @Test
    void detectsAlreadySolvedPuzzle() {
        Board board = createBoard(
                "534678912" +
                "672195348" +
                "198342567" +
                "859761423" +
                "426853791" +
                "713924856" +
                "961537284" +
                "287419635" +
                "345286179"
        );

        SolverResult result = A3.solve(board, new SolverOptions(10000,15));

        assertEquals(SolverStatus.ALREADY_SOLVED, result.status());
        assertEquals(1, result.solutionCount());
    }

    @Test
    void doesNotModifyOriginalBoard() {
        Board board = createBoard(
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

        String original = serialize(board);

        A3.solve(board, new SolverOptions(10000,15));

        assertEquals(original, serialize(board));
    }

    @Test
    void recordsMetrics() {
        Board board = createBoard(
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

        SolverResult result = A3.solve(board, new SolverOptions(10000,15));

        assertTrue(result.timeMs() >= 0);
        assertTrue(result.nodesVisited() > 0);
        assertTrue(result.backtracks() >= 0);
    }

    @Test
    void solutionRespectsOriginalGivens() {
        Board board = createBoard(
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

        SolverResult result = A3.solve(board, new SolverOptions(10000,15));

        Board solution = result.solutions().get(0);

        for (int row = 0; row < 9; row++) {
            for (int col = 0; col < 9; col++) {
                if (board.get(row, col) != 0) {
                    assertEquals(
                            board.get(row, col),
                            solution.get(row, col)
                    );
                }
            }
        }
    }

    
    @Test
    void testsAllSharedEdgeCaseFixtures() throws Exception {

        Path fixturePath = Path.of(
                "../../../data/puzzles/edge_cases.json"
        );

        JsonArray fixtures = JsonParser.parseString(
                Files.readString(fixturePath)
        ).getAsJsonArray();

        int tested = 0;

        for (var element : fixtures) {

            JsonObject fixture = element.getAsJsonObject();

            String id = fixture.get("id").getAsString();
            String grid = fixture.get("grid").getAsString();

            if (fixture.has("algorithms")) {
                JsonArray algorithms = fixture.getAsJsonArray("algorithms");

                boolean applicable = false;

                for (var algorithm : algorithms) {
                    if (algorithm.getAsString().equals("A3")) {
                        applicable = true;
                        break;
                    }
                }

                if (!applicable) {
                    continue;
                }
            }

            if (id.equals("EC010") ||
                    id.equals("EC011") ||
                    id.equals("EC012")) {

                assertFalse(
                        Parser.validateFormat(grid),
                        id + ": Expected invalid format"
                );

                tested++;
                continue;
            }

            Board board = createBoard(grid);
            String original = serialize(board);

            long timeout = fixture.has("deadline_ms")
                    ? fixture.get("deadline_ms").getAsLong()
                    : 10000L;

            SolverResult result = A3.solve(
                    board,
                    new SolverOptions(timeout, 15)
            );

            SolverStatus expectedStatus = SolverStatus.valueOf(
                    fixture.get("expected_status")
                            .getAsString()
                            .toUpperCase(Locale.ROOT)
            );

            int expectedCount = fixture.has("expected_solution_count")
                && !fixture.get("expected_solution_count").isJsonNull()
                ? fixture.get("expected_solution_count").getAsInt()
                : 0;

            String countType = fixture
                    .get("count_type")
                    .getAsString();

            if (id.equals("EC019") || id.equals("EC020")) {
                assertTrue(
                        result.status() == SolverStatus.TIMEOUT
                                || result.status() == SolverStatus.UNIQUE,
                        id + ": Unexpected status"
                );
            } else {
                assertEquals(
                        expectedStatus,
                        result.status(),
                        id + ": Incorrect status"
                );
            }

            if (fixture.has("expected_solution_count")
                    && !fixture.get("expected_solution_count").isJsonNull()) {

                if (countType.equals("exact")) {
                    assertEquals(expectedCount, result.solutionCount(),
                            id + ": Incorrect solution count");
                } else {
                    assertTrue(result.solutionCount() >= expectedCount,
                            id + ": Solution count below lower bound");
                }
            }

            assertFalse(
                    result.countCapped(),
                    id + ": Count should not be capped"
            );

            assertTrue(
                    result.solutions().size() <= 15,
                    id + ": Stored more than 15 solutions"
            );

            if (expectedStatus == SolverStatus.TIMEOUT
                    && result.status() == SolverStatus.TIMEOUT) {
                assertTrue(result.timedOut(), id + ": Expected timeout flag");
            }

            for (Board solution : result.solutions()) {

                assertTrue(
                        Validator.validateBoard(solution).isEmpty(),
                        id + ": Invalid solution generated"
                );

                for (int row = 0; row < 9; row++) {
                    for (int col = 0; col < 9; col++) {

                        if (board.get(row, col) != 0) {
                            assertEquals(
                                    board.get(row, col),
                                    solution.get(row, col),
                                    id + ": Original given changed"
                            );
                        }
                    }
                }
            }

            assertEquals(
                    original,
                    serialize(board),
                    id + ": Original board was modified"
            );

            tested++;
        }

        assertEquals(20, tested);
    }

    @Test
    void countsAll16SolutionsButStoresOnly15() {

        Board board = createBoard(
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

        SolverResult result = A3.solve(
                board,
                new SolverOptions(10000, 15)
        );

        assertEquals(SolverStatus.MULTIPLE, result.status());
        assertEquals(16, result.solutionCount());
        assertEquals(15, result.solutions().size());
        assertFalse(result.countCapped());
    }

}
