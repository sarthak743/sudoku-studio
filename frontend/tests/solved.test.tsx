import { render, screen, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import App from '../src/App';
import { fromGridString } from '../src/sudoku';

// A valid complete sudoku grid
const SOLVED_GRID =
  '534678912672195348198342567859761423426853791713924856961537284287419635345286179';

describe('Puzzle Solved Popup', () => {
  it('triggers "Puzzle Solved!" popup in Play mode when the final cell is completed with no conflicts', async () => {
    render(<App />);

    // 1. In Edit Puzzle mode, fill cells 0..79
    const digits = fromGridString(SOLVED_GRID);

    // Let's enter the first 80 digits using keyboard or numpad
    for (let i = 0; i < 80; i++) {
      const cell = screen.getByLabelText(new RegExp(`Row ${Math.floor(i / 9) + 1}, column ${(i % 9) + 1}`));
      fireEvent.mouseDown(cell);
      fireEvent.keyDown(cell.parentElement!, { key: String(digits[i]) });
    }

    // Switch to Play mode
    const playTab = screen.getByRole('tab', { name: 'Play' });
    await userEvent.click(playTab);

    // Grid should not show popup yet
    expect(screen.queryByText('Puzzle Solved!')).not.toBeInTheDocument();

    // Select the 81st cell (Row 9, Column 9)
    const lastCell = screen.getByLabelText(/Row 9, column 9/);
    fireEvent.mouseDown(lastCell);

    // First enter an invalid digit (say 1 instead of 9, causing duplicate conflict)
    fireEvent.keyDown(lastCell.parentElement!, { key: '1' });
    expect(screen.queryByText('Puzzle Solved!')).not.toBeInTheDocument();

    // Now enter the correct digit 9
    fireEvent.keyDown(lastCell.parentElement!, { key: '9' });

    // Popup must appear
    expect(screen.getByText('Puzzle Solved!')).toBeInTheDocument();

    // Close the popup via Continue button
    const continueBtn = screen.getByRole('button', { name: 'Continue' });
    await userEvent.click(continueBtn);
    expect(screen.queryByText('Puzzle Solved!')).not.toBeInTheDocument();

    // Trigger only once per puzzle: changing and re-entering the digit does not re-trigger popup
    fireEvent.keyDown(lastCell.parentElement!, { key: '9' });
    expect(screen.queryByText('Puzzle Solved!')).not.toBeInTheDocument();

    // Resetting the board resets the state
    const resetBtn = screen.getByRole('button', { name: 'Reset all' });
    await userEvent.click(resetBtn);
    const confirmBtn = screen.getByRole('button', { name: 'Yes, reset' });
    await userEvent.click(confirmBtn);
    expect(screen.queryByText('Puzzle Solved!')).not.toBeInTheDocument();

    // Loading a sample puzzle also resets the state
    const easySampleBtn = screen.getByRole('button', { name: 'Easy' });
    await userEvent.click(easySampleBtn);
    expect(screen.queryByText('Puzzle Solved!')).not.toBeInTheDocument();
  });
});
