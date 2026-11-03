#include "sudoku/parser.hpp"

#include <stdexcept>

namespace sudoku
{

    bool validate_format(const std::string &grid)
    {
        if (grid.size() != 81)
        {
            return false;
        }

        for (char ch : grid)
        {
            if (ch != '.' && (ch < '0' || ch > '9'))
            {
                return false;
            }
        }

        return true;
    }

    Board parse_grid(const std::string &grid)
    {
        if (!validate_format(grid))
        {
            throw std::invalid_argument("Invalid Sudoku grid format.");
        }

        Board board{};

        for (std::size_t i = 0; i < grid.size(); ++i)
        {
            char ch = grid[i];

            board[i / 9][i % 9] =
                (ch == '.' || ch == '0') ? 0 : ch - '0';
        }

        return board;
    }

    std::string serialize_grid(const Board &board)
    {
        std::string result;
        result.reserve(81);

        for (const auto &row : board)
        {
            for (int value : row)
            {
                if (value < 0 || value > 9)
                {
                    throw std::invalid_argument("Invalid Sudoku cell value.");
                }

                result += (value == 0)
                              ? '.'
                              : static_cast<char>('0' + value);
            }
        }

        return result;
    }

} // namespace sudoku