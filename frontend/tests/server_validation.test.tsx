import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import App from '../src/App';
import * as api from '../src/api';

describe('Server validation grid highlight & API errors', () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('highlights conflicting cells on grid when server validation returns conflicts', async () => {
    vi.spyOn(api, 'validateGrid').mockResolvedValueOnce({
      valid: false,
      conflicts: [
        { row: 0, col: 0 },
        { row: 0, col: 8 },
      ],
    });

    render(<App />);

    // Click "Check with server" (disabled when filled === 0, so load a sample first)
    const easyBtn = screen.getByRole('button', { name: 'Easy' });
    await userEvent.click(easyBtn);

    const checkBtn = screen.getByRole('button', { name: /Check with server/i });
    await userEvent.click(checkBtn);

    // Wait for server response notice
    await waitFor(() => {
      expect(screen.getByText(/Server found 2 conflicting cells/i)).toBeInTheDocument();
    });

    // Check that row 1 col 1 (index 0) and row 1 col 9 (index 8) have conflict styling / accessible label
    const cell0 = screen.getByLabelText(/Row 1, column 1.*conflict/i);
    const cell8 = screen.getByLabelText(/Row 1, column 9.*conflict/i);
    expect(cell0).toBeInTheDocument();
    expect(cell8).toBeInTheDocument();
  });

  it('parses structured backend ErrorResponse messages and details in api.ts', async () => {
    const errorBody = {
      code: 'VALIDATION_ERROR',
      message: 'Request validation failed.',
      details: {
        errors: [{ msg: 'Grid must contain exactly 81 characters.' }],
      },
    };

    vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce({
      ok: false,
      status: 422,
      json: async () => errorBody,
    } as Response);

    await expect(api.validateGrid('short_grid')).rejects.toThrow(
      'Request validation failed. (Grid must contain exactly 81 characters.)'
    );
  });
});
