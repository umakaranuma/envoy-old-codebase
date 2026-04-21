'use client';
import { useTrans } from '@/helpers/services/lang/langService';
import { Button, Input, Label } from '@apptimus-ui/ui-element';
import React, { useEffect, useRef, useState } from 'react';
import { Modal, ModalBody, ModalFooter, ModalHeader } from '@apptimus-ui/modal';
import { form } from '@/constans/Form';
import { clearError, printError } from '@/helpers/handlers/validationErrorHandler';
import QuillEditor from './QuillEditor';
import { Flexicon } from '@apptimus-ui/flexicon';
import { fileUploader } from '@/helpers/services/storageService';
import FilePreviewInput from '@/components/others/page-related/uploader/FilePreviewInput';
import CloseConfirmPop from '../CloseConfirmPop';
import FileDownloadButton from '../uploader/FileDownloadButton';

interface IEmailDocument {
  doc: string;
  name: string;
}

function EmailForm({
  isOpen,
  onCancel,
  recipientNames,
  defaultTemplate,
  emailData,
  defaultFiles,
  disableRemove = false,
  isFormProcessing,
}: {
  isOpen: boolean;
  onCancel: Function;
  recipientNames: string[];
  defaultTemplate?: string;
  emailData: Function;
  defaultFiles?: IEmailDocument[];
  disableRemove?: boolean;
  isFormProcessing: boolean;
}) {
  const t = useTrans('label.email,otr.common');
  const tBe = useTrans('be.msg,be.error,be.attri');
  const [formData, setFormData] = useState({ subject: '', body: '', defaultDocuments: [] });
  const fileInput = useRef<any>(null);
  const [inputKey, setInputKey] = useState(0);
  const [files, setFiles] = useState<File[]>([]);
  const [sizeError, setSizeError] = useState(false);
  console.log('isFormProcessing', isFormProcessing);
  const onFormChange = (name: string, value: any) => {
    setFormData((prevFormData) => ({ ...prevFormData, [name]: value }));
  };

  useEffect(() => {
    onFormChange('defaultDocuments', defaultFiles);
  }, [defaultFiles]);

  async function onSubmit() {
    clearError(form.email.store);
    const error: { [key: string]: Array<{ error_type: string; tokens: { _attribute: string } }> } = {};

    if (!formData.subject) {
      error['subject'] = [
        {
          error_type: 'required',
          tokens: {
            _attribute: 'subject',
          },
        },
      ];
    }

    // if (!formData.body) {
    //   error['body'] = [
    //     {
    //       error_type: 'required',
    //       tokens: {
    //         _attribute: 'body',
    //       },
    //     },
    //   ];
    // }

    if (Object.keys(error).length > 0) {
      printError(error, form.email.store, tBe);
    } else {
      if (files.length > 0) {
        const fileData = await handleFileUpload();
        const documents = [...(formData.defaultDocuments ?? []), ...(fileData ?? [])];
        emailData({ ...formData, documents });
      } else {
        emailData({ ...formData, documents: formData.defaultDocuments });
      }
    }
  }

  const handleFileUpload = async () => {
    if (files.length === 0) {
      return null;
    }

    const fileData: any[] = [];

    for (const file of files) {
      const s3FormData = new FormData();
      s3FormData.append('file', file);
      const key = await fileUploader(s3FormData, 'envoy-test');
      const fileType = file.name.split('.').pop();
      const fileName = file.name;
      fileData.push({ doc: key, name: fileName, type: fileType });
    }

    return fileData;
  };

  const fileChange = () => {
    setSizeError(false);
    const file: File = fileInput.current.files[0];
    const fileSize = file.size;
    if (fileSize > 25200000) {
      setSizeError(true);
      return;
    }
    setFiles((prevFile) => [...prevFile, file]);
    setInputKey((prevKey) => prevKey + 1);
  };

  const handleRemove = (file: File) => {
    setFiles((prevFiles) => prevFiles.filter((f) => f.name !== file.name));
  };

  const handleRemoveDocument = (name: string) => {
    const updatedDocuments = formData.defaultDocuments.filter((doc: IEmailDocument) => doc.name !== name);
    onFormChange('defaultDocuments', updatedDocuments);
  };

  return (
    <Modal isOpen={isOpen} size="lg" scrollable>
      <ModalHeader title={t('send_email')} onClose={() => onCancel()} />
      <ModalBody>
        <div className="row" id={`${form.email.store}`}>
          <div className="col-12 col-md-6 mb-3 custom-select">
            <Label htmlFor="recipients" label={t('recipients')} isRequired />
            <div className="d-flex flex-row align-items-center gap-1">
              {recipientNames.map((name, index) => (
                <div key={index} className="border border-2 px-1 bg-light rounded-1">
                  {name}
                </div>
              ))}
            </div>
          </div>
          <div className="col-12 mb-3">
            <Input isRequired label={t('subject')} value={formData.subject} onChange={(e) => onFormChange('subject', e.target.value)} className="form-control error-subject" name="subject" />
          </div>
          <div className="mb-3 text">
            <Label label={t('body')} isRequired />
            <QuillEditor defaultContent={defaultTemplate} onChange={(body: any) => onFormChange('body', body)} />
          </div>
          <div className="mb-3">
            <div className="fw-semibold">{t('attached_files')}</div>
            {formData.defaultDocuments?.length > 0 && (
              <div className="d-flex flex-column gap-2">
                {formData.defaultDocuments.map((file: IEmailDocument, key) => (
                  <React.Fragment key={key}>
                    {disableRemove ? (
                      <FileDownloadButton fileName={file.name} s3Key={file.doc} />
                    ) : (
                      <FilePreviewInput key={key} fileName={file.name} onCancel={() => handleRemoveDocument(file.name)} />
                    )}
                  </React.Fragment>
                ))}
              </div>
            )}
            {files.length > 0 && (
              <div className="d-flex flex-column gap-2 mt-2">
                {files.map((file, key) => (
                  <FilePreviewInput key={key} fileName={file.name} onCancel={() => handleRemove(file)} />
                ))}
              </div>
            )}
          </div>
          <span className="d-flex align-items-center flex-row gap-1 text-primary fs-14 pointer w-fit-content" onClick={() => fileInput.current?.click()}>
            <Flexicon icon="plus" size={15} />
            {t('add')}
            <input id="file_uploader" className="d-none" type="file" ref={fileInput} onChange={fileChange} key={inputKey} />
          </span>
          {sizeError && <span style={{ color: 'red' }}>File size exceeds the 25 MB limit. Please upload a smaller file.</span>}
        </div>
      </ModalBody>
      <ModalFooter>
        <div className="d-flex justify-content-end gap-2">
          <Button text={t('send')} onClick={onSubmit} width="sm" isLoading={isFormProcessing} />
          {/* <Button text={t('cancel')} color="light" width="sm" onClick={() => onCancel()} /> */}
          <CloseConfirmPop trigger={<Button text={t('cancel')} color="light" width="sm" />} handleOnClose={() => onCancel()} />
        </div>
      </ModalFooter>
    </Modal>
  );
}

export default EmailForm;
