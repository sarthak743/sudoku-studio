import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import NumPad from '../src/components/NumPad';
describe('NumPad', () => {
  it('is a 3x3 grid ordered 1-9', () => {
    render(<NumPad onDigit={() => {}} onClear={() => {}} disabled={false} />);
    const pad = screen.getByTestId('numpad');
    expect(pad.className).toContain('grid-cols-3'); expect(pad.className).toContain('grid-rows-3');
    expect(Array.from(pad.querySelectorAll('button')).map((b) => b.textContent)).toEqual(['1','2','3','4','5','6','7','8','9']);
  });
  it('fires callbacks and respects disabled', async () => {
    const f = vi.fn(); const { rerender } = render(<NumPad onDigit={f} onClear={() => {}} disabled={false} />);
    await userEvent.click(screen.getByLabelText('Enter 7')); expect(f).toHaveBeenCalledWith(7);
    rerender(<NumPad onDigit={f} onClear={() => {}} disabled />); expect(screen.getByLabelText('Enter 7')).toBeDisabled();
  });
});
