import Image from 'next/image';
import React from 'react';
import ImageSvg from '../../../../../../../public/images/file-svg/image.svg';
import PdfSvg from '../../../../../../../public/images/file-svg/pdf.svg';
import WordSvg from '../../../../../../../public/images/file-svg/word.svg';
import ExcelSvg from '../../../../../../../public/images/file-svg/excel.svg';
import TxtSvg from '../../../../../../../public/images/file-svg/txt.svg';
import VideoSvg from '../../../../../../../public/images/file-svg/video.svg';
import FileSvg from '../../../../../../../public/images/file-svg/txt.svg';
import { IFilePreviewer } from '../model';
import { Flexicon } from '@apptimus-ui/flexicon';

const FilePreviewer = ({ file, removeFile, handleDocExtraction }: { file: IFilePreviewer | null; removeFile?: (id: number) => void; handleDocExtraction?: (file: IFilePreviewer) => void }) => {
  if (!file) return null;

  const getFileIcon = (fileType?: string) => {
    const iconSize = { width: 30, height: 30 };

    switch (fileType) {
      case 'png':
      case 'jpg':
      case 'jpeg':
      case 'image/jpeg':
        return <Image src={ImageSvg} alt="Image Icon" {...iconSize} className="flex-shrink-0" />;
      case 'pdf':
        return <Image src={PdfSvg} alt="PDF Icon" {...iconSize} className="flex-shrink-0" />;
      case 'docx':
        return <Image src={WordSvg} alt="Word Icon" {...iconSize} className="flex-shrink-0" />;
      case 'excel':
      case 'xlsx':
        return <Image src={ExcelSvg} alt="Excel Icon" {...iconSize} className="flex-shrink-0" />;
      case 'text':
        return <Image src={TxtSvg} alt="Text Icon" {...iconSize} className="flex-shrink-0" />;
      case 'video':
        return <Image src={VideoSvg} alt="Video Icon" {...iconSize} className="flex-shrink-0" />;
      case 'audio':
        return <Image src={FileSvg} alt="Audio Icon" {...iconSize} className="flex-shrink-0" />;
      default:
        return <Image src={FileSvg} alt="File Icon" {...iconSize} className="flex-shrink-0" />;
    }
  };

  const handleViewFile = () => {
    try {
      if (!file?.url) {
        console.error('No s3Url provided');
        return;
      }
      window.open(file.url, '_blank');
    } catch (error) {
      console.error('Error viewing file:', error);
    }
  };

  const handleDownloadFile = async () => {
    console;
    try {
      if (!file?.url) {
        console.error('No s3Url provided');
        return;
      }

      const response = await fetch(file.url);
      if (!response.ok) {
        throw new Error(`Failed to fetch file: ${response.status}`);
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);

      const link = document.createElement('a');
      link.href = url;
      link.download = file.name || 'attachment';
      link.style.display = 'none';

      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);

      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Error downloading file:', error);
    }
  };

  const getFileExtension = (fileName: string) => {
    return fileName.split('.').pop()?.toLowerCase() || 'file';
  };

  const getFileNameWithoutExtension = (fileName: string) => {
    return fileName.substring(0, fileName.lastIndexOf('.'));
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div className="border border-light border-2 rounded-3 p-1 py-2 mt-2" style={{ maxWidth: '320px' }}>
      <div className="d-flex align-items-center justify-content-between">
        {/* File Info Section */}
        <div
          className="d-flex align-items-center gap-2 flex-grow-1 me-3"
          style={{ cursor: 'pointer', minWidth: 0 }}
          onClick={handleViewFile}
          role="button"
          tabIndex={0}
          onKeyDown={(e) => {
            if (e.key === 'Enter' || e.key === ' ') {
              handleViewFile();
            }
          }}
        >
          {getFileIcon(file.type)}

          <div className="flex-grow-1" style={{ minWidth: 0 }}>
            <div className="d-flex align-items-center mb-1">
              <span className="text-truncate fw-semibold text-dark" style={{ maxWidth: '150px' }} title={file.name}>
                {getFileNameWithoutExtension(file.name)}
              </span>
              <span className="text-muted fw-medium ms-1 flex-shrink-0">.{getFileExtension(file.name)}</span>
            </div>
            <div className="text-muted small">
              <i className="bi bi-file-earmark-text me-1"></i>
              {formatFileSize(file.size)}
            </div>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="d-flex align-items-center gap-3 flex-shrink-0 me-3">
          {/* Download Button */}
          <Flexicon icon="download-01" variant="line" size={20} onClick={handleDownloadFile} className="pointer text-primary" />
          {/* Extract Button */}
          {handleDocExtraction && <Flexicon icon="file-download-02" variant="line" size={20} onClick={() => handleDocExtraction(file)} className="pointer text-warning" />}
          {/* Remove Button */}
          {removeFile && (
            <button type="button" className="btn btn-outline-danger btn-sm p-1 rounded-2" onClick={() => removeFile(file.id)} title={`Remove ${file.name}`} aria-label={`Remove ${file.name}`}>
              <i className="bi bi-trash"></i>
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default FilePreviewer;
