import { Label } from '@apptimus-ui/ui-element';
import React from 'react';

function PdfViewer({ label, value }: { label?: string; value: string }) {
  const fileUrl = `${process.env.S3CDN}/${value}`;

  // Extract the actual filename from the value
  const extractFilename = (url: string) => {
    const parts = url.split('_');
    return parts.length > 1 ? parts[parts.length - 1] : url;
  };

  const fullFilename = extractFilename(value);
  const displayFilename = fullFilename.length > 30 ? `${fullFilename.substring(0, 15)}...${fullFilename.slice(-10)}` : fullFilename;

  return (
    <div className="my-2">
      {label && (
        <div className="mb-1">
          <Label label={label} />
        </div>
      )}

      <div className="card border-1 shadow-sm">
        <div className="card-body p-2 p-md-3">
          <div className="d-flex flex-wrap align-items-center justify-content-between gap-2">
            <div className="d-flex align-items-center flex-grow-1 min-width-0" style={{ minWidth: '200px' }} onClick={() => window.open(fileUrl, '_blank')}>
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" className="flex-shrink-0 me-2">
                <path
                  d="M14 2H6C5.46957 2 4.96086 2.21071 4.58579 2.58579C4.21071 2.96086 4 3.46957 4 4V20C4 20.5304 4.21071 21.0391 4.58579 21.4142C4.96086 21.7893 5.46957 22 6 22H18C18.5304 22 19.0391 21.7893 19.4142 21.4142C19.7893 21.0391 20 20.5304 20 20V8L14 2Z"
                  stroke="#dc3545"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  fill="#f8d7da"
                />
                <path d="M14 2V8H20" stroke="#dc3545" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                <path d="M16 13H8" stroke="#dc3545" strokeWidth="2" strokeLinecap="round" />
                <path d="M16 17H8" stroke="#dc3545" strokeWidth="2" strokeLinecap="round" />
                <path d="M10 9H9H8" stroke="#dc3545" strokeWidth="2" strokeLinecap="round" />
              </svg>
              <span className="text-dark fw-semibold text-truncate" title={fullFilename}>
                {displayFilename}
              </span>
            </div>
            <div className="d-flex justify-content-end flex-shrink-0">
              <button onClick={() => window.open(fileUrl, '_blank')} className="btn btn-light d-inline-flex align-items-center">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" className="me-2">
                  <path d="M15 12C15 13.6569 13.6569 15 12 15C10.3431 15 9 13.6569 9 12C9 10.3431 10.3431 9 12 9C13.6569 9 15 10.3431 15 12Z" stroke="currentColor" strokeWidth="2" />
                  <path d="M12 6C15.6 6 18.6 8.4 20.2 12C18.6 15.6 15.6 18 12 18C8.4 18 5.4 15.6 3.8 12C5.4 8.4 8.4 6 12 6Z" stroke="currentColor" strokeWidth="2" />
                </svg>
                <span>View PDF</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default PdfViewer;
