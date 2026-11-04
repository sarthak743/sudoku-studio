import { render, screen } from '@testing-library/react';
import Results from '../src/components/Results';
const r = { status: 'multiple' as const, solution_count: 2, solutions: ['a', 'b'], count_capped: false, timed_out: false, time_ms: 1.2, nodes_visited: 10, backtracks: 2, algorithm: 'A2' };
describe('Results', () => {
  it('shows pagination for multiple solutions', () => {
    render(<Results panel={{ kind: 'solve', outcome: { result: r, runs: [] } }} index={0} onIndex={() => {}} onSample={() => {}} />);
    expect(screen.getByText(/Solution 1 of 2/)).toBeInTheDocument(); expect(screen.getByText('Previous').closest('button')).toBeDisabled();
  });
  it('shows timeout state', () => {
    render(<Results panel={{ kind: 'solve', outcome: { result: { ...r, status: 'timeout', solutions: [] }, runs: [] } }} index={0} onIndex={() => {}} onSample={() => {}} />);
    expect(screen.getByText('Timed out')).toBeInTheDocument();
  });
});
