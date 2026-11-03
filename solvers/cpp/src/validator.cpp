#include "sudoku/validator.hpp"

#include "sudoku/parser.hpp"

#include <algorithm>
#include <array>
#include <set>

namespace sudoku
{

    std::vector<CellPosition> find_row_conflicts(const Board &board)
    {
        std::set<CellPosition> conflicts;

        for (int row = 0; row < GRID_SIZE; ++row)
        {
            std::array<int, 10> counts{};

            for (int col = 0; col < GRID_SIZE; ++col)
            {
                int value = board[row][col];

                if (value == 0)
                {
                    continue;
                }

                if (value < 1 || value > 9 || ++counts[value] > 1)
                {
                    conflicts.emplace(row, col);
                }
            }
        }

        return {conflicts.begin(), conflicts.end()};
    }

    std::vector<CellPosition> find_column_conflicts(const Board &board)
    {
        std::set<CellPosition> conflicts;

        for (int col = 0; col < GRID_SIZE; ++col)
        {
            std::array<int, 10> counts{};

            for (int row = 0; row < GRID_SIZE; ++row)
            {
                int value = board[row][col];

                if (value == 0)
                {
                    continue;
                }

                if (value < 1 || value > 9 || ++counts[value] > 1)
                {
                    conflicts.emplace(row, col);
                }
            }
        }

        return {conflicts.begin(), conflicts.end()};
    }

    std::vector<CellPosition> find_box_conflicts(const Board &board)
    {
        std::set<CellPosition> conflicts;

        for (int box_row = 0; box_row < GRID_SIZE; box_row += BOX_SIZE)
        {
            for (int box_col = 0; box_col < GRID_SIZE; box_col += BOX_SIZE)
            {
                std::array<int, 10> counts{};

                for (int row = box_row; row < box_row + BOX_SIZE; ++row)
                {
                    for (int col = box_col; col < box_col + BOX_SIZE; ++col)
                    {
                        int value = board[row][col];

                        if (value == 0)
                        {
                            continue;
                        }

                        if (value < 1 || value > 9 || ++counts[value] > 1)
                        {
                            conflicts.emplace(row, col);
                        }
                    }
                }
            }
        }

        return {conflicts.begin(), conflicts.end()};
    }

    std::vector<CellPosition> validate_board(const Board &board)
    {
        std::set<CellPosition> conflicts;

        for (const auto &position : find_row_conflicts(board))
        {
            conflicts.insert(position);
        }

        for (const auto &position : find_column_conflicts(board))
        {
            conflicts.insert(position);
        }

        for (const auto &position : find_box_conflicts(board))
        {
            conflicts.insert(position);
        }

        return {conflicts.begin(), conflicts.end()};
    }

    bool validate_input(const std::string &grid)
    {
        if (!validate_format(grid))
        {
            return false;
        }

        return validate_board(parse_grid(grid)).empty();
    }

    SolverStatus classify_completed_grid(const Board &board)
    {
        if (!validate_board(board).empty())
        {
            return SolverStatus::INVALID;
        }

        for (const auto &row : board)
        {
            if (std::find(row.begin(), row.end(), 0) != row.end())
            {
                return SolverStatus::INVALID;
            }
        }

        return SolverStatus::ALREADY_SOLVED;
    }

} // namespace sudoku