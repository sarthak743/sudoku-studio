#pragma once

#include <array>
#include <chrono>
#include <cstddef>
#include <string>
#include <vector>

namespace sudoku
{

    constexpr int GRID_SIZE = 9;
    constexpr int BOX_SIZE = 3;
    constexpr int MAX_STORED_SOLUTIONS = 15;

    using Board = std::array<std::array<int, GRID_SIZE>, GRID_SIZE>;
    using Solution = Board;

    enum class SolverStatus
    {
        INVALID_FORMAT,
        INVALID,
        ALREADY_SOLVED,
        UNSOLVABLE,
        UNIQUE,
        MULTIPLE,
        TIMEOUT
    };

    struct SolverResult
    {
        SolverStatus status;
        std::size_t solution_count = 0;
        std::vector<Solution> solutions;

        bool count_capped = false;
        bool timed_out = false;

        double time_ms = 0.0;
        std::size_t nodes_visited = 0;
        std::size_t backtracks = 0;

        std::string algorithm;
    };

} // namespace sudoku