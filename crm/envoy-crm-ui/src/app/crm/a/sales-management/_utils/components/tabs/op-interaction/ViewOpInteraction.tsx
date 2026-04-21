import { useEffect, useRef, useState } from 'react';
import { Modal, ModalBody, ModalFooter, ModalHeader } from '@apptimus-ui/modal';
import { Button, Skeleton } from '@apptimus-ui/ui-element';
import { Description } from '@/components/others/Description';
import { useTrans } from '@/helpers/services/lang/langService';
import { addDocuments, deleteDocument, getAllDocuments, getOneOpInteraction } from '../../../api-service';
import { IDocument, IInteraction } from '../../../model';
import { Flexicon } from '@apptimus-ui/flexicon';
import { toaster } from '@/helpers/services/toaster';
import { fileReceiver, fileRemover, fileUploader } from '@/helpers/services/storageService';
import { printError } from '@/helpers/handlers/validationErrorHandler';
import { form } from '@/constans/Form';
import DeleteConfirmPop from '@/components/others/DeleteConfirmPop';

export const ViewOpInteraction = ({ isOpen, viewId, onClose, opportunityId }: { isOpen: boolean; viewId: string; onClose: Function; opportunityId: string }) => {
  const t = useTrans('label.sales_managements,otr.common');
  const tBe = useTrans('be.msg,be.error,be.attri');
  const [data, setData] = useState({} as IInteraction);
  const [skeleton, setSkeleton] = useState(true);
  const [tab, setTab] = useState('Basic');
  const [documents, setDocuments] = useState<IDocument[]>([]);
  const [docInit, setDocInit] = useState(false);
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const [resourceUploadskeleton, setResourceUploadskeleton] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      const responseData = await getOneOpInteraction(opportunityId, viewId);
      if (responseData?.is_success) {
        fetchAllDocuments(responseData.result.entity_id);
        setData(responseData.result);
        setSkeleton(false);
      }
    };

    if (viewId) {
      setSkeleton(true);
      fetchData();
    }
  }, [viewId]);

  const fetchAllDocuments = async (entity_id: string) => {
    const res = await getAllDocuments(entity_id);
    if (res.is_success) {
      setDocuments(res.result);
      setDocInit(true);
    }
  };

  const removeDocuments = async (id: string, key: string) => {
    const responseData = await deleteDocument(data.entity_id, id);

    if (responseData.is_success) {
      await fileRemover(key);
      fetchAllDocuments(data.entity_id);
      toaster.success(tBe(responseData.message));
    }
  };

  const viewFile = async (key: string) => {
    try {
      const fileUrl = await fileReceiver({ key });
      window.open(fileUrl, '_blank');
    } catch (error) {
      console.error('Error opening file:', error);
    }
  };

  const triggerFileUpload = () => {
    if (fileInputRef.current) {
      fileInputRef.current.click();
    }
  };

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    if (!event.target.files || event.target.files.length === 0) return;
    setResourceUploadskeleton(true);

    const file = event.target.files[0];
    const fileType = file.type;
    console.log('Selected file:', file.name, 'Type:', fileType);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const key = await fileUploader(formData, 'documents');

      const response = await addDocuments(data.entity_id, {
        name: file.name,
        doc: key,
        type: fileType,
      });

      if (response.status_code === 417) {
        printError(response.result, form.document_crud.store, tBe);
      }

      if (response.is_success) {
        toaster.success(tBe(response.message));
        fetchAllDocuments(data.entity_id);
        setResourceUploadskeleton(false);
      }
    } catch (error) {
      console.error('File upload error:', error);
    }
  };

  return (
    <Modal isOpen={isOpen}>
      <ModalHeader title={t('interactions_details')} onClose={() => onClose()} />
      <ModalBody>
        <div className="il-tab mb-3">
          <div className={`il-tab-item ${tab === 'Basic' ? 'active' : ''}`} onClick={() => setTab('Basic')}>
            {t('basic_info')}
          </div>
          <div className={`il-tab-item ${tab === 'resource' ? 'active' : ''}`} onClick={() => setTab('resource')}>
            {t('resources')}
          </div>
        </div>
        {tab === 'Basic' ? (
          <div className="row">
            <div className="col-12 col-md-6 mb-3">
              <Description label={t('date')} value={data?.date || '-'} skeleton={skeleton} />
            </div>
            <div className="col-12 col-md-6 mb-3">
              <Description label={t('channel')} value={data?.channel_name || '-'} skeleton={skeleton} />
            </div>
            <div className="col-12 col-md-6 mb-3">
              <Description label={t('contact')} value={data?.contact_by_display_name || '-'} skeleton={skeleton} />
            </div>
            <div className="col-12 col-md-6 mb-3">
              <Description label={t('remarks')} value={data?.notes || '-'} skeleton={skeleton} />
            </div>
          </div>
        ) : (
          <div>
            {!docInit && <Skeleton width="225px" height="36px" />}
            {documents.length > 0 ? (
              <>
                {documents.map((doc: IDocument) => (
                  <div key={doc.id} className="d-flex  gap-2 align-items-center mb-2">
                    <div className="border border-2 d-flex justify-content-between gap-3 align-items-center rounded-1 col-6 px-2 p-1">
                      <div>{doc.name}</div>
                      <DeleteConfirmPop
                        trigger={<Flexicon icon="x-square" variant="line" className="text-danger action-icon" />}
                        deleteId={doc.id}
                        handleOnDelete={() => removeDocuments(doc.id, doc.doc)}
                        onClose={onClose}
                      />
                    </div>
                    <Flexicon icon="eye" variant="line" className="action-icon" onClick={() => viewFile(doc.doc)} />
                  </div>
                ))}
                {resourceUploadskeleton && <Skeleton width="225px" height="36px" />}
              </>
            ) : (
              <>{docInit && <div>{t('no_documents_found')}</div>}</>
            )}
            <Button size="sm" className="d-flex align-items-center gap-1 mt-3" onClick={triggerFileUpload}>
              <Flexicon icon="plus-circle" size={15} />
              <span className="d-none d-sm-inline">{t('add_new')}</span>
              <input type="file" className="d-none" ref={fileInputRef} onChange={handleFileUpload} />
            </Button>
          </div>
        )}
      </ModalBody>
      <ModalFooter>
        <div className="d-flex justify-content-end gap-2">
          {/* <Button text={t('edit_task_details')} type="submit"  width="sm" onClick={handleEditTaskConfig} /> */}
          <Button text={t('close')} color="light" width="sm" onClick={() => onClose()} />
        </div>
      </ModalFooter>
    </Modal>
  );
};
