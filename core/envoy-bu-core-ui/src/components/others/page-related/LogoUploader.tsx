import { useTrans } from '@/helpers/services/lang/langService';
import { Flexicon } from '@apptimus-ui/flexicon';
import { Modal, ModalBody, ModalFooter, ModalHeader } from '@apptimus-ui/modal';
import { Button } from '@apptimus-ui/ui-element';
import React, { useState, useRef, useEffect, useCallback } from 'react';
import Cropper from 'react-easy-crop';
import NextImage from 'next/image';

interface LogoUploaderProps {
  onChange?: (file: File | null) => void;
  initialUrl?: string;
  className?: string;
  dropZoneClassName?: string;
  previewClassName?: string;
  fileName?: string;
  elementId?: string;
  aspectRatio?: number;
  cropShape?: 'rect' | 'round';
  showGrid?: boolean;
  width?: number | string;
  height?: number | string;
}

interface FileObject {
  file?: File;
  url: string;
  name?: string;
}

const LogoUploader: React.FC<LogoUploaderProps> = ({
  onChange = () => {},
  initialUrl,
  className = '',
  dropZoneClassName = '',
  fileName: propFileName = '',
  elementId,
  aspectRatio = 1,
  cropShape = 'round',
  showGrid = false,
  width = '100%',
  height = '100%',
}) => {
  const [originalFile, setOriginalFile] = useState<FileObject | null>(null);
  const [croppingFile, setCroppingFile] = useState<FileObject | null>(null);
  const [fileBeforeCrop, setFileBeforeCrop] = useState<FileObject | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [fileName, setFileName] = useState(propFileName);
  const [crop, setCrop] = useState({ x: 0, y: 0 });
  const [zoom, setZoom] = useState(1);
  const [rotation, setRotation] = useState(0);
  const [croppedAreaPixels, setCroppedAreaPixels] = useState<Area | null>(null);
  const [showCropControls, setShowCropControls] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const t = useTrans('otr.common,be.msg');

  const maxSizeMB = 300;

  const handleFile = (selectedFiles: FileList | null) => {
    if (!selectedFiles || selectedFiles.length === 0) return;

    const selectedFile = selectedFiles[0];

    if (!selectedFile.type.startsWith('image/')) {
      setError('Please select an image file');
      return;
    }

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

    setFileBeforeCrop(originalFile);
    setCroppingFile(fileObj);
    setFileName(selectedFile.name.replace(/\.[^/.]+$/, ''));
    setShowCropControls(true);
  };

  const handleClick = () => {
    fileInputRef.current?.click();
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    handleFile(e.target.files);
    if (e.target) e.target.value = '';
  };

  const onCropComplete = useCallback((_: Area, croppedAreaPixels: Area) => {
    setCroppedAreaPixels(croppedAreaPixels);
  }, []);

  const showCroppedImage = useCallback(async () => {
    try {
      if (!croppingFile || !croppedAreaPixels) return;

      const croppedImage = await getCroppedImg(croppingFile.url, croppedAreaPixels, rotation);

      const finalFile = {
        ...croppingFile,
        url: croppedImage,
      };

      if (originalFile?.file) {
        URL.revokeObjectURL(originalFile.url);
      }
      if (fileBeforeCrop?.file) {
        URL.revokeObjectURL(fileBeforeCrop.url);
      }

      setOriginalFile(finalFile);
      setShowCropControls(false);
      setFileBeforeCrop(null);

      if (croppingFile.file) {
        URL.revokeObjectURL(croppingFile.url);
        const response = await fetch(croppedImage);
        const blob = await response.blob();
        const croppedFile = new File([blob], croppingFile.file.name, {
          type: croppingFile.file.type,
        });
        onChange(croppedFile);
      }
    } catch (e) {
      console.error('Error cropping image', e);
    } finally {
      setCroppingFile(null);
    }
  }, [croppedAreaPixels, rotation, croppingFile, originalFile, fileBeforeCrop, onChange]);

  const handleCancelCrop = useCallback(() => {
    if (croppingFile) {
      setOriginalFile({
        file: croppingFile.file,
        url: croppingFile.url,
        name: croppingFile.name,
      });

      setCroppingFile(null);
      setShowCropControls(false);

      if (croppingFile.file) {
        onChange(croppingFile.file);
      }
    }

    setCrop({ x: 0, y: 0 });
    setZoom(1);
    setRotation(0);
    setCroppedAreaPixels(null);
  }, [croppingFile, onChange]);

  const handleDeleteAndReplace = (e: React.MouseEvent) => {
    e.stopPropagation();

    const input = document.createElement('input');
    input.type = 'file';
    input.accept = 'image/*';
    input.style.display = 'none';

    input.onchange = (event) => {
      const files = (event.target as HTMLInputElement).files;
      if (files && files.length > 0) {
        handleFile(files);
      }
      document.body.removeChild(input);
    };

    document.body.appendChild(input);
    input.click();
  };

  useEffect(() => {
    return () => {
      if (originalFile?.file) {
        URL.revokeObjectURL(originalFile.url);
      }
      if (croppingFile?.file) {
        URL.revokeObjectURL(croppingFile.url);
      }
      if (fileBeforeCrop?.file) {
        URL.revokeObjectURL(fileBeforeCrop.url);
      }
    };
  }, [originalFile, croppingFile, fileBeforeCrop]);

  useEffect(() => {
    if (initialUrl) {
      const urlParts = initialUrl.split('/');
      const urlFileName = urlParts[urlParts.length - 1];
      setOriginalFile({
        url: initialUrl,
        name: urlFileName,
      });
      setFileName(urlFileName.replace(/\.[^/.]+$/, ''));
    } else {
      setOriginalFile(null);
      setCroppingFile(null);
      setFileBeforeCrop(null);
      setFileName('');
      setShowCropControls(false);
    }
  }, [initialUrl]);

  useEffect(() => {
    if (propFileName !== fileName) {
      setFileName(propFileName);
    }
  }, [propFileName]);

  const renderPreview = () => {
    if (!originalFile) return null;

    return (
      <div className="d-flex flex-column align-items-center">
        <div className="position-relative d-inline-block">
          <div
            className={`${cropShape === 'round' ? 'rounded-circle' : 'rounded-3'} overflow-hidden border border-2 border-primary shadow-sm`}
            style={{
              width: typeof width === 'number' ? `${width}px` : width,
              height: typeof height === 'number' ? `${height}px` : height,
            }}
          >
            <NextImage
              src={originalFile.url}
              alt="Logo preview"
              width={typeof width === 'number' ? width : 400}
              height={typeof height === 'number' ? height : 400}
              style={{
                width: '100%',
                height: '100%',
                objectFit: 'cover',
              }}
              unoptimized={originalFile.url.startsWith('blob:')}
            />
          </div>

          <button
            onClick={(e) => {
              e.preventDefault();
              handleDeleteAndReplace(e);
            }}
            className="position-absolute bg-white border border-2 border-primary rounded-circle d-flex align-items-center justify-content-center shadow-sm"
            style={{
              width: '28px',
              height: '28px',
              bottom: '-6px',
              right: '-6px',
              cursor: 'pointer',
            }}
            aria-label="Replace logo"
          >
            <Flexicon icon="pencil-line" variant="line" size={14} className="text-primary" />
          </button>
        </div>
      </div>
    );
  };

  const renderCropControls = () => {
    if (!croppingFile || !showCropControls) return null;

    return (
      <Modal isOpen={showCropControls} onBackdrop={handleCancelCrop}>
        <ModalHeader title="" onClose={handleCancelCrop} />
        <ModalBody>
          <div className="mt-3">
            <div
              style={{
                position: 'relative',
                height: '300px',
                width: '100%',
              }}
            >
              <Cropper
                image={croppingFile.url}
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
          </div>
        </ModalBody>
        <ModalFooter>
          <div className="d-flex justify-content-end gap-2">
            <Button text={t('cancel')} color="light" width="sm" onClick={handleCancelCrop} />
            <Button text={t('apply_crop')} type="submit" width="sm" onClick={showCroppedImage} />
          </div>
        </ModalFooter>
      </Modal>
    );
  };

  const renderDropZoneContent = () => {
    return (
      <div>
        <div
          className="d-flex align-items-center justify-content-center border border-2 border-dashed border-primary rounded-3 bg-light bg-opacity-50 shadow-sm transition-all hover:shadow-md"
          style={{
            width: typeof width === 'number' ? `${width}px` : width,
            height: typeof height === 'number' ? `${height}px` : height,
          }}
        >
          <svg width="28" height="28" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" className="text-primary">
            <path d="M12 5V19M5 12H19" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
        </div>
        {error && <div className="text-danger mt-2 fs-12 text-center">{error}</div>}
      </div>
    );
  };

  return (
    <div className={`${className}`} id={elementId}>
      {originalFile && <div className="d-flex flex-wrap justify-content-start">{renderPreview()}</div>}

      {showCropControls && renderCropControls()}

      {!originalFile && (
        <div>
          <input type="file" ref={fileInputRef} accept="image/*" onChange={handleChange} className="d-none pointer" aria-hidden="true" disabled={!!croppingFile && showCropControls} />
          <div onClick={handleClick} className={`pointer ${dropZoneClassName}`} role="button" aria-label="Image upload area" tabIndex={0}>
            {renderDropZoneContent()}
          </div>
        </div>
      )}
    </div>
  );
};

export default LogoUploader;

async function getCroppedImg(imageSrc: string, pixelCrop: Area, rotation = 0): Promise<string> {
  const image = await createImage(imageSrc);
  const canvas = document.createElement('canvas');
  const ctx = canvas.getContext('2d');

  if (!ctx) {
    throw new Error('Could not create canvas context');
  }

  const maxSize = Math.max(image.width, image.height);
  const safeArea = 2 * ((maxSize / 2) * Math.sqrt(2));

  canvas.width = safeArea;
  canvas.height = safeArea;

  ctx.translate(safeArea / 2, safeArea / 2);
  ctx.rotate((rotation * Math.PI) / 180);
  ctx.translate(-safeArea / 2, -safeArea / 2);

  ctx.drawImage(image, safeArea / 2 - image.width / 2, safeArea / 2 - image.height / 2);

  const data = ctx.getImageData(0, 0, safeArea, safeArea);

  canvas.width = pixelCrop.width;
  canvas.height = pixelCrop.height;

  ctx.putImageData(data, Math.round(0 - safeArea / 2 + image.width / 2 - pixelCrop.x), Math.round(0 - safeArea / 2 + image.height / 2 - pixelCrop.y));

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
    const image = new window.Image();
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
