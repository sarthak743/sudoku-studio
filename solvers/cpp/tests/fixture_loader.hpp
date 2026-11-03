#pragma once

#ifndef SUDOKU_PROJECT_ROOT
#define SUDOKU_PROJECT_ROOT "."
#endif

#include <nlohmann/json.hpp>

#include <fstream>
#include <stdexcept>
#include <string>
#include <vector>

namespace sudoku::test
{

    using json = nlohmann::json;

    inline json load_edge_cases()
    {
        const std::string path =
            std::string(SUDOKU_PROJECT_ROOT) +
            "/data/puzzles/edge_cases.json";

        std::ifstream file(path);

        if (!file.is_open())
        {
            throw std::runtime_error(
                "Could not open edge_cases.json: " + path);
        }

        json fixtures;
        file >> fixtures;

        if (!fixtures.is_array())
        {
            throw std::runtime_error(
                "Edge-case fixture file must contain a JSON array.");
        }

        return fixtures;
    }

} // namespace sudoku::test