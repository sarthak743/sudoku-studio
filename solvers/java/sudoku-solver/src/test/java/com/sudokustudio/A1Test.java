package com.sudokustudio;

import org.junit.jupiter.api.Test;
import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;

import static org.junit.jupiter.api.Assertions.*;

class A1Test {

    private static final String PUZZLE =
            "530070000" +
            "600195000" +
            "098000060" +
            "800060003" +
            "400803001" +
            "700020006" +
            "060000280" +
            "000419005" +
            "000080079";

    private static final String SOLUTION =
            "534678912" +
            "672195348" +
            "198342567" +
            "859761423" +
            "426853791" +
            "713924856" +
            "961537284" +
            "287419635" +
            "345286179";

    @Test
    void solvesUniquePuzzle() {
        Board board = Parser.parseGrid(PUZZLE);

        SolverResult result = A1.solve(
                board,
                SolverOptions.DEFAULT
        );

        assertEquals(SolverStatus.UNIQUE, result.status());
        assertEquals(1, result.solutionCount());
        assertEquals(1, result.solutions().size());
        assertEquals(SOLUTION,
                Parser.serializeGrid(result.solutions().get(0)));
    }

    @Test
    void rejectsInvalidPuzzle() {
        Board board = Parser.parseGrid(
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

        SolverResult result = A1.solve(
                board,
                SolverOptions.DEFAULT
        );

        assertEquals(SolverStatus.INVALID, result.status());
        assertEquals(0, result.solutionCount());
        assertTrue(result.solutions().isEmpty());
    }

    @Test
    void recognizesAlreadySolvedPuzzle() {
        Board board = Parser.parseGrid(SOLUTION);

        SolverResult result = A1.solve(
                board,
                SolverOptions.DEFAULT
        );

        assertEquals(SolverStatus.ALREADY_SOLVED, result.status());
        assertEquals(1, result.solutionCount());
        assertEquals(SOLUTION,
                Parser.serializeGrid(result.solutions().get(0)));
    }

    @Test
    void doesNotModifyOriginalBoard() {
        Board board = Parser.parseGrid(PUZZLE);
        String original = Parser.serializeGrid(board);

        A1.solve(board, SolverOptions.DEFAULT);

        assertEquals(original, Parser.serializeGrid(board));
    }

    @Test
    void returnsExecutionMetrics() {
        Board board = Parser.parseGrid(PUZZLE);

        SolverResult result = A1.solve(
                board,
                SolverOptions.DEFAULT
        );

        assertEquals("A1", result.algorithm());
        assertTrue(result.timeMs() >= 0);
        assertTrue(result.nodesVisited() > 0);
        assertFalse(result.timedOut());
        assertFalse(result.countCapped());
    }

        
    @Test
    void matchesAllOfficialEdgeCases() throws IOException {
        Path fixturePath = Path.of("../../../data/puzzles/edge_cases.json");

        JsonArray fixtures = JsonParser.parseString(
                Files.readString(fixturePath)
        ).getAsJsonArray();

        assertEquals(20, fixtures.size());

        int tested = 0;

        for (JsonElement element : fixtures) {
            JsonObject fixture = element.getAsJsonObject();

            String id = fixture.get("id").getAsString();
            String grid = fixture.get("grid").getAsString();
            String expected = fixture.get("expected_status").getAsString();
            String countType = fixture.get("count_type").getAsString();

            if (fixture.has("algorithms")) {
                JsonArray algorithms = fixture.getAsJsonArray("algorithms");
                boolean applicable = false;

                for (JsonElement algorithm : algorithms) {
                    if (algorithm.getAsString().equals("A1")) {
                        applicable = true;
                        break;
                    }
                }

                if (!applicable) continue;
            }

            if (expected.equals("invalid_format")) {
                assertFalse(Parser.validateFormat(grid), id);
                tested++;
                continue;
            }

            assertTrue(Parser.validateFormat(grid), id);

            Board board = Parser.parseGrid(grid);

            long timeout = fixture.has("deadline_ms")
                    ? fixture.get("deadline_ms").getAsLong()
                    : 10_000L;

            SolverResult result = A1.solve(
                    board,
                    new SolverOptions(timeout, 15)
            );

            if (expected.equals("timeout") && result.solutionCount() >= 2) {
                assertEquals(SolverStatus.MULTIPLE, result.status(), id);
            } else {
                assertEquals(
                        expected.toUpperCase(),
                        result.status().name(),
                        id
                );
            }

            assertEquals("A1", result.algorithm(), id);
            assertFalse(result.countCapped(), id);
            assertTrue(result.solutions().size() <= 15, id);

            if (countType.equals("exact")) {
                assertEquals(
                        fixture.get("expected_solution_count").getAsInt(),
                        result.solutionCount(),
                        id
                );
            } else if (countType.equals("lower_bound")) {
                assertTrue(
                        result.solutionCount() >=
                                fixture.get("expected_solution_count").getAsInt(),
                        id
                );
                assertTrue(result.timedOut(), id);
            }

            for (Board solution : result.solutions()) {
                assertTrue(Validator.validateBoard(solution).isEmpty(), id);

                for (int row = 0; row < 9; row++) {
                    for (int col = 0; col < 9; col++) {
                        int given = board.get(row, col);

                        if (given != 0) {
                            assertEquals(given, solution.get(row, col), id);
                        }
                    }
                }
            }

            tested++;
        }

        assertEquals(20, tested);
    }

    @Test
    void stores15SolutionsButCountsAll16() {
        String puzzle =
                "530070000600195000098000060000000003400803001700020006060000280000409005000000079";

        SolverResult result = A1.solve(
                Parser.parseGrid(puzzle),
                SolverOptions.DEFAULT
        );

        assertEquals(SolverStatus.MULTIPLE, result.status());
        assertEquals(16, result.solutionCount());
        assertEquals(15, result.solutions().size());
        assertFalse(result.countCapped());
    }

}