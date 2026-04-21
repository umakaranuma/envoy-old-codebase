import { Flexicon } from '@apptimus-ui/flexicon';
import { Button } from '@apptimus-ui/ui-element';
import React from 'react';
import { IFilePreviewer, IMessage } from '../model';
import { useTrans } from '@/helpers/services/lang/langService';
import FilePreviewer from './FilePreviewer';

function ViewMsg({ selectedEmail, setSelectedEmail, handleDocExtraction }: { selectedEmail: IMessage; setSelectedEmail: Function; handleDocExtraction?: (file: IFilePreviewer) => void }) {
  const t = useTrans('label.chat,otr.common');

  return (
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
              {selectedEmail.attachments.map((attachment) => {
                return (
                  <div key={attachment.id} className="col-12 col-md-8 me-2">
                    <FilePreviewer
                      handleDocExtraction={handleDocExtraction ? (file) => handleDocExtraction(file) : undefined}
                      file={{
                        id: attachment.id,
                        name: attachment.file_name,
                        size: attachment.size_bytes,
                        type: attachment.content_type,
                        url: attachment.file_url,
                      }}
                    />
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default ViewMsg;
