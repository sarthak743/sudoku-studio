import { useCallback, useRef, useState } from 'react';
import { AlertCircle, FileImage, ImageUp, Info, Loader2, RotateCw, Trash2, Upload } from 'lucide-react';

const VALID_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.webp'];
const VALID_MIME_TYPES = ['image/jpeg', 'image/png', 'image/webp'];
const ACCEPTED_EXT = '.jpg,.jpeg,.png,.webp';
const MAX_SIZE_MB = 5;
const MAX_SIZE_BYTES = MAX_SIZE_MB * 1024 * 1024;

export interface UploadedImage {
  file: File;
  dataUrl: string;
  rotation: number;
}

interface Props {
  onImageChange?: (image: UploadedImage | null) => void;
}

function formatBytes(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
}

function validateFile(file: File): string | null {
  const ext = '.' + file.name.split('.').pop()?.toLowerCase();
  const hasValidExt = VALID_EXTENSIONS.includes(ext);
  const hasValidMime = VALID_MIME_TYPES.includes(file.type.toLowerCase()) || file.type === '';

  if (!hasValidExt && !hasValidMime) {
    return `Unsupported format "${file.name.split('.').pop() || file.type}". Please upload a JPG, JPEG, PNG, or WEBP image.`;
  }
  if (file.size > MAX_SIZE_BYTES) {
    return `File is too large (${formatBytes(file.size)}). Maximum allowed size is ${MAX_SIZE_MB} MB.`;
  }
  return null;
}

function readAsDataUrl(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result as string);
    reader.onerror = () => reject(new Error('Could not read file.'));
    reader.readAsDataURL(file);
  });
}

export default function ImageUpload({ onImageChange }: Props) {
  const [image, setImage] = useState<UploadedImage | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const processFile = useCallback(async (file: File) => {
    setError(null);
    const err = validateFile(file);
    if (err) {
      setError(err);
      return;
    }
    setIsProcessing(true);
    try {
      const dataUrl = await readAsDataUrl(file);
      const newImg: UploadedImage = { file, dataUrl, rotation: 0 };
      setImage(newImg);
      onImageChange?.(newImg);
    } catch {
      setError('Could not read the selected image file. Please try again.');
    } finally {
      setIsProcessing(false);
    }
  }, [onImageChange]);

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) processFile(file);
    e.target.value = '';
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.dataTransfer) {
      e.dataTransfer.dropEffect = 'copy';
    }
    if (!isDragging) setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (!e.currentTarget.contains(e.relatedTarget as Node)) {
      setIsDragging(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
    const file = e.dataTransfer?.files?.[0];
    if (file) processFile(file);
  };

  const handleRotate = () => {
    if (!image) return;
    const nextRotation = (image.rotation + 90) % 360;
    const updated = { ...image, rotation: nextRotation };
    setImage(updated);
    onImageChange?.(updated);
  };

  const handleReplace = () => {
    fileInputRef.current?.click();
  };

  const handleRemove = () => {
    setImage(null);
    setError(null);
    onImageChange?.(null);
  };

  // Processing state
  if (isProcessing) {
    return (
      <div className="panel p-8 text-center rise space-y-3" role="status" aria-live="polite">
        <Loader2 className="mx-auto animate-spin text-acc" size={32} />
        <h3 className="font-serif text-xl">Loading image…</h3>
        <p className="text-xs text-mute">Reading and preparing image preview</p>
      </div>
    );
  }

  // Empty / Drop Zone state
  if (!image) {
    return (
      <div className="space-y-4">
        <div
          role="button"
          tabIndex={0}
          aria-label="Upload Sudoku image. Click or drag and drop a JPG, PNG, or WEBP file up to 5 MB."
          data-testid="upload-dropzone"
          className={`relative flex flex-col items-center justify-center gap-3 rounded-2xl border-2 border-dashed p-8 sm:p-10 text-center cursor-pointer transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-acc ${
            isDragging
              ? 'border-acc bg-hl scale-[1.01]'
              : 'border-line hover:border-mute bg-surf/50 hover:bg-surf2/60'
          }`}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
          onKeyDown={(e) => {
            if (e.key === 'Enter' || e.key === ' ') {
              e.preventDefault();
              fileInputRef.current?.click();
            }
          }}
        >
          <div
            className={`grid place-items-center size-14 rounded-2xl transition-colors ${
              isDragging ? 'bg-acc text-onacc shadow-lg shadow-acc/20' : 'bg-surf2 border border-line text-mute'
            }`}
          >
            {isDragging ? <Upload size={24} /> : <ImageUp size={24} />}
          </div>
          <div>
            <p className={`font-medium text-base ${isDragging ? 'text-acc' : 'text-ink'}`}>
              {isDragging ? 'Drop image here' : 'Choose an image or drag & drop'}
            </p>
            <p className="text-xs text-mute mt-1">Supports JPG, JPEG, PNG, WEBP · Up to {MAX_SIZE_MB} MB</p>
          </div>
          <span className="btn btn-acc text-xs mt-1 pointer-events-none">
            Select from computer
          </span>
          <input
            ref={fileInputRef}
            type="file"
            accept={ACCEPTED_EXT}
            className="sr-only"
            aria-hidden="true"
            onChange={handleFileInput}
            data-testid="image-file-input"
          />
        </div>

        {error && (
          <div
            role="alert"
            data-testid="upload-error"
            className="flex items-start gap-2.5 rounded-lg px-3.5 py-3 text-sm rise border"
            style={{ background: 'var(--badbg)', borderColor: 'var(--bad)', color: 'var(--bad)' }}
          >
            <AlertCircle size={18} className="mt-0.5 shrink-0" />
            <div className="flex-1">
              <div className="font-semibold text-xs uppercase tracking-wide">Upload Error</div>
              <div className="text-xs mt-0.5">{error}</div>
            </div>
          </div>
        )}

        <div className="panel p-3.5 flex items-start gap-3 text-xs text-mute">
          <Info size={16} className="mt-0.5 shrink-0 text-acc" />
          <div className="space-y-1">
            <p className="font-medium text-ink">Image Recognition Integration Pending</p>
            <p>
              Image selection, previewing, and orientation rotation are fully operational.
              Once the computer vision backend service (ADR 0002) is deployed, digit extraction will automatically populate the board.
            </p>
          </div>
        </div>
      </div>
    );
  }

  // Preview & Workspace state
  return (
    <div className="space-y-4 rise">
      <input
        ref={fileInputRef}
        type="file"
        accept={ACCEPTED_EXT}
        className="sr-only"
        aria-hidden="true"
        onChange={handleFileInput}
        data-testid="image-file-input"
      />

      <div
        className="relative overflow-hidden rounded-2xl border border-line bg-surf2 flex items-center justify-center p-3"
        style={{ minHeight: '16rem', maxHeight: '24rem' }}
        data-testid="image-preview-container"
      >
        <img
          src={image.dataUrl}
          alt={`Sudoku puzzle preview: ${image.file.name}`}
          className="max-h-[22rem] w-auto max-w-full object-contain rounded-lg transition-transform duration-300"
          style={{ transform: `rotate(${image.rotation}deg)` }}
          draggable={false}
          data-testid="image-preview"
        />
      </div>

      <div className="panel px-4 py-3 flex flex-wrap items-center justify-between gap-2 text-xs">
        <div className="flex items-center gap-2 min-w-0">
          <FileImage size={15} className="text-acc shrink-0" />
          <span className="font-mono text-ink truncate max-w-[12rem] sm:max-w-xs" title={image.file.name}>
            {image.file.name}
          </span>
          <span className="text-mute">({formatBytes(image.file.size)})</span>
        </div>
        {image.rotation !== 0 && (
          <span className="font-mono text-acc bg-acc/10 border border-acc/20 px-2 py-0.5 rounded text-[11px]">
            Rotated {image.rotation}°
          </span>
        )}
      </div>

      <div className="flex flex-wrap gap-2 items-center">
        <button
          type="button"
          className="btn"
          onClick={handleRotate}
          title="Rotate 90 degrees clockwise"
          aria-label="Rotate image 90 degrees clockwise"
        >
          <RotateCw size={15} /> Rotate
        </button>
        <button
          type="button"
          className="btn"
          onClick={handleReplace}
          title="Choose a different image file"
          aria-label="Replace current image"
        >
          <Upload size={15} /> Replace
        </button>
        <button
          type="button"
          className="btn !text-bad !border-bad/40 hover:!border-bad"
          onClick={handleRemove}
          title="Remove uploaded image"
          aria-label="Remove image"
        >
          <Trash2 size={15} /> Remove
        </button>
      </div>

      {error && (
        <div
          role="alert"
          data-testid="upload-error"
          className="flex items-start gap-2.5 rounded-lg px-3.5 py-3 text-sm rise border"
          style={{ background: 'var(--badbg)', borderColor: 'var(--bad)', color: 'var(--bad)' }}
        >
          <AlertCircle size={18} className="mt-0.5 shrink-0" />
          <div className="flex-1">
            <div className="font-semibold text-xs uppercase tracking-wide">Upload Error</div>
            <div className="text-xs mt-0.5">{error}</div>
          </div>
        </div>
      )}

      <div className="panel p-4 space-y-3">
        <div className="flex items-start gap-2.5 text-xs text-mute">
          <Info size={15} className="mt-0.5 shrink-0 text-acc" />
          <div>
            <p className="font-semibold text-ink">Ready for Recognition</p>
            <p className="mt-0.5">
              Image is prepared and oriented. Automatic digit extraction endpoint will be integrated when backend vision service is available.
            </p>
          </div>
        </div>
        <button
          type="button"
          className="btn btn-acc w-full justify-center"
          disabled
          title="Backend recognition endpoint is not yet implemented"
          aria-label="Extract clues from image (backend recognition pending)"
        >
          <ImageUp size={15} /> Extract clues (Recognition pending)
        </button>
      </div>
    </div>
  );
}
