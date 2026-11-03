
#include "fixture_loader.hpp"
#include "sudoku/parser.hpp"
#include "sudoku/solver.hpp"
#include "sudoku/validator.hpp"

#include <array>
#include <chrono>
#include <string>
#include <vector>

#include <gtest/gtest.h>

namespace
{
    using sudoku::Board;
    using sudoku::SolverResult;
    using sudoku::SolverStatus;
    using sudoku::test::json;

    struct Algorithm
    {
        std::string name;
        sudoku::SolverFunction solve;
    };

    const std::array<Algorithm, 4> algorithms = {{
        {"A1", sudoku::solve_a1},
        {"A2", sudoku::solve_a2},
        {"A3", sudoku::solve_a3},
        {"A4", sudoku::solve_a4},
    }};

    void verify_solution(const Board &original, const Board &solution)
    {
        EXPECT_TRUE(sudoku::validate_board(solution).empty());

        for (int row = 0; row < sudoku::GRID_SIZE; ++row)
        {
            for (int col = 0; col < sudoku::GRID_SIZE; ++col)
            {
                EXPECT_NE(solution[row][col], 0);

                if (original[row][col] != 0)
                {
                    EXPECT_EQ(solution[row][col], original[row][col]);
                }
            }
        }
    }
}

TEST(CrossAlgorithm, ConsistentResultsAcrossEdgeCases)
{
    const json fixtures = sudoku::test::load_edge_cases();

    for (const auto &fixture : fixtures)
    {
        const std::string id = fixture.at("id").get<std::string>();
        SCOPED_TRACE("Fixture: " + id);

        const std::string grid = fixture.at("grid").get<std::string>();

        if (!sudoku::validate_format(grid))
        {
            continue;
        }

        const Board board = sudoku::parse_grid(grid);

        const int deadline_ms = fixture.value("deadline_ms", 10'000);

        std::vector<SolverResult> results;

        for (const auto &algorithm : algorithms)
        {
            sudoku::SolverOptions options;
            options.timeout = std::chrono::milliseconds(deadline_ms);

            SolverResult result = algorithm.solve(board, options);

            EXPECT_EQ(result.algorithm, algorithm.name);
            EXPECT_FALSE(result.count_capped);
            EXPECT_LE(result.solutions.size(), sudoku::MAX_STORED_SOLUTIONS);

            for (const auto &solution : result.solutions)
            {
                verify_solution(board, solution);
            }

            results.push_back(std::move(result));
        }

        // Compare completed searches. A timeout may legitimately
        // interrupt an algorithm before it discovers every solution.
        for (std::size_t i = 1; i < results.size(); ++i)
        {
            const auto &reference = results[0];
            const auto &current = results[i];

            if (!reference.timed_out && !current.timed_out)
            {
                EXPECT_EQ(current.status, reference.status);
                EXPECT_EQ(current.solution_count, reference.solution_count);
            }
        }
    }
}
