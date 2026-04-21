'use client';
import { useTrans } from '@/helpers/services/lang/langService';
import { Input, Label } from '@apptimus-ui/ui-element';
import React, { useEffect, useRef, useState } from 'react';
import { form } from '@/constans/Form';
import { Flexicon } from '@apptimus-ui/flexicon';
import FilePreviewInput from '@/components/others/page-related/uploader/FilePreviewInput';
import QuillEditor from '@/components/others/page-related/email-form/QuillEditor';
import FileDownloadButton from '@/components/others/page-related/uploader/FileDownloadButton';
import { printError } from '@/helpers/handlers/validationErrorHandler';

interface IEmailDocument {
  doc: string;
  name: string;
  type?: string;
}

function EmailView({
  formData,
  setFormData,
  recipientNames,
  isSubjectError,
}: {
  formData: { subject: string; body: string; documents: IEmailDocument[]; defaultTemplate: string; recipientNames: string[]; files?: File[] };
  setFormData: Function;
  recipientNames: string[];
  isSubjectError: boolean;
}) {
  const t = useTrans('otr.common');
  const tBe = useTrans('be.msg,be.error,be.attri');
  const fileInput = useRef<any>(null);
  const [inputKey, setInputKey] = useState(0);
  const [sizeError, setSizeError] = useState(false);

  const onFormChange = (name: string, value: any) => {
    setFormData((prevFormData: any) => ({ ...prevFormData, [name]: value }));
  };

  useEffect(() => {
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
    if (Object.keys(error).length > 0) {
      printError(error, form.email.store, tBe);
    }
  }, [isSubjectError]);

  const fileChange = () => {
    setSizeError(false);
    const file: File = fileInput.current.files[0];
    const fileSize = file.size;
    if (fileSize > 25200000) {
      setSizeError(true);
      return;
    }

    const updatedFiles = formData.files ? [...formData.files, file] : [file];
    onFormChange('files', updatedFiles);
    setInputKey((prevKey) => prevKey + 1);
  };

  const handleRemove = (file: File) => {
    const updatedFiles = formData.files?.filter((f) => f.name !== file.name);
    onFormChange('files', updatedFiles);
  };

  return (
    <div className="row" id={`${form.email.store}`}>
      <div className="col-12 col-md-6 mb-3 custom-select">
        <Label htmlFor="recipients" label={t('recipients')} isRequired />
        <div className="d-flex flex-row flex-wrap align-items-center gap-1">
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
      <div className="mb-3">
        <Label label={t('body')} isRequired />
        <QuillEditor defaultContent={formData.defaultTemplate} onChange={(body: any) => onFormChange('body', body)} />
      </div>
      <div className="mb-3">
        <div className="fw-semibold mb-2">{t('attached_files')}</div>
        {formData.documents && formData.documents?.length > 0 && (
          <div className="d-flex flex-column gap-2">
            {formData.documents.map((file: IEmailDocument, key) => (
              // <FilePreviewInput key={key} fileName={file.name} onCancel={() => handleRemoveDocument(file.name)} disableRemove={true}/>
              <FileDownloadButton fileName={file.name} s3Key={file.doc} key={key} fileType={file.name?.split('.').pop()?.toLowerCase() === 'xlsx' ? 'excel' : 'pdf'} />
            ))}
          </div>
        )}
        {formData.files && formData.files.length > 0 && (
          <div className="d-flex flex-column gap-2 mt-2">
            {formData.files.map((file, key) => (
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
  );
}

export default EmailView;
