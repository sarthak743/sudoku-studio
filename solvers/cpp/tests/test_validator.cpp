#include "sudoku/parser.hpp"
#include "sudoku/validator.hpp"

#include <gtest/gtest.h>

using namespace sudoku;

TEST(ValidatorTest, AcceptsValidIncompleteBoard)
{
    const std::string grid =
        "530070000"
        "600195000"
        "098000060"
        "800060003"
        "400803001"
        "700020006"
        "060000280"
        "000419005"
        "000080079";

    EXPECT_TRUE(validate_input(grid));
}

TEST(ValidatorTest, DetectsRowConflict)
{
    Board board{};
    board[0][0] = 5;
    board[0][1] = 5;

    const auto conflicts = find_row_conflicts(board);

    EXPECT_EQ(conflicts.size(), 1);
    EXPECT_EQ(conflicts[0], (CellPosition{0, 1}));
}

TEST(ValidatorTest, DetectsColumnConflict)
{
    Board board{};
    board[0][0] = 5;
    board[1][0] = 5;

    const auto conflicts = find_column_conflicts(board);

    EXPECT_EQ(conflicts.size(), 1);
    EXPECT_EQ(conflicts[0], (CellPosition{1, 0}));
}

TEST(ValidatorTest, DetectsBoxConflict)
{
    Board board{};
    board[0][0] = 5;
    board[1][1] = 5;

    const auto conflicts = find_box_conflicts(board);

    EXPECT_EQ(conflicts.size(), 1);
    EXPECT_EQ(conflicts[0], (CellPosition{1, 1}));
}

TEST(ValidatorTest, IgnoresEmptyCells)
{
    Board board{};

    EXPECT_TRUE(validate_board(board).empty());
}

TEST(ValidatorTest, DetectsCombinedConflicts)
{
    Board board{};
    board[0][0] = 5;
    board[0][1] = 5;
    board[1][0] = 5;

    const auto conflicts = validate_board(board);

    EXPECT_EQ(conflicts.size(), 2);
}

TEST(ValidatorTest, RejectsInvalidInput)
{
    EXPECT_FALSE(validate_input("12345"));
}

TEST(ValidatorTest, ClassifiesCompletedValidBoard)
{
    const std::string solved =
        "534678912"
        "672195348"
        "198342567"
        "859761423"
        "426853791"
        "713924856"
        "961537284"
        "287419635"
        "345286179";

    EXPECT_EQ(
        classify_completed_grid(parse_grid(solved)),
        SolverStatus::ALREADY_SOLVED);
}

TEST(ValidatorTest, ClassifiesIncompleteBoard)
{
    Board board{};

    EXPECT_EQ(
        classify_completed_grid(board),
        SolverStatus::INVALID);
}