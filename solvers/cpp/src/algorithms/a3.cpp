
#include "sudoku/solver.hpp"
#include "sudoku/validator.hpp"

#include <algorithm>
#include <array>
#include <chrono>
#include <cstdint>
#include <bit>

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

        class A3Search
        {
        public:
            A3Search(
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

            int count_candidates(Mask mask) const
            {
                return std::popcount(mask);
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

                int best_row = -1;
                int best_col = -1;
                Mask best_candidates = 0;
                int minimum_candidates = 10;

                // MRV: choose the empty cell with the fewest candidates.
                // Row-major scanning naturally breaks ties.
                for (int row = 0; row < GRID_SIZE; ++row)
                {
                    for (int col = 0; col < GRID_SIZE; ++col)
                    {
                        if (board_[row][col] != 0)
                        {
                            continue;
                        }

                        const Mask available = candidates(row, col);
                        const int candidate_count =
                            count_candidates(available);

                        if (candidate_count == 0)
                        {
                            ++result_.backtracks;
                            return;
                        }

                        if (candidate_count < minimum_candidates)
                        {
                            minimum_candidates = candidate_count;
                            best_row = row;
                            best_col = col;
                            best_candidates = available;
                        }
                    }
                }

                // No empty cell means a complete solution.
                if (best_row == -1)
                {
                    ++result_.solution_count;

                    if (result_.solutions.size() < max_solutions_)
                    {
                        result_.solutions.push_back(board_);
                    }

                    return;
                }

                const int box = get_box(best_row, best_col);

                // Try candidates in ascending order.
                for (int digit = 1; digit <= 9; ++digit)
                {
                    const Mask bit = get_digit_mask(digit);

                    if ((best_candidates & bit) == 0)
                    {
                        continue;
                    }

                    const std::size_t previous_count =
                        result_.solution_count;

                    board_[best_row][best_col] = digit;
                    row_masks_[best_row] |= bit;
                    col_masks_[best_col] |= bit;
                    box_masks_[box] |= bit;

                    search();

                    // Restore board and masks.
                    board_[best_row][best_col] = 0;
                    row_masks_[best_row] &= static_cast<Mask>(~bit);
                    col_masks_[best_col] &= static_cast<Mask>(~bit);
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

    SolverResult solve_a3(
        const Board &board,
        const SolverOptions &options)
    {
        SolverResult result{};
        result.algorithm = "A3";

        if (!validate_board(board).empty())
        {
            result.status = SolverStatus::INVALID;
            return result;
        }

        Board working_board = board;

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

        A3Search search(working_board, result, options);
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
