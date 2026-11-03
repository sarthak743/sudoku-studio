#include "sudoku/parser.hpp"
#include "sudoku/solver.hpp"
#include "sudoku/validator.hpp"

#include <gtest/gtest.h>

#include <algorithm>
#include <chrono>
#include <string>

using namespace sudoku;
using namespace std::chrono_literals;

namespace
{

    const std::string STANDARD_PUZZLE =
        "530070000"
        "600195000"
        "098000060"
        "800060003"
        "400803001"
        "700020006"
        "060000280"
        "000419005"
        "000080079";

    const std::string EXPECTED_SOLUTION =
        "534678912"
        "672195348"
        "198342567"
        "859761423"
        "426853791"
        "713924856"
        "961537284"
        "287419635"
        "345286179";

} // namespace

TEST(A1Test, SolvesStandardSudoku)
{
    Board board = parse_grid(STANDARD_PUZZLE);

    SolverResult result = solve_a1(board);

    EXPECT_EQ(result.status, SolverStatus::UNIQUE);
    EXPECT_EQ(result.solution_count, 1);
    ASSERT_EQ(result.solutions.size(), 1);

    EXPECT_EQ(
        serialize_grid(result.solutions[0]),
        EXPECTED_SOLUTION);
}

TEST(A1Test, PreservesOriginalBoard)
{
    Board board = parse_grid(STANDARD_PUZZLE);
    const Board original = board;

    solve_a1(board);

    EXPECT_EQ(board, original);
}

TEST(A1Test, DetectsUnsolvablePuzzle)
{
    std::string grid = STANDARD_PUZZLE;

    // This clue is conflict-free but makes the puzzle unsolvable.
    grid[2] = '1';

    Board board = parse_grid(grid);

    ASSERT_TRUE(validate_board(board).empty());

    SolverResult result = solve_a1(board);

    EXPECT_EQ(result.status, SolverStatus::UNSOLVABLE);
    EXPECT_EQ(result.solution_count, 0);
    EXPECT_TRUE(result.solutions.empty());
}

TEST(A1Test, HandlesAlreadySolvedBoard)
{
    Board board = parse_grid(EXPECTED_SOLUTION);

    SolverResult result = solve_a1(board);

    EXPECT_EQ(result.status, SolverStatus::ALREADY_SOLVED);
    EXPECT_EQ(result.solution_count, 1);
    ASSERT_EQ(result.solutions.size(), 1);
    EXPECT_EQ(result.solutions[0], board);
}

TEST(A1Test, RejectsInvalidBoard)
{
    Board board = parse_grid(STANDARD_PUZZLE);

    board[0][0] = 5;
    board[0][1] = 5;

    SolverResult result = solve_a1(board);

    EXPECT_EQ(result.status, SolverStatus::INVALID);
    EXPECT_EQ(result.solution_count, 0);
    EXPECT_TRUE(result.solutions.empty());
}

TEST(A1Test, FindsMultipleSolutions)
{
    Board board{};

    SolverOptions options;
    options.timeout = 10ms;

    SolverResult result = solve_a1(board, options);

    EXPECT_EQ(result.status, SolverStatus::MULTIPLE);
    EXPECT_GE(result.solution_count, 2);
    EXPECT_TRUE(result.timed_out || result.solution_count >= 2);
}

TEST(A1Test, LimitsStoredSolutionsToFifteen)
{
    Board board{};

    SolverOptions options;
    options.timeout = 10ms;

    SolverResult result = solve_a1(board, options);

    EXPECT_LE(result.solutions.size(), MAX_STORED_SOLUTIONS);
    EXPECT_GE(result.solution_count, result.solutions.size());
    EXPECT_FALSE(result.count_capped);
}

TEST(A1Test, RecordsSearchMetrics)
{
    Board board = parse_grid(STANDARD_PUZZLE);

    SolverResult result = solve_a1(board);

    EXPECT_GT(result.nodes_visited, 0);
    EXPECT_GE(result.backtracks, 0);
    EXPECT_GE(result.time_ms, 0.0);
    EXPECT_EQ(result.algorithm, "A1");
}

TEST(A1Test, HandlesTimeoutBeforeFindingSolution)
{
    const std::string grid =
        "000000000"
        "000003085"
        "001020000"
        "000507000"
        "004000100"
        "090000000"
        "500000073"
        "002010000"
        "000040009";

    Board board = parse_grid(grid);

    SolverOptions options;
    options.timeout = 1ms;

    SolverResult result = solve_a1(board, options);

    EXPECT_EQ(result.status, SolverStatus::TIMEOUT);
    EXPECT_TRUE(result.timed_out);
    EXPECT_EQ(result.solution_count, 0);
    EXPECT_TRUE(result.solutions.empty());
}

TEST(A1Test, EveryStoredSolutionIsValid)
{
    Board board{};

    SolverOptions options;
    options.timeout = 10ms;

    SolverResult result = solve_a1(board, options);

    for (const auto &solution : result.solutions)
    {
        EXPECT_TRUE(validate_board(solution).empty());
    }
}