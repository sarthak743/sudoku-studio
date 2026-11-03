include(FetchContent)

FetchContent_Declare(
    googletest
    URL https://github.com/google/googletest/archive/refs/tags/v1.17.0.zip
    DOWNLOAD_EXTRACT_TIMESTAMP TRUE
)

set(gtest_force_shared_crt ON CACHE BOOL "" FORCE)

FetchContent_MakeAvailable(googletest)

add_executable(sudoku_tests
    test_parser.cpp
    test_validator.cpp
    test_a1.cpp
    test_a1_fixtures.cpp
    test_a2.cpp
    test_a3.cpp
    test_a4.cpp
    test_cross_algorithm.cpp
)

target_compile_definitions(sudoku_tests PRIVATE
    SUDOKU_PROJECT_ROOT="${CMAKE_CURRENT_SOURCE_DIR}/../../.."
)

target_link_libraries(sudoku_tests
    PRIVATE
        sudoku_core
        GTest::gtest_main
        nlohmann_json::nlohmann_json
)

include(GoogleTest)
gtest_discover_tests(sudoku_tests)