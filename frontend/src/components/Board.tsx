import { useRef } from 'react';
import { peers } from '../sudoku';
export type CellKind = 'clue' | 'user' | 'solved' | 'empty';
interface Props { values: number[]; kinds: CellKind[]; conflicts: Set<number>; selected: number | null; onSelect: (i: number | null) => void; onKey: (e: React.KeyboardEvent) => void }
export default function Board({ values, kinds, conflicts, selected, onSelect, onKey }: Props) {
  const ref = useRef<HTMLDivElement>(null);
  const selVal = selected !== null ? values[selected] : 0;
  const move = (e: React.PointerEvent) => {
    const r = e.currentTarget.getBoundingClientRect();
    ref.current?.style.setProperty('--mx', `${e.clientX - r.left}px`); ref.current?.style.setProperty('--my', `${e.clientY - r.top}px`);
  };
  return (
    <div ref={ref} onPointerMove={move} className="board panel p-2 sm:p-3 w-full max-w-[34rem]" style={{ aspectRatio: '1 / 1' }}>
      <div role="grid" aria-label="Sudoku board" aria-rowcount={9} aria-colcount={9} tabIndex={0} onKeyDown={onKey}
        aria-activedescendant={selected !== null ? `cell-${selected}` : undefined}
        className="relative grid grid-cols-9 grid-rows-9 w-full h-full overflow-hidden rounded-lg outline-none focus-visible:ring-2 ring-acc" style={{ border: '2px solid var(--line2)' }}>
        {values.map((v, i) => {
          const r = Math.floor(i / 9), c = i % 9, k = kinds[i];
          const isSel = i === selected, bad = conflicts.has(i);
          const inPeer = selected !== null && !isSel && peers(selected, i);
          const match = selVal !== 0 && v === selVal && !isSel;
          const bg = bad ? 'var(--badbg)' : isSel ? 'var(--sel)' : match ? 'var(--match)' : inPeer ? 'var(--hl)' : 'transparent';
          return (
            <div key={i} id={`cell-${i}`} role="gridcell" aria-selected={isSel} aria-rowindex={r + 1} aria-colindex={c + 1}
              aria-label={`Row ${r + 1}, column ${c + 1}, ${v ? v : 'empty'}${bad ? ', conflict' : ''}`}
              onMouseDown={(e) => { e.preventDefault(); onSelect(i); (e.currentTarget.parentElement as HTMLElement).focus(); }}
              className={`cell grid place-items-center cursor-pointer select-none font-mono overflow-hidden ${k === 'clue' ? 'font-medium text-ink' : k === 'user' ? 'text-acc' : 'text-mute italic'} ${bad ? '!text-bad' : ''}`}
              style={{ minWidth: 0, minHeight: 0, boxSizing: 'border-box', background: bg, borderRight: c === 8 ? 0 : `${c % 3 === 2 ? 2 : 1}px solid ${c % 3 === 2 ? 'var(--line2)' : 'var(--line)'}`, borderBottom: r === 8 ? 0 : `${r % 3 === 2 ? 2 : 1}px solid ${r % 3 === 2 ? 'var(--line2)' : 'var(--line)'}`, boxShadow: isSel ? 'inset 0 0 0 2px var(--acc)' : undefined, fontSize: 'clamp(0.75rem, 2.2cqi, 1.75rem)' }}>
              {v ? <span key={`${v}-${k}`} className="pop leading-none">{v}</span> : null}
            </div>
          );
        })}
      </div>
    </div>
  );
}
