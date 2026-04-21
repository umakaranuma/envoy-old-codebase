import { Flexicon } from '@apptimus-ui/flexicon';
import React from 'react';

function FilePreviewInput({ fileName, onCancel }: { fileName: string | null; onCancel: Function }) {
  return (
    <div className="d-flex flex-row justify-content-between align-items-center form-control">
      <span className="text-truncate">{fileName}</span>
      <div>
        <Flexicon icon="x-square" variant="line" size={24} className="text-danger action-icon" onClick={() => onCancel()} />
      </div>
    </div>
  );
}

export default FilePreviewInput;
