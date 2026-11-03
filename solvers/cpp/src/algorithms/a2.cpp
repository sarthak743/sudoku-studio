
#include "sudoku/solver.hpp"
#include "sudoku/validator.hpp"

#include <algorithm>
#include <array>
#include <chrono>
#include <cstdint>
#include <string>

namespace sudoku
{

    namespace
    {

        using Mask = std::uint16_t;

        constexpr Mask FULL_MASK = 0x03FE;

        int get_box(int row, int col)
        {
            return (row / BOX_SIZE) * BOX_SIZE + (col / BOX_SIZE);
        }

        Mask get_digit_mask(int digit)
        {
            return static_cast<Mask>(1U << digit);
        }

        class A2Search
        {
        public:
            A2Search(
                Board &board,
                SolverResult &result,
                const SolverOptions &options)
                : board_(board),
                  result_(result),
                  deadline_(
                      std::chrono::steady_clock::now() + options.timeout),
                  max_solutions_(
                      std::min(
                          options.max_stored_solutions,
                          static_cast<std::size_t>(MAX_STORED_SOLUTIONS)))
            {
                initialize_masks();
            }

            void run()
            {
                search();
            }

            bool timed_out() const
            {
                return timed_out_;
            }

        private:
            Board &board_;
            SolverResult &result_;

            std::array<Mask, GRID_SIZE> row_masks_{};
            std::array<Mask, GRID_SIZE> col_masks_{};
            std::array<Mask, GRID_SIZE> box_masks_{};

            std::chrono::steady_clock::time_point deadline_;
            std::size_t max_solutions_;
            bool timed_out_ = false;

            void initialize_masks()
            {
                for (int row = 0; row < GRID_SIZE; ++row)
                {
                    for (int col = 0; col < GRID_SIZE; ++col)
                    {
                        const int digit = board_[row][col];

                        if (digit == 0)
                        {
                            continue;
                        }

                        const Mask bit = get_digit_mask(digit);
                        const int box = get_box(row, col);

                        row_masks_[row] |= bit;
                        col_masks_[col] |= bit;
                        box_masks_[box] |= bit;
                    }
                }
            }

            Mask candidates(int row, int col) const
            {
                const int box = get_box(row, col);

                return static_cast<Mask>(
                    FULL_MASK &
                    ~(row_masks_[row] |
                      col_masks_[col] |
                      box_masks_[box]));
            }

            bool check_timeout()
            {
                if (result_.nodes_visited % 1024 != 0)
                {
                    return false;
                }

                if (std::chrono::steady_clock::now() >= deadline_)
                {
                    timed_out_ = true;
                    return true;
                }

                return false;
            }

            void search()
            {
                if (timed_out_)
                {
                    return;
                }

                ++result_.nodes_visited;

                if (check_timeout())
                {
                    return;
                }

                // Find the first empty cell in row-major order.
                int target_row = -1;
                int target_col = -1;

                for (int row = 0; row < GRID_SIZE; ++row)
                {
                    for (int col = 0; col < GRID_SIZE; ++col)
                    {
                        if (board_[row][col] == 0)
                        {
                            target_row = row;
                            target_col = col;
                            break;
                        }
                    }

                    if (target_row != -1)
                    {
                        break;
                    }
                }

                // No empty cells: one complete solution found.
                if (target_row == -1)
                {
                    ++result_.solution_count;

                    if (result_.solutions.size() < max_solutions_)
                    {
                        result_.solutions.push_back(board_);
                    }

                    return;
                }

                const int row = target_row;
                const int col = target_col;
                const int box = get_box(row, col);

                const Mask available = candidates(row, col);

                // Try digits in ascending order.
                for (int digit = 1; digit <= 9; ++digit)
                {
                    const Mask bit = get_digit_mask(digit);

                    if ((available & bit) == 0)
                    {
                        continue;
                    }

                    const std::size_t previous_count =
                        result_.solution_count;

                    // Place the digit and update all three masks.
                    board_[row][col] = digit;
                    row_masks_[row] |= bit;
                    col_masks_[col] |= bit;
                    box_masks_[box] |= bit;

                    search();

                    // Always restore state, even after timeout.
                    board_[row][col] = 0;
                    row_masks_[row] &= static_cast<Mask>(~bit);
                    col_masks_[col] &= static_cast<Mask>(~bit);
                    box_masks_[box] &= static_cast<Mask>(~bit);

                    if (result_.solution_count == previous_count)
                    {
                        ++result_.backtracks;
                    }

                    if (timed_out_)
                    {
                        return;
                    }
                }
            }
        };

    } // namespace

    SolverResult solve_a2(
        const Board &board,
        const SolverOptions &options)
    {
        SolverResult result{};
        result.algorithm = "A2";

        // Reject conflicting or out-of-range givens.
        if (!validate_board(board).empty())
        {
            result.status = SolverStatus::INVALID;
            return result;
        }

        Board working_board = board;

        // Check whether the puzzle is already complete.
        bool has_empty_cell = false;

        for (const auto &row : board)
        {
            for (const int value : row)
            {
                if (value == 0)
                {
                    has_empty_cell = true;
                    break;
                }
            }

            if (has_empty_cell)
            {
                break;
            }
        }

        if (!has_empty_cell)
        {
            result.status = SolverStatus::ALREADY_SOLVED;
            result.solution_count = 1;
            result.solutions.push_back(board);
            return result;
        }

        const auto start = std::chrono::steady_clock::now();

        A2Search search(
            working_board,
            result,
            options);

        search.run();

        const auto end = std::chrono::steady_clock::now();

        result.time_ms =
            std::chrono::duration<double, std::milli>(
                end - start)
                .count();

        result.timed_out = search.timed_out();

        if (result.timed_out)
        {
            result.status =
                result.solution_count >= 2
                    ? SolverStatus::MULTIPLE
                    : SolverStatus::TIMEOUT;
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
