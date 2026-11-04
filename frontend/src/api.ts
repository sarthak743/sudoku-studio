import type { ErrorResponse, SolveAllResponse, SolveOutcome, SolveResponse, ValidationResponse } from './types';
const BASE = (import.meta.env.VITE_API_BASE_URL as string | undefined) ?? 'http://127.0.0.1:8000';
export class ApiError extends Error {
  code?: string;
  details?: Record<string, unknown> | null;
  constructor(message: string, code?: string, details?: Record<string, unknown> | null) {
    super(message);
    this.name = 'ApiError';
    this.code = code;
    this.details = details;
  }
}
async function post<T>(path: string, body: unknown): Promise<T> {
  let res: Response;
  try { res = await fetch(`${BASE}${path}`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) }); }
  catch { throw new ApiError(`Cannot reach the server at ${BASE}. Is the backend running?`); }
  if (!res.ok) {
    let errBody: ErrorResponse | undefined;
    try { errBody = (await res.json()) as ErrorResponse; } catch { /* ignore non-JSON error */ }
    if (errBody?.message) {
      const detailMsg = Array.isArray((errBody.details as { errors?: Array<{ msg?: string }> } | undefined)?.errors)
        ? (errBody.details as { errors: Array<{ msg?: string }> }).errors.map((e) => e.msg).filter(Boolean).join('; ')
        : '';
      const displayMsg = detailMsg ? `${errBody.message} (${detailMsg})` : errBody.message;
      throw new ApiError(displayMsg, errBody.code, errBody.details);
    }
    throw new ApiError(`Server error (${res.status}).`);
  }
  return (await res.json()) as T;
}
export const validateGrid = (grid: string) => post<ValidationResponse>('/api/validate', { grid });
export async function solveGrid(grid: string): Promise<SolveOutcome> {
  const data = await post<SolveResponse | SolveAllResponse>('/api/solve', { grid, algorithm: 'all' });
  return 'selected_result' in data ? { result: data.selected_result, runs: data.algorithm_results } : { result: data, runs: [] };
}
