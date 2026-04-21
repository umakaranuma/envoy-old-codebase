import { Label } from '@apptimus-ui/ui-element';
import React, { useState, useRef, useCallback } from 'react';
import Image from 'next/image';
import { Flexicon } from '@apptimus-ui/flexicon';
import { useTrans } from '@/helpers/services/lang/langService';
import ImageSvg from '../../../../../../../public/images/file-svg/image.svg';
import PdfSvg from '../../../../../../../public/images/file-svg/pdf.svg';
import WordSvg from '../../../../../../../public/images/file-svg/word.svg';
import ExcelSvg from '../../../../../../../public/images/file-svg/excel.svg';
import TxtSvg from '../../../../../../../public/images/file-svg/txt.svg';
import VideoSvg from '../../../../../../../public/images/file-svg/video.svg';
import FileSvg from '../../../../../../../public/images/file-svg/txt.svg';

interface AttachmentFile {
  id: string;
  file: File;
  name: string;
  size: number;
  type: string;
  url: string;
}

interface AttachmentInputProps {
  className?: string;
  maxFiles?: number;
  maxSize?: number;
  acceptedTypes?: string[];
  onChange?: (files: AttachmentFile[]) => void;
  onError?: (error: string) => void;
  disabled?: boolean;
  elementId?: string;
}

const MAX_FILE_SIZE = 20 * 1024 * 1024;
const AttachmentInput = ({
  className = '',
  maxFiles = 1000,
  maxSize = MAX_FILE_SIZE,
  acceptedTypes = ['image/*', 'application/pdf', '.doc', '.docx', '.xls', '.xlsx', '.txt', 'audio/*', 'video/*'],
  onChange,
  onError,
  disabled = false,
  elementId,
}: AttachmentInputProps) => {
  const t = useTrans('label.chat,otr.common,be.msg');
  const [files, setFiles] = useState<AttachmentFile[]>([]);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const validateFile = useCallback(
    (file: File): string | null => {
      if (file.size > maxSize) {
        return `File "${file.name}" exceeds the ${maxSize / (1024 * 1024)}MB size limit`;
      }

      const fileExtension = '.' + file.name.split('.').pop()?.toLowerCase();
      const isValidType = acceptedTypes.some((type) => {
        if (type.startsWith('.')) return fileExtension === type.toLowerCase();
        return file.type.match(type.replace('*', '.*'));
      });

      if (!isValidType) {
        return `File "${file.name}" is not a supported file type`;
      }
      return null;
    },
    [maxSize, acceptedTypes],
  );

  const addFiles = useCallback(
    (newFiles: FileList) => {
      const fileArray = Array.from(newFiles);
      if (files.length + fileArray.length > maxFiles) {
        const errorMsg = `Cannot add more than ${maxFiles} files.`;
        setError(errorMsg);
        onError?.(errorMsg);
        return;
      }

      const validFiles: AttachmentFile[] = [];
      const errors: string[] = [];

      fileArray.forEach((file) => {
        const validationError = validateFile(file);
        if (validationError) errors.push(validationError);
        else
          validFiles.push({
            id: Math.random().toString(36).substring(2, 9),
            file,
            name: file.name,
            size: file.size,
            type: file.type,
            url: URL.createObjectURL(file),
          });
      });

      if (errors.length > 0) {
        const errorMsg = errors.join('; ');
        setError(errorMsg);
        onError?.(errorMsg);
      } else setError(null);

      if (validFiles.length > 0) {
        const updatedFiles = [...files, ...validFiles];
        setFiles(updatedFiles);
        onChange?.(updatedFiles);
      }
    },
    [files, maxFiles, validateFile, onChange, onError],
  );

  const handleFileSelect = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      if (e.target.files) {
        addFiles(e.target.files);
        e.target.value = '';
      }
    },
    [addFiles],
  );

  const handleClick = useCallback(() => {
    if (!disabled) fileInputRef.current?.click();
  }, [disabled]);

  const removeFile = useCallback(
    (fileId: string) => {
      const fileToRemove = files.find((f) => f.id === fileId);
      if (fileToRemove) URL.revokeObjectURL(fileToRemove.url);

      const updatedFiles = files.filter((f) => f.id !== fileId);
      setFiles(updatedFiles);
      onChange?.(updatedFiles);
      setError(null);
    },
    [files, onChange],
  );

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const getFileIcon = (fileType: string) => {
    const iconSize = { width: 32, height: 32 };
    if (fileType.startsWith('image/')) return <Image src={ImageSvg} alt="Image" {...iconSize} />;
    if (fileType === 'application/pdf') return <Image src={PdfSvg} alt="PDF" {...iconSize} />;
    if (fileType.includes('word')) return <Image src={WordSvg} alt="Word" {...iconSize} />;
    // Excel MIME types and extensions
    if (
      fileType.includes('excel') ||
      fileType === 'application/vnd.ms-excel' ||
      fileType === 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' ||
      fileType.endsWith('.xls') ||
      fileType.endsWith('.xlsx')
    )
      return <Image src={ExcelSvg} alt="Excel" {...iconSize} />;
    if (fileType.includes('text')) return <Image src={TxtSvg} alt="Text" {...iconSize} />;
    if (fileType.startsWith('video/')) return <Image src={VideoSvg} alt="Video" {...iconSize} />;
    if (fileType.startsWith('audio/')) return <Image src={FileSvg} alt="Audio" {...iconSize} />;
    return <Image src="public/images/file-svg/file.svg" alt="File" {...iconSize} />;
  };

  return (
    <div className={`attachment-input ${className}`} id={elementId}>
      <Label label={t('attachment_files')} />

      {/* File List */}
      {files.length > 0 && (
        <div className="mt-2">
          {files.map((file) => (
            <div key={file.id} className="d-flex justify-content-between align-items-center border border-light border-2 rounded-3 p-1 mb-2">
              <div className="d-flex align-items-center gap-2 flex-grow-1">
                {getFileIcon(file.type)}
                <div className="">
                  <div className="d-flex align-items-center">
                    <span className="text-truncate fw-medium" style={{ maxWidth: '180px' }} title={file.name}>
                      {file.name.substring(0, file.name.lastIndexOf('.'))}
                    </span>
                    <span className="fw-medium">.{file.name.split('.').pop()}</span>
                  </div>
                  <div className="text-muted small">{formatFileSize(file.size)}</div>
                </div>
              </div>
              <div onClick={() => removeFile(file.id)}>
                <Flexicon icon="x-close" variant="line" className="pointer text-danger" />
              </div>
            </div>
          ))}
        </div>
      )}
      {/* Add File Button */}
      <div onClick={() => handleClick()} className="d-flex gap-2 align-items-center text-primary pointer">
        <Flexicon icon="plus" variant="line" size={14} />
        {t('add_file')}
      </div>

      <input ref={fileInputRef} type="file" multiple accept={acceptedTypes.join(',')} onChange={handleFileSelect} className="d-none" disabled={disabled} />

      {error && <div className="text-danger small mt-2">{error}</div>}
    </div>
  );
};

export default AttachmentInput;
