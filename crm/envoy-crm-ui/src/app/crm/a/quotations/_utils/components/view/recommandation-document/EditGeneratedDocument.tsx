import { form } from '@/constans/Form';
import { useTrans } from '@/helpers/services/lang/langService';
import { Modal, ModalBody, ModalFooter, ModalHeader } from '@apptimus-ui/modal';
import { AsyncSelect, Select } from '@apptimus-ui/select';
import { Button, Input, Label, Skeleton } from '@apptimus-ui/ui-element';
import React, { useEffect, useMemo, useRef, useState } from 'react';
import { Flexicon } from '@apptimus-ui/flexicon';
import { IAttribute, IEmailDocument, initGenerateForm, IReceivedQuotation } from '../../../model';
import KeyPointsQuotationList from '../received/shortlisted/KeyPointsQuotationList';
import { createPDF, generateDocument, getAllVendorQuotation, getDocumentNextVersion, getOneGeneratedDocument } from '../../../api-service';
import { fetchAllCriteria, fetchAllShortListDropdownData, getPDFhtml } from '../../../service';
import { clearError, printError } from '@/helpers/handlers/validationErrorHandler';
import { toaster } from '@/helpers/services/toaster';
import { InputSkeleton } from '@/components/others/InputSkeleton';
import { getLocalStorage } from '@/helpers/handlers/localStorageHandler';
import { local_storage } from '@/constans/StorageKeys';

function EditGeneratedDocument({
  isOpen,
  onCancel,
  setEmailData,
  currentEditId,
  afterSave,
  quotationId,
}: {
  isOpen: boolean;
  onCancel: Function;
  setEmailData: Function;
  currentEditId: string;
  afterSave: Function;
  quotationId: string;
}) {
  const t = useTrans('label.quotations,otr.common');
  const tBe = useTrans('be.msg,be.error,be.attri');
  const [formData, setFormData] = useState(initGenerateForm);
  const [selectedQuotation, setSelectedQuotation] = useState<IReceivedQuotation[]>([]);
  const [defaultValue, setDefaultValue] = useState();
  const [allCriteria, setAllCriteria] = useState<IAttribute[]>([]);
  const [criteria, setCriteria] = useState<IAttribute[]>([]);
  const [isFormProcessing, setIsFormProcessing] = useState(false);
  const [skeleton, setSkeleton] = useState(false);
  const [loading, setLoading] = useState(false);
  const [isPdfGenerated, setIsPdfGenerated] = useState(false);
  const date = new Date();
  const pdfRef = useRef<HTMLDivElement>(null);
  const user = useMemo(() => getLocalStorage(local_storage.auth_user_info), []);
  const [selectedAttributes, setSelectedAttributes] = useState<{ column: string; title: string }[]>([]);

  useEffect(() => {
    const fetchData = async () => {
      const responseData = await getOneGeneratedDocument(currentEditId);
      if (responseData.is_success) {
        setFormData(responseData.result);
        setSelectedAttributes(responseData.result.selected_columns);
        setSelectedQuotation(responseData.result.vendor_response_ids);

        if (responseData.result.customer) {
          onFormChange('customer_id', responseData.result.customer.id);
          onFormChange('customer_name', responseData.result.customer.name);
        }

        const criteriaData = await fetchAllCriteria();
        if (criteriaData.length > 0) {
          setAllCriteria(criteriaData);
          const requiredTitles = responseData.result.attribute_ids ? responseData.result.attribute_ids.map((item: any) => item.column) : [];
          const filterValues = criteriaData.filter((item: any) => requiredTitles.includes(item.column));
          const attributeIds = filterValues.map((att: any) => att.id);
          onFormChange('attribute_id', attributeIds);
          setCriteria(filterValues);
          setDefaultValue(filterValues);
          setSkeleton(false);
        }
      }
    };

    if (currentEditId) {
      setSkeleton(true);
      fetchData();
      onFormChange('document_id', currentEditId);
    }
  }, [currentEditId]);

  const handlePreviewPDF = () => {
    const newWindow = window.open('', '_blank');

    if (newWindow) {
      const content = getPDFhtml(pdfRef.current ? pdfRef.current.innerHTML : '', selectedQuotation, formData.version, formData.comment);

      // Write the base content first
      newWindow.document.write(content);
      newWindow.document.close();

      // Wait until the document is fully loaded before injecting styles
      newWindow.onload = () => {
        const style = newWindow.document.createElement('style');
        style.textContent = `    
          body {
            margin: 50px 200px 50px 200px;
          }
            [role="img"] {
        display: none !important;
          }
        `;
        newWindow.document.head.appendChild(style);
      };
    } else {
      console.error('Failed to open a new window.');
    }
  };

  useEffect(() => {
    const fetchAllSP = async () => {
      const response = await getAllVendorQuotation({ filter: 'shortlisted' }, quotationId);
      if (response.is_success) {
        const receivedList = response.result;
        const selectedQuotationIds = selectedQuotation.map((att) => att.id);
        const matchedDocs = receivedList?.filter((a: any) => selectedQuotationIds.includes(a.id));
        setSelectedQuotation(matchedDocs);
        setLoading(false);
      }
    };

    const fetchData = async () => {
      const criteriaData = await fetchAllCriteria();
      if (criteriaData.length > 0) {
        setAllCriteria(criteriaData);
        const requiredTitles = selectedAttributes.map((attribute) => attribute.column);
        const filterValues = criteriaData.filter((item: any) => requiredTitles.includes(item.column));
        setCriteria(filterValues);
        setDefaultValue(filterValues);
        setSkeleton(false);
      }
    };

    if (selectedAttributes.length > 0) {
      setSkeleton(true);
      setLoading(true);
      fetchAllSP();
      fetchData();
    }
  }, [selectedAttributes]);

  useEffect(() => {
    if (criteria.length > 0) {
      const columnNames = criteria.map((att) => att.column);
      onFormChange('columns', columnNames);
    } else {
      onFormChange('columns', []);
    }
  }, [criteria]);

  const onFormChange = (name: string, value: any) => {
    setFormData((prevFormData) => ({ ...prevFormData, [name]: value }));
  };

  async function onSubmit({ is_sent, is_draft }: { is_sent?: boolean; is_draft?: boolean }) {
    clearError(form.generate_doc.store);
    setIsFormProcessing(true);

    try {
      const responseData = await generateDocument(quotationId, {
        ...formData,
        vendor_response_ids: selectedQuotation.length > 0 ? selectedQuotation.map((quote: IReceivedQuotation) => quote.id) : [],
        is_sent,
        is_draft,
      });
      setIsFormProcessing(false);

      if (responseData.status_code === 417) {
        printError(responseData.result, form.generate_doc.store, tBe);
      }

      if (responseData.is_success) {
        setIsPdfGenerated(true);
        const res = await getDocumentNextVersion(selectedQuotation.map((q) => q.id));
        onFormChange('version', res.result.new_version);
        onFormChange('customer_id', responseData.result.customer.customer_id);
        onFormChange('customer_name', responseData.result.customer.display_name);
        onFormChange('document_id', responseData.result.document_id);
        if (is_draft) {
          afterSave();
        }
        toaster.success(tBe(responseData.message));
        if (!is_sent && !is_draft) {
          const response = await createPDF(currentEditId, { html_tag: getPDFhtml(pdfRef.current ? pdfRef.current.innerHTML : '', selectedQuotation, formData.version, formData.comment) });
          if (response.is_success) {
            const preDocuments: IEmailDocument[] = response.result.document_details;
            const documents = preDocuments.map((doc) => ({ name: doc.coverage_details_name, doc: doc.coverage_details }));
            documents.push({ name: response.result.pdf_data.coverage_details_name, doc: response.result.pdf_data.coverage_details });
            onFormChange('documents', documents);
          }
        }
      }
    } catch (error) {
      console.error('An error occurred:', error);
    }
  }

  const handleSendOpen = () => {
    if (formData.customer_id !== '') {
      onCancel();
      setTimeout(() => {
        setEmailData({ id: formData.customer_id, name: formData.customer_name, send_quotation_id: formData.document_id, documents: formData.documents });
      }, 100);
    }
  };

  return (
    <Modal isOpen={isOpen} size="xl" scrollable>
      <ModalHeader title={t('edit_consolidated_recommendation_document')} onClose={() => onCancel()} />
      <ModalBody>
        <div className="row" id={`${form.generate_doc.store}`}>
          <div className="col-12 col-md-6 mb-3 custom-select">
            <Label htmlFor="selected_quotations" label={t('selected_quotations')} isRequired />
            {skeleton || loading ? (
              <InputSkeleton />
            ) : (
              <AsyncSelect
                onChange={(_value: any, data: any) => setSelectedQuotation(data)}
                className="form-control error-form_submission_id"
                option={{ label: 'code', value: 'id' }}
                isSearchable={true}
                multiple
                defaultValue={selectedQuotation ?? []}
                loadOptions={(searchValue, currentPage) => fetchAllShortListDropdownData(searchValue, currentPage, quotationId)}
              />
            )}
          </div>
          <div className="col-12 col-md-6 mb-3 custom-select">
            <Label htmlFor="key_data_points_from_quotations" label={t('key_data_points_from_quotations')} isRequired />
            {skeleton ? (
              <InputSkeleton />
            ) : (
              <Select
                onChange={(_value: any, data: any) => setCriteria(data)}
                className="form-control error-columns"
                option={{ label: 'title', value: 'column' }}
                multiple
                isSearchable={true}
                options={allCriteria ?? []}
                defaultValue={defaultValue ?? []}
              />
            )}
          </div>
          <div className="col-12 col-md-6 mb-3">
            <Label label={t('expiry_date')} />
            {skeleton ? (
              <InputSkeleton />
            ) : (
              <Input
                type="date"
                value={formData.expiry_date || ''}
                min={new Date().toISOString().split('T')[0]}
                onChange={(e) => onFormChange('expiry_date', e.target.value)}
                className="form-control error-expiry_date"
                name="expiry_date"
              />
            )}
          </div>
        </div>
        <div className="col-12 col-md-12 mb-3">
          <div className="fs-15 fw-medium mb-3">{t('recommendation_comments')}</div>
          <Input type="textarea" value={formData.comment || ''} onChange={(e) => onFormChange('comment', e.target.value)} className="form-control error-comment" name="comment" />
        </div>
        <div>
          <div className="fs-15 fw-medium mb-3 ">{t('key_data_points_from_quotations')}</div>
          <div className="row mb-3 pdf-data-container">
            <div className="col-6 mb-2">
              <Label label={t('field')} />
            </div>
            <div className="col-6 mb-2">
              <Label label={t('value')} />
            </div>
            <div className="col-6 mb-2 fs-15">{t('version')}</div>
            <div className="col-6 mb-2">{!loading ? formData.version : <Skeleton width="100px" height="20px" />}</div>
            <div className="col-6 mb-2 fs-15">{t('date')}</div>
            <div className="col-6 mb-2">{date.toLocaleDateString('en-SL')}</div>
            <div className="col-6 mb-2 fs-15">{t('created_by')}</div>
            <div className="col-6 mb-2">{user ? user.display_name : ''}</div>
            <div className="col-6 mb-2 fs-15">{t('selected_quotations')}</div>
            <div className="col-6 mb-2">{selectedQuotation.length > 0 ? selectedQuotation.map((quote) => quote.code).join(' | ') : <Skeleton width="100px" height="20px" />}</div>
          </div>
          <div className="fs-15 fw-medium mb-3">{t('consolidated_recommendation_document')}</div>
          <div ref={pdfRef}>
            {selectedQuotation.length > 0 && <KeyPointsQuotationList selectedColumns={criteria} selectedQuotations={selectedQuotation.map((quote) => quote.id)} quotationId={quotationId} />}
          </div>
          <div className="col-12 col-md-12 mb-5 pdf-comments">
            <div className="fs-15 fw-medium mb-3">{t('recommendation_comments')}</div>
            <Input type="textarea" value={formData.comment || '-'} readOnly />
          </div>
        </div>
      </ModalBody>
      <ModalFooter>
        <div className="d-flex justify-content-between flex-wrap gap-2 ">
          <div className="d-flex gap-2">
            <Button color="primary" className="d-flex align-items-center gap-1" onClick={() => onSubmit({ is_draft: false, is_sent: false })} disabled={isFormProcessing}>
              <Flexicon icon="pencil-line" size={18} />
              <span className="d-none d-sm-inline">{t('generate_recommendation_document')}</span>
            </Button>
            <Button color="light" className="d-flex align-items-center text-primary gap-1" onClick={handlePreviewPDF} disabled={isFormProcessing}>
              <Flexicon icon="eye" size={18} />
              <span className="d-none d-sm-inline">{t('preview')}</span>
            </Button>
          </div>
          {isPdfGenerated && (
            <div className="d-flex gap-2">
              <Button color="light" className="d-flex align-items-center text-primary gap-1" onClick={() => onSubmit({ is_draft: true, is_sent: false })} disabled={isFormProcessing}>
                <Flexicon icon="save-01" variant="line" size={18} />
                <span className="d-none d-sm-inline">{t('save_as_a_draft')}</span>
              </Button>
              <Button color="light" className="d-flex align-items-center text-primary gap-1" onClick={() => handleSendOpen()} disabled={isFormProcessing}>
                <Flexicon icon="send-01" variant="line" size={18} />
                <span className="d-none d-sm-inline">{t('send_now')}</span>
              </Button>
              {/* <Button text={t('cancel')} color="light" width="sm" onClick={() => onCancel()} /> */}
            </div>
          )}
        </div>
      </ModalFooter>
    </Modal>
  );
}

export default EditGeneratedDocument;
