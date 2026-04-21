import { useTrans } from '@/helpers/services/lang/langService';
import React, { useEffect, useState } from 'react';
import { Modal, ModalBody, ModalFooter, ModalHeader } from '@apptimus-ui/modal';
import { Button, Input } from '@apptimus-ui/ui-element';

export const SalesReportView = ({ isOpen, viewId, onClose }: { isOpen: boolean; viewId: string; onClose: Function; setEditId: Function }) => {
  const t = useTrans('label.sales_report,otr.common');

  useEffect(() => {
    const fetchData = async () => {};

    if (viewId) {
      fetchData();
    }
  }, [viewId]);
  const [exportType, setExportType] = useState('pdf');

  return (
    <Modal isOpen={isOpen}>
      <ModalHeader title={t('choose_file')} onClose={() => onClose()} />
      <ModalBody>
        <>
          <div className="d-flex flex-wrap gap-3">
            <div className="form-check">
              <Input type="radio" id="pdf" name="commission-type" className="form-check-input pointer" checked={exportType === 'pdf'} onChange={() => setExportType('pdf')} />
              <label className="form-check-label" htmlFor="pdf">
                Pdf
              </label>
            </div>
            <div className="form-check">
              <Input type="radio" id="excel" name="commission-type" className="form-check-input pointer" checked={exportType === 'excel'} onChange={() => setExportType('excel')} />
              <label className="form-check-label" htmlFor="excel">
                Excel
              </label>
            </div>
          </div>
        </>
      </ModalBody>
      <ModalFooter>
        <div className="d-flex justify-content-end gap-2">
          <Button text={t('create')} type="submit" width="sm" onClick={() => {}} />
          <Button text={t('close')} color="light" width="sm" onClick={() => onClose()} />
        </div>
      </ModalFooter>
    </Modal>
  );
};
