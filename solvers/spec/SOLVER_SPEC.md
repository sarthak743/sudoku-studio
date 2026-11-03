# Sudoku Solver Specification

## 1. Puzzle Input Format

### 1.1 External Representation

All Sudoku puzzles must be represented as a string containing exactly 81 characters.

- Characters `1–9` represent filled cells.
- Character `0` or `.` represents an empty cell.
- Cells are ordered row-major, from left to right and top to bottom.
- The first 9 characters represent row 0, the next 9 represent row 1, and so on.

Example:

```text
530070000600195000098000060800060003400803001700020006060000280000419005000080079
```

### 1.2 Internal Representation

Each language must convert the input string into a native 9×9 two-dimensional character array before solving.

| Language | Data Structure |
|---|---|
| Python | `list[list[str]]` |
| C++ | `vector<vector<char>>` |
| Java | `char[][]` |

### 1.3 Empty Cell Representation

Internally, `.` will be used consistently across all three languages to represent empty cells.

Inputs containing `0` must normalize empty cells to `.` during parsing.

### 1.4 Input Validation

The parser must reject:

- Strings containing fewer or more than 81 characters.
- Characters other than `0`, `.`, and `1–9`.

Rule violations such as duplicate digits in a row, column or 3×3 box will be handled by the validation module, not the parser.

### 1.5 Serialization

When converting a solved board back to external representation, serialize it into the same 81-character row-major format, using digits `1–9` and no empty cells for complete solutions.

## 2. Result Statuses

### 2.1 Supported Statuses

The solver must return exactly one of the following statuses:

| Status | Meaning |
|---|---|
| `invalid_format` | Input does not contain exactly 81 valid characters. |
| `invalid` | Given digits violate Sudoku rules in a row, column or 3×3 box. |
| `already_solved` | Every cell is filled and all Sudoku rules are satisfied. |
| `unsolvable` | Input is valid, but exhaustive search finds no solution. |
| `unique` | Exactly one solution exists, confirmed by exhaustive search. |
| `multiple` | Two or more solutions have been discovered. |
| `timeout` | Search timed out before determining whether zero, one or multiple solutions exist. |

### 2.3 Enumeration Flags

The solver must expose two boolean flags:

- `count_capped`: Always `false`, because no independent solution-count cap is applied.
- `timed_out`: Indicates whether the execution deadline was reached.

Both flags must default to `false`.

### 2.4 Status Classification

For searches that finish without interruption:

- Zero solutions → `unsolvable`
- Exactly one solution → `unique`
- Two or more solutions → `multiple`

When the execution deadline is reached:

- Zero solutions found → `timeout`.
- Exactly one solution found → `timeout`, with the discovered solution returned as a partial result.
- Two or more solutions found → `multiple`, with `timed_out` set to `true`.

When the status is `timeout`, the reported solution count represents the number of solutions discovered before termination, not the exact total.

When the status is `multiple` and `timed_out` is `true`, the solution count represents a lower bound on the actual total.

The solver must never classify an interrupted search as `unique` or `unsolvable`.

## 3. Algorithm Definitions

### 3.1 Supported Algorithms

Sudoku Studio will implement exactly four core solving algorithms.

| ID | Algorithm | Description |
|---|---|---|
| A1 | Basic Backtracking | Recursive backtracking with row, column and box validity checks. |
| A2 | Bitmask Backtracking | Backtracking with bitmask-based candidate checking. |
| A3 | MRV Backtracking | Bitmask backtracking with Minimum Remaining Values cell selection. |
| A4 | Propagation + Search | Constraint propagation using naked singles and hidden singles, followed by MRV branching. |

### 3.2 Language Support

| Algorithm | Python | C++ | Java |
|---|---|---|---|
| A1 | Required | Required | Required |
| A2 | Required | Required | Required |
| A3 | Required | Required | Required |
| A4 | Required | Required | Required |

All four algorithms must be implemented and benchmarked in all three languages.

### 3.3 Algorithm Behaviour

**A1 - Basic Backtracking**
- Select the first empty cell in row-major order.
- Try candidate digits in ascending order (1–9).
- Check row, column and 3×3 box constraints.
- Backtrack when no candidate is valid.

**A2 - Bitmask Backtracking**
- Maintain occupancy bitmasks for every row, column and box.
- Use bitwise operations for candidate checking.
- Follow the same cell-selection order as A1.

**A3 - MRV Backtracking**
- Use row, column and box bitmasks.
- Select the empty cell with the fewest available candidates.
- Break ties by selecting the lowest row-major cell index.
- Backtrack immediately if any empty cell has zero candidates.

**A4 - Constraint Propagation + Search**

- Apply naked singles and hidden singles before branching.
- Scan naked singles in row-major order.
- Scan hidden singles in this order: rows, columns, then 3×3 boxes.
- Within each unit, check digits in ascending order (1–9).
- After assigning any digit, restart propagation from the beginning.
- Continue propagation until no more forced assignments are possible.
- Use A3's MRV branching strategy when propagation reaches a fixed point.
- Repeat propagation after every branch.
- Never discard a branch that could contain a valid solution.

### 3.4 Common Requirements

- All algorithms must follow the same input and output contract.
- All algorithms must support solution enumeration.
- All algorithms must store no more than 15 solutions while continuing to count additional solutions.
- All algorithms must respect the execution deadline.
- All algorithms must produce valid Sudoku solutions.
- Algorithm behaviour must be deterministic within each implementation.
- Results must be cross-validated using shared puzzle fixtures.

## 4. Solution Enumeration Order

### 4.1 Deterministic Search Order

All algorithms must produce deterministic solution enumeration within their respective implementations.

**Cell selection:**

- A1: Select the first empty cell in row-major order.
- A2: Select the first empty cell in row-major order.
- A3: Select the empty cell with the fewest candidates (MRV). Break ties using the lowest row-major index.
- A4: Apply constraint propagation first, then use A3's MRV branching strategy. When multiple propagation operations are possible, process cells in ascending row-major order.

**Digit selection:**

- Try candidate digits in ascending order (1–9).
- All three language implementations must follow identical candidate iteration rules.

### 4.2 Cross-Algorithm Enumeration

- Different algorithms are allowed to discover solutions in different orders.
- Cross-algorithm correctness comparisons must compare solution sets rather than discovery order.
- Within the same algorithm, Python, C++ and Java must produce identical solution ordering.

### 4.3 Solution Collection and Display

- The solver must search for solutions until the search space is exhausted or the execution deadline is reached.
- The solver must store only the first 15 solutions in deterministic enumeration order.
- The solver must continue counting solutions after collecting the first 15, without storing additional solutions.
- The maximum number of solutions returned to the frontend is 15.
- If the search completes, return the exact total solution count.
- If the search times out, return the number of solutions found so far as a lower bound.
- The frontend must clearly distinguish exact counts from lower-bound counts.

### 4.4 Enumeration Limits and Timeout

- Maximum stored solutions: 15.
- Maximum returned solutions: 15.
- Solution counting must not stop merely because 15 solutions have been collected.
- Every algorithm must respect a configurable execution deadline.
- The deadline must be checked periodically during recursive search.
- When the deadline is reached, terminate the search safely and preserve the solutions and count obtained so far.
- The `timed_out` flag must indicate whether the deadline was reached.
- The `count_capped` flag must remain false because no independent solution-count cap is being applied.

## 5. Time Budget and Execution Deadline

### 5.1 Default Configuration

- Default solver execution timeout: 10000 milliseconds (10 seconds).
- The timeout must be configurable through an environment variable named `SOLVER_DEADLINE_MS`.
- The solver must use a monotonic clock to measure elapsed execution time.
- The timeout must apply independently to every solver execution.

### 5.2 Deadline Handling

- The execution deadline must begin when the solver starts searching for solutions.
- Input parsing and initial validation must occur before the search deadline begins.
- Every algorithm must periodically check whether the execution deadline has been reached.
- Deadline checks must occur at least once every 1024 visited search nodes.
- When the deadline is reached, the solver must stop searching safely.
- The solver must preserve all solutions and the solution count obtained before termination.

### 5.3 Cross-Language Consistency

All Python, C++ and Java implementations must:

- Use equivalent monotonic timing mechanisms.
- Apply the same configured timeout.
- Follow the same periodic deadline-checking policy.
- Report whether the execution deadline was reached.
- Never claim that an interrupted search produced an exact total solution count.

### 5.4 Timeout Result

When the execution deadline is reached:

- Set `timed_out` to `true`.
- Return the number of solutions discovered before termination.
- Return at most the first 15 stored solutions.
- Treat the reported solution count as a lower bound.
- Preserve the results collected before the timeout.

When the search finishes before the deadline:

- Set `timed_out` to `false`.
- Return the exact total solution count.

### 5.5 Configuration

The default timeout must be configurable rather than hardcoded.

The backend will provide the configured timeout to the solver, allowing different environments to use different execution limits.

## 6. CLI Input and Output JSON

### 6.1 Input Format

All three language implementations must accept a JSON input containing:

| Field | Type | Description |
|---|---|---|
| `grid` | string | 81-character Sudoku puzzle |
| `algorithm` | string | Algorithm identifier: A1, A2, A3 or A4 |
| `deadline_ms` | integer | Maximum search execution time in milliseconds |

Example:

```json
{
  "grid": "530070000600195000098000060800060003400803001700020006060000280000419005000080079",
  "algorithm": "A3",
  "deadline_ms": 10000
}
```

### 6.2 Output Format

Every implementation must return a JSON object containing:

| Field | Type | Description |
|---|---|---|
| `status` | string | Final result status |
| `solution_count` | integer | Number of solutions discovered |
| `solutions` | array of strings | First 15 solutions at most |
| `count_capped` | boolean | Always false |
| `timed_out` | boolean | Whether the deadline was reached |
| `time_ms` | number | Solver execution time in milliseconds |
| `nodes_visited` | integer | Total search nodes visited |
| `backtracks` | integer | Total backtracks performed |
| `algorithm` | string | Algorithm used |

### 6.3 Output Requirements

- All implementations must use identical field names and compatible data types.
- Every solution must use the standard 81-character representation.
- The `solutions` array must contain no more than 15 entries.
- `solution_count` must represent the total discovered solutions, even when more than 15 exist.
- `time_ms` must measure solver execution time only.
- `nodes_visited` and `backtracks` must be non-negative integers.
- `count_capped` must always be false.
- The output must be valid JSON without additional console messages mixed into it.

## 7. Common Solver Interface

### 7.1 Purpose

All four algorithms must follow a common interface so they can be executed, tested and benchmarked consistently.

The interface must be implemented independently in Python, C++ and Java.

### 7.2 Solver Input

Every algorithm must accept:

- `grid`: Parsed 9×9 Sudoku board.
- `deadline_ms`: Maximum execution time in milliseconds.
- `max_stored_solutions`: Maximum number of solutions to store (15).

### 7.3 Solver Output

Every algorithm must return a common result structure containing:

- `status`
- `solution_count`
- `solutions`
- `count_capped`
- `timed_out`
- `time_ms`
- `nodes_visited`
- `backtracks`
- `algorithm`

### 7.4 Algorithm Registry

Each language must maintain an algorithm registry mapping algorithm IDs to their respective implementations.

| ID | Algorithm |
|---|---|
| A1 | Basic Backtracking |
| A2 | Bitmask Backtracking |
| A3 | MRV Backtracking |
| A4 | Propagation + Search |

The registry must allow algorithms to be executed using their IDs without requiring separate calling logic.

### 7.5 Normal Solving Workflow

When a user requests a solution:

1. The backend executes all four Python algorithms independently and concurrently.
2. Each algorithm receives the same puzzle and timeout configuration.
3. The backend collects their results and execution times.
4. Algorithms that time out or fail are excluded from winner selection.
5. The solution from the fastest successfully completed algorithm is displayed.
6. Execution times for all four algorithms are displayed.

**All-Algorithm Timeout Handling**

- If at least one algorithm completes successfully, display the solution from the fastest successfully completed algorithm.
- If all four algorithms time out but at least one discovers a valid solution, display one discovered solution as a partial result and clearly indicate that solving timed out.
- If all four algorithms time out without discovering a solution, display a timeout message.
- Never claim that a puzzle is unique or unsolvable unless an algorithm completes exhaustive search and establishes that result.
- Preserve the individual result statuses and timeout flags for all four algorithms.

### 7.6 Consistency Requirements

- All implementations must follow the same input/output contract.
- Each algorithm must operate independently without modifying another algorithm's board.
- One algorithm's failure must not prevent the remaining algorithms from completing.
- Results must be deterministic within each implementation.
- All four algorithms must be available in Python, C++ and Java.

## 8. Shared Test Fixtures

### 8.1 Purpose

Shared test fixtures provide a common set of Sudoku puzzles for validating all solver implementations.

The same fixtures must be used across Python, C++ and Java to ensure consistent behaviour and correctness.

### 8.2 Fixture Categories

Two main fixture categories will be maintained.

**A. Edge-Case Fixtures**

The edge-case dataset must cover:

| Puzzle Type | Expected Behaviour |
|---|---|
| Easy puzzle | Successfully solved |
| Duplicate givens | `invalid` |
| Complete and valid | `already_solved` |
| Complete but invalid | `invalid` |
| Valid but unsolvable | `unsolvable` |
| Multiple solutions | `multiple` |
| Empty grid | Large solution space |
| Near-empty grid | Performance under heavy search |

**B. Benchmark Fixtures**

- Maintain approximately 15–20 benchmark puzzles.
- Include a range of difficulty levels: easy, medium, hard and very hard.
- Difficulty labels are for internal testing and benchmarking only.
- Difficulty labels must not be displayed to users or used as user-facing options.

### 8.3 Fixture File Organization

Store shared puzzle fixtures in `data/puzzles/` using the following files:

| File | Purpose |
|---|---|
| `edge_cases.json` | Special puzzles covering result statuses and edge cases. |
| `benchmark_set.json` | Puzzles used for algorithm and language performance comparisons. |
| `samples.json` | Valid sample puzzles available for users to try. |

### 8.4 Fixture Structure

Each fixture must contain:

| Field | Description |
|---|---|
| `id` | Unique puzzle identifier. |
| `description` | Description of the test scenario. |
| `grid` | Sudoku puzzle string. |
| `expected_status` | Expected solver result status. |
| `expected_solution_count` | Expected solution count or lower bound; `null` when not applicable. |
| `count_type` | `exact`, `lower_bound`, or `not_applicable`. |
| `difficulty` | Optional difficulty label for benchmark fixtures only. |
| `deadline_ms` | Optional per-test execution deadline override. |
| `algorithms` | Optional list restricting the algorithms tested by this fixture. If omitted, test all four algorithms. |

**Count types:**
- `exact`: The solver must finish and return the exact expected solution count.
- `lower_bound`: The solver must discover at least the specified number of solutions. It may time out.
- `not_applicable`: Solution counting does not apply.

**Fixture loader requirements:**
- Validate grid length and characters according to `expected_status`.
- Do not reject intentionally malformed grids used for `invalid_format` tests before they reach the parser.
- Apply `deadline_ms` when provided; otherwise use the default configured deadline.
- Apply `algorithms` when provided; otherwise test A1–A4.

### 8.5 Testing Requirements

- All four algorithms in all three languages must be tested against the shared fixtures.
- Every implementation must produce valid Sudoku solutions.
- Solution counts must match the expected values whenever searches complete.
- Invalid puzzles must be rejected consistently.
- Repeated executions must produce deterministic results within each algorithm.
- Benchmark difficulty labels must remain internal and must never appear in the user interface.

### 8.6 Fixture Verification

- Expected solution counts must be verified using a trusted reference solver.
- Important edge cases must be independently verified before being accepted as ground truth.
- No fixture should be treated as authoritative until its expected result has been verified.

## 9. Error Handling and Validation

### 9.1 Input Error Handling

The system must handle the following input errors consistently:

| Scenario | Expected Behaviour |
|---|---|
| Input contains fewer or more than 81 characters | `invalid_format` |
| Input contains unsupported characters | `invalid_format` |
| Duplicate digits in a row, column or 3×3 box | `invalid` |
| Valid puzzle with no solution | `unsolvable` |
| Unsupported algorithm ID | Return a clear error |
| Invalid JSON input | Return a clear input error |
| Unexpected solver failure | Return an internal error |

### 9.2 Validation Responsibilities

Validation must happen at two levels.

**Frontend Validation**
- Perform immediate validation while the user enters digits.
- Detect duplicate digits in rows, columns and 3×3 boxes.
- Highlight only the most recently entered or edited cell when it creates a conflict.
- Remove the conflict highlight when the issue is resolved.

**Backend Validation**
- Perform authoritative validation before executing any solver.
- Reject malformed puzzle inputs.
- Detect duplicate givens in rows, columns and 3×3 boxes.
- Return the conflicting cell indices when validation fails.
- Never pass an invalid puzzle to a solving algorithm.

### 9.3 Error Response Requirements

- Errors must use a consistent response structure.
- Every error must include a meaningful error code and human-readable message.
- Additional details may be included when relevant.
- Internal exceptions must not expose stack traces or sensitive implementation details to users.

### 9.4 Validation Consistency

- Frontend and backend validation must follow the same Sudoku rules.
- Shared edge-case fixtures must be used to test both validation implementations.
- Backend validation remains authoritative if frontend and backend results disagree.

## 10. Performance Measurement and Benchmarking

### 10.1 Metrics

Every solver implementation must record the following metrics:

| Metric | Description |
|---|---|
| `time_ms` | Solver execution time in milliseconds. |
| `nodes_visited` | Total number of search nodes visited. |
| `backtracks` | Total number of backtracks performed. |
| `solution_count` | Total number of solutions discovered. |

### 10.2 Benchmarking Requirements

- All four algorithms must be benchmarked in Python, C++ and Java.
- All implementations must use the same benchmark puzzle dataset.
- All language benchmarks must run on the same machine under controlled conditions.
- C++ and Java must use optimized execution builds.
- Solver execution time must be measured separately from input parsing, process startup and output serialization.

### 10.3 Benchmark Repetitions

- Each benchmark combination must have five measured runs.
- A benchmark combination consists of one puzzle, one algorithm and one programming language.
- Java implementations must perform at least one warm-up run before the five measured runs to allow JVM JIT compilation.
- Warm-up runs must not be included in the benchmark measurements.
- The median execution time must be used as the primary comparison metric.
- The average execution time may also be reported as an additional metric.
- Development tests may use a single run to reduce execution time.
- Preserve individual measurements from all five runs.

### 10.4 Benchmark Results

- Store benchmark results as JSON files inside `benchmarks/results/`.
- Preserve individual run measurements.
- Record the median and average execution times.
- Include the puzzle ID, algorithm ID and programming language.
- Record nodes visited, backtracks and solution counts.
- Failed or timed-out executions must be identified separately and must not be treated as successful performance results.

### 10.5 Fair Comparison Rules

- Use identical puzzle inputs across all implementations.
- Use the same timeout configuration.
- Run benchmarks on the same hardware.
- Benchmark each algorithm independently, without running other benchmark algorithms concurrently.
- Avoid unnecessary background workloads during benchmark execution.
- Use optimized Release builds for C++ and Java.
- Java warm-up runs must be excluded from measured results.
- Do not include process startup, input parsing or output serialization in solver execution time.
- Clearly distinguish solver execution time from total program execution time.
- Avoid comparing results collected under substantially different system conditions.

### 10.6 Benchmark Reporting

The benchmarking report must provide:

- Performance comparison across A1–A4.
- Performance comparison across Python, C++ and Java.
- Median execution time for each benchmark combination.
- Algorithm-wise and language-wise comparisons.
- Identification of the fastest algorithm and fastest language for each benchmark puzzle.

## 11. Project-Wide Configuration

### 11.1 Configuration Parameters

The following settings must be configurable and must not be hardcoded across multiple modules.

| Setting | Default Value | Description |
|---|---:|---|
| `SOLVER_DEADLINE_MS` | 10000 | Maximum solver search time in milliseconds. |
| `MAX_STORED_SOLUTIONS` | 15 | Maximum number of solutions stored per solver execution. |
| `BENCHMARK_REPETITIONS` | 5 | Number of repetitions for each benchmark combination. |

### 11.2 Configuration Requirements

- Configuration values must have centralized definitions.
- All three language implementations must follow the same configuration.
- Normal solving and benchmarking must use the same solver timeout.
- Changing a configuration value must not require modifying multiple algorithm implementations.
- Configuration values must be validated before execution.
- Invalid configuration values must produce a clear error.

### 11.3 Default Behaviour

Unless explicitly overridden, the application must use the default values defined in Section 11.1.

The same configuration must be applied consistently across Python, C++ and Java implementations.

## 12. Final Contract Summary

### 12.1 Finalized Decisions

| Area | Decision |
|---|---|
| External input format | 81-character string |
| Internal board representation | 9×9 character array |
| Supported algorithms | A1, A2, A3 and A4 |
| Programming languages | Python, C++ and Java |
| Supported result statuses | `invalid_format`, `invalid`, `already_solved`, `unsolvable`, `unique`, `multiple`, `timeout` |
| Maximum stored solutions | 15 |
| Solution enumeration | Continue counting beyond 15 |
| Default execution timeout | 10,000 milliseconds |
| User-facing solving | Execute all four Python algorithms |
| Displayed solution | Solution from the fastest successfully completed algorithm |
| Execution times | Display execution times for all four algorithms |
| Algorithm selector | Not required |
| Benchmark repetitions | 5 |
| Primary benchmark metric | Median execution time |
| Test fixtures | Shared across all three languages |
| Difficulty labels | Internal benchmarking only |

### 12.2 Timeout Handling

The solver must follow these rules when the execution deadline is reached:

| Solutions Found | Status | Behaviour |
|---|---|---|
| 0 | `timeout` | Cannot prove that the puzzle is unsolvable. |
| 1 | `timeout` | Return the discovered solution as a partial result. |
| 2 or more | `multiple` | Return discovered solutions with `timed_out: true`. |

Additional requirements:

- `unique` must only be returned after exhaustive search confirms exactly one solution.
- `unsolvable` must only be returned after exhaustive search confirms zero solutions.
- A timed-out result must never be incorrectly classified as `unique` or `unsolvable`.
- When the status is `timeout`, the solution count represents the number discovered before termination.
- When the status is `multiple` and `timed_out` is true, the solution count represents a lower bound on the actual total.

### 12.3 Parallel Algorithm Execution

- All four Python algorithms must execute independently.
- Each algorithm must receive its own copy of the puzzle.
- Each algorithm must have its own execution deadline.
- Failure or timeout in one algorithm must not prevent the others from completing.
- The fastest successfully completed algorithm will provide the displayed solution.
- Execution times for all four algorithms must be displayed.

### 12.4 Specification Completion Criteria

Before implementation begins:

- All sections must have clearly defined requirements.
- All major design decisions must be finalized.
- Python, C++ and Java implementations must follow the same contract.
- Shared test fixtures must be prepared.
- Any changes to the specification must be documented and reflected across all implementations.