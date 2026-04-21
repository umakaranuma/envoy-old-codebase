import Image from 'next/image';
import React from 'react';
import ImageSvg from '../../../../../../../public/images/file-svg/image.svg';
import PdfSvg from '../../../../../../../public/images/file-svg/pdf.svg';
import WordSvg from '../../../../../../../public/images/file-svg/word.svg';
import ExcelSvg from '../../../../../../../public/images/file-svg/excel.svg';
import TxtSvg from '../../../../../../../public/images/file-svg/txt.svg';
import VideoSvg from '../../../../../../../public/images/file-svg/video.svg';
import FileSvg from '../../../../../../../public/images/file-svg/txt.svg';
import { Flexicon } from '@apptimus-ui/flexicon';

interface FilePreviewer {
  id: number;
  name: string;
  size: string;
  type?: string;
  url: string;
}

const AttachmentFile = ({
  file,
  removeFile,
  handleAddQuotation,
  loading,
  isReceived,
}: {
  file: FilePreviewer | null;
  removeFile?: (id: number) => void;
  handleAddQuotation: (id: string) => void;
  loading: boolean;
  isReceived: boolean;
}) => {
  if (!file) return null;

  const handleClick = () => {
    if (!file.url) return;

    const link = document.createElement('a');
    link.href = file.url;
    link.target = '_blank';
    link.click();
  };

  const getFileIcon = (fileType?: string) => {
    const iconSize = { width: 32, height: 32 };

    switch (fileType) {
      case 'png':
      case 'jpg':
      case 'jpeg':
      case 'image/jpeg':
        return <Image src={ImageSvg} alt="Image Icon" {...iconSize} />;
      case 'pdf':
        return <Image src={PdfSvg} alt="PDF Icon" {...iconSize} />;
      case 'docx':
        return <Image src={WordSvg} alt="Word Icon" {...iconSize} />;
      case 'excel':
      case 'xlsx':
        return <Image src={ExcelSvg} alt="Excel Icon" {...iconSize} />;
      case 'text':
        return <Image src={TxtSvg} alt="Text Icon" {...iconSize} />;
      case 'video':
        return <Image src={VideoSvg} alt="Video Icon" {...iconSize} />;
      case 'audio':
        return <Image src={FileSvg} alt="Audio Icon" {...iconSize} />;
      default:
        return <Image src={FileSvg} alt="File Icon" {...iconSize} />;
    }
  };

  return (
    <div className="mt-2">
      <div className="d-flex flex-row justify-content-between align-items-center border border-light border-2 rounded-3 p-1 py-2">
        <div className="d-flex align-items-center gap-2 flex-grow-1">
          {getFileIcon(file.type)}
          <div className="">
            <div className="d-flex align-items-center">
              <span className="text-truncate fw-medium" style={{ maxWidth: '180px' }} title={file.name}>
                {file.name.substring(0, file.name.lastIndexOf('.'))}
              </span>
              <span className="fw-medium">.{file.name.split('.').pop()}</span>
            </div>
            <div className="text-muted small">{file.size}</div>
          </div>
        </div>
        <div className="p-2 d-flex flex-row gap-3">
          <Flexicon icon="download-01" variant="line" className="text-primary action-icon" onClick={handleClick} />
          {isReceived && (
            <>
              {!loading ? (
                <Flexicon icon="bookmark-add" variant="line" className="text-secondary action-icon" onClick={() => handleAddQuotation(file.id.toString())} />
              ) : (
                <div className="spinner-border spinner-border-sm text-primary mt-1" role="status"></div>
              )}
            </>
          )}
        </div>

        {removeFile && (
          <button type="button" className="btn btn-link p-0 ms-2 text-danger flex-shrink-0" onClick={() => removeFile(file.id)} aria-label={`Remove ${file.name}`}>
            {/* Trash icon SVG */}
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor" viewBox="0 0 16 16" role="img" aria-hidden="true">
              <path d="M5.5 5.5a.5.5 0 0 1 .5.5v6a.5.5 0 0 1-1 0v-6a.5.5 0 0 1 .5-.5zm2.5 0a.5.5 0 0 1 .5.5v6a.5.5 0 0 1-1 0v-6a.5.5 0 0 1 .5-.5zm3 .5a.5.5 0 0 0-1 0v6a.5.5 0 0 0 1 0v-6z" />
              <path
                fillRule="evenodd"
                d="M14.5 3a1 1 0 0 1-1 1H13v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V4h-.5a1 1 0 0 1 0-2H5h6h2.5a1 1 0 0 1 1 1zM4.118 4 4 4.059V13a1 1 0 0 0 1 1h6a1 1 0 0 0 1-1V4.059L11.882 4H4.118zM2.5 3h11a.5.5 0 0 0 0-1H10a1 1 0 0 0-1-1H7a1 1 0 0 0-1 1H2.5a.5.5 0 0 0 0 1z"
              />
            </svg>
          </button>
        )}
      </div>
    </div>
  );
};

export default AttachmentFile;
