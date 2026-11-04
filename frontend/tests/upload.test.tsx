import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import ImageUpload from '../src/components/ImageUpload';
import App from '../src/App';

function createMockFile(name: string, sizeBytes: number, mimeType: string): File {
  const content = new Uint8Array(sizeBytes);
  return new File([content], name, { type: mimeType });
}

describe('ImageUpload Component', () => {
  beforeEach(() => {
    // Mock FileReader for jsdom
    class MockFileReader {
      result: string | null = null;
      onload: (() => void) | null = null;
      onerror: (() => void) | null = null;
      readAsDataURL() {
        this.result = 'data:image/png;base64,mockImageData';
        setTimeout(() => this.onload?.(), 10);
      }
    }
    vi.stubGlobal('FileReader', MockFileReader);
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('renders the empty dropzone with format and size requirements', () => {
    render(<ImageUpload />);
    expect(screen.getByTestId('upload-dropzone')).toBeInTheDocument();
    expect(screen.getByText(/Choose an image or drag & drop/i)).toBeInTheDocument();
    expect(screen.getByText(/Supports JPG, JPEG, PNG, WEBP · Up to 5 MB/i)).toBeInTheDocument();
  });

  it('selects and loads a valid image file via the file input', async () => {
    render(<ImageUpload />);
    const file = createMockFile('sudoku_puzzle.png', 1024 * 50, 'image/png');
    const input = screen.getByTestId('image-file-input');

    fireEvent.change(input, { target: { files: [file] } });

    await waitFor(() => {
      expect(screen.getByTestId('image-preview')).toBeInTheDocument();
    });

    expect(screen.getByText('sudoku_puzzle.png')).toBeInTheDocument();
    expect(screen.getByText('(50.0 KB)')).toBeInTheDocument();
  });

  it('supports drag-and-drop file upload', async () => {
    render(<ImageUpload />);
    const dropzone = screen.getByTestId('upload-dropzone');
    const file = createMockFile('board.jpg', 1024 * 120, 'image/jpeg');

    fireEvent.dragOver(dropzone);
    expect(screen.getByText('Drop image here')).toBeInTheDocument();

    fireEvent.drop(dropzone, {
      dataTransfer: { files: [file] },
    });

    await waitFor(() => {
      expect(screen.getByTestId('image-preview')).toBeInTheDocument();
    });
    expect(screen.getByText('board.jpg')).toBeInTheDocument();
  });

  it('rejects unsupported file formats with a clear error message', async () => {
    render(<ImageUpload />);
    const file = createMockFile('document.pdf', 1024 * 10, 'application/pdf');
    const input = screen.getByTestId('image-file-input');

    fireEvent.change(input, { target: { files: [file] } });

    await waitFor(() => {
      expect(screen.getByTestId('upload-error')).toBeInTheDocument();
    });
    expect(screen.getByText(/Unsupported format/i)).toBeInTheDocument();
  });

  it('rejects oversized files exceeding 5 MB with a clear error message', async () => {
    render(<ImageUpload />);
    const oversizedFile = createMockFile('huge.png', 6 * 1024 * 1024, 'image/png');
    const input = screen.getByTestId('image-file-input');

    fireEvent.change(input, { target: { files: [oversizedFile] } });

    await waitFor(() => {
      expect(screen.getByTestId('upload-error')).toBeInTheDocument();
    });
    expect(screen.getByText(/File is too large/i)).toBeInTheDocument();
    expect(screen.getByText(/Maximum allowed size is 5 MB/i)).toBeInTheDocument();
  });

  it('rotates the image 90 degrees clockwise on each Rotate button click', async () => {
    render(<ImageUpload />);
    const file = createMockFile('puzzle.png', 1024 * 20, 'image/png');
    fireEvent.change(screen.getByTestId('image-file-input'), { target: { files: [file] } });

    await waitFor(() => {
      expect(screen.getByTestId('image-preview')).toBeInTheDocument();
    });

    const rotateBtn = screen.getByRole('button', { name: /Rotate image 90 degrees clockwise/i });

    // Rotate 1: 90 deg
    await userEvent.click(rotateBtn);
    expect(screen.getByTestId('image-preview')).toHaveStyle('transform: rotate(90deg)');
    expect(screen.getByText('Rotated 90°')).toBeInTheDocument();

    // Rotate 2: 180 deg
    await userEvent.click(rotateBtn);
    expect(screen.getByTestId('image-preview')).toHaveStyle('transform: rotate(180deg)');
    expect(screen.getByText('Rotated 180°')).toBeInTheDocument();

    // Rotate 3: 270 deg
    await userEvent.click(rotateBtn);
    expect(screen.getByTestId('image-preview')).toHaveStyle('transform: rotate(270deg)');
    expect(screen.getByText('Rotated 270°')).toBeInTheDocument();

    // Rotate 4: 360 -> 0 deg
    await userEvent.click(rotateBtn);
    expect(screen.getByTestId('image-preview')).toHaveStyle('transform: rotate(0deg)');
  });

  it('allows replacing the current image with a new one', async () => {
    render(<ImageUpload />);
    const file1 = createMockFile('photo1.jpg', 1024 * 30, 'image/jpeg');
    fireEvent.change(screen.getByTestId('image-file-input'), { target: { files: [file1] } });

    await waitFor(() => {
      expect(screen.getByText('photo1.jpg')).toBeInTheDocument();
    });

    // Replace with photo2
    const file2 = createMockFile('photo2.webp', 1024 * 45, 'image/webp');
    fireEvent.change(screen.getByTestId('image-file-input'), { target: { files: [file2] } });

    await waitFor(() => {
      expect(screen.getByText('photo2.webp')).toBeInTheDocument();
    });
    expect(screen.queryByText('photo1.jpg')).not.toBeInTheDocument();
  });

  it('removes the image and returns to empty dropzone on Remove click', async () => {
    render(<ImageUpload />);
    const file = createMockFile('test.png', 1024 * 15, 'image/png');
    fireEvent.change(screen.getByTestId('image-file-input'), { target: { files: [file] } });

    await waitFor(() => {
      expect(screen.getByTestId('image-preview')).toBeInTheDocument();
    });

    const removeBtn = screen.getByRole('button', { name: /Remove image/i });
    await userEvent.click(removeBtn);

    expect(screen.queryByTestId('image-preview')).not.toBeInTheDocument();
    expect(screen.getByTestId('upload-dropzone')).toBeInTheDocument();
  });
});

describe('App Integration - Upload Sudoku Image Workflow', () => {
  it('switches to the Upload workspace and preserves board state', async () => {
    render(<App />);

    // Load easy sample
    const easyBtn = screen.getByRole('button', { name: 'Easy' });
    await userEvent.click(easyBtn);

    // Click "Upload Image"
    const uploadBtn = screen.getByRole('button', { name: /Upload Sudoku Image/i });
    await userEvent.click(uploadBtn);

    // Verify upload workspace is visible
    expect(screen.getByRole('heading', { name: 'Upload Sudoku Image' })).toBeInTheDocument();
    expect(screen.getByTestId('upload-dropzone')).toBeInTheDocument();

    // Verify interactive board companion is also present
    expect(screen.getByText(/Interactive Board/i)).toBeInTheDocument();

    // Switch back to board
    const backBtn = screen.getByRole('button', { name: 'Back to Board' });
    await userEvent.click(backBtn);

    // Board and solvers results are back, puzzle state preserved
    expect(screen.getByRole('button', { name: /Solve/i })).toBeInTheDocument();
    expect(screen.getByRole('grid', { name: 'Sudoku board' })).toBeInTheDocument();
  });
});
