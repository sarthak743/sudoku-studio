#pragma once

#include "sudoku/types.hpp"

#include <chrono>
#include <cstddef>

namespace sudoku
{

    struct SolverOptions
    {
        std::chrono::milliseconds timeout{10'000};
        std::size_t max_stored_solutions = MAX_STORED_SOLUTIONS;
    };

    using SolverFunction = SolverResult (*)(
        const Board &,
        const SolverOptions &);

    // Algorithm declarations
    SolverResult solve_a1(
        const Board &board,
        const SolverOptions &options = {});

    SolverResult solve_a2(
        const Board &board,
        const SolverOptions &options = {});

    SolverResult solve_a3(
        const Board &board,
        const SolverOptions &options = {});

    SolverResult solve_a4(
        const Board &board,
        const SolverOptions &options = {});

} // namespace sudoku