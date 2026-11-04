import { findConflicts, fromGridString, toGridString, SAMPLES } from '../src/sudoku';
describe('sudoku helpers', () => {
  it('round-trips grid strings', () => { expect(toGridString(fromGridString(SAMPLES.Easy))).toBe(SAMPLES.Easy); });
  it('sample puzzles have no conflicts', () => { Object.values(SAMPLES).forEach((s) => expect(findConflicts(fromGridString(s)).size).toBe(0)); });
  it('detects row, column and box conflicts', () => {
    const g = Array(81).fill(0); g[0] = 5; g[8] = 5; expect([...findConflicts(g)].sort()).toEqual([0, 8]);
    const c = Array(81).fill(0); c[0] = 3; c[72] = 3; expect(findConflicts(c).size).toBe(2);
    const b = Array(81).fill(0); b[0] = 7; b[20] = 7; expect(findConflicts(b).size).toBe(2);
  });
});
