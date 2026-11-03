#pragma once

#include "sudoku/types.hpp"

#include <string>

namespace sudoku
{

    bool validate_format(const std::string &grid);

    Board parse_grid(const std::string &grid);

    std::string serialize_grid(const Board &board);

} // namespace sudoku