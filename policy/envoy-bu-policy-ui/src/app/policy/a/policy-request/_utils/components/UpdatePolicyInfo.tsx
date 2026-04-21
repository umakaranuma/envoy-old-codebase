'use client';
import { Label, Skeleton } from '@apptimus-ui/ui-element';
import { useEffect, useState } from 'react';
import { useTrans } from '@/helpers/services/lang/langService';
import { ConfirmedVendorResponse, DocumentValue, IRequestPolicy } from '../model';
import { getOnePolicyRequest } from '../api-service';
import GoTo from '@/components/others/page-related/GoTo';
import { useParams, useRouter } from 'next/navigation';
import { Description } from '@/components/others/Description';
import FileDownloadButton from '@/components/others/page-related/uploader/FileDownloadButton';
import { capitalizeFirstLetter, formatDate, thousandSeparator } from '@/helpers/services/commonService';
import ViewRiskTypes from '@/components/others/common/risk-type-view/ViewRiskTypes';
import { getCurrency } from '@/helpers/services/currencyService';
import ChatContent from './ChatContent';
import DocExtractionModal from './DocExtractionModel';
import { IFilePreviewer } from '@/components/others/page-related/chat/_utils/model';

export const UpdatePolicyInfo = () => {
  const t = useTrans('label.policy_request,otr.common,be.msg');
  // const tBe = useTrans('be.msg,be.error,be.attri');
  // const [isFormProcessing, setIsFormProcessing] = useState(false);
  // const [formData, setFormData] = useState(initUpdatePolicyRequestFormData);
  const [skeleton, setSkeleton] = useState(true);
  // const [policyResource, setPolicyResource] = useState<File | null>(null);
  // const [invoiceResource, setInvoiceResource] = useState<File | null>(null);
  const router = useRouter();
  const [data, setData] = useState({} as IRequestPolicy);
  const [quotationData, setQuotationData] = useState<ConfirmedVendorResponse[]>([]);
  // const [formKey, setFormKey] = useState(0);
  const params = useParams();
  const policyId = params.policyRequestId?.toString() || '';
  const [activeSelectedTab, setSelectedActiveTab] = useState(0);
  const currency = getCurrency();
  const [isDocExtractionOpen, setIsDocExtractionOpen] = useState(false);
  const [createKey, setCreateKey] = useState(0);
  const [docExtractionData, setDocExtractionData] = useState<any>(null);

  useEffect(() => {
    const fetchData = async () => {
      const responseData = await getOnePolicyRequest(policyId);
      if (responseData?.is_success) {
        setData(responseData.result);
        setQuotationData(responseData.result.confirmed_vendor_responses || []);
        setSkeleton(false);
      }
    };

    if (policyId) {
      setSkeleton(true);
      fetchData();
    }
  }, [policyId]);

  // const onFormChange = (name: string, value: any) => {
  //   setFormData((prevFormData) => ({ ...prevFormData, [name]: value }));
  // };

  // async function onSubmit() {
  //   clearError(form.policy_request.update);
  //   setIsFormProcessing(true);

  //   try {
  //     const docData = policyResource ? await handleFileUpload(policyResource) : null;
  //     const invoiceFileData = invoiceResource ? await handleFileUpload(invoiceResource) : null;
  //     let responseData;
  //     if (issuedPolicyId) {
  //       responseData = await renewalPolicyRequest(issuedPolicyId, {
  //         ...formData,
  //         policy_document: docData?.doc,
  //         policy_document_name: docData?.name,
  //         invoice_document: invoiceFileData?.doc,
  //         invoice_document_name: invoiceFileData?.name,
  //       });
  //     } else {
  //       responseData = await addPolicyRequest(policyId, {
  //         ...formData,
  //         policy_document: docData?.doc,
  //         policy_document_name: docData?.name,
  //         invoice_document: invoiceFileData?.doc,
  //         invoice_document_name: invoiceFileData?.name,
  //       });
  //     }

  //     setIsFormProcessing(false);

  //     if (responseData.status_code === 417) {
  //       printError(responseData.result, form.policy_request.update, tBe);
  //     }

  //     if (responseData.is_success) {
  //       toaster.success(tBe(responseData.message));
  //       setFormKey((prevKey) => prevKey + 1);
  //       setFormData(initUpdatePolicyRequestFormData);
  //     }
  //   } catch (error) {
  //     console.error('An error occurred:', error);
  //   }
  // }

  return (
    <div>
      <GoTo goTo={() => router.push('/policy/a/policy-request')} title={t('policy_info')} />
      <div>
        {/* <div className="panel">
          <div className="panel-title">{t('product_information')}</div>
          <div className="row">
            <div className="col-12 col-md-3 mb-3">
              <Description label={t('risk_type')} value={data?.request_type || '-'} skeleton={skeleton} />
            </div>
            <div className="col-12 col-md-3 mb-3">
              <Description label={t('product_name')} value={data?.product_name || '-'} skeleton={skeleton} />
            </div>
            <div className="col-12 col-md-3 mb-3">
              <Description label={t('coverage_type')} value={data?.coverage_type || '-'} skeleton={skeleton} />
            </div>
          </div>
        </div> */}
        <div className="panel">
          <div className="panel-title">{t('policyholder_info')}</div>
          <div className="row">
            <div className="col-12 col-md-3 mb-3">
              <Description label={t('policy_request_id')} value={data?.policy_request_id || '-'} skeleton={skeleton} />
            </div>
            <div className="col-12 col-md-3 mb-3">
              <Description label={t('full_name')} value={data?.customer_name || '-'} skeleton={skeleton} />
            </div>
            <div className="col-12 col-md-3 mb-3">
              <Description label={t('primary_contact_number')} value={data?.customer_primary_contact || '-'} skeleton={skeleton} />
            </div>
            {/* <div className="col-12 col-md-3 mb-3">
              <Description label={t('email')} value={data?.customer_email || '-'} skeleton={skeleton} />
            </div> */}
            <div className="col-12 col-md-3 mb-3">
              <Description label={t('insurer_name')} value={data?.insurer_company_name || '-'} skeleton={skeleton} />
            </div>
            {/* <div className="col-12 col-md-3 mb-3">
              <Description label={t('address')} value={data?.customer_address || '-'} skeleton={skeleton} />
            </div> */}
            <div className="col-12 col-md-3 mb-3">
              <Description label={t('product_name')} value={data?.products?.map((product) => product.name).join(', ') || '-'} skeleton={skeleton} />
            </div>
            <div className="col-12 col-md-3 mb-3">
              <Description label={t('sum_insured')} value={`${currency.code} ${thousandSeparator(data?.sum_insured)}`} skeleton={skeleton} />
            </div>
            <div className="col-12 col-md-3 mb-3">
              <Description label={t('start_date')} value={formatDate(data?.policy_start_date)} skeleton={skeleton} />
            </div>
            <div className="col-12 col-md-3 mb-3">
              <Description label={t('end_date')} value={formatDate(data?.policy_expiry_date)} skeleton={skeleton} />
            </div>
            {/* <div className="col-12 col-md-3 mb-3">
              <Description label={t('payment_mode')} value={formatDate(data?.payment_plan)} skeleton={skeleton} />
            </div> */}
          </div>
        </div>
        <div className="panel">
          <div className="panel-title">{t('quotation_info')}</div>
          <div className="row">
            <div className="col-12 col-md-3 mb-3">
              <Description label={t('quotation_id')} value={quotationData[0]?.quotation_code ? quotationData[0]?.quotation_code : data?.quotation_code || '-'} skeleton={skeleton} />
            </div>
            <div className="col-12 col-md-4 mb-3">
              <div className="text-muted">{t('confirmed_quotation')}</div>
              {/* <Label label={t('confirmed_quotation')} /> */}
              {skeleton ? (
                <Skeleton width={'65%'} height={'24px'} />
              ) : (
                <FileDownloadButton
                  s3Key={quotationData[0]?.quotation_document ? quotationData[0]?.quotation_document : data?.quotation_document || ''}
                  fileName={quotationData[0]?.quotation_document_name || data?.quotation_document_name || ''}
                />
              )}
            </div>
            <div className="col-12 col-md-3 mb-3">
              <Description label={t('premium_amount')} value={data?.premium_amount || '-'} skeleton={skeleton} />
            </div>
            <div className="col-12 col-md-3 mb-3">
              <Description
                label={t('quotation_issued_date')}
                value={quotationData[0]?.quotation_issued_date ? quotationData[0]?.quotation_issued_date : data?.quotation_issued_date || '-'}
                skeleton={skeleton}
              />
            </div>
            <div className="col-12 col-md-3 mb-3">
              <Description
                label={t('quotation_expiry_date')}
                value={quotationData[0]?.quotation_expiry_date ? quotationData[0]?.quotation_expiry_date : data?.quotation_expiry_date || '-'}
                skeleton={skeleton}
              />
            </div>
          </div>
        </div>
        <div className="panel">
          <div className="panel-title">{t('conversation_log')}</div>
          <div>
            {!skeleton ? (
              <ChatContent
                id={data.id?.toString()}
                handleDocExtraction={(data: IFilePreviewer) => {
                  setDocExtractionData(data);
                  setIsDocExtractionOpen(true);
                }}
              />
            ) : (
              <Skeleton width={'100%'} height={'200px'} />
            )}
          </div>
        </div>
        {/* <div className="panel">
          <div className="panel-title">{t('insurer_info')}</div>
          <div className="row">
            <div className="col-12 col-md-3 mb-3">
              <Description label={t('insurer_name')} value={data?.insurer_company_name || '-'} skeleton={skeleton} />
            </div>
            <div className="col-12 col-md-3 mb-3">
              <Description label={t('primary_contact_number')} value={data?.customer_primary_contact || '-'} skeleton={skeleton} />
            </div>
            <div className="col-12 col-md-3 mb-3">
              <Description label={t('email')} value={data?.insurer_email || '-'} skeleton={skeleton} />
            </div>
            <div className="col-12 col-md-3 mb-3">
              <Description label={t('remarks')} value={data?.insurer_notes || '-'} skeleton={skeleton} />
            </div>
          </div>
        </div> */}
        {/* <div className="panel">
          <div className="panel-title">{t('policy_request_info')}</div>
          <div className="row">
            <div className="col-12 col-md-3 mb-3">
              <Description label={t('policy_request_id')} value={data?.policy_request_id || '-'} skeleton={skeleton} />
            </div>
            <div className="col-12 col-md-3 mb-3">
              <Description label={t('requested_by')} value={data?.created_by || '-'} skeleton={skeleton} />
            </div>
            <div className="col-12 col-md-3 mb-3">
              <Description label={t('date')} value={data?.policy_start_date || '-'} skeleton={skeleton} />
            </div>
          </div>
        </div> */}
        {data.risk_types?.length > 0 && (
          <div className="panel">
            <div className="panel-title">{t('risk_details')}</div>
            <div className="il-box-tab">
              {data.risk_types?.map((riskType, index) => (
                <div key={riskType.risk_type_id} className={`il-box-tab-item ${activeSelectedTab === index ? 'active' : ''}`} onClick={() => setSelectedActiveTab(index)}>
                  {capitalizeFirstLetter(riskType.risk_type_name)}
                </div>
              ))}
            </div>
            {data.risk_types?.map((riskType, index) =>
              activeSelectedTab === index ? (
                <ViewRiskTypes key={riskType.risk_type_id} selectedTypeId={riskType.risk_type_id.toString()} policyBaseId={data.policy_base_id.toString()} customerId={data.customer_id?.toString()} />
              ) : null,
            )}
          </div>
        )}
        <div className="panel">
          <div className="panel-title">{t('document_attachments')}</div>
          {skeleton ? (
            <Skeleton width={'100%'} height={'200px'} />
          ) : (
            <>
              <div className="panel-subtitle">{t('policy_related')}</div>
              {data?.policy_document_value?.length > 0 ? (
                <div className="col-12 col-md-3 mb-3">
                  {data.policy_document_value.map((doc: DocumentValue) => (
                    <div key={doc.id}>
                      <Label label={doc.document_name || 'N/A'} />
                      <FileDownloadButton s3Key={doc.value ? JSON.parse(doc.value?.replace(/'/g, '"')).doc : ''} />
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center fs-13">{t('no_documents_available')}</div>
              )}

              <div className="panel-subtitle">{t('risk_related')}</div>
              {data?.risk_document_value?.length > 0 ? (
                <div className="col-12 col-md-3 mb-3">
                  {data.risk_document_value.map((doc: DocumentValue) => (
                    <div key={doc.id}>
                      <Label label={doc.document_name || 'N/A'} />
                      <FileDownloadButton s3Key={doc.value ? JSON.parse(doc.value?.replace(/'/g, '"')).doc : ''} />
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center fs-13">{t('no_documents_available')}</div>
              )}
            </>
          )}
        </div>
        <div className="panel">
          {/* <div className="panel-title">{t('policyholder_info')}</div> */}
          <div className="row">
            <div className="col-12 col-md-3 mb-3">
              <Description label={t('account_manager')} value={data?.account_manager_name || '-'} skeleton={skeleton} />
            </div>
            <div className="col-12 col-md-3 mb-3">
              <Description label={t('sales_agent')} value={data?.sales_agent_name || '-'} skeleton={skeleton} />
            </div>
            <div className="col-12 col-md-3 mb-3">
              <Description label={t('requested_by')} value={data?.requested_by || '-'} skeleton={skeleton} />
            </div>
            <div className="col-12 col-md-3 mb-3">
              <Description label={t('date')} value={data?.policy_request_date || '-'} skeleton={skeleton} />
            </div>
          </div>
        </div>
      </div>
      {/* <div className="panel">
        <div className="panel-title">{t('policy_information')}</div>
        {from === 'ip' ? (
          <div className="row">
            <div className="col-12 col-md-3 mb-3">
              <Description label={t('insurer_policy_id')} value={data?.insurer_policy_id || '-'} skeleton={skeleton} />
            </div>
            <div className="col-12 col-md-3 mb-3">
              <Description label={t('insurer_invoice_iD')} value={data?.insurer_invoice_id || '-'} skeleton={skeleton} />
            </div>
            <div className="col-12 col-md-3 mb-3">
              <Description label={t('policy_issue_date')} value={formatDate(data?.policy_effective_date)} skeleton={skeleton} />
            </div>
            <div className="col-12 col-md-3 mb-3">
              <Description label={t('start_date')} value={formatDate(data?.policy_start_date)} skeleton={skeleton} />
            </div>
            <div className="col-12 col-md-3 mb-3">
              <Description label={t('end_date')} value={formatDate(data?.policy_expiry_date)} skeleton={skeleton} />
            </div>
            <div className="col-12 col-md-3 mb-3">
              <Description label={t('premium_amount')} value={data?.premium_amount || '-'} skeleton={skeleton} />
            </div>
            <div className="col-12 col-md-3 mb-3">
              <Description label={t('credit_period')} value={data?.credit_period_days || '-'} skeleton={skeleton} />
            </div>
            <div className="col-12 col-md-3 mb-3">
              <Description label={t('credit_age')} value={data?.credit_age_days || '-'} skeleton={skeleton} />
            </div>
          </div>
        ) : (
          <form id={`${form.policy_request.update}`} key={formKey}>
            <div className="row">
              <div className="col-12 col-md-3 mb-3">
                <Input
                  isRequired
                  label={t('insurer_policy_id')}
                  value={formData.insurer_policy_id}
                  onChange={(e) => onFormChange('insurer_policy_id', e.target.value)}
                  className="form-control error-insurer_policy_id"
                  name="insurer_policy_id"
                />
              </div>
              <div className="col-12 col-md-3 mb-3">
                <Input
                  isRequired
                  label={t('insurer_invoice_iD')}
                  value={formData.insurer_invoice_id}
                  onChange={(e) => onFormChange('insurer_invoice_id', e.target.value)}
                  className="form-control error-insurer_invoice_id"
                  name="insurer_invoice_id"
                />
              </div>
              <div className="col-12 col-md-3 mb-3">
                <Label htmlFor="invoice_documents" label={t('invoice_documents')} />
                {!invoiceResource ? (
                  <InputFileUploader data={(file: File) => setInvoiceResource(file)} className="form-control error-invoice_document" name="invoice_document" />
                ) : (
                  <FilePreviewInput
                    fileName={invoiceResource?.name}
                    onCancel={() => {
                      setInvoiceResource(null);
                    }}
                  />
                )}
              </div>
              <div className="col-12 col-md-3 mb-3">
                <Label htmlFor="policy_documents" label={t('policy_documents')} />
                {!policyResource ? (
                  <InputFileUploader data={(file: File) => setPolicyResource(file)} className="form-control error-policy_document" name="policy_document" />
                ) : (
                  <FilePreviewInput
                    fileName={policyResource?.name}
                    onCancel={() => {
                      setPolicyResource(null);
                    }}
                  />
                )}
              </div>
            </div>
            <div className="row">
              <div className="col-12 col-md-3 mb-3">
                <Input
                  isRequired
                  label={t('policy_issue_date')}
                  value={formData.policy_effective_date}
                  onChange={(e) => onFormChange('policy_effective_date', e.target.value)}
                  className="form-control error-policy_effective_date"
                  name="policy_effective_date"
                  type="date"
                />
              </div>
              <div className="col-12 col-md-3 mb-3">
                <Input
                  isRequired
                  label={t('start_date')}
                  value={formData.start_date}
                  onChange={(e) => onFormChange('start_date', e.target.value)}
                  className="form-control error-start_date"
                  name="start_date"
                  type="date"
                />
              </div>
              <div className="col-12 col-md-3 mb-3">
                <Input
                  isRequired
                  label={t('end_date')}
                  value={formData.end_date}
                  onChange={(e) => onFormChange('end_date', e.target.value)}
                  className="form-control error-end_date"
                  name="end_date"
                  type="date"
                />
              </div>
              <div className="col-12 col-md-3 mb-3">
                <Input
                  isRequired
                  label={t('sum_insured')}
                  value={formData.sum_insured}
                  onChange={(e) => onFormChange('sum_insured', e.target.value)}
                  className="form-control error-sum_insured"
                  name="sum_insured"
                />
              </div>
            </div>
            <div className="row">
              <div className="col-12 col-md-3 mb-3">
                <Input
                  isRequired
                  label={t('premium_amount')}
                  value={formData.premium_amount}
                  onChange={(e) => onFormChange('premium_amount', e.target.value)}
                  className="form-control error-premium_amount"
                  name="premium_amount"
                />
              </div>
              <div className="col-12 col-md-3 mb-3">
                <Input
                  isRequired
                  label={t('credit_period')}
                  value={formData.credit_period_days}
                  onChange={(e) => onFormChange('credit_period_days', e.target.value)}
                  className="form-control error-credit_period_days"
                  name="credit_period"
                />
              </div>
              <div className="col-12 col-md-3 mb-3">
                <Input
                  isRequired
                  label={t('credit_age')}
                  value={formData.credit_age_days}
                  onChange={(e) => onFormChange('credit_age_days', e.target.value)}
                  className="form-control error-credit_age_days"
                  name="credit_age"
                />
              </div>
            </div>
            <div className="d-flex justify-content-end gap-2">
              <Button text={t('submit')} onClick={onSubmit} width="sm" isLoading={isFormProcessing} />
              <Button text={t('cancel')} color="light" width="sm" />
            </div>
          </form>
        )}
      </div> */}
      <DocExtractionModal
        isOpen={isDocExtractionOpen}
        onCancel={() => {
          setIsDocExtractionOpen(false);
          setCreateKey((prev) => prev + 1);
        }}
        afterSave={() => {
          setIsDocExtractionOpen(false);
          setCreateKey((prev) => prev + 1);
        }}
        policyRequestId={data.id?.toString() || ''}
        docExtractionData={docExtractionData || null}
        key={createKey}
      />
    </div>
  );
};
