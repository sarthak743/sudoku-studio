export const toGridString = (cells: number[]): string => cells.map((c) => (c === 0 ? '0' : String(c))).join('');
export const fromGridString = (s: string): number[] => Array.from(s, (c) => (c >= '1' && c <= '9' ? Number(c) : 0));
export const boxOf = (i: number): number => Math.floor(i / 27) * 3 + Math.floor((i % 9) / 3);
export const peers = (a: number, b: number): boolean => Math.floor(a / 9) === Math.floor(b / 9) || a % 9 === b % 9 || boxOf(a) === boxOf(b);
/** Indices of cells that duplicate a digit in their row, column or box. */
export function findConflicts(cells: number[]): Set<number> {
  const bad = new Set<number>();
  for (let i = 0; i < 81; i++) {
    if (!cells[i]) continue;
    for (let j = i + 1; j < 81; j++) if (cells[j] === cells[i] && peers(i, j)) { bad.add(i); bad.add(j); }
  }
  return bad;
}
export const SAMPLES: Record<string, string> = {
  Easy: '530070000600195000098000060800060003400803001700020006060000280000419005000080079',
  Medium: '009000000080605020501078000000000700706040102004000000000720903090301080000000600',
  Hard: '000000907000420180000705026100904000050000040000507009920108000034059000507000000',
  Expert: '800000000003600000070090200050007000000045700000100030001000068008500010090000400',
  'Many solutions': '123456789' + '0'.repeat(72),
};
