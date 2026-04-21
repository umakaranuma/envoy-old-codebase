import { Label } from '@apptimus-ui/ui-element';
import React, { useState, useMemo, useRef, useEffect, DragEvent } from 'react';

type FileType = 'All' | 'Image' | 'Video' | 'PDF';

interface FilePreviewerProps {
  fileType?: FileType;
  onChange?: (file: File | null, fileType: FileType) => void;
  initialUrl?: string;
  className?: string;
  dropZoneClassName?: string;
  previewClassName?: string;
  onDelete?: () => void;
  fileName?: string;
  onSave?: () => void;
  label?: string;
  isRequired?: boolean;
  elementId?: string;
}

interface FileObject {
  file?: File;
  url: string;
  type: string;
  id: string;
  name?: string;
}

const FilePreviewer: React.FC<FilePreviewerProps> = ({
  fileType = 'All',
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
}) => {
  const [file, setFile] = useState<FileObject | null>(null);
  const [dragOver, setDragOver] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [fileName, setFileName] = useState(propFileName);
  const [cleared, setCleared] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // SVG Icons
  const FileIcons = {
    image: (
      <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" fill="currentColor" viewBox="0 0 16 16">
        <path d="M6.002 5.5a1.5 1.5 0 1 1-3 0 1.5 1.5 0 0 1 3 0z" />
        <path d="M2.002 1a2 2 0 0 0-2 2v10a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V3a2 2 0 0 0-2-2h-12zm12 1a1 1 0 0 1 1 1v6.5l-3.777-1.947a.5.5 0 0 0-.577.093l-3.71 3.71-2.66-1.772a.5.5 0 0 0-.63.062L1.002 12V3a1 1 0 0 1 1-1h12z" />
      </svg>
    ),
    video: (
      <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" fill="currentColor" viewBox="0 0 16 16">
        <path d="M0 12V4a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2zm6.79-6.907A.5.5 0 0 0 6 5.5v5a.5.5 0 0 0 .79.407l3.5-2.5a.5.5 0 0 0 0-.814l-3.5-2.5z" />
      </svg>
    ),
    pdf: (
      <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" fill="currentColor" viewBox="0 0 16 16">
        <path d="M5.523 10.424c.14-.082.293-.162.459-.238a7.878 7.878 0 0 1-.45.606c-.28.337-.498.516-.635.572a.266.266 0 0 1-.035.012.282.282 0 0 1-.026-.044c-.056-.11-.054-.216.04-.36.106-.165.319-.354.647-.548zm2.455-1.647c-.119.025-.237.05-.356.078a21.035 21.035 0 0 0 .5-1.05 11.96 11.96 0 0 0 .51.858c-.217.032-.436.07-.654.114zm2.525.939a3.888 3.888 0 0 1-.435-.41c.228.005.434.022.612.054.317.057.466.147.518.209a.095.095 0 0 1 .026.064.436.436 0 0 1-.06.2.307.307 0 0 1-.094.124.107.107 0 0 1-.069.015c-.09-.003-.258-.066-.498-.256zM8.278 6.97c-.04.244-.108.524-.2.829a4.86 4.86 0 0 1-.089-.346c-.076-.353-.087-.63-.046-.822.038-.177.11-.248.196-.283a.517.517 0 0 1 .145-.04c.013.03.028.092.032.198.005.122-.007.277-.038.465z" />
        <path
          fillRule="evenodd"
          d="M4 0h8a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V2a2 2 0 0 1 2-2zm.165 11.668c.09.18.23.343.438.419.207.075.412.04.58-.03.318-.13.635-.436.926-.786.333-.401.683-.927 1.021-1.51a11.64 11.64 0 0 1 1.997-.406c.3.383.61.713.91.95.28.22.603.403.934.417a.856.856 0 0 0 .51-.138c.155-.101.27-.247.354-.416.09-.181.145-.37.138-.563a.844.844 0 0 0-.2-.518c-.226-.27-.596-.4-.96-.465a5.76 5.76 0 0 0-1.335-.05 10.954 10.954 0 0 1-.98-1.686c.25-.66.437-1.284.52-1.794.036-.218.055-.426.048-.614a1.238 1.238 0 0 0-.127-.538.7.7 0 0 0-.477-.365c-.202-.043-.41 0-.601.077-.377.15-.576.47-.651.823-.073.34-.04.736.046 1.136.088.406.238.848.43 1.295a19.707 19.707 0 0 1-1.062 2.227 7.662 7.662 0 0 0-1.482.645c-.37.22-.699.48-.897.787-.21.326-.275.714-.08 1.103z"
        />
      </svg>
    ),
    all: (
      <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" fill="currentColor" viewBox="0 0 16 16">
        <path d="M14 4.5V14a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V2a2 2 0 0 1 2-2h5.5L14 4.5zm-3 0A1.5 1.5 0 0 1 9.5 3V1H4a1 1 0 0 0-1 1v12a1 1 0 0 0 1 1h8a1 1 0 0 0 1-1V4.5h-2z" />
      </svg>
    ),
  };

  // Different size limits for each file type
  const fileSizeLimits = {
    Image: 5,
    Video: 100,
    PDF: 100,
    All: 100,
  };

  const acceptType = useMemo(() => {
    switch (fileType) {
      case 'Image':
        return 'image/*';
      case 'Video':
        return 'video/*';
      case 'PDF':
        return 'application/pdf';
      default:
        return 'image/*,video/*,application/pdf';
    }
  }, [fileType]);

  const fileTypeInfo = useMemo(() => {
    switch (fileType) {
      case 'Image':
        return {
          name: 'Image',
          icon: FileIcons.image,
          maxSize: fileSizeLimits.Image,
        };
      case 'Video':
        return {
          name: 'Video',
          icon: FileIcons.video,
          maxSize: fileSizeLimits.Video,
        };
      case 'PDF':
        return {
          name: 'PDF',
          icon: FileIcons.pdf,
          maxSize: fileSizeLimits.PDF,
        };
      default:
        return {
          name: 'File',
          icon: FileIcons.all,
          maxSize: fileSizeLimits.All,
        };
    }
  }, [fileType]);

  const handleFile = (selectedFiles: FileList | null) => {
    if (!selectedFiles || selectedFiles.length === 0) return;

    const selectedFile = selectedFiles[0];
    const maxSizeMB = fileTypeInfo.maxSize;

    // Validate file type
    if (
      (fileType === 'Image' && !selectedFile.type.startsWith('image/')) ||
      (fileType === 'Video' && !selectedFile.type.startsWith('video/')) ||
      (fileType === 'PDF' && selectedFile.type !== 'application/pdf')
    ) {
      setError(`Please select a ${fileTypeInfo.name} file`);
      return;
    }

    // Validate file size
    if (selectedFile.size > maxSizeMB * 1024 * 1024) {
      setError(`File size exceeds ${maxSizeMB}MB limit`);
      return;
    }

    setError(null);
    const fileObj = {
      file: selectedFile,
      url: URL.createObjectURL(selectedFile),
      type: selectedFile.type,
      id: Math.random().toString(36).substring(2, 9),
      name: selectedFile.name,
    };

    setFile(fileObj);
    setFileName(selectedFile.name.replace(/\.[^/.]+$/, '')); // Set name without extension
    setCleared(false);
    onChange(selectedFile, fileType);
  };

  const handleClick = () => {
    fileInputRef.current?.click();
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    handleFile(e.target.files);
    if (e.target) e.target.value = '';
  };

  const handleDrop = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setDragOver(false);
    handleFile(e.dataTransfer.files);
  };

  const handleDragOver = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setDragOver(true);
  };

  const handleDragLeave = () => {
    setDragOver(false);
  };

  const handleDelete = () => {
    if (onDelete) {
      onDelete();
    }
    setFile(null);
    setFileName('');
    setError(null);
    setCleared(true);
    onChange(null, fileType);
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
    if (initialUrl && !cleared) {
      // Determine the type from the URL extension
      let type = '';
      if (initialUrl.match(/\.(jpeg|jpg|gif|png)$/i)) {
        type = 'image/jpeg';
      } else if (initialUrl.match(/\.(mp4|webm|ogg)$/i)) {
        type = 'video/mp4';
      } else if (initialUrl.match(/\.(pdf)$/i)) {
        type = 'application/pdf';
      } else {
        type = 'unknown';
      }

      // Extract filename from URL
      const urlParts = initialUrl.split('/');
      const urlFileName = urlParts[urlParts.length - 1];

      // Create a file object without the File instance
      setFile({
        url: initialUrl,
        type,
        id: Math.random().toString(36).substring(2, 9),
        name: urlFileName,
      });

      // Set initial filename without extension
      setFileName(urlFileName.replace(/\.[^/.]+$/, ''));
    } else if (!initialUrl || cleared) {
      setFile(null);
      setFileName('');
    }
  }, [initialUrl, cleared]);

  // Reset cleared if initialUrl changes
  useEffect(() => {
    setCleared(false);
  }, [initialUrl]);

  // Sync prop filename with state
  useEffect(() => {
    if (propFileName !== fileName) {
      setFileName(propFileName);
    }
  }, [propFileName]);

  const renderPreview = () => {
    if (!file) return null;

    const { url, type } = file;

    return (
      <div className={`position-relative ${previewClassName}`} style={{ display: 'inline-block', margin: '10px' }}>
        {type.startsWith('image/') && <img src={url} alt="Preview" className="img-fluid rounded" style={{ maxHeight: '300px', maxWidth: '100%' }} />}
        {type.startsWith('video/') && (
          <video width="300" height="200" controls className="rounded">
            <source src={url} type={type} />
            Your browser does not support the video tag.
          </video>
        )}
        {type === 'application/pdf' && (
          <div className="border rounded p-2">
            <iframe src={url} width="100%" height="300px" title="PDF preview" style={{ border: 'none' }} />
          </div>
        )}
        <button
          onClick={(e) => {
            e.stopPropagation();
            handleDelete();
          }}
          className="position-absolute top-0 end-0 btn btn-danger btn-sm rounded-circle"
          style={{ transform: 'translate(30%, -30%)' }}
          aria-label="Remove file"
        >
          ×
        </button>
      </div>
    );
  };

  const renderDropZoneContent = () => {
    if (file) {
      return <div className="d-flex flex-wrap justify-content-center">{renderPreview()}</div>;
    }

    return (
      <div className="d-flex flex-column justify-content-center h-100">
        <div className="mb-3">{fileTypeInfo.icon}</div>
        <p className="text-muted">Drag and drop {fileType === 'All' ? 'a file' : `a ${fileTypeInfo.name}`} here or click to choose</p>
        <p className="text-muted small">
          {fileType === 'All' ? 'Supports images, videos, and PDFs' : `Supports ${fileTypeInfo.name}s`}
          {` • Max size: ${fileTypeInfo.maxSize}MB`}
        </p>
        {error && <div className="text-danger mt-2">{error}</div>}
      </div>
    );
  };

  return (
    <div className={`${className}`} id={elementId}>
      {label && <Label label={label} isRequired={isRequired} />}
      <input type="file" ref={fileInputRef} accept={acceptType} onChange={handleChange} className="d-none" aria-hidden="true" disabled={!!file} />

      <div
        onClick={handleClick}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        className={`border-dashed rounded p-4 text-center ${dragOver ? 'bg-light' : 'bg-white'} ${dropZoneClassName}`}
        style={{
          border: '2px dashed #ccc',
          minHeight: '200px',
          cursor: 'pointer',
        }}
        role="button"
        aria-label="File upload area"
        tabIndex={0}
      >
        {renderDropZoneContent()}
      </div>
    </div>
  );
};

export default FilePreviewer;
