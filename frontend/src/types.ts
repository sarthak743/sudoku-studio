export type SolverStatus = 'invalid_format'|'invalid'|'already_solved'|'unsolvable'|'unique'|'multiple'|'timeout';
export interface ErrorResponse { code: string; message: string; details?: Record<string, unknown> | null }
export interface CellPosition { row: number; col: number }
export interface ValidationResponse { valid: boolean; conflicts: CellPosition[] }
export interface SolveResponse { status: SolverStatus; solution_count: number; solutions: string[]; count_capped: boolean; timed_out: boolean; time_ms: number; nodes_visited: number; backtracks: number; algorithm: string }
export interface AlgorithmRunResult { algorithm: string; status: SolverStatus; solution_count: number; time_ms: number; nodes_visited: number; backtracks: number; timed_out: boolean }
export interface SolveAllResponse { selected_result: SolveResponse; algorithm_results: AlgorithmRunResult[] }
export interface SolveOutcome { result: SolveResponse; runs: AlgorithmRunResult[] }
