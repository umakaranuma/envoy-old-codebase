import { form } from '@/constans/Form';
import { clearError, printError } from '@/helpers/handlers/validationErrorHandler';
import { useTrans } from '@/helpers/services/lang/langService';
import { toaster } from '@/helpers/services/toaster';
import { Modal, ModalBody, ModalFooter, ModalHeader } from '@apptimus-ui/modal';
import { Button, Input, Label } from '@apptimus-ui/ui-element';
import React, { FormEvent, useState } from 'react';
import { Flexicon } from '@apptimus-ui/flexicon';
import { fileUploader } from '@/helpers/services/storageService';
import { IMultiDocuments } from '@/app/policy/a/policy-request/_utils/model';
import { createIssuedPolicyDocuments } from '../../../../api-service';

function AddPolicyDocument({ isOpen, onCancel, afterSave, issuedPolicyId }: { isOpen: boolean; onCancel: Function; afterSave: Function; issuedPolicyId: string }) {
  const t = useTrans('label.policy_request,otr.common');
  const tBe = useTrans('be.msg,be.error,be.attri');
  const [isFormProcessing, setIsFormProcessing] = useState(false);
  const [resources, setResources] = useState<IMultiDocuments[]>([]);
  const [inputKey, setInputKey] = useState(0);
  const [error, setError] = useState('');

  async function onSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    clearError(form.document.store);
    setIsFormProcessing(true);

    const erroredResource = resources.find((res) => {
      return res.error;
    });

    if (erroredResource) {
      setIsFormProcessing(false);
      return;
    }

    try {
      const [documents] = await Promise.all([Promise.all(resources.map((res) => handleFileUpload(res)))]);

      if (documents.some((res) => res === null)) {
        setIsFormProcessing(false);
        return;
      }

      const data = documents.map((res: any, index) => {
        return {
          ...resources[index],
          file: res.key,
          file_name: res.name + `.${res.type}`,
          document_type: res.type,
          notes: res.notes,
          document_category: 'Policy-Related',
        };
      });

      const responseData = await createIssuedPolicyDocuments({ issued_policy_id: issuedPolicyId, documents: data });
      setIsFormProcessing(false);

      if (responseData.status_code === 417) {
        printError(responseData.result, form.document.store, tBe);
      }

      if (responseData.is_success) {
        afterSave();
        toaster.success(tBe(responseData.message));
      }
    } catch (error) {
      console.error('An error occurred:', error);
    }
  }

  const fileChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const target = e.target;

    if (target instanceof HTMLInputElement && target.files) {
      const files = Array.from(target.files);
      if (files.length > 5) {
        setError('You can only upload up to 5 files.');
        return;
      }
      const hasNonPdf = files.some((file) => file.type !== 'application/pdf' && file.name.split('.').pop()?.toLowerCase() !== 'pdf');
      if (hasNonPdf) {
        setError('Only PDF files are allowed.');
        return;
      }
      const newResources: IMultiDocuments[] = files.map((file) => {
        const isTooLarge = file.size > 25 * 1000000;

        const originalName = file.name;
        const dotIndex = originalName.lastIndexOf('.');
        const baseName = originalName.substring(0, dotIndex);
        const extension = originalName.substring(dotIndex + 1);

        return {
          file,
          error: isTooLarge,
          baseName,
          extension,
          notes: '',
        };
      });

      setResources((prev) => [...prev, ...newResources]);
      setInputKey((prev) => prev + 1);
    }
  };

  const handleRemoveFile = (index: number) => {
    setResources((prev) => prev.filter((_, i) => i !== index));
  };

  const handleFileUpload = async (resource: IMultiDocuments) => {
    const formData = new FormData();
    if (!resource.file) {
      return null;
    }
    formData.append('file', resource.file);
    const fileName = resource.baseName;
    const fileExtension = resource.extension;
    const key = await fileUploader(formData, 'envoy-test');
    return { key: key, name: fileName, type: fileExtension, notes: resource.notes };
  };

  return (
    <Modal isOpen={isOpen}>
      <ModalHeader title={t('upload_attachment_file')} onClose={() => onCancel()} />
      <form onSubmit={onSubmit} id={`${form.document.store}`}>
        <ModalBody>
          <div className="row">
            <div className="col-12 mb-3">
              {resources.length > 0 ? (
                <div>
                  {resources.map((res, index) => (
                    <div className="mb-2 p-2 border rounded-2" key={index}>
                      <div className="d-flex flex-row gap-2 align-items-center">
                        <div>
                          <Label label={t('rename')} />
                          <Input
                            type="text"
                            value={res.baseName}
                            onChange={(e) => {
                              const updated = [...resources];
                              updated[index].baseName = e.target.value;
                              setResources(updated);
                            }}
                          />
                        </div>
                        <div className="mt-4">.{res.extension}</div>
                        <div>
                          <Label label={t('notes')} />
                          <Input
                            type="text"
                            value={res.notes}
                            onChange={(e) => {
                              const updated = [...resources];
                              updated[index].notes = e.target.value;
                              setResources(updated);
                            }}
                          />
                        </div>
                        <div className="d-flex flex-row justify-content-between gap-2 mt-4">
                          <Flexicon icon="x-square" variant="line" className="text-danger action-icon" onClick={() => handleRemoveFile(index)} />
                        </div>
                      </div>
                      <div style={{ color: 'red' }} className="mt-1">
                        {res.error ? 'This file size is larger than 25mb.' : ''}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="col-12 mb-3">
                  <Label htmlFor="document" label={t('document')} isRequired />
                  <input type="file" accept="application/pdf" multiple onChange={fileChange} className="form-control error-documents" />
                </div>
              )}
              {resources.length > 0 && resources.length < 5 && (
                <div className="clickable-text" onClick={() => document.getElementById('file_uploader')?.click()}>
                  <Flexicon icon="plus" size={15} />
                  {t('add')}
                  <input id="file_uploader" className="d-none" type="file" onChange={fileChange} key={inputKey} />
                </div>
              )}
              {error && <span style={{ color: 'red' }}>{error}</span>}
            </div>
          </div>
        </ModalBody>
        <ModalFooter>
          <div className="d-flex justify-content-end gap-2">
            <Button text={t('submit')} type="submit" width="sm" isLoading={isFormProcessing} />
            <Button text={t('cancel')} color="light" width="sm" onClick={() => onCancel()} />
          </div>
        </ModalFooter>
      </form>
    </Modal>
  );
}

export default AddPolicyDocument;
