import React, { useRef, useState } from 'react';
import Image from 'next/image';
import ImageSvg from '../../../../public/images/file-svg/image.svg';
import WordSvg from '../../../../public/images/file-svg/word.svg';
import ExcelSvg from '../../../../public/images/file-svg/excel.svg';
import TxtSvg from '../../../../public/images/file-svg/txt.svg';
import VideoSvg from '../../../../public/images/file-svg/video.svg';
import FileSvg from '../../../../public/images/file-svg/txt.svg';
import PdfSvg from '../../../../public/images/file-svg/pdf.svg';
import { Flexicon } from '@apptimus-ui/flexicon';

// File type options for simplified usage
type FileTypeOption = 'pdf' | 'word' | 'excel' | 'powerpoint' | 'image' | 'video' | 'audio' | 'text' | 'archive' | 'all';

// Mapping from simplified types to MIME types
const FILE_TYPE_MAPPING: Record<FileTypeOption, readonly string[]> = {
  pdf: ['application/pdf'],
  word: ['application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'],
  excel: ['application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'],
  powerpoint: ['application/vnd.ms-powerpoint', 'application/vnd.openxmlformats-officedocument.presentationml.presentation'],
  image: ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp', 'image/svg+xml', 'image/bmp', 'image/tiff'],
  video: ['video/mp4', 'video/avi', 'video/mov', 'video/wmv', 'video/flv', 'video/webm', 'video/mkv'],
  audio: ['audio/mp3', 'audio/wav', 'audio/ogg', 'audio/mpeg'],
  text: ['text/plain', 'text/csv'],
  archive: ['application/zip', 'application/x-rar-compressed', 'application/x-7z-compressed'],
  all: [
    // Images
    'image/jpeg',
    'image/jpg',
    'image/png',
    'image/gif',
    'image/webp',
    'image/svg+xml',
    'image/bmp',
    'image/tiff',
    // PDF
    'application/pdf',
    // Excel
    'application/vnd.ms-excel',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    // Word
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    // PowerPoint
    'application/vnd.ms-powerpoint',
    'application/vnd.openxmlformats-officedocument.presentationml.presentation',
    // Video
    'video/mp4',
    'video/avi',
    'video/mov',
    'video/wmv',
    'video/flv',
    'video/webm',
    'video/mkv',
    // Audio
    'audio/mp3',
    'audio/wav',
    'audio/ogg',
    'audio/mpeg',
    // Text
    'text/plain',
    'text/csv',
    // Archives
    'application/zip',
    'application/x-rar-compressed',
    'application/x-7z-compressed',
  ],
} as const;

// File validation interface
interface FileValidation {
  maxSize?: number; // in MB
  allowedTypes?: FileTypeOption[]; // Simplified file type options
  minWidth?: number;
  minHeight?: number;
  maxWidth?: number;
  maxHeight?: number;
  customValidator?: (file: File) => Promise<boolean> | boolean;
}

interface ImageDragAndDropProps {
  multiple?: boolean;
  validation?: FileValidation;
  maxFiles?: number;
  onChange?: (files: File[]) => void;
  customDropZone?: React.ReactNode;
  onError?: (error: string) => void;
}

// Simplified component with only essential props
const ImageDragAndDrop = (props: ImageDragAndDropProps) => {
  const { multiple = false, validation = {}, maxFiles = Infinity, onChange, customDropZone, onError } = props;
  const fileInput = useRef<HTMLInputElement>(null);
  const [inputKey, setInputKey] = useState(0);
  const [dragState, setDragState] = useState({
    isDragOver: false,
    isDragActive: false,
    isUploading: false,
  });
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [_, setErrors] = useState<string[]>([]);

  // Convert simplified file types to MIME types
  const convertToMimeTypes = (allowedTypes: FileTypeOption[]): string[] => {
    const mimeTypes: string[] = [];
    allowedTypes.forEach((type) => {
      const typeMimeTypes = FILE_TYPE_MAPPING[type];
      mimeTypes.push(...typeMimeTypes);
    });
    return mimeTypes;
  };

  // Generate file type description based on allowed types
  const getFileTypeDescription = (allowedTypes: FileTypeOption[]): string => {
    if (allowedTypes.includes('all')) {
      return 'Images, PDF, Excel, Word, Video, Audio, Text';
    }

    const typeLabels: Record<FileTypeOption, string> = {
      image: 'Images',
      pdf: 'PDF',
      word: 'Word',
      excel: 'Excel',
      powerpoint: 'PowerPoint',
      video: 'Video',
      audio: 'Audio',
      text: 'Text',
      archive: 'Archives',
      all: 'All Files',
    };

    const descriptions = allowedTypes
      .filter((type) => type !== 'all')
      .map((type) => typeLabels[type])
      .filter(Boolean);

    return descriptions.length > 0 ? descriptions.join(', ') : 'Files';
  };

  // Get appropriate icon for file type
  const getFileIcon = (fileType: string, style?: React.CSSProperties): React.ReactElement => {
    const defaultStyle = { width: 24, height: 24, ...style };

    if (fileType.startsWith('image/')) {
      return <Image src={ImageSvg} alt="Image file" width={defaultStyle.width as number} height={defaultStyle.height as number} style={{ color: '#0d6efd' }} />;
    }
    if (fileType.toLowerCase().includes('pdf') || fileType === 'application/pdf') {
      return <Image src={PdfSvg} alt="PDF file" width={defaultStyle.width as number} height={defaultStyle.height as number} style={{ color: '#0d6efd' }} />;
    }
    if (fileType.includes('word') || fileType.includes('document')) {
      return <Image src={WordSvg} alt="Word document" width={defaultStyle.width as number} height={defaultStyle.height as number} style={{ color: '#0d6efd' }} />;
    }
    if (fileType.includes('excel') || fileType.includes('spreadsheet')) {
      return <Image src={ExcelSvg} alt="Excel file" width={defaultStyle.width as number} height={defaultStyle.height as number} style={{ color: '#0d6efd' }} />;
    }
    if (fileType.includes('powerpoint') || fileType.includes('presentation')) {
      return <Image src={WordSvg} alt="PowerPoint file" width={defaultStyle.width as number} height={defaultStyle.height as number} style={{ color: '#0d6efd' }} />;
    }
    if (fileType.startsWith('video/')) {
      return <Image src={VideoSvg} alt="Video file" width={defaultStyle.width as number} height={defaultStyle.height as number} style={{ color: '#0d6efd' }} />;
    }
    if (fileType.startsWith('audio/')) {
      return <Image src={FileSvg} alt="Audio file" width={defaultStyle.width as number} height={defaultStyle.height as number} style={{ color: '#0d6efd' }} />;
    }
    if (fileType.includes('zip') || fileType.includes('rar') || fileType.includes('7z')) {
      return <Image src={FileSvg} alt="Archive file" width={defaultStyle.width as number} height={defaultStyle.height as number} style={{ color: '#0d6efd' }} />;
    }
    if (fileType.startsWith('text/')) {
      return <Image src={TxtSvg} alt="Text file" width={defaultStyle.width as number} height={defaultStyle.height as number} style={{ color: '#0d6efd' }} />;
    }
    return <Image src={FileSvg} alt="File" width={defaultStyle.width as number} height={defaultStyle.height as number} style={{ color: '#0d6efd' }} />;
  };

  // Validation configuration with defaults
  const validationConfig: Required<FileValidation> = {
    maxSize: validation.maxSize || 10, // 10MB default
    allowedTypes: validation.allowedTypes || ['all'],
    minWidth: validation.minWidth || 0,
    minHeight: validation.minHeight || 0,
    maxWidth: validation.maxWidth || Infinity,
    maxHeight: validation.maxHeight || Infinity,
    customValidator: validation.customValidator || (() => true),
  };

  // Convert to MIME types for actual validation
  const mimeTypes = convertToMimeTypes(validationConfig.allowedTypes);

  // Enhanced file validation
  const validateFile = async (file: File): Promise<string[]> => {
    const errors: string[] = [];

    // Size validation
    if (file.size > validationConfig.maxSize * 1000000) {
      errors.push(`File size exceeds ${validationConfig.maxSize}MB limit`);
    }

    // Type validation
    if (!mimeTypes.includes(file.type)) {
      errors.push(`File type not allowed`);
    }

    // Custom validation
    try {
      const isValid = await validationConfig.customValidator(file);
      if (!isValid) {
        errors.push('File failed custom validation');
      }
    } catch (error) {
      errors.push('Custom validation error');
    }

    return errors;
  };

  // Process files (handles both single and multiple)
  const processFiles = async (files: File[]) => {
    try {
      // For single file mode, only take the first file
      const filesToProcess = multiple ? files : [files[0]];

      // Check max files limit
      if (filesToProcess.length > maxFiles) {
        const errorMessage = `Maximum ${maxFiles} files allowed. You tried to upload ${filesToProcess.length} files.`;
        setErrors([errorMessage]);
        onError?.(errorMessage);
        return;
      }

      // Check if adding these files would exceed the limit
      if (selectedFiles.length + filesToProcess.length > maxFiles) {
        const errorMessage = `Maximum ${maxFiles} files allowed. You already have ${selectedFiles.length} files and tried to add ${filesToProcess.length} more.`;
        setErrors([errorMessage]);
        onError?.(errorMessage);
        return;
      }

      const validFiles: File[] = [];
      const allErrors: string[] = [];

      // Validate each file
      for (const file of filesToProcess) {
        const validationErrors = await validateFile(file);
        if (validationErrors.length > 0) {
          allErrors.push(`${file.name}: ${validationErrors.join(', ')}`);
        } else {
          validFiles.push(file);
        }
      }

      if (allErrors.length > 0) {
        setErrors(allErrors);
        // Call onError callback with the first error for parent component handling
        onError?.(allErrors[0]);
      }

      if (validFiles.length > 0) {
        setErrors([]);
        // For single file mode, replace existing files; for multiple, add to existing
        const allFiles = multiple ? [...selectedFiles, ...validFiles] : validFiles;
        setSelectedFiles(allFiles);
        onChange?.(allFiles);
      }

      setInputKey((prev) => prev + 1);
    } catch (error) {
      const errorMessage = 'Failed to process files';
      setErrors([errorMessage]);
      onError?.(errorMessage);
    }
  };

  // Drag and drop handlers
  const handleDragEnter = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragState((prev) => ({ ...prev, isDragActive: true, isDragOver: true }));
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragState((prev) => ({ ...prev, isDragOver: false }));
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragState((prev) => ({ ...prev, isDragOver: true }));
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragState((prev) => ({ ...prev, isDragActive: false, isDragOver: false }));

    const files = Array.from(e.dataTransfer.files);
    if (files.length > 0) {
      processFiles(files);
    }
  };

  const handleFileChange = () => {
    if (!fileInput.current) return;

    const files = Array.from(fileInput.current.files || []);
    if (files.length > 0) {
      processFiles(files);
    }

    // Reset the input value to allow selecting the same files again
    if (fileInput.current) {
      fileInput.current.value = '';
    }
  };

  const handleRemoveFile = (fileIndex: number) => {
    const newFiles = selectedFiles.filter((_, index) => index !== fileIndex);
    setSelectedFiles(newFiles);
    onChange?.(newFiles);
  };

  return (
    <div>
      {/* Custom drop zone */}
      {customDropZone && (
        <div
          className="border-dashed-primary bg-white rounded p-4 text-center cursor-pointer position-relative overflow-hidden"
          onClick={() => fileInput.current?.click()}
          onDragEnter={handleDragEnter}
          onDragLeave={handleDragLeave}
          onDragOver={handleDragOver}
          onDrop={handleDrop}
          style={{
            borderWidth: '2px',
            borderColor: dragState.isDragOver ? '#0d6efd' : '#0d6efd',
            backgroundColor: dragState.isDragOver ? '#f8f9fa' : '#ffffff',
            transition: 'all 0.3s ease',
          }}
        >
          <div
            style={{
              transition: 'transform 0.2s ease',
              transform: dragState.isDragOver ? 'scale(1.02)' : 'scale(1)',
            }}
          >
            {customDropZone}
          </div>
        </div>
      )}

      {/* File list */}
      {selectedFiles.length > 0 && (
        <div className="mt-2">
          {selectedFiles.map((file, index) => {
            return (
              <div key={`${file.name}-${index}`} className="d-flex align-items-center bg-light rounded p-2 mb-1">
                <div className="me-2" style={{ width: '24px', height: '24px', flexShrink: 0 }}>
                  {getFileIcon(file.type)}
                </div>
                <div className="flex-grow-1" style={{ minWidth: '0' }}>
                  <div className="text-dark fw-medium" style={{ fontSize: '0.8rem' }}>
                    {file.name}
                  </div>
                  <div className="text-muted" style={{ fontSize: '0.75rem' }}>
                    {(() => {
                      const sizeInMB = file.size / 1024 / 1024;
                      if (sizeInMB < 0.1) {
                        return `${(file.size / 1024).toFixed(0)}KB`;
                      }
                      return `${sizeInMB.toFixed(1)}MB`;
                    })()}
                  </div>
                </div>
                <Flexicon icon="x-square" variant="line" className="text-danger action-icon" onClick={() => handleRemoveFile(index)} />
              </div>
            );
          })}
        </div>
      )}

      {/* Unified dropzone for both single and multiple uploads */}
      {(selectedFiles.length === 0 || (multiple && selectedFiles.length < maxFiles)) && (
        <div
          className="border-dashed-primary bg-white rounded p-4 text-center cursor-pointer mt-1 position-relative"
          onClick={() => fileInput.current?.click()}
          onDragEnter={handleDragEnter}
          onDragLeave={handleDragLeave}
          onDragOver={handleDragOver}
          onDrop={handleDrop}
          style={{
            borderWidth: '2px',
            borderColor: dragState.isDragOver ? '#0d6efd' : '#0d6efd',
            backgroundColor: dragState.isDragOver ? '#f8f9fa' : '#ffffff',
            transition: 'all 0.3s ease',
          }}
        >
          <div className="d-flex flex-column align-items-center">
            <Flexicon icon="upload-cloud-01" variant="line" className="text-muted" />
            <div>
              <div className="fw-medium text-primary mb-1">
                <span className="text-primary fw-semibold">Click to upload</span>
                <span className="text-muted"> or drag and drop</span>
              </div>
              <div className="small text-muted">
                {multiple
                  ? selectedFiles.length > 0
                    ? `${selectedFiles.length} of ${maxFiles} files selected`
                    : `Select up to ${maxFiles} files`
                  : selectedFiles.length === 0
                    ? 'Select a file'
                    : 'Replace current file'}
              </div>
              <div className="text-muted small mt-1">
                {getFileTypeDescription(validationConfig.allowedTypes)} (max. {validationConfig.maxSize}MB)
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Errors */}
      {/* {errors.length > 0 && (
                <div className="mt-3">
                    {errors.map((error, index) => (
                        <div key={index} className="err-msg">
                            {error}
                        </div>
                    ))}
                </div>
            )} */}

      {/* Hidden file input */}
      <input ref={fileInput} type="file" accept={mimeTypes.join(',')} multiple={multiple} onChange={handleFileChange} key={inputKey} className="d-none" />
    </div>
  );
};

export { ImageDragAndDrop };
