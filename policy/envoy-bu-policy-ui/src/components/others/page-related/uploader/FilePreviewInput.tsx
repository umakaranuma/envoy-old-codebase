import { fileReceiver } from '@/helpers/services/storageService';
import { Flexicon } from '@apptimus-ui/flexicon';
import React from 'react';

function FilePreviewInput({ fileName, onCancel, downloadable = false, s3Key }: { fileName: string | null; onCancel: Function; downloadable?: boolean; s3Key?: string | null }) {
  async function handleDownloadTemplate() {
    const file = await fileReceiver({ key: s3Key || '' });
    const link = document.createElement('a');
    link.href = file;
    link.target = '_blank';
    link.rel = 'noopener noreferrer';
    link.download = s3Key || '';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }
  console.log('s3Key', s3Key);

  return (
    <div className="d-flex flex-row justify-content-between align-items-center form-control">
      <span className="text-truncate">{fileName}</span>
      <div className={downloadable ? 'd-flex gap-1' : ''}>
        {downloadable && <Flexicon icon="download-cloud-02" variant="line" size={24} className="text-primary action-icon" onClick={() => handleDownloadTemplate()} />}
        <Flexicon icon="x-square" variant="line" size={24} className="text-danger action-icon" onClick={() => onCancel()} />
      </div>
    </div>
  );
}

export default FilePreviewInput;
