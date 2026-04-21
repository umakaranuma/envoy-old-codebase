import React, { useState } from 'react';
import { ImageDragAndDrop } from './ImageDragAndDrop';
import FilePreviewInput from './FilePreviewInput';

type DefaultValue = { fileName?: string; key: string };

function FileUploader({
  htmlFor = 'document',
  className,
  fileType = 'pdf',
  maximumSize,
  selectedFile,
  variant = 'card',
  name,
  defaultValue,
  onCancel,
}: {
  htmlFor: string;
  className?: string;
  fileType?: 'pdf' | 'image' | 'excel';
  maximumSize?: number;
  selectedFile?: (file: File) => void;
  variant?: 'card' | 'input';
  name?: string;
  defaultValue?: DefaultValue;
  onCancel?: () => void;
}) {
  const [resource, setResource] = useState<File | null>(null);
  return (
    <>
      {defaultValue?.key ? (
        <FilePreviewInput
          fileName={defaultValue.fileName || 'Download'}
          onCancel={() => {
            resource ? setResource(null) : onCancel && onCancel();
          }}
        />
      ) : (
        <>
          {variant === 'card' ? (
            <ImageDragAndDrop
              htmlFor={htmlFor}
              selectedImage={(file: File) => {
                setResource(file);
                if (selectedFile) selectedFile(file);
              }}
              className={className}
              fileType={fileType}
              maxSize={maximumSize}
            />
          ) : (
            <input
              name={name}
              type="file"
              id={htmlFor}
              className={className}
              onChange={(e) => {
                const file = e.target.files?.[0];
                if (file) {
                  setResource(file);
                  if (selectedFile) selectedFile(file);
                }
              }}
            />
          )}
        </>
      )}
    </>
  );
}

export default FileUploader;
