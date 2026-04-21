import { form } from '@/constans/Form';
import { clearError, printError } from '@/helpers/handlers/validationErrorHandler';
import { useTrans } from '@/helpers/services/lang/langService';
import { Flexicon } from '@apptimus-ui/flexicon';
import { Button, Input, Label, Skeleton } from '@apptimus-ui/ui-element';
import React, { useEffect, useState } from 'react';
import { createSupportingDocuments, getSupportingDocuments } from '../../../../api-service';
import { IResource, ISupportingDocument } from '../../../../model';
import { fileUploader } from '@/helpers/services/storageService';
import { useParams, useSearchParams } from 'next/navigation';
import FilePreviewInput from '@/components/others/page-related/uploader/FilePreviewInput';

function SupportingDocuments({ setToggleTab, requestId, type }: { setToggleTab: Function; requestId: string; type: string }) {
  const t = useTrans('label.my_policy,otr.common');
  const tBe = useTrans('be.msg,be.error,be.attri');
  const [documents, setDocuments] = useState<ISupportingDocument[]>([]);
  const [isFormProcessing, setIsFormProcessing] = useState(false);
  const [skeleton, setSkeleton] = useState(false);
  const [formData, setFormData] = useState({} as IResource);

  const [uploadingDocs, setUploadingDocs] = useState<{ [docId: string]: boolean }>({});

  const params = useParams();
  const searchParams = useSearchParams();
  const appId = params.appId as string;
  const rId = searchParams.get('rId');
  const riskTypeIds = Array.from(rId ? rId.split(',') : []);

  useEffect(() => {
    const fetchData = async () => {
      const responseData = await getSupportingDocuments({ type: riskTypeIds.length > 1 ? 'group' : 'product' }, requestId);
      if (responseData?.is_success) {
        setDocuments(responseData.result.data);
        setSkeleton(false);
      }
    };
    setSkeleton(true);
    fetchData();
  }, []);

  const onFormChange = (name: string, value: any) => {
    setFormData((prevFormData) => ({ ...prevFormData, [name]: value }));
  };

  useEffect(() => {
    console.log('Form Data Updated:', formData);
  }, [formData]);

  async function onSubmit() {
    clearError(form.supporting_documents.store);
    const error: { [key: string]: Array<{ error_type: string; tokens: { _attribute: string } }> } = {};

    documents.forEach((doc) => {
      if (doc.is_mandatory === 1 && !formData[doc.id]) {
        error[doc.id] = [
          {
            error_type: 'required',
            tokens: {
              _attribute: doc.id.toString(),
            },
          },
        ];
      }
    });

    if (Object.keys(error).length > 0) {
      printError(error, form.supporting_documents.store, tBe);
    } else {
      try {
        setIsFormProcessing(true);
        const responseData = await createSupportingDocuments({ values: formData, request_id: requestId, type: type });
        setIsFormProcessing(false);

        if (responseData.status_code === 417) {
          printError(responseData.result, form.supporting_documents.store, tBe);
        }

        if (responseData.is_success) {
          setToggleTab('terms_and_conditions');
        }
      } catch (error) {
        console.error('An error occurred:', error);
      }
    }
  }

  const handleFileUpload = async (file: File) => {
    const fileData = new FormData();
    if (!file) {
      return null;
    }
    fileData.append('file', file);
    const fileName = file.name;
    const fileExtension = file.name.split('.').pop();
    const key = await fileUploader(fileData, `${appId}/policy/supporting-documents`);
    return { doc: key, name: fileName, type: fileExtension };
  };

  useEffect(() => {
    console.log('Form Data:', formData);
  }, [formData]);

  const handleChangeFile = async (name: string, file: File) => {
    clearError(form.supporting_documents.store);

    try {
      setUploadingDocs((prev) => ({ ...prev, [name]: true }));

      const fileData = await handleFileUpload(file);

      if (fileData) {
        onFormChange(name, fileData);
      } else {
        console.error('File upload failed');
      }
    } catch (error) {
      console.error(error);
    } finally {
      setUploadingDocs((prev) => ({ ...prev, [name]: false }));
    }
  };
  return (
    <>
      <div className="mb-4">
        <form id={`${form.supporting_documents.store}`}>
          <div className="panel-title">{t('supporting_documents_attachments')}</div>
          {skeleton ? (
            <Skeleton height="100px" width="100%" />
          ) : (
            <>
              {documents.length > 0 ? (
                <>
                  {
                    <>
                      {documents.filter((doc) => doc.type === 'policy').length > 0 && (
                        <div className="row mb-3">
                          <div className="panel-subtitle">{t('policy_related')}</div>
                          {documents
                            .filter((doc) => doc.type === 'policy')
                            .map((doc) => (
                              <div key={doc.id} className="col-12 col-md-4 mb-2 d-flex flex-column">
                                <div className="d-flex flex-row">
                                  <Label label={doc.name} isRequired={doc.is_mandatory === 1} />
                                </div>
                                <div>
                                  {formData[doc.id] ? (
                                    <FilePreviewInput fileName={formData[doc.id]?.name} onCancel={() => onFormChange(`${doc.id}`, null)} />
                                  ) : (
                                    <>
                                      <Input
                                        type="file"
                                        value={''}
                                        onChange={(e: any) => handleChangeFile(`${doc.id}`, e.target.files[0])}
                                        className={`form-control error-${doc.id}`}
                                        name={`${doc.id}`}
                                      />
                                      {uploadingDocs[doc.id] && (
                                        <div className="w-100 mt-1">
                                          <div className="progress" style={{ height: '6px' }}>
                                            <div className="progress-bar progress-bar-striped progress-bar-animated" role="progressbar" style={{ width: '100%' }} />
                                          </div>
                                          <small>Uploading...</small>
                                        </div>
                                      )}
                                    </>
                                  )}
                                </div>
                              </div>
                            ))}
                        </div>
                      )}
                    </>
                  }
                  <>
                    {documents.filter((doc) => doc.type === 'risk').length > 0 && (
                      <div className="row">
                        <div className="panel-subtitle">{t('risk_related')}</div>
                        {documents
                          .filter((doc) => doc.type === 'risk')
                          .map((doc) => (
                            <div key={doc.id} className="col-12 col-md-4 mb-2 d-flex flex-column">
                              <div className="d-flex flex-row">
                                <Label label={doc.name} isRequired={doc.is_mandatory === 1} />
                              </div>
                              <div>
                                {formData[doc.id] ? (
                                  <FilePreviewInput fileName={formData[doc.id]?.name} onCancel={() => onFormChange(`${doc.id}`, null)} />
                                ) : (
                                  <>
                                    <Input
                                      type="file"
                                      value={''}
                                      onChange={(e: any) => handleChangeFile(`${doc.id}`, e.target.files[0])}
                                      className={`form-control error-${doc.id}`}
                                      name={`${doc.id}`}
                                    />
                                    {uploadingDocs[doc.id] && (
                                      <div className="w-100 mt-1">
                                        <div className="progress" style={{ height: '6px' }}>
                                          <div className="progress-bar progress-bar-striped progress-bar-animated" role="progressbar" style={{ width: '100%' }} />
                                        </div>
                                        <small>Uploading...</small>
                                      </div>
                                    )}
                                  </>
                                )}
                              </div>
                            </div>
                          ))}
                      </div>
                    )}
                  </>
                </>
              ) : (
                <div className="text-muted panel-title my-2 text-center">{t('no_documents_available')}</div>
              )}
            </>
          )}
        </form>
      </div>
      <div className="d-flex justify-content-start gap-2 mt-3">
        <Button color="light" className="d-flex align-items-center gap-1" onClick={() => setToggleTab('payment_info')}>
          <Flexicon icon="chevron-left" variant="line" size={18} />
          <span className="d-none d-sm-inline">{t('back')}</span>
        </Button>
        <Button color="primary" className="d-flex align-items-center gap-1" type="submit" onClick={onSubmit} isLoading={isFormProcessing}>
          <span className="d-none d-sm-inline">{t('next')}</span>
          <Flexicon icon="chevron-right" variant="line" size={18} />
        </Button>
        {/* <Button text={t('update')} type="submit" width="sm" isLoading={undefined} disabled={skeleton} />
                              <Button text={t('cancel')} color="light" width="sm" /> */}
      </div>
    </>
  );
}

export default SupportingDocuments;
