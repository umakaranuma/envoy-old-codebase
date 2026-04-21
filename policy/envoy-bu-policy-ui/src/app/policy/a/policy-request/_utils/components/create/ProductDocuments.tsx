import { form } from '@/constans/Form';
import { clearError, printError } from '@/helpers/handlers/validationErrorHandler';
import { useTrans } from '@/helpers/services/lang/langService';
import { Input, Label, Skeleton } from '@apptimus-ui/ui-element';
import React, { forwardRef, useEffect, useImperativeHandle, useState } from 'react';
import { fileUploader } from '@/helpers/services/storageService';
import { IDocument, IProductDocument } from '../../model';
import { getProductDocuments } from '../../api-service';
import FilePreviewInput from '@/components/others/page-related/uploader/FilePreviewInput';

const ProductDocuments = forwardRef(
  ({ productId, productType, defaultDocuments, isDraft }: { productId: string; productType: string; defaultDocuments: IProductDocument[]; isDraft: boolean }, ref) => {
    const t = useTrans('label.policy_request,otr.common');
    const tBe = useTrans('be.msg,be.error,be.attri');
    const [documents, setDocuments] = useState<IProductDocument[]>([]);
    const [skeleton, setSkeleton] = useState(false);
    const [formData, setFormData] = useState({} as IDocument);
    const [uploadingDocs, setUploadingDocs] = useState<{ [docId: string]: boolean }>({});

    useEffect(() => {
      const fetchData = async () => {
        const responseData = await getProductDocuments({ type: productType }, productId);
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

    function convertPolicyDocuments(items: any[]) {
      const output: IDocument = {};
      items.forEach((item) => {
        if (!item.value) return;
        // Convert Python-style object string to valid JSON
        const parsed = JSON.parse(item.value?.replace(/'/g, '"'));

        output[item.id] = {
          doc: parsed.doc,
          name: parsed.name,
          type: parsed.type,
        };
      });

      return output;
    }

    useEffect(() => {
      if (defaultDocuments.length > 0) {
        const convertedDocs = convertPolicyDocuments(defaultDocuments as any[]);
        setFormData(convertedDocs);
        console.log('convertedDocs', convertedDocs);
      }
    }, [defaultDocuments]);

    useEffect(() => {
      console.log('formData', formData);
    }, [formData]);

    async function onSubmit() {
      clearError(form.product_document.store);
      const error: { [key: string]: Array<{ error_type: string; tokens: { _attribute: string } }> } = {};

      documents.forEach((doc) => {
        if (doc.is_mandatory === 1 && !formData[doc.id]) {
          error[doc.id] = [
            {
              error_type: 'required',
              tokens: {
                _attribute: 'document',
              },
            },
          ];
        }
      });

      if (Object.keys(error).length > 0 && !isDraft) {
        console.log('Validation errors found:', error);
        printError(error, form.product_document.store, tBe);
        return null;
      } else {
        return formData;
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
      const key = await fileUploader(fileData, `policy/product-documents`);
      return { doc: key, name: fileName, type: fileExtension };
    };

    const handleChangeFile = async (name: string, file: File) => {
      clearError(form.product_document.store);

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

    useImperativeHandle(ref, () => ({
      onSubmit,
    }));

    return (
      <div>
        <form id={`${form.product_document.store}`}>
          <div className="panel-title">{t('document_attachments')}</div>
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
    );
  },
);
export default ProductDocuments;
