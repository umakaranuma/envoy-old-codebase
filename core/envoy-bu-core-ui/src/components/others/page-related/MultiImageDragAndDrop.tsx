import { useCallback, useRef, useState } from 'react';
import Cropper, { Area } from 'react-easy-crop';

interface CroppedArea extends Area {
  photo?: string;
}

const SingleImageUpload = ({ onUpload, onCancel }: { onUpload: (file: File) => Promise<void>; onCancel: () => void }) => {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [imageSrc, setImageSrc] = useState<string | null>(null);
  const [crop, setCrop] = useState({ x: 0, y: 0 });
  const [zoom, setZoom] = useState(1);
  const [croppedArea, setCroppedArea] = useState<CroppedArea | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  // Handle file selection
  const onFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      const file = e.target.files[0];
      const reader = new FileReader();
      reader.addEventListener('load', () => {
        setImageSrc(reader.result as string);
      });
      reader.readAsDataURL(file);
    }
  };

  // Handle crop completion
  const onCropComplete = useCallback((_: Area, croppedAreaPixels: Area) => {
    setCroppedArea(croppedAreaPixels);
  }, []);

  // Trigger file input click
  const triggerFileInput = () => {
    fileInputRef.current?.click();
  };

  // Remove selected image
  const removeImage = () => {
    setImageSrc(null);
    setCroppedArea(null);
  };

  // Process and upload the cropped image
  const handleUpload = async () => {
    if (!imageSrc || !croppedArea) return;

    setIsLoading(true);
    try {
      // Create canvas to get cropped image
      const canvas = document.createElement('canvas');
      const image = new Image();
      image.src = imageSrc;

      await new Promise((resolve) => {
        image.onload = resolve;
      });

      canvas.width = croppedArea.width;
      canvas.height = croppedArea.height;
      const ctx = canvas.getContext('2d');

      if (!ctx) return;

      ctx.drawImage(image, croppedArea.x, croppedArea.y, croppedArea.width, croppedArea.height, 0, 0, croppedArea.width, croppedArea.height);

      // Convert canvas to blob
      canvas.toBlob(
        async (blob) => {
          if (blob) {
            const file = new File([blob], 'cropped-image.jpg', { type: 'image/jpeg' });
            await onUpload(file);
          }
        },
        'image/jpeg',
        0.9,
      );
    } catch (error) {
      console.error('Error cropping image:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="image-upload-container">
      {/* Hidden file input */}
      <input type="file" ref={fileInputRef} onChange={onFileChange} accept="image/*" style={{ display: 'none' }} />

      {!imageSrc ? (
        /* Upload area when no image is selected */
        <div className="upload-area" onClick={triggerFileInput}>
          <svg viewBox="0 0 24 24" width="48" height="48">
            <path d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z" />
          </svg>
          <p>Click to select an image</p>
          <p className="hint">(JPG, PNG, max 5MB)</p>
        </div>
      ) : (
        /* Cropping interface when image is selected */
        <div className="cropping-interface">
          <div className="crop-container">
            <Cropper
              image={imageSrc}
              crop={crop}
              zoom={zoom}
              aspect={1} // Square aspect ratio
              onCropChange={setCrop}
              onZoomChange={setZoom}
              onCropComplete={onCropComplete}
            />
          </div>

          <div className="controls">
            <button onClick={removeImage} className="secondary-button">
              Change Image
            </button>
            <div className="zoom-control">
              <label>Zoom:</label>
              <input type="range" min="1" max="3" step="0.1" value={zoom} onChange={(e) => setZoom(Number(e.target.value))} />
            </div>
          </div>

          <div className="action-buttons">
            <button onClick={onCancel} className="cancel-button">
              Cancel
            </button>
            <button onClick={handleUpload} disabled={!croppedArea || isLoading} className="upload-button">
              {isLoading ? 'Uploading...' : 'Upload Image'}
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default SingleImageUpload;
