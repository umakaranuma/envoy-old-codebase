import { useTrans } from '@/helpers/services/lang/langService';
import { Button, Label } from '@apptimus-ui/ui-element';
import React, { useState, useRef, useEffect, useCallback } from 'react';
import Cropper from 'react-easy-crop';

interface FilePreviewerProps {
  onChange?: (file: File | null) => void;
  initialUrl?: string;
  className?: string;
  dropZoneClassName?: string;
  previewClassName?: string;
  onDelete?: () => void;
  fileName?: string;
  label?: string;
  isRequired?: boolean;
  elementId?: string;
  aspectRatio?: number;
  cropShape?: 'rect' | 'round';
  showGrid?: boolean;
}

interface FileObject {
  file?: File;
  url: string;
  name?: string;
}

const FilePreviewer: React.FC<FilePreviewerProps> = ({
  onChange = () => {},
  initialUrl,
  className = '',
  dropZoneClassName = '',
  previewClassName = '',
  onDelete,
  fileName: propFileName = '',
  isRequired,
  label,
  elementId,
  aspectRatio = 4 / 3,
  cropShape = 'rect',
  showGrid = false,
}) => {
  const [file, setFile] = useState<FileObject | null>(null);
  const [dragOver, setDragOver] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [fileName, setFileName] = useState(propFileName);
  const [crop, setCrop] = useState({ x: 0, y: 0 });
  const [zoom, setZoom] = useState(1);
  const [rotation, setRotation] = useState(0);
  const [croppedAreaPixels, setCroppedAreaPixels] = useState<Area | null>(null);
  const [showCropControls, setShowCropControls] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const t = useTrans('otr.common,be.msg');

  const maxSizeMB = 30;

  const handleFile = (selectedFiles: FileList | null) => {
    if (!selectedFiles || selectedFiles.length === 0) return;

    const selectedFile = selectedFiles[0];

    // Validate file type
    if (!selectedFile.type.startsWith('image/')) {
      setError('Please select an image file');
      return;
    }

    // Validate file size
    if (selectedFile.size > maxSizeMB * 1024 * 1024) {
      setError(`Image size exceeds ${maxSizeMB}MB limit`);
      return;
    }

    setError(null);
    const fileObj = {
      file: selectedFile,
      url: URL.createObjectURL(selectedFile),
      name: selectedFile.name,
    };

    setFile(fileObj);
    setFileName(selectedFile.name.replace(/\.[^/.]+$/, '')); // Set name without extension
    setShowCropControls(true);
    onChange(selectedFile);
  };

  const handleClick = () => {
    fileInputRef.current?.click();
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    handleFile(e.target.files);
    if (e.target) e.target.value = '';
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setDragOver(false);
    handleFile(e.dataTransfer.files);
  };

  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setDragOver(true);
  };

  const handleDragLeave = () => {
    setDragOver(false);
  };

  const onCropComplete = useCallback((_: Area, croppedAreaPixels: Area) => {
    setCroppedAreaPixels(croppedAreaPixels);
  }, []);

  const showCroppedImage = useCallback(async () => {
    try {
      if (!file || !croppedAreaPixels) return;

      const croppedImage = await getCroppedImg(file.url, croppedAreaPixels, rotation);

      // Update the file URL with the cropped version
      const updatedFile = {
        ...file,
        url: croppedImage,
      };

      setFile(updatedFile);
      setShowCropControls(false);

      // If we have the original file, we should create a new File object with the cropped image
      if (file.file) {
        const response = await fetch(croppedImage);
        const blob = await response.blob();
        const croppedFile = new File([blob], file.file.name, {
          type: file.file.type,
        });
        onChange(croppedFile);
      }
    } catch (e) {
      console.error('Error cropping image', e);
    }
  }, [croppedAreaPixels, rotation, file, onChange]);

  const handleDelete = () => {
    if (onDelete) {
      onDelete();
    }
    setFile(null);
    setFileName('');
    setError(null);
    setShowCropControls(false);
    onChange(null);
  };

  // Clean up object URL
  useEffect(() => {
    return () => {
      if (file?.file) {
        URL.revokeObjectURL(file.url);
      }
    };
  }, [file]);

  // Handle initial URL and reset when initialUrl changes
  useEffect(() => {
    if (initialUrl) {
      // Extract filename from URL
      const urlParts = initialUrl.split('/');
      const urlFileName = urlParts[urlParts.length - 1];

      // Create a file object without the File instance
      setFile({
        url: initialUrl,
        name: urlFileName,
      });

      // Set initial filename without extension
      setFileName(urlFileName.replace(/\.[^/.]+$/, ''));
    } else {
      // Clear the file if initialUrl is removed
      setFile(null);
      setFileName('');
      setShowCropControls(false);
    }
  }, [initialUrl]);

  // Sync prop filename with state
  useEffect(() => {
    if (propFileName !== fileName) {
      setFileName(propFileName);
    }
  }, [propFileName]);

  const renderPreview = () => {
    if (!file) return null;

    return (
      <div className={`position-relative ${previewClassName}`} style={{ display: 'inline-block', margin: '10px' }}>
        <img src={file.url} alt="Preview" className="img-fluid rounded" style={{ maxHeight: '300px', maxWidth: '100%' }} />
        <button
          onClick={(e) => {
            e.stopPropagation();
            handleDelete();
          }}
          className="position-absolute top-0 end-0 btn btn-danger btn-sm rounded-circle"
          style={{ transform: 'translate(30%, -30%)' }}
          aria-label="Remove image"
        >
          ×
        </button>
      </div>
    );
  };

  const renderCropControls = () => {
    if (!file || !showCropControls) return null;

    return (
      <div className="mt-3">
        <div style={{ position: 'relative', height: '300px', width: '100%' }}>
          <Cropper
            image={file.url}
            crop={crop}
            zoom={zoom}
            rotation={rotation}
            aspect={aspectRatio}
            onCropChange={setCrop}
            onCropComplete={onCropComplete}
            onZoomChange={setZoom}
            onRotationChange={setRotation}
            cropShape={cropShape}
            showGrid={showGrid}
          />
        </div>
        <div className="mt-3">
          <div className="d-flex justify-content-end gap-2">
            <Button text={t('cancel')} color="light" width="sm" onClick={() => setShowCropControls(false)} />
            <Button text={t('apply_crop')} type="submit" width="sm" onClick={showCroppedImage} />
          </div>
        </div>
      </div>
    );
  };

  const renderDropZoneContent = () => {
    if (file) {
      return <div>{showCropControls ? renderCropControls() : <div className="d-flex flex-wrap justify-content-center">{renderPreview()}</div>}</div>;
    }

    return (
      <div className="d-flex flex-column justify-content-center">
        <div className="text-center">
          <div className="my-3">
            <svg className="shadow-sm p-1 rounded-1 border" xmlns="http://www.w3.org/2000/svg" width="26" height="26" viewBox="0 0 24 24" fill="none">
              <path
                d="M8 16L12 12M12 12L16 16M12 12V21M20 16.7428C21.2215 15.734 22 14.2079 22 12.5C22 9.46243 19.5376 7 16.5 7C16.2815 7 16.0771 6.886 15.9661 6.69774C14.6621 4.48484 12.2544 3 9.5 3C5.35786 3 2 6.35786 2 10.5C2 12.5661 2.83545 14.4371 4.18695 15.7935"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
          </div>
          <div className="fw-medium text-muted fs-12 ">
            <label role="button" className="text-primary">
              {t('click_to_upload')}
            </label>{' '}
            {t('or_drag_and_drop')}
          </div>
          <div className="fs-10 text-muted py-1">SVG, PNG, JPG or GIF (max. 800x400px)</div>
        </div>
        {error && <div className="text-danger mt-2">{error}</div>}
      </div>
    );
  };

  return (
    <div className={`${className}`} id={elementId}>
      {label && <Label label={label} isRequired={isRequired} />}
      <input type="file" ref={fileInputRef} accept="image/*" onChange={handleChange} className="d-none pointer" aria-hidden="true" disabled={!!file && showCropControls} />

      <div
        onClick={handleClick}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        className={`border border-2 border-primary pointer rounded py-4 px-2 text-center ${dragOver ? 'bg-light' : 'bg-white'} ${dropZoneClassName}`}
        role="button"
        aria-label="Image upload area"
        tabIndex={0}
      >
        {renderDropZoneContent()}
      </div>
    </div>
  );
};

export default FilePreviewer;

// cropImage.ts
export async function getCroppedImg(imageSrc: string, pixelCrop: Area, rotation = 0): Promise<string> {
  const image = await createImage(imageSrc);
  const canvas = document.createElement('canvas');
  const ctx = canvas.getContext('2d');

  if (!ctx) {
    throw new Error('Could not create canvas context');
  }

  const maxSize = Math.max(image.width, image.height);
  const safeArea = 2 * ((maxSize / 2) * Math.sqrt(2));

  // Set canvas dimensions
  canvas.width = safeArea;
  canvas.height = safeArea;

  // Translate to center of canvas
  ctx.translate(safeArea / 2, safeArea / 2);
  ctx.rotate((rotation * Math.PI) / 180);
  ctx.translate(-safeArea / 2, -safeArea / 2);

  // Draw image centered on canvas
  ctx.drawImage(image, safeArea / 2 - image.width / 2, safeArea / 2 - image.height / 2);

  // Get the cropped image data
  const data = ctx.getImageData(0, 0, safeArea, safeArea);

  // Set canvas width to final desired crop size
  canvas.width = pixelCrop.width;
  canvas.height = pixelCrop.height;

  // Paste the generated rotated image with correct offsets for x,y crop values
  ctx.putImageData(data, Math.round(0 - safeArea / 2 + image.width / 2 - pixelCrop.x), Math.round(0 - safeArea / 2 + image.height / 2 - pixelCrop.y));

  // Return as a blob URL
  return new Promise((resolve) => {
    canvas.toBlob(
      (blob) => {
        if (!blob) {
          console.error('Canvas is empty');
          return;
        }
        resolve(URL.createObjectURL(blob));
      },
      'image/jpeg',
      0.9,
    );
  });
}

function createImage(url: string): Promise<HTMLImageElement> {
  return new Promise((resolve, reject) => {
    const image = new Image();
    image.addEventListener('load', () => resolve(image));
    image.addEventListener('error', (error) => reject(error));
    image.setAttribute('crossOrigin', 'anonymous');
    image.src = url;
  });
}

export type Area = {
  width: number;
  height: number;
  x: number;
  y: number;
};
