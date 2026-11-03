#include "sudoku/solver.hpp"

#include "sudoku/validator.hpp"

#include <algorithm>
#include <chrono>
#include <functional>
#include <string>

namespace sudoku
{
    namespace
    {

        bool is_valid_placement(
            const Board &board,
            int row,
            int col,
            int digit)
        {
            for (int i = 0; i < GRID_SIZE; ++i)
            {
                if (board[row][i] == digit || board[i][col] == digit)
                {
                    return false;
                }
            }

            const int box_row = (row / BOX_SIZE) * BOX_SIZE;
            const int box_col = (col / BOX_SIZE) * BOX_SIZE;

            for (int r = box_row; r < box_row + BOX_SIZE; ++r)
            {
                for (int c = box_col; c < box_col + BOX_SIZE; ++c)
                {
                    if (board[r][c] == digit)
                    {
                        return false;
                    }
                }
            }

            return true;
        }

    } // namespace

    SolverResult solve_a1(
        const Board &original_board,
        const SolverOptions &options)
    {
        SolverResult result{};
        result.algorithm = "A1";

        // Validate the original board before starting the deadline.
        if (!validate_board(original_board).empty())
        {
            result.status = SolverStatus::INVALID;
            return result;
        }

        Board board = original_board;

        // Handle an already completed valid board.
        bool already_solved = true;

        for (const auto &row : board)
        {
            if (std::find(row.begin(), row.end(), 0) != row.end())
            {
                already_solved = false;
                break;
            }
        }

        if (already_solved)
        {
            result.status = SolverStatus::ALREADY_SOLVED;
            result.solution_count = 1;
            result.solutions.push_back(board);
            return result;
        }

        const auto start_time = std::chrono::steady_clock::now();
        const auto deadline = start_time + options.timeout;

        const std::size_t storage_limit = std::min(
            options.max_stored_solutions,
            static_cast<std::size_t>(MAX_STORED_SOLUTIONS));

        // Returns false when the search must stop.
        std::function<bool()> search = [&]() -> bool
        {
            ++result.nodes_visited;

            // Check the deadline at least once every 1024 search nodes.
            if (result.nodes_visited % 1024 == 0 &&
                std::chrono::steady_clock::now() >= deadline)
            {
                result.timed_out = true;
                return false;
            }

            // Find the first empty cell in row-major order.
            int empty_row = -1;
            int empty_col = -1;

            for (int row = 0; row < GRID_SIZE && empty_row == -1; ++row)
            {
                for (int col = 0; col < GRID_SIZE; ++col)
                {
                    if (board[row][col] == 0)
                    {
                        empty_row = row;
                        empty_col = col;
                        break;
                    }
                }
            }

            // No empty cells: a complete solution was found.
            if (empty_row == -1)
            {
                ++result.solution_count;

                if (result.solutions.size() < storage_limit)
                {
                    result.solutions.push_back(board);
                }

                return true;
            }

            // Try candidate digits in ascending order.
            for (int digit = 1; digit <= GRID_SIZE; ++digit)
            {
                if (!is_valid_placement(board, empty_row, empty_col, digit))
                {
                    continue;
                }

                board[empty_row][empty_col] = digit;

                const std::size_t previous_solution_count =
                    result.solution_count;

                const bool should_continue = search();

                // Always restore the board before returning.
                board[empty_row][empty_col] = 0;

                if (!should_continue)
                {
                    return false;
                }

                if (result.solution_count == previous_solution_count)
                {
                    ++result.backtracks;
                }
            }

            return true;
        };

        search();

        const auto end_time = std::chrono::steady_clock::now();

        result.time_ms =
            std::chrono::duration<double, std::milli>(
                end_time - start_time)
                .count();

        // Classify the final result.
        if (result.timed_out && result.solution_count < 2)
        {
            result.status = SolverStatus::TIMEOUT;
        }
        else if (result.solution_count == 0)
        {
            result.status = SolverStatus::UNSOLVABLE;
        }
        else if (result.solution_count == 1)
        {
            result.status = SolverStatus::UNIQUE;
        }
        else
        {
            result.status = SolverStatus::MULTIPLE;
        }

        return result;
    }

} // namespace sudoku