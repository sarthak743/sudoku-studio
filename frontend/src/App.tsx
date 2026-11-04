import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { Eraser, Grid3x3, ImageUp, Moon, Play, RotateCcw, ShieldCheck, Sun, Trophy, X } from 'lucide-react';
import Board, { type CellKind } from './components/Board';
import NumPad from './components/NumPad';
import Results, { type Panel } from './components/Results';
import ImageUpload from './components/ImageUpload';
import { solveGrid, validateGrid } from './api';
import { findConflicts, fromGridString, SAMPLES, toGridString } from './sudoku';

type Mode = 'set' | 'play';
type View = 'board' | 'upload';
const blank = (): number[] => Array<number>(81).fill(0);
const msg = (e: unknown): string => (e instanceof Error ? e.message : 'Unexpected error.');

export default function App() {
  const [givens, setGivens] = useState<number[]>(blank);
  const [entries, setEntries] = useState<number[]>(blank);
  const [mode, setMode] = useState<Mode>('set');
  const [view, setView] = useState<View>('board');
  const [sel, setSel] = useState<number | null>(null);
  const [panel, setPanel] = useState<Panel>({ kind: 'idle' });
  const [sIdx, setSIdx] = useState(0);
  const [confirm, setConfirm] = useState(false);
  const [theme, setTheme] = useState(document.documentElement.dataset.theme ?? 'dark');
  const [sample, setSample] = useState<string | null>(null);
  const [serverConflicts, setServerConflicts] = useState<Set<number>>(new Set());
  const [showSolved, setShowSolved] = useState(false);
  const [hasTriggeredSolved, setHasTriggeredSolved] = useState(false);
  const digitEnteredRef = useRef(false);

  const solution = panel.kind === 'solve' ? panel.outcome.result.solutions[sIdx] : undefined;
  const base = useMemo(() => givens.map((g, i) => g || entries[i]), [givens, entries]);
  const localConflicts = useMemo(() => findConflicts(base), [base]);
  const conflicts = useMemo(() => {
    if (serverConflicts.size === 0) return localConflicts;
    const combined = new Set(localConflicts);
    serverConflicts.forEach((c) => combined.add(c));
    return combined;
  }, [localConflicts, serverConflicts]);
  const solved = useMemo(() => (solution ? fromGridString(solution) : null), [solution]);
  const values = useMemo(() => base.map((v, i) => v || solved?.[i] || 0), [base, solved]);
  const kinds: CellKind[] = useMemo(() => base.map((v, i) => (givens[i] ? 'clue' : v ? 'user' : values[i] ? 'solved' : 'empty')), [base, givens, values]);
  const filled = base.filter(Boolean).length;
  const busy = panel.kind === 'loading';

  useEffect(() => {
    if (digitEnteredRef.current) {
      digitEnteredRef.current = false;
      if (mode === 'play' && !hasTriggeredSolved && filled === 81 && conflicts.size === 0) {
        setShowSolved(true);
        setHasTriggeredSolved(true);
      }
    }
  }, [mode, filled, conflicts, hasTriggeredSolved]);

  useEffect(() => {
    if (!showSolved) return;
    const onKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') setShowSolved(false);
    };
    window.addEventListener('keydown', onKeyDown);
    return () => window.removeEventListener('keydown', onKeyDown);
  }, [showSolved]);

  const setCell = useCallback((i: number, d: number) => {
    if (mode === 'set') {
      setGivens((g) => g.map((x, k) => (k === i ? d : x)));
      setEntries((e) => e.map((x, k) => (k === i ? 0 : x)));
    } else {
      if (givens[i]) return;
      if (d >= 1 && d <= 9) digitEnteredRef.current = true;
      setEntries((e) => e.map((x, k) => (k === i ? d : x)));
    }
    setServerConflicts((sc) => (sc.has(i) ? new Set([...sc].filter((x) => x !== i)) : sc));
    setPanel((p) => (p.kind === 'idle' ? p : { kind: 'idle' }));
    setSIdx(0);
  }, [mode, givens]);
  const enter = (d: number): void => { if (sel !== null) setCell(sel, d); };

  const onKey = (e: React.KeyboardEvent): void => {
    const m: Record<string, [number, number]> = { ArrowUp: [-1, 0], ArrowDown: [1, 0], ArrowLeft: [0, -1], ArrowRight: [0, 1] };
    const mv = m[e.key];
    if (mv) { e.preventDefault(); if (sel === null) return setSel(0); const r = Math.min(8, Math.max(0, Math.floor(sel / 9) + mv[0])), c = Math.min(8, Math.max(0, (sel % 9) + mv[1])); setSel(r * 9 + c); }
    else if (e.key >= '1' && e.key <= '9') enter(Number(e.key));
    else if (['Backspace', 'Delete', '0'].includes(e.key)) { e.preventDefault(); enter(0); }
    else if (e.key === 'Escape') setSel(null);
  };

  const loadSample = (name: string): void => {
    setGivens(fromGridString(SAMPLES[name]));
    setEntries(blank());
    setSample(name);
    setSel(null);
    setServerConflicts(new Set());
    setPanel({ kind: 'idle' });
    setSIdx(0);
    setShowSolved(false);
    setHasTriggeredSolved(false);
  };
  const solve = async (): Promise<void> => {
    if (conflicts.size) return setPanel({ kind: 'notice', ok: false, message: `${conflicts.size} cells conflict. Resolve them before solving.` });
    if (filled === 0) return setPanel({ kind: 'notice', ok: false, message: 'Add some clues first.' });
    setPanel({ kind: 'loading', what: 'Racing four solvers' }); setSIdx(0);
    try { setPanel({ kind: 'solve', outcome: await solveGrid(toGridString(base)) }); } catch (e) { setPanel({ kind: 'error', message: msg(e) }); }
  };
  const check = async (): Promise<void> => {
    setPanel({ kind: 'loading', what: 'Checking with server' });
    try {
      const v = await validateGrid(toGridString(base));
      const serverSet = new Set(v.conflicts.map((c) => c.row * 9 + c.col));
      setServerConflicts(serverSet);
      setPanel({
        kind: 'notice',
        ok: v.valid,
        message: v.valid
          ? 'Server confirms: no conflicts.'
          : `Server found ${v.conflicts.length} conflicting cells: ${v.conflicts.map((c) => `R${c.row + 1}C${c.col + 1}`).join(', ')}.`,
      });
    } catch (e) {
      setPanel({ kind: 'error', message: msg(e) });
    }
  };
  const toggleTheme = (): void => { const t = theme === 'dark' ? 'light' : 'dark'; setTheme(t); document.documentElement.dataset.theme = t; try { localStorage.setItem('theme', t); } catch { /* ignore */ } };
  const reset = (): void => {
    setGivens(blank());
    setEntries(blank());
    setServerConflicts(new Set());
    setPanel({ kind: 'idle' });
    setSel(null);
    setSample(null);
    setConfirm(false);
    setSIdx(0);
    setShowSolved(false);
    setHasTriggeredSolved(false);
  };

  return (
    <div className="mx-auto max-w-6xl px-4 py-6 sm:py-10">
      <header className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3"><div className="grid place-items-center size-10 rounded-xl bg-acc text-onacc"><Grid3x3 size={20} /></div>
          <div><h1 className="font-serif text-3xl leading-none">Sudoku Studio</h1></div></div>
        <button className="btn btn-icon !rounded-full !w-11 !h-11 !p-0 flex items-center justify-center" onClick={toggleTheme} aria-label="Toggle theme">{theme === 'dark' ? <Sun size={16} /> : <Moon size={16} />}</button>
      </header>
      <div className="flex justify-between gap-4 mb-5">
        <div className="space-y-1">
          <h2 className="font-serif text-2xl sm:text-3xl">
            Ready to crack the grid?
          </h2>
          <p className="text-sm text-mute">
            Enter a puzzle, upload an image, and let four algorithms race to find its solution.
          </p>
        </div>
        <button
          type="button"
          onClick={() => setView((v) => (v === 'upload' ? 'board' : 'upload'))}
          className={`btn ${view === 'upload' ? '!border-acc !text-acc font-semibold' : ''}`}
          aria-label={view === 'upload' ? 'Back to Board' : 'Upload Sudoku Image'}
          aria-pressed={view === 'upload'}
        >
          <ImageUp size={16} />
          {view === 'upload' ? 'Back to Board' : 'Upload Image'}
        </button>
      </div>
      {view === 'upload' ? (
        <main className="grid lg:grid-cols-[minmax(0,34rem)_1fr] gap-6 lg:gap-10 items-start">
          <section className="space-y-4">
            <div className="panel p-5 space-y-4">
              <div className="flex items-center justify-between border-b border-line pb-3">
                <div>
                  <h2 className="font-serif text-2xl leading-none">Upload Sudoku Image</h2>
                  <p className="text-xs text-mute mt-1">Select or drop a puzzle image to preview and orient.</p>
                </div>
                <button
                  type="button"
                  className="btn text-xs"
                  onClick={() => setView('board')}
                >
                  View Board
                </button>
              </div>
              <ImageUpload />
            </div>
          </section>
          <section className="space-y-4">
            <div className="panel p-4 space-y-2">
              <div className="flex items-center justify-between">
                <h3 className="font-serif text-lg leading-none">Interactive Board</h3>
                <span className="text-xs text-mute font-mono">{filled} of 81 cells filled</span>
              </div>
              <p className="text-xs text-mute">
                Reference your uploaded image while transcribing clues or playing. Switch back to full board view anytime.
              </p>
            </div>
            <Board values={values} kinds={kinds} conflicts={conflicts} selected={sel} onSelect={setSel} onKey={onKey} />
            <div className="flex items-center gap-3 flex-wrap">
              <div className="flex p-1 rounded-lg bg-surf2 border border-line" role="tablist" aria-label="Mode">
                {(['set', 'play'] as const).map((m) => (
                  <button
                    key={m}
                    role="tab"
                    aria-selected={mode === m}
                    onClick={() => setMode(m)}
                    title={m === 'set' ? 'Edit Puzzle: enter or remove original clues' : 'Play: fill in empty cells while clues stay locked'}
                    className={`px-3 py-1 rounded-md text-sm transition ${mode === m ? 'bg-acc text-onacc font-semibold' : 'text-mute'}`}
                  >
                    {m === 'set' ? 'Edit Puzzle' : 'Play'}
                  </button>
                ))}
              </div>
            </div>
            <NumPad onDigit={enter} onClear={() => enter(0)} disabled={sel === null} />
          </section>
        </main>
      ) : (
        <main className="grid lg:grid-cols-[minmax(0,34rem)_1fr] gap-6 lg:gap-10 items-start">
          <section className="space-y-4">
            <div className="flex flex-wrap gap-2 items-center" role="group" aria-label="Sample puzzles">
              {Object.keys(SAMPLES).map((n) => (
                <button
                  key={n}
                  onClick={() => loadSample(n)}
                  aria-pressed={sample === n}
                  className={`btn ${sample === n ? '!border-acc !text-acc' : ''}`}
                >
                  {n}
                </button>
              ))}
            </div>
            <Board values={values} kinds={kinds} conflicts={conflicts} selected={sel} onSelect={setSel} onKey={onKey} />
            <p className={`text-xs ${conflicts.size ? 'text-bad' : 'text-mute'}`} aria-live="polite">
              {conflicts.size ? `${conflicts.size} cells conflict with a row, column or box.` : `${filled} of 81 cells filled.`}
            </p>
            <div className="flex items-center gap-3 flex-wrap">
              <div className="flex p-1 rounded-lg bg-surf2 border border-line" role="tablist" aria-label="Mode">
                {(['set', 'play'] as const).map((m) => (
                  <button
                    key={m}
                    role="tab"
                    aria-selected={mode === m}
                    onClick={() => setMode(m)}
                    title={m === 'set' ? 'Edit Puzzle: enter or remove original clues' : 'Play: fill in empty cells while clues stay locked'}
                    className={`px-3 py-1 rounded-md text-sm transition ${mode === m ? 'bg-acc text-onacc font-semibold' : 'text-mute'}`}
                  >
                    {m === 'set' ? 'Edit Puzzle' : 'Play'}
                  </button>
                ))}
              </div>
              <span className="text-xs text-mute hidden sm:block">
                {mode === 'set' ? 'Edit Puzzle: enter or remove clues' : 'Play: clues are locked, fill empty cells'} · Arrows move · 1–9 enter · Backspace clears
              </span>
            </div>
            <NumPad onDigit={enter} onClear={() => enter(0)} disabled={sel === null} />
          </section>
          <section className="space-y-4">
            <div className="flex flex-wrap gap-2 items-center">
              <button className="btn btn-acc" onClick={solve} disabled={busy}><Play size={15} />Solve</button>
              <button className="btn" onClick={check} disabled={busy || filled === 0}><ShieldCheck size={15} />Check with server</button>
              <button className="btn" onClick={() => { setPanel({ kind: 'idle' }); setSIdx(0); }} disabled={panel.kind !== 'solve'}><Eraser size={15} />Clear solution</button>
              {confirm ? (
                <span className="flex items-center gap-2 text-sm" role="alertdialog" aria-label="Confirm reset">
                  Erase everything?
                  <button className="btn !border-bad !text-bad" onClick={reset}>Yes, reset</button>
                  <button className="btn" onClick={() => setConfirm(false)}>Cancel</button>
                </span>
              ) : (
                <button className="btn" onClick={() => setConfirm(true)}><RotateCcw size={15} />Reset all</button>
              )}
            </div>
            <div className="panel p-5 min-h-[16rem]" aria-live="polite">
              <Results panel={panel} index={sIdx} onIndex={setSIdx} onSample={() => loadSample('Easy')} />
            </div>
            <div className="flex gap-4 text-xs text-mute">
              <span className="text-ink font-mono">■ clue</span>
              <span className="text-acc font-mono">■ yours</span>
              <span className="font-mono italic">■ solver</span>
            </div>
          </section>
        </main>
      )}
      {showSolved && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm"
          onClick={() => setShowSolved(false)}
          role="dialog"
          aria-modal="true"
          aria-labelledby="puzzle-solved-title"
        >
          <div
            className="panel relative max-w-sm w-full p-6 sm:p-8 text-center rise"
            onClick={(e) => e.stopPropagation()}
          >
            <button
              type="button"
              className="btn absolute top-3 right-3 !p-1.5 !h-auto text-mute hover:text-ink"
              onClick={() => setShowSolved(false)}
              aria-label="Close"
            >
              <X size={16} />
            </button>
            <div className="inline-grid place-items-center size-14 rounded-2xl bg-acc text-onacc mb-4 mx-auto shadow-lg shadow-acc/20">
              <Trophy size={28} />
            </div>
            <h2 id="puzzle-solved-title" className="font-serif text-3xl leading-none">Puzzle Solved!</h2>
            <p className="text-mute text-sm mt-2">All 81 cells are correctly filled with no conflicts.</p>
            <div className="mt-6">
              <button
                type="button"
                className="btn btn-acc w-full justify-center"
                onClick={() => setShowSolved(false)}
              >
                Continue
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
