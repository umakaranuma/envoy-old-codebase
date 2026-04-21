import { Flexicon } from '@apptimus-ui/flexicon';
import React, { useEffect, useState } from 'react';
import { getEndorsementRequestDocuments } from '../../api-service';
import JSZip from 'jszip';

function Documents({ endorsementsRequestId, endorsement_request_code }: { endorsementsRequestId: number; endorsement_request_code: string }) {
  const [documents, setDocuments] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isDownloading, setIsDownloading] = useState(false);

  useEffect(() => {
    const fetchDocuments = async () => {
      try {
        setIsLoading(true);
        const response = await getEndorsementRequestDocuments(endorsementsRequestId.toString());
        setDocuments(response.result);
        setIsLoading(false);
      } catch (error) {
        console.error('Error fetching documents:', error);
        setIsLoading(false);
      }
    };
    fetchDocuments();
  }, [endorsementsRequestId]);

  const downloadAllDocuments = async (docs: any[]) => {
    try {
      const zip = new JSZip();
      const folderName = `Endorsement_Documents_${endorsement_request_code}`;
      const folder = zip.folder(folderName);

      if (!folder) {
        throw new Error('Failed to create folder in zip');
      }

      // Check if there are any documents
      if (docs.length === 0) {
        // Add a placeholder file to indicate empty folder
        folder.file('No documents available.txt', 'This folder contains no documents for this endorsement request.');
      } else {
        // Download all files and add them to the zip
        for (const doc of docs) {
          if (doc.file_url) {
            try {
              const response = await fetch(doc.file_url);
              if (!response.ok) {
                console.warn(`Failed to fetch file: ${doc.file_url}`);
                continue;
              }

              const blob = await response.blob();

              // Get original file name and extension
              let fileName = doc.file_name || doc.original_name || `document_${docs.indexOf(doc) + 1}`;

              // Ensure file has proper extension if not present
              if (!fileName.includes('.')) {
                const contentType = response.headers.get('content-type');
                let extension = '';

                if (contentType) {
                  if (contentType.includes('pdf')) extension = '.pdf';
                  else if (contentType.includes('image/jpeg') || contentType.includes('image/jpg')) extension = '.jpg';
                  else if (contentType.includes('image/png')) extension = '.png';
                  else if (contentType.includes('image/gif')) extension = '.gif';
                  else if (contentType.includes('application/msword')) extension = '.doc';
                  else if (contentType.includes('application/vnd.openxmlformats-officedocument.wordprocessingml.document')) extension = '.docx';
                  else if (contentType.includes('application/vnd.ms-excel')) extension = '.xls';
                  else if (contentType.includes('application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')) extension = '.xlsx';
                  else if (contentType.includes('text/plain')) extension = '.txt';
                  else if (contentType.includes('application/zip')) extension = '.zip';
                  else if (contentType.includes('application/x-rar-compressed')) extension = '.rar';
                }

                if (!extension && doc.file_url) {
                  const urlPath = new URL(doc.file_url).pathname;
                  const urlExtension = urlPath.substring(urlPath.lastIndexOf('.'));
                  if (urlExtension && urlExtension.length <= 5) {
                    extension = urlExtension;
                  }
                }

                fileName += extension;
              }

              // Add file to the folder in zip with original format preserved
              folder.file(fileName, blob);
            } catch (error) {
              console.error(`Error downloading file ${doc.file_url}:`, error);
            }
          }
        }
      }

      // Generate and download the zip file
      const zipBlob = await zip.generateAsync({ type: 'blob' });
      const downloadUrl = window.URL.createObjectURL(zipBlob);

      const link = document.createElement('a');
      link.href = downloadUrl;
      link.download = `${folderName}.zip`;
      document.body.appendChild(link);
      link.click();

      // Cleanup
      document.body.removeChild(link);
      window.URL.revokeObjectURL(downloadUrl);
    } catch (error) {
      console.error('Error creating zip file:', error);
    } finally {
      setIsDownloading(false);
    }
  };

  if (isLoading) {
    return (
      <div className="d-flex justify-content-center align-items-center" style={{ minHeight: '50px' }}>
        <div className="text-center">
          <div className="spinner-border spinner-border-sm text-primary" role="status"></div>
        </div>
      </div>
    );
  }

  const handleDownloadClick = async () => {
    setIsDownloading(true);
    await downloadAllDocuments(documents);
  };

  return (
    <div className="d-flex align-items-center">
      {isDownloading ? (
        <div className="d-flex align-items-center">
          <div className="spinner-border spinner-border-sm text-primary me-2" role="status"></div>
        </div>
      ) : (
        <Flexicon icon="download-03" variant="line" className="text-primary pointer" onClick={handleDownloadClick} />
      )}
    </div>
  );
}

export default Documents;
