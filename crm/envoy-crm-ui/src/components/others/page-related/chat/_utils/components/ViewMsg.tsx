import { Flexicon } from '@apptimus-ui/flexicon';
import { Button } from '@apptimus-ui/ui-element';
import React from 'react';
import { IMessage } from '../model';
import { useTrans } from '@/helpers/services/lang/langService';
import AttachmentFile from './FilePreviewer';

function ViewMsg({ selectedEmail, setSelectedEmail, handleAddQuotation, loading }: { selectedEmail: IMessage; setSelectedEmail: Function; handleAddQuotation: (id: any) => void; loading: boolean }) {
  const t = useTrans('label.chat,otr.common');
  const autoConvertBytes = (bytes: number, binary = true) => {
    const units = ['B', 'KB', 'MB', 'GB', 'TB'];
    const divisor = binary ? 1024 : 1000;

    if (bytes === 0) return '0 B';

    let unitIndex = 0;
    while (bytes >= divisor && unitIndex < units.length - 1) {
      bytes /= divisor;
      unitIndex++;
    }

    return `${Math.round(bytes * 100) / 100} ${units[unitIndex]}`;
  };

  return (
    <>
      <div className="p-3 text">
        <div className="d-flex align-items-center gap-2">
          <Button className="btn btn-sm btn-outline-primary" onClick={() => setSelectedEmail(null)}>
            <Flexicon icon="chevron-left" variant="line" size={16} />
          </Button>
          <div className="fw-semibold">{t('message_detail')}</div>
        </div>
        <div className="p-3">
          <div dangerouslySetInnerHTML={{ __html: selectedEmail.body }} />
          {selectedEmail.attachments && selectedEmail.attachments.length > 0 && (
            <div className="mt-4 border-top pt-3">
              <h6 className="fw-bold mb-3">
                {t('attachment_files')} ({selectedEmail.attachments.length})
              </h6>
              <div className="row">
                {selectedEmail.attachments.map((attachment, index) => {
                  return (
                    <div className="col-12 col-md-8 me-2" key={index}>
                      <AttachmentFile
                        file={{
                          id: attachment.id,
                          name: attachment.file_name,
                          size: autoConvertBytes(attachment.size_bytes),
                          type: attachment.content_type,
                          url: attachment.download_url,
                        }}
                        handleAddQuotation={handleAddQuotation}
                        loading={loading}
                        isReceived={selectedEmail.type !== 'sent'}
                      />
                    </div>
                  );
                })}
              </div>
            </div>
          )}
        </div>
      </div>
    </>
  );
}

export default ViewMsg;
