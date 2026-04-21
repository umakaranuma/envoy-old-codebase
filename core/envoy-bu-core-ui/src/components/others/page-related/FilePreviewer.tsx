import { Flexicon } from '@apptimus-ui/flexicon';
import React from 'react';
import Image from 'next/image';
import pdfIcon from '../../../../public/images/file-svg/pdf.svg';
import wordIcon from '../../../../public/images/file-svg/word.svg';
import excelIcon from '../../../../public/images/file-svg/excel.svg';
import imageIcon from '../../../../public/images/file-svg/image.svg';
import videoIcon from '../../../../public/images/file-svg/video.svg';
import txtIcon from '../../../../public/images/file-svg/txt.svg';

function FilePreviewer({
  fileName,
  downloadable = true,
  s3Url,
  fileType = 'txt',
  downloadFileName,
}: {
  fileName: string | null;
  downloadable?: boolean;
  s3Url?: string | null;
  fileType?: string;
  downloadFileName?: string;
}) {
  function getFileTypeIcon(fileType: string) {
    const extension = fileType.toLowerCase();

    switch (extension) {
      case 'pdf':
        return pdfIcon;
      case 'doc':
      case 'docx':
        return wordIcon;
      case 'xls':
      case 'xlsx':
        return excelIcon;
      case 'jpg':
      case 'jpeg':
      case 'png':
      case 'gif':
      case 'bmp':
      case 'svg':
      case 'webp':
        return imageIcon;
      case 'mp4':
      case 'avi':
      case 'mov':
      case 'wmv':
      case 'flv':
      case 'webm':
        return videoIcon;
      case 'txt':
        return txtIcon;
      default:
        return txtIcon;
    }
  }

  async function handleViewFile() {
    try {
      if (!s3Url) {
        console.error('No s3Url provided');
        return;
      }

      window.open(s3Url, '_blank');
    } catch (error) {
      console.error('Error viewing file:', error);
    }
  }
  async function handleDownloadTemplate() {
    try {
      if (!s3Url) {
        console.error('No s3Url provided');
        return;
      }

      // Fetch the file first to ensure it downloads rather than opens
      const response = await fetch(s3Url);
      if (!response.ok) {
        throw new Error(`Failed to fetch file: ${response.status}`);
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);

      const link = document.createElement('a');
      link.href = url;
      link.download = downloadFileName || fileName || 'download';
      link.style.display = 'none';

      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);

      // Clean up the object URL
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Error downloading file:', error);
    }
  }

  console.log('s3Url', s3Url);

  return (
    <div className="d-flex align-items-center gap-2">
      <Image src={getFileTypeIcon(fileType)} alt="File type" width={18} height={18} />
      <span className="text-truncate" style={{ cursor: 'pointer' }} onClick={handleViewFile} title="Click to view file in new tab">
        {fileName}
      </span>
      {downloadable && <Flexicon icon="download-01" variant="line" size={16} className="text-primary pointer" onClick={() => handleDownloadTemplate()} />}
    </div>
  );
}

export default FilePreviewer;
