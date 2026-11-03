
#include "fixture_loader.hpp"
#include "sudoku/parser.hpp"
#include "sudoku/solver.hpp"
#include "sudoku/validator.hpp"

#include <algorithm>
#include <chrono>
#include <string>
#include <vector>

#include <gtest/gtest.h>

const std::string algorithm_name = "A4";

namespace
{

    using sudoku::Board;
    using sudoku::SolverResult;
    using sudoku::SolverStatus;
    using sudoku::test::json;

    std::string status_to_string(SolverStatus status)
    {
        switch (status)
        {
        case SolverStatus::INVALID_FORMAT:
            return "invalid_format";
        case SolverStatus::INVALID:
            return "invalid";
        case SolverStatus::ALREADY_SOLVED:
            return "already_solved";
        case SolverStatus::UNSOLVABLE:
            return "unsolvable";
        case SolverStatus::UNIQUE:
            return "unique";
        case SolverStatus::MULTIPLE:
            return "multiple";
        case SolverStatus::TIMEOUT:
            return "timeout";
        }

        return "unknown";
    }

    bool includes_algorithm(const json &fixture)
    {
        const std::vector<std::string> default_algorithms = {
            "A1", "A2", "A3", "A4"};

        const auto supported_algorithms =
            fixture.value("algorithms", default_algorithms);

        return std::find(
                   supported_algorithms.begin(),
                   supported_algorithms.end(),
                   algorithm_name) != supported_algorithms.end();
    }

    void verify_solution(
        const Board &original,
        const Board &solution)
    {
        // Every solution must be a valid completed Sudoku.
        EXPECT_TRUE(sudoku::validate_board(solution).empty());

        for (int row = 0; row < sudoku::GRID_SIZE; ++row)
        {
            for (int col = 0; col < sudoku::GRID_SIZE; ++col)
            {
                EXPECT_NE(solution[row][col], 0);

                // Original clues must never change.
                if (original[row][col] != 0)
                {
                    EXPECT_EQ(
                        solution[row][col],
                        original[row][col]);
                }
            }
        }
    }

} // namespace

TEST(A4Fixtures, MatchesOfficialEdgeCases)
{
    const json fixtures = sudoku::test::load_edge_cases();

    for (const auto &fixture : fixtures)
    {
        if (!includes_algorithm(fixture))
        {
            continue;
        }

        const std::string id = fixture.at("id").get<std::string>();

        SCOPED_TRACE("Fixture: " + id);

        const std::string grid =
            fixture.at("grid").get<std::string>();

        // Start with the global fixture expectations.
        json expectations = fixture;

        // Override them if this algorithm has specific expectations.
        if (fixture.contains("expected_by_algorithm") &&
            fixture["expected_by_algorithm"].contains(algorithm_name))
        {
            expectations = fixture["expected_by_algorithm"][algorithm_name];
        }

        const std::string expected_status =
            expectations.at("expected_status").get<std::string>();

        const std::string count_type =
            expectations.at("count_type").get<std::string>();

        const int deadline_ms =
            fixture.value("deadline_ms", 10'000);

        // Validate the external grid format first.
        if (!sudoku::validate_format(grid))
        {
            EXPECT_EQ(expected_status, "invalid_format");
            continue;
        }

        const Board board = sudoku::parse_grid(grid);

        sudoku::SolverOptions options;
        options.timeout = std::chrono::milliseconds(deadline_ms);

        const SolverResult result =
            sudoku::solve_a4(board, options);

        // Check the expected result status.
        const std::string actual_status =
            status_to_string(result.status);

        if (expectations.contains("acceptable_statuses"))
        {
            const auto acceptable_statuses =
                expectations.at("acceptable_statuses")
                    .get<std::vector<std::string>>();

            EXPECT_NE(
                std::find(
                    acceptable_statuses.begin(),
                    acceptable_statuses.end(),
                    actual_status),
                acceptable_statuses.end());
        }
        else
        {
            EXPECT_EQ(actual_status, expected_status);
        }

        // Common result contract.
        EXPECT_FALSE(result.count_capped);
        EXPECT_LE(
            result.solutions.size(),
            sudoku::MAX_STORED_SOLUTIONS);

        EXPECT_GE(result.nodes_visited, 0);
        EXPECT_GE(result.backtracks, 0);
        EXPECT_GE(result.time_ms, 0.0);

        EXPECT_EQ(result.algorithm, algorithm_name);

        // Verify solution counts.
        if (count_type == "exact")
        {
            const std::size_t expected_count =
                expectations.at("expected_solution_count")
                    .get<std::size_t>();

            EXPECT_EQ(result.solution_count, expected_count);
        }
        else if (count_type == "lower_bound")
        {
            const std::size_t minimum_count =
                fixture.at("expected_solution_count")
                    .get<std::size_t>();

            EXPECT_GE(result.solution_count, minimum_count);
        }
        else
        {
            EXPECT_EQ(count_type, "not_applicable");
        }

        // Timeout fixtures must report interruption.
        if (result.status == SolverStatus::TIMEOUT)
        {
            EXPECT_TRUE(result.timed_out);
        }

        // A timed-out search that discovers multiple solutions
        // must report multiple, not timeout.
        if (result.timed_out && result.solution_count >= 2)
        {
            EXPECT_EQ(result.status, SolverStatus::MULTIPLE);
        }

        // Every returned solution must be valid and preserve clues.
        for (const auto &solution : result.solutions)
        {
            verify_solution(board, solution);
        }
    }
}
