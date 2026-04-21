'use client';
import { Modal, ModalBody, ModalFooter } from '@apptimus-ui/modal';
import { Button } from '@apptimus-ui/ui-element';
import { useCallback, useState } from 'react';
import Cropper, { Area } from 'react-easy-crop';
import helper from './helper';

const ImageCropper = ({ isOpen, imageSrc, croppedImageSrc, size = 1 / 1, croppedImage }: { isOpen: boolean; imageSrc: string; size?: number; croppedImage?: Function; croppedImageSrc: Function }) => {
  const [crop, setCrop] = useState({ x: 0, y: 0 });
  const [zoom, setZoom] = useState(1);
  const [croppedAreaPixels, setCroppedAreaPixels] = useState<Area | null>(null);

  const onCropCompleteHandler = useCallback((_croppedArea: Area, croppedAreaPixels: Area) => {
    setCroppedAreaPixels(croppedAreaPixels);
  }, []);

  const onCropComplete = (croppedObject: any) => {
    if (croppedImage) {
      const file = new File([croppedObject], `${'image_' + Date.now()}.jpeg`, { type: 'image/jpeg' });
      croppedImage(file);
    }
    const url = URL.createObjectURL(croppedObject);
    croppedImageSrc(url);
  };

  const handleCrop = useCallback(async () => {
    if (!croppedAreaPixels) return;
    const croppedImage = await helper(imageSrc, croppedAreaPixels);
    onCropComplete(croppedImage);
  }, [croppedAreaPixels, imageSrc, onCropComplete]);

  return (
    <Modal isOpen={isOpen} position="center">
      <ModalBody>
        <div style={{ height: '300px' }}>
          <Cropper image={imageSrc} crop={crop} zoom={zoom} aspect={size} onCropChange={setCrop} onZoomChange={setZoom} onCropComplete={onCropCompleteHandler} />
        </div>
      </ModalBody>
      <ModalFooter>
        <div className="text-center">
          <Button text="Crop" size="sm" width="sm" onClick={handleCrop} />
        </div>
      </ModalFooter>
    </Modal>
  );
};

export default ImageCropper;
