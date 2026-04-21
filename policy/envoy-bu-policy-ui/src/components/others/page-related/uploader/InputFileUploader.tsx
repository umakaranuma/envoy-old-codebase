import { Input } from '@apptimus-ui/ui-element';
import React, { useRef, useState } from 'react';

function InputFileUploader({
  data,
  className,
  name,
  fileType = 'pdf',
  maxSize = 25,
}: {
  data: (file: File) => void;
  className?: string;
  name?: string;
  fileType?: 'pdf' | 'image' | 'excel';
  maxSize?: number;
}) {
  const [errors, setErrors] = useState<{ sizeError: boolean; typeError: boolean }>({ sizeError: false, typeError: false });
  const fileInput = useRef<any>(null);

  const fileChange = () => {
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
    data(file);
  };
  return (
    <>
      <Input type="file" ref={fileInput} onChange={() => fileChange()} className={className} name={name} />
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
    </>
  );
}

export default InputFileUploader;
