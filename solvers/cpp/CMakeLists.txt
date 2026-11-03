cmake_minimum_required(VERSION 3.20)

project(SudokuSolvers
    VERSION 1.0.0
    LANGUAGES CXX
)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Compiler warnings
if(MSVC)
    add_compile_options(/W4 /WX)
else()
    add_compile_options(-Wall -Wextra -Wpedantic -Werror)
endif()

include(FetchContent)

FetchContent_Declare(
    nlohmann_json
    URL https://github.com/nlohmann/json/releases/download/v3.12.0/json.tar.xz
    DOWNLOAD_EXTRACT_TIMESTAMP TRUE
)

FetchContent_MakeAvailable(nlohmann_json)

# Shared Sudoku solver library
add_library(sudoku_core STATIC
    src/parser.cpp
    src/validator.cpp
    src/algorithms/a1.cpp
    src/algorithms/a2.cpp
    src/algorithms/a3.cpp
    src/algorithms/a4.cpp
)

target_include_directories(sudoku_core
    PUBLIC
        ${CMAKE_CURRENT_SOURCE_DIR}/include
)

# Testing
include(CTest)

if(BUILD_TESTING)
    add_subdirectory(tests)
endif()