import { useTrans } from '@/helpers/services/lang/langService';
import React, { useEffect, useState } from 'react';
import { getIssuedPolicyDocuments, updateIssuedPolicyDocument } from '../../../api-service';
import { Button, Input, Label, Skeleton } from '@apptimus-ui/ui-element';
import { IPolicyDocuments } from '../../../model';
import FilePreviewInput from '@/components/others/page-related/uploader/FilePreviewInput';
import { clearError, printError } from '@/helpers/handlers/validationErrorHandler';
import { form } from '@/constans/Form';
import { handleFileUpload } from '@/helpers/services/commonService';
import { toaster } from '@/helpers/services/toaster';

function Documents({ policyBaseId }: { policyBaseId: string }) {
  const t = useTrans('label.policy_request,otr.common');
  const tBe = useTrans('be.msg,be.error,be.attri');
  // const router = useRouter();
  // const searchParams = useSearchParams();
  const [documents, setDocuments] = useState<IPolicyDocuments[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isFormProcessing, setIsFormProcessing] = useState(false);

  const onFormChange = (id: number, newValue: any) => {
    setDocuments((prevDocuments) => prevDocuments.map((doc) => (doc.id === id ? { ...doc, value: newValue } : doc)));
  };

  useEffect(() => {
    // const tab = searchParams.get('st') || 'policy-related';
    // toggleTableTab(tab);
    fetchData();
  }, []);

  async function onSubmit() {
    clearError(form.product_document.store);
    setIsFormProcessing(true);
    const error: { [key: string]: Array<{ error_type: string; tokens: { _attribute: string } }> } = {};

    documents.forEach((doc) => {
      if (doc.is_mandatory === 1 && !documents[doc.id]) {
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
      printError(error, form.product_document.store, tBe);
      setIsFormProcessing(false);
    } else {
      const responseData = await updateIssuedPolicyDocument(policyBaseId, documents);
      if (responseData?.is_success) {
        fetchData();
        toaster.success(tBe(responseData.message));
      }
      setIsFormProcessing(false);
    }
  }

  const fetchData = async () => {
    setIsLoading(true);
    try {
      const responseData = await getIssuedPolicyDocuments(policyBaseId);
      if (responseData.is_success) {
        const values =
          responseData.result.data.map((doc: any) => ({
            ...doc,
            value: doc.value ? JSON.parse(doc.value.replace(/'/g, '"')) : null,
          })) || [];
        setDocuments(values);
      }
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleChangeFile = async (id: number, file: File) => {
    clearError(form.product_document.store);
    const fileData = await handleFileUpload(file);
    if (fileData) {
      onFormChange(id, { doc: fileData.key, type: file.type, name: file.name });
    } else {
      console.error('File upload failed');
    }
  };

  useEffect(() => {
    console.log('Documents updated:', documents);
  }, [documents]);

  return (
    <div>
      {isLoading ? (
        <Skeleton width="100%" height="200px" />
      ) : (
        <div>
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
                              {doc.value ? (
                                <FilePreviewInput downloadable s3Key={doc.value.doc} fileName={doc.value.name} onCancel={() => onFormChange(doc.id, null)} />
                              ) : (
                                <Input type="file" value={''} onChange={(e: any) => handleChangeFile(doc.id, e.target.files[0])} className={`form-control error-${doc.id}`} name={`${doc.id}`} />
                              )}
                              {/* <FileDownloadButton s3Key={doc.value ? JSON.parse(doc.value?.replace(/'/g, '"')).doc : ''} /> */}
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
                            {doc.value ? (
                              <FilePreviewInput downloadable s3Key={doc.value.doc} fileName={doc.value.name} onCancel={() => onFormChange(doc.id, null)} />
                            ) : (
                              <Input type="file" value={''} onChange={(e: any) => handleChangeFile(doc.id, e.target.files[0])} className={`form-control error-${doc.id}`} name={`${doc.id}`} />
                            )}
                            {/* <FileDownloadButton s3Key={doc.value ? JSON.parse(doc.value?.replace(/'/g, '"')).doc : ''} /> */}
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
        </div>
      )}
      <div className="d-flex justify-content-end gap-2">
        <Button text={t('update')} onClick={onSubmit} width="sm" isLoading={isFormProcessing} />
      </div>
    </div>
  );
}

export default Documents;
