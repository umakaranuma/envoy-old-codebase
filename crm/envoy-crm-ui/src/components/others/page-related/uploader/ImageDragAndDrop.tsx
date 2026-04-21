import { useTrans } from '@/helpers/services/lang/langService';
import { useRef, useState } from 'react';

export const ImageDragAndDrop = ({
  htmlFor,
  selectedImage,
  selectedImageSrc,
  className,
  fileType = 'pdf',
  maxSize = 25,
}: {
  htmlFor: string;
  selectedImage?: Function;
  selectedImageSrc?: Function;
  className?: string;
  fileType?: 'pdf' | 'image' | 'excel';
  maxSize?: number;
}) => {
  const t = useTrans('otr.common,be.msg');
  const fileInput = useRef<any>(null);
  const [inputKey, setInputKey] = useState(0);
  const [errors, setErrors] = useState<{ sizeError: boolean; typeError: boolean }>({ sizeError: false, typeError: false });

  const handleDragOver = (e: any) => {
    e.preventDefault();
  };

  const handleDrop = (e: any) => {
    e.preventDefault();
    const files = e.dataTransfer.files[0];
    fileSaver(files);
  };

  const fileSaver = (image: any) => {
    if (selectedImage) {
      selectedImage(image);
    }
    if (selectedImageSrc) {
      const img = URL.createObjectURL(image);
      selectedImageSrc(img);
    }
    setInputKey((prevKey) => prevKey + 1);
  };

  const fileChange = () => {
    const image = fileInput.current.files[0];
    setErrors({ sizeError: false, typeError: false });
    const file: File = fileInput.current.files[0];
    const fileSize = file.size;
    if (fileType === 'image') {
      if (!['image/png', 'image/jpeg', 'image/gif'].includes(file.type)) {
        setErrors((prev) => ({ ...prev, typeError: true }));
        return;
      }
    } else if (fileType === 'pdf' && !['application/pdf'].includes(file.type)) {
      setErrors((prev) => ({ ...prev, typeError: true }));
      return;
    } else if (fileType === 'excel' && !['application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'application/vnd.ms-excel'].includes(file.type)) {
      setErrors((prev) => ({ ...prev, typeError: true }));
      return;
    }
    if (fileSize > maxSize * 1000000) {
      setErrors((prev) => ({ ...prev, sizeError: true }));
      return;
    }
    fileSaver(image);
  };

  return (
    <div>
      <div className={className} style={{ border: '1px solid #ccc', borderRadius: '10px', padding: '7px' }} onDragOver={handleDragOver} onDrop={handleDrop}>
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
            <label role="button" htmlFor={htmlFor} className="text-primary">
              {t('click_to_upload')}
            </label>{' '}
            {t('or_drag_and_drop')}
          </div>
          <div className="fs-10 text-muted py-1">
            {fileType === 'pdf' ? 'PDF' : fileType === 'image' ? 'SVG, PNG,or JPG ' : 'XLSX, DOC, or CSV'} {`(max. ${maxSize}mb)`}
          </div>
        </div>
        <input id={htmlFor} className="d-none" type="file" ref={fileInput} onChange={fileChange} key={inputKey} />
      </div>
      {errors.sizeError && (
        <strong style={{ color: '#dc3545' }} className="fs-13">
          File size exceeds the {maxSize} MB limit.
        </strong>
      )}
      {errors.typeError && (
        <strong style={{ color: '#dc3545' }} className="fs-13">
          Invalid file type. Please upload a valid file.
        </strong>
      )}
    </div>
  );
};
