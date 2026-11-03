#pragma once

#include "sudoku/types.hpp"

#include <string>
#include <utility>
#include <vector>

namespace sudoku
{

    using CellPosition = std::pair<int, int>;

    std::vector<CellPosition> find_row_conflicts(const Board &board);

    std::vector<CellPosition> find_column_conflicts(const Board &board);

    std::vector<CellPosition> find_box_conflicts(const Board &board);

    std::vector<CellPosition> validate_board(const Board &board);

    bool validate_input(const std::string &grid);

    SolverStatus classify_completed_grid(const Board &board);

} // namespace sudoku