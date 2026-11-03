
#include "sudoku/parser.hpp"
#include "sudoku/solver.hpp"
#include "sudoku/validator.hpp"

#include <chrono>
#include <string>

#include <gtest/gtest.h>

namespace
{

    using namespace sudoku;

    const std::string CLASSIC_PUZZLE =
        "530070000600195000098000060800060003400803001700020006060000280000419005000080079";

    const std::string CLASSIC_SOLUTION =
        "534678912672195348198342567859761423426853791713924856961537284287419635345286179";

    TEST(A3, SolvesClassicPuzzle)
    {
        const Board board = parse_grid(CLASSIC_PUZZLE);
        const SolverResult result = solve_a3(board);

        ASSERT_EQ(result.status, SolverStatus::UNIQUE);
        ASSERT_EQ(result.solution_count, 1);
        ASSERT_EQ(result.solutions.size(), 1);

        EXPECT_EQ(
            serialize_grid(result.solutions[0]),
            CLASSIC_SOLUTION);
    }

    TEST(A3, DoesNotModifyOriginalBoard)
    {
        const Board board = parse_grid(CLASSIC_PUZZLE);

        solve_a3(board);

        EXPECT_EQ(board, parse_grid(CLASSIC_PUZZLE));
    }

    TEST(A3, DetectsUnsolvablePuzzle)
    {
        std::string grid = CLASSIC_PUZZLE;
        grid[2] = '1';

        const Board board = parse_grid(grid);
        const SolverResult result = solve_a3(board);

        EXPECT_EQ(result.status, SolverStatus::UNSOLVABLE);
        EXPECT_EQ(result.solution_count, 0);
    }

    TEST(A3, DetectsAlreadySolvedPuzzle)
    {
        const Board board = parse_grid(CLASSIC_SOLUTION);
        const SolverResult result = solve_a3(board);

        EXPECT_EQ(result.status, SolverStatus::ALREADY_SOLVED);
        EXPECT_EQ(result.solution_count, 1);
    }

    TEST(A3, RejectsInvalidBoard)
    {
        Board board = parse_grid(CLASSIC_PUZZLE);
        board[0][1] = 5;

        const SolverResult result = solve_a3(board);

        EXPECT_EQ(result.status, SolverStatus::INVALID);
    }

    TEST(A3, FindsMultipleSolutions)
    {
        Board board{};

        SolverOptions options;
        options.timeout = std::chrono::milliseconds(1000);

        const SolverResult result = solve_a3(board, options);

        EXPECT_EQ(result.status, SolverStatus::MULTIPLE);
        EXPECT_GE(result.solution_count, 2);
        EXPECT_LE(result.solutions.size(), MAX_STORED_SOLUTIONS);
    }

    TEST(A3, StoresAtMostFifteenSolutions)
    {
        Board board{};

        SolverOptions options;
        options.timeout = std::chrono::milliseconds(1000);

        const SolverResult result = solve_a3(board, options);

        EXPECT_LE(result.solutions.size(), 15);
        EXPECT_FALSE(result.count_capped);
    }

    TEST(A3, RecordsMetrics)
    {
        const Board board = parse_grid(CLASSIC_PUZZLE);
        const SolverResult result = solve_a3(board);

        EXPECT_GT(result.nodes_visited, 0);
        EXPECT_GE(result.backtracks, 0);
        EXPECT_GE(result.time_ms, 0.0);
        EXPECT_EQ(result.algorithm, "A3");
    }

    TEST(A3, EveryReturnedSolutionIsValid)
    {
        Board board{};

        SolverOptions options;
        options.timeout = std::chrono::milliseconds(1000);

        const SolverResult result = solve_a3(board, options);

        for (const auto &solution : result.solutions)
        {
            EXPECT_TRUE(validate_board(solution).empty());

            for (const auto &row : solution)
            {
                for (const int value : row)
                {
                    EXPECT_GE(value, 1);
                    EXPECT_LE(value, 9);
                }
            }
        }
    }

} // namespace
