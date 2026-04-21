import { Button, Label } from '@apptimus-ui/ui-element';
import React, { FormEvent, useEffect, useState } from 'react';
import { Flexicon } from '@apptimus-ui/flexicon';
import { useTrans } from '@/helpers/services/lang/langService';
import { form } from '@/constans/Form';
import { clearError, printError } from '@/helpers/handlers/validationErrorHandler';
import { toaster } from '@/helpers/services/toaster';
import { fileUploader } from '@/helpers/services/storageService';
import AttachmentInput from './AttachmentInput';
import QuillEditor from '@/app/crm/a/quotations/_utils/components/create/QuillEditor';

function CreateMsg({
  setIsCreateMsgOpen,
  conversation_id,
  afterSave,
  setFormData,
  formData,
  createMsgFn,
}: {
  setIsCreateMsgOpen: Function;
  conversation_id: string;
  afterSave: Function;
  setFormData: Function;
  formData: any;
  createMsgFn: Function;
}) {
  const t = useTrans('label.chat,otr.common');
  const tBe = useTrans('be.msg,be.error,be.attri');
  const [isFormProcessing, setIsFormProcessing] = useState<boolean>(false);
  const [attachmentFiles, setAttachmentFiles] = useState<any[]>([]);

  useEffect(() => {
    setFormData((prev: any) => ({ ...prev, conversation_id: conversation_id }));
  }, []);

  const onFormChange = (field: string, value: any) => {
    setFormData((prev: any) => ({ ...prev, [field]: value }));
  };

  const handleFileUpload = async (file: File) => {
    if (!file) return null;
    const formData = new FormData();
    formData.append('file', file);
    const fileName = file.name;
    const fileExtension = file.name.split('.').pop();
    const key = await fileUploader(formData, 'envoy-test');
    return { doc: key, name: fileName, type: fileExtension };
  };

  async function onSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    clearError(form.approval.store);
    setIsFormProcessing(true);

    try {
      // Upload all attachment files first
      const uploadedAttachments = await Promise.all(
        attachmentFiles.map(async (file) => {
          const res = await handleFileUpload(file.file);
          return {
            size: file.size,
            type: res?.type,
            name: file.name,
            doc: res?.doc,
          };
        }),
      );

      // Add uploaded attachments to form data
      const payload = { ...formData, documents: uploadedAttachments };

      const responseData = await createMsgFn(payload);
      setIsFormProcessing(false);

      if (responseData.status_code === 417) {
        printError(responseData.result, form.approval.store, tBe);
      }

      if (responseData.is_success) {
        onFormChange('body', '');
        setAttachmentFiles([]);
        afterSave();
        toaster.success(tBe(responseData.message));
      }
    } catch (error) {
      console.error('An error occurred:', error);
      setIsFormProcessing(false);
    }
  }

  const defaultTemplate = `
<h3 style="text-align: center; text-decoration: underline;">[Heading]</h3>
<p>Dear Sir/Madam,</p>
<p>I hope this message finds you well.</p>
<p><br></p>
<p>Kind regards,</p>
<p>[Your Name]</p>
`;

  return (
    <form onSubmit={onSubmit} id={`${form.approval.store}`}>
      <div className="row mt-4 py-5 px-3">
        <div className="col-12 mb-3">
          <div className="d-flex gap-3 panel-title align-items-center">
            <Button
              className="btn btn-sm btn-outline-primary d-flex align-items-center justify-content-center"
              onClick={() => {
                setIsCreateMsgOpen(false);
                onFormChange('body', '');
              }}
            >
              <Flexicon icon="chevron-left" variant="line" size={16} />
            </Button>
            <span>{t('send_new_message')}</span>
          </div>
        </div>
        <div className="mb-3">
          <Label label={t('body')} isRequired />
          <QuillEditor defaultContent={defaultTemplate} onChange={(body: any) => onFormChange('body', body)} />
        </div>
        <div className="col-8">
          <AttachmentInput
            onChange={(files) => {
              setAttachmentFiles(files);
            }}
            onError={() => {}}
          />
        </div>
        <div className="d-flex justify-content-end gap-2">
          <Button text={t('send')} type="submit" width="sm" isLoading={isFormProcessing} />
          <Button
            text={t('cancel')}
            color="light"
            width="sm"
            onClick={() => {
              setIsCreateMsgOpen(false);
              onFormChange('body', '');
            }}
          />
        </div>
      </div>
    </form>
  );
}

export default CreateMsg;
