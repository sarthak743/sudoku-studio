import { Delete } from 'lucide-react';
interface Props { onDigit: (d: number) => void; onClear: () => void; disabled: boolean }
export default function NumPad({ onDigit, onClear, disabled }: Props) {
  return (
    <div className="flex items-stretch gap-3" aria-label="Number pad">
      <div data-testid="numpad" className="grid grid-cols-3 grid-rows-3 gap-2 flex-1 max-w-[15rem]">
        {[1, 2, 3, 4, 5, 6, 7, 8, 9].map((d) => (
          <button key={d} type="button" disabled={disabled} onClick={() => onDigit(d)} aria-label={`Enter ${d}`}
            className="pad aspect-[4/3] rounded-xl border border-line bg-surf2 font-mono text-2xl disabled:opacity-35 disabled:cursor-not-allowed">{d}</button>
        ))}
      </div>
      <button type="button" disabled={disabled} onClick={onClear} aria-label="Clear cell"
        className="pad w-14 rounded-xl border border-line bg-surf2 grid place-items-center text-mute disabled:opacity-35"><Delete size={20} /></button>
    </div>
  );
}
