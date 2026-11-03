#include "sudoku/parser.hpp"

#include <gtest/gtest.h>

#include <stdexcept>
#include <string>

using namespace sudoku;

TEST(ParserTest, ParsesValidGrid)
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

    Board board = parse_grid(grid);

    EXPECT_EQ(board[0][0], 5);
    EXPECT_EQ(board[0][1], 3);
    EXPECT_EQ(board[0][2], 0);
    EXPECT_EQ(board[8][8], 9);
}

TEST(ParserTest, AcceptsDotsAsEmptyCells)
{
    const std::string grid =
        "53..7...."
        "6..195..."
        ".98....6."
        "8...6...3"
        "4..8.3..1"
        "7...2...6"
        ".6....28."
        "...419..5"
        "....8..79";

    Board board = parse_grid(grid);

    EXPECT_EQ(board[0][2], 0);
    EXPECT_EQ(board[0][3], 0);
}

TEST(ParserTest, RejectsIncorrectLength)
{
    EXPECT_FALSE(validate_format("12345"));
    EXPECT_THROW(parse_grid("12345"), std::invalid_argument);
}

TEST(ParserTest, RejectsUnsupportedCharacters)
{
    std::string grid(81, '0');
    grid[10] = 'X';

    EXPECT_FALSE(validate_format(grid));
    EXPECT_THROW(parse_grid(grid), std::invalid_argument);
}

TEST(ParserTest, SerializesBoardCorrectly)
{
    const std::string grid =
        "53..7...."
        "6..195..."
        ".98....6."
        "8...6...3"
        "4..8.3..1"
        "7...2...6"
        ".6....28."
        "...419..5"
        "....8..79";

    EXPECT_EQ(serialize_grid(parse_grid(grid)), grid);
}

TEST(ParserTest, RejectsInvalidCellDuringSerialization)
{
    Board board{};
    board[0][0] = 10;

    EXPECT_THROW(serialize_grid(board), std::invalid_argument);
}