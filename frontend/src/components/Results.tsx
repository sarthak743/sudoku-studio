import { AlertTriangle, CheckCircle2, ChevronLeft, ChevronRight, Clock, Loader2, Sparkles, XCircle } from 'lucide-react';
import type { SolveOutcome, SolverStatus } from '../types';
const ALGORITHM_NAMES: Record<string, string> = {
  A1: 'Basic Backtracking',
  A2: 'Bitmask Backtracking',
  A3: 'MRV Backtracking',
  A4: 'Propagation + Search',
};
const STATUS_LABELS: Record<string, string> = {
  unique: 'Solution found',
  multiple: 'Multiple solutions',
  timeout: 'Hit Time limit',
  invalid: 'Invalid puzzle',
  unsolvable: 'No solution',
  already_solved: 'Already solved',
  invalid_format: 'Invalid format',
};
export type Panel = { kind: 'idle' } | { kind: 'loading'; what: string } | { kind: 'error'; message: string } | { kind: 'notice'; ok: boolean; message: string } | { kind: 'solve'; outcome: SolveOutcome };
const COPY: Record<SolverStatus, { t: string; d: string; tone: 'ok' | 'bad' | 'warn' }> = {
  unique: { t: 'Unique solution', d: 'Exactly one valid completion exists.', tone: 'ok' },
  multiple: { t: 'Multiple solutions', d: 'This puzzle has more than one valid completion.', tone: 'ok' },
  already_solved: { t: 'Already solved', d: 'The grid is complete and valid.', tone: 'ok' },
  unsolvable: { t: 'Unsolvable', d: 'No valid completion exists for these clues.', tone: 'bad' },
  invalid: { t: 'Invalid puzzle', d: 'The grid breaks Sudoku rules. Fix the highlighted cells.', tone: 'bad' },
  invalid_format: { t: 'Invalid format', d: 'The server could not read this grid.', tone: 'bad' },
  timeout: { t: 'Timed out', d: 'The solvers hit their time limit before finishing.', tone: 'warn' },
};
const Stat = ({ l, v }: { l: string; v: string }) => (<div className="rounded-lg bg-surf2 border border-line px-3 py-2"><div className="text-[0.65rem] uppercase tracking-widest text-mute">{l}</div><div className="font-mono text-base break-words leading-snug">{v}</div></div>);
interface Props { panel: Panel; index: number; onIndex: (i: number) => void; onSample: () => void }
export default function Results({ panel, index, onIndex, onSample }: Props) {
  if (panel.kind === 'idle') return (
    <div className="text-center py-10 rise"><Sparkles className="mx-auto text-acc" /><h3 className="font-serif text-3xl mt-3">Nothing solved yet</h3>
      <p className="text-mute text-sm mt-2 max-w-xs mx-auto">Enter clues or load a sample, then press Solve. Counts, timings and the winning algorithm land here.</p>
      <button className="btn mt-5" onClick={onSample}>Load the Easy sample</button></div>);
  if (panel.kind === 'loading') return <div className="py-12 text-center text-mute" role="status"><Loader2 className="mx-auto animate-spin text-acc" /><p className="mt-3 text-sm">{panel.what}…</p></div>;
  if (panel.kind === 'error') return <div role="alert" className="py-8 text-center rise"><XCircle className="mx-auto text-bad" /><h3 className="font-serif text-2xl mt-2">Something went wrong</h3><p className="text-sm text-mute mt-1">{panel.message}</p></div>;
  if (panel.kind === 'notice') return <div role="status" className="py-8 text-center rise">{panel.ok ? <CheckCircle2 className="mx-auto text-ok" /> : <AlertTriangle className="mx-auto text-bad" />}<p className="mt-2 text-sm">{panel.message}</p></div>;
  const { result: r, runs } = panel.outcome; const c = COPY[r.status]; const n = r.solutions.length;
  const Icon = c.tone === 'ok' ? CheckCircle2 : c.tone === 'warn' ? Clock : XCircle;
  return (
    <div className="rise space-y-4">
      <div className="flex items-start gap-3"><Icon className={c.tone === 'ok' ? 'text-ok' : c.tone === 'warn' ? 'text-acc' : 'text-bad'} /><div><h3 className="font-serif text-3xl leading-none">{c.t}</h3><p className="text-sm text-mute mt-1">{c.d}</p></div></div>
      <div className="grid grid-cols-2 gap-2">
        <Stat
          l="Number Of Solutions"
          v={`${r.solution_count}${r.count_capped ? '+' : ''}`}
        />
        <Stat
          l="Winner"
          v={ALGORITHM_NAMES[r.algorithm ?? ''] ?? r.algorithm ?? '—'}
        />
        <Stat
          l="Time"
          v={`${r.time_ms.toFixed(1)} ms`}
        />
        <Stat
          l="Backtracks"
          v={r.backtracks.toLocaleString()}
        />
      </div>
      {n > 1 && (<div className="flex items-center justify-between panel px-3 py-2"><button className="btn" disabled={index === 0} onClick={() => onIndex(index - 1)}><ChevronLeft size={16} />Previous</button>
        <span className="font-mono text-sm" aria-live="polite">Solution {index + 1} of {n}{r.count_capped ? ` (count capped at ${r.solution_count})` : ''}</span>
        <button className="btn" disabled={index === n - 1} onClick={() => onIndex(index + 1)}>Next<ChevronRight size={16} /></button></div>)}
      {runs.length > 0 && (
        <div>
          <div className="text-[0.65rem] uppercase tracking-widest text-mute mb-2">
            Solver race
          </div>

          <div className="overflow-x-auto rounded-lg border border-line">
            <table className="w-full text-xs text-left font-mono">
              <thead className="bg-surf2 text-mute uppercase tracking-wider font-mono">
                <tr>
                  <th className="px-3 py-2">Algorithm</th>
                  <th className="px-3 py-2">Result</th>
                  <th className="px-3 py-2">Status</th>
                </tr>
              </thead>

              <tbody>
                {runs.map((a) => (
                  <tr
                    key={a.algorithm}
                    className={
                      a.algorithm === r.algorithm
                        ? 'bg-acc/10 text-acc border-t border-line'
                        : 'border-t border-line text-mute'
                    }
                  >
                    <td className="px-3 py-2 font-medium">
                      {ALGORITHM_NAMES[a.algorithm] ?? a.algorithm}
                    </td>

                    <td className="px-3 py-2">
                      {a.status === 'multiple'
                        ? 'Multiple solutions'
                        : a.status === 'unique'
                          ? 'Unique solution'
                          : a.status === 'already_solved'
                            ? 'Already solved'
                            : a.status === 'unsolvable'
                              ? 'No solution'
                              : a.status === 'invalid'
                                ? 'Invalid puzzle'
                                : a.status === 'invalid_format'
                                  ? 'Invalid format'
                                  : a.status === 'timeout'
                                    ? 'Not completed'
                                    : a.status}
                    </td>

                    <td className="px-3 py-2">
                      {a.timed_out
                        ? STATUS_LABELS.timeout
                        : STATUS_LABELS[a.status] ?? a.status}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>);
}
