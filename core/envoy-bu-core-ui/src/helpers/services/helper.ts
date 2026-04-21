import { Area } from 'react-easy-crop';

export default function helper(imageSrc: string, pixelCrop: Area): Promise<Blob | null> {
  return new Promise((resolve, reject) => {
    const image = new Image();
    image.src = imageSrc;
    image.onload = () => {
      const canvas = document.createElement('canvas');
      const ctx = canvas.getContext('2d');

      if (!ctx) return null;

      canvas.width = pixelCrop.width;
      canvas.height = pixelCrop.height;

      ctx.drawImage(image, pixelCrop.x, pixelCrop.y, pixelCrop.width, pixelCrop.height, 0, 0, pixelCrop.width, pixelCrop.height);
      canvas.toBlob(
        (blob) => {
          if (!blob) {
            console.error('Canvas is empty');
            return reject(null);
          }
          resolve(blob);
        },
        'image/jpeg',
        0.8, // quality (0–1)
      );
    };
    image.onerror = (error) => reject(error);
  });
}
