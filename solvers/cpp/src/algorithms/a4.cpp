
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

        using MaskArray = std::array<Mask, GRID_SIZE>;

        struct SearchState
        {
            Board board{};
            MaskArray row_masks{};
            MaskArray col_masks{};
            MaskArray box_masks{};
        };

        int get_box(int row, int col)
        {
            return (row / BOX_SIZE) * BOX_SIZE + (col / BOX_SIZE);
        }

        Mask get_digit_mask(int digit)
        {
            return static_cast<Mask>(1U << digit);
        }

        Mask candidates(const SearchState &state, int row, int col)
        {
            const int box = get_box(row, col);

            return static_cast<Mask>(
                FULL_MASK &
                ~(state.row_masks[row] |
                  state.col_masks[col] |
                  state.box_masks[box]));
        }

        int count_candidates(Mask mask)
        {
            return std::popcount(mask);
        }

        void place_digit(
            SearchState &state,
            int row,
            int col,
            int digit)
        {
            const Mask bit = get_digit_mask(digit);
            const int box = get_box(row, col);

            state.board[row][col] = digit;
            state.row_masks[row] |= bit;
            state.col_masks[col] |= bit;
            state.box_masks[box] |= bit;
        }

        // Initialize occupancy masks from the original board.
        void initialize_masks(SearchState &state)
        {
            for (int row = 0; row < GRID_SIZE; ++row)
            {
                for (int col = 0; col < GRID_SIZE; ++col)
                {
                    const int digit = state.board[row][col];

                    if (digit == 0)
                    {
                        continue;
                    }

                    const Mask bit = get_digit_mask(digit);
                    const int box = get_box(row, col);

                    state.row_masks[row] |= bit;
                    state.col_masks[col] |= bit;
                    state.box_masks[box] |= bit;
                }
            }
        }

        // Apply the first available naked single.
        // Returns true if a digit was assigned.
        bool apply_naked_single(
            SearchState &state,
            bool &contradiction)
        {
            for (int row = 0; row < GRID_SIZE; ++row)
            {
                for (int col = 0; col < GRID_SIZE; ++col)
                {
                    if (state.board[row][col] != 0)
                    {
                        continue;
                    }

                    const Mask available =
                        candidates(state, row, col);

                    const int count = count_candidates(available);

                    if (count == 0)
                    {
                        contradiction = true;
                        return false;
                    }

                    if (count == 1)
                    {
                        for (int digit = 1; digit <= 9; ++digit)
                        {
                            if ((available & get_digit_mask(digit)) != 0)
                            {
                                place_digit(state, row, col, digit);
                                return true;
                            }
                        }
                    }
                }
            }

            return false;
        }

        // Find and apply the first hidden single in a unit.
        // unit_type: 0 = row, 1 = column, 2 = box.
        bool apply_hidden_single(
            SearchState &state,
            int unit_type,
            int unit_index,
            bool &contradiction)
        {
            for (int digit = 1; digit <= 9; ++digit)
            {
                const Mask bit = get_digit_mask(digit);

                Mask occupied = 0;

                if (unit_type == 0)
                {
                    occupied = state.row_masks[unit_index];
                }
                else if (unit_type == 1)
                {
                    occupied = state.col_masks[unit_index];
                }
                else
                {
                    occupied = state.box_masks[unit_index];
                }

                if ((occupied & bit) != 0)
                {
                    continue;
                }

                int candidate_count = 0;
                int candidate_row = -1;
                int candidate_col = -1;

                for (int offset = 0; offset < GRID_SIZE; ++offset)
                {
                    int row = 0;
                    int col = 0;

                    if (unit_type == 0)
                    {
                        row = unit_index;
                        col = offset;
                    }
                    else if (unit_type == 1)
                    {
                        row = offset;
                        col = unit_index;
                    }
                    else
                    {
                        const int box_row =
                            (unit_index / BOX_SIZE) * BOX_SIZE;

                        const int box_col =
                            (unit_index % BOX_SIZE) * BOX_SIZE;

                        row = box_row + offset / BOX_SIZE;
                        col = box_col + offset % BOX_SIZE;
                    }

                    if (state.board[row][col] != 0)
                    {
                        continue;
                    }

                    if ((candidates(state, row, col) & bit) != 0)
                    {
                        ++candidate_count;
                        candidate_row = row;
                        candidate_col = col;
                    }
                }

                if (candidate_count == 0)
                {
                    contradiction = true;
                    return false;
                }

                if (candidate_count == 1)
                {
                    place_digit(
                        state,
                        candidate_row,
                        candidate_col,
                        digit);

                    return true;
                }
            }

            return false;
        }

        // Apply propagation until a fixed point is reached.
        bool propagate(SearchState &state)
        {
            while (true)
            {
                bool contradiction = false;

                // 1. Naked singles, row-major.
                if (apply_naked_single(state, contradiction))
                {
                    continue;
                }

                if (contradiction)
                {
                    return false;
                }

                // 2. Hidden singles in rows.
                bool assigned = false;

                for (int row = 0; row < GRID_SIZE; ++row)
                {
                    if (apply_hidden_single(
                            state, 0, row, contradiction))
                    {
                        assigned = true;
                        break;
                    }

                    if (contradiction)
                    {
                        return false;
                    }
                }

                if (assigned)
                {
                    continue;
                }

                // 3. Hidden singles in columns.
                for (int col = 0; col < GRID_SIZE; ++col)
                {
                    if (apply_hidden_single(
                            state, 1, col, contradiction))
                    {
                        assigned = true;
                        break;
                    }

                    if (contradiction)
                    {
                        return false;
                    }
                }

                if (assigned)
                {
                    continue;
                }

                // 4. Hidden singles in boxes.
                for (int box = 0; box < GRID_SIZE; ++box)
                {
                    if (apply_hidden_single(
                            state, 2, box, contradiction))
                    {
                        assigned = true;
                        break;
                    }

                    if (contradiction)
                    {
                        return false;
                    }
                }

                if (assigned)
                {
                    continue;
                }

                // No more assignments: propagation reached a fixed point.
                return true;
            }
        }

        class A4Search
        {
        public:
            A4Search(
                SolverResult &result,
                const SolverOptions &options)
                : result_(result),
                  deadline_(
                      std::chrono::steady_clock::now() + options.timeout),
                  max_solutions_(
                      std::min(
                          options.max_stored_solutions,
                          static_cast<std::size_t>(MAX_STORED_SOLUTIONS)))
            {
            }

            void run(SearchState state)
            {
                search(state);
            }

            bool timed_out() const
            {
                return timed_out_;
            }

        private:
            SolverResult &result_;

            std::chrono::steady_clock::time_point deadline_;
            std::size_t max_solutions_;
            bool timed_out_ = false;

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

            void search(SearchState &state)
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

                // Propagate before branching.
                if (!propagate(state))
                {
                    ++result_.backtracks;
                    return;
                }

                int best_row = -1;
                int best_col = -1;
                int minimum_candidates = 10;
                Mask best_candidates = 0;

                // MRV with row-major tie-breaking.
                for (int row = 0; row < GRID_SIZE; ++row)
                {
                    for (int col = 0; col < GRID_SIZE; ++col)
                    {
                        if (state.board[row][col] != 0)
                        {
                            continue;
                        }

                        const Mask available =
                            candidates(state, row, col);

                        const int count = count_candidates(available);

                        if (count == 0)
                        {
                            ++result_.backtracks;
                            return;
                        }

                        if (count < minimum_candidates)
                        {
                            minimum_candidates = count;
                            best_row = row;
                            best_col = col;
                            best_candidates = available;
                        }
                    }
                }

                // No empty cells: solution found.
                if (best_row == -1)
                {
                    ++result_.solution_count;

                    if (result_.solutions.size() < max_solutions_)
                    {
                        result_.solutions.push_back(state.board);
                    }

                    return;
                }

                // Branch using ascending candidate digits.
                for (int digit = 1; digit <= 9; ++digit)
                {
                    const Mask bit = get_digit_mask(digit);

                    if ((best_candidates & bit) == 0)
                    {
                        continue;
                    }

                    SearchState child = state;

                    place_digit(
                        child,
                        best_row,
                        best_col,
                        digit);

                    const std::size_t previous_count =
                        result_.solution_count;

                    search(child);

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

    SolverResult solve_a4(
        const Board &board,
        const SolverOptions &options)
    {
        SolverResult result{};
        result.algorithm = "A4";

        if (!validate_board(board).empty())
        {
            result.status = SolverStatus::INVALID;
            return result;
        }

        SearchState state;
        state.board = board;

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

        initialize_masks(state);

        const auto start = std::chrono::steady_clock::now();

        A4Search search(result, options);
        search.run(state);

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
