import { useTrans } from '@/helpers/services/lang/langService';
import { Modal, ModalBody, ModalFooter, ModalHeader } from '@apptimus-ui/modal';
import { Button } from '@apptimus-ui/ui-element';
import React from 'react';

function Preview({ isOpen, setIsPreviewOpen, previewData }: { isOpen: boolean; setIsPreviewOpen: Function; previewData: any }) {
  const t = useTrans('label.quotations,otr.common');

  return (
    <Modal isOpen={isOpen} size="lg" scrollable>
      <ModalHeader title={t('preview')} />
      <ModalBody>
        <div dangerouslySetInnerHTML={{ __html: previewData }} className="p-4 border border-2"></div>
      </ModalBody>
      <ModalFooter>
        <div className="d-flex justify-content-end gap-2">
          <Button text={t('close')} color="light" width="sm" onClick={() => setIsPreviewOpen(false)} />
        </div>
      </ModalFooter>
    </Modal>
  );
}

export default Preview;
