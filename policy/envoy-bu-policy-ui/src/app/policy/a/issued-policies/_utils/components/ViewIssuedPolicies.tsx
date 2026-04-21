'use client';
import { Description } from '@/components/others/Description';
import GoTo from '@/components/others/page-related/GoTo';
import { useTrans } from '@/helpers/services/lang/langService';
import { useParams, useRouter, useSearchParams } from 'next/navigation';
import React, { useEffect, useState } from 'react';
import { Button, Input, Label, Skeleton } from '@apptimus-ui/ui-element';
import { Flexicon } from '@apptimus-ui/flexicon';
import EndorsementRequests from './endorsement-requests/EndorsementRequests';
import Invoices from './tab/invoices/Invoices';
import PolicyInheritanceHistory from './tab/PolicyInheritanceHistory';
import Notes from './tab/notes/Notes';
import { getOneIssuedPolicy, updateIssuedPolicy } from '../api-service';
import { form } from '@/constans/Form';
import { clearError, printError } from '@/helpers/handlers/validationErrorHandler';
import { toaster } from '@/helpers/services/toaster';
import { IIssuedPolicy } from '../model';
import { capitalizeFirstLetter, formatDate, handleFileUpload, thousandSeparator } from '@/helpers/services/commonService';
import EndorsementsDetailsList from './endorsements-details/EndorsementsDetailsList';
import Documents from './tab/documents/Documents';
import FileDownloadButton from '@/components/others/page-related/uploader/FileDownloadButton';
import FilePreviewInput from '@/components/others/page-related/uploader/FilePreviewInput';
import InputFileUploader from '@/components/others/page-related/uploader/InputFileUploader';
import Payments from './tab/payments/Payments';
import { getCurrency } from '@/helpers/services/currencyService';
import ProfileInfo from '@/components/others/page-related/ProfileInfo';
import ViewRiskTypes from '@/components/others/common/risk-type-view/ViewRiskTypes';
import { useBreadcrumb } from '@/contexts/BreadcrumbContext';

function ViewIssuedPolicies() {
  const t = useTrans('label.issued_policies,otr.common');
  const tBe = useTrans('be.msg,be.error,be.attri');
  const router = useRouter();
  const searchParams = useSearchParams();
  const { setCustomBreadcrumb } = useBreadcrumb();
  const currency = getCurrency();
  const [skeleton, setSkeleton] = useState(false);
  const [data, setData] = useState({} as IIssuedPolicy);
  const [tab, setTab] = useState('invoices');
  const params = useParams();
  const policyId = params.policyId?.toString() || '';
  const [formKey, setFormKey] = useState(0);
  const [policyResource, setPolicyResource] = useState<File | null>(null);
  const [invoiceResource, setInvoiceResource] = useState<File | null>(null);
  const [isFormProcessing, setIsFormProcessing] = useState(false);
  const [editable, setEditable] = useState(false);
  const [endorsementDetailTableVersion, setEndorsementDetailTableVersion] = useState(0);
  const [invoiceKey, setInvoiceKey] = useState(0);
  const [activeSelectedTab, setSelectedActiveTab] = useState(0);

  useEffect(() => {
    setCustomBreadcrumb({
      text: 'Issued Policies',
      backurl: '/policy/a/issued-policies',
    });
    return () => setCustomBreadcrumb(null);
  }, []);

  useEffect(() => {
    const tab = searchParams.get('t') || 'invoices';
    toggleTableTab(tab);
  }, []);

  const toggleTableTab = (activeTab: string) => {
    setTab(activeTab);
    router.push(`/policy/a/issued-policies/${policyId}?t=${activeTab}`, { scroll: false });
  };

  const fetchData = async () => {
    const responseData = await getOneIssuedPolicy(policyId);
    if (responseData?.is_success) {
      setData(responseData.result);

      setSkeleton(false);
    }
  };

  useEffect(() => {
    if (policyId) {
      setSkeleton(true);
      fetchData();
    }
  }, [policyId]);

  const onFormChange = (name: string, value: any) => {
    setData((prevFormData) => ({ ...prevFormData, [name]: value }));
  };

  async function onSubmit() {
    clearError(form.policy_request.update);
    setIsFormProcessing(true);

    try {
      const docData = policyResource ? await handleFileUpload(policyResource) : null;
      const invoiceFileData = invoiceResource ? await handleFileUpload(invoiceResource) : null;
      const responseData = await updateIssuedPolicy(policyId, {
        ...data,
        policy_document: docData?.key,
        policy_document_name: docData?.name,
        invoice_document: invoiceFileData?.key,
        invoice_document_name: invoiceFileData?.name,
        policy_document_size: undefined,
      });
      setIsFormProcessing(false);

      if (responseData.status_code === 417) {
        printError(responseData.result, form.policy_request.update, tBe);
      }

      if (responseData.is_success) {
        toaster.success(tBe(responseData.message));
        setFormKey((prevKey) => prevKey + 1);
        setEditable(false);
        fetchData();
      }
    } catch (error) {
      console.error('An error occurred:', error);
    }
  }

  return (
    <>
      <GoTo goTo={() => router.push('/policy/a/issued-policies')} title={t('policy_details')} />
      <div>
        {/* <div className="panel">
          <div className="panel-title">{t('product_information')}</div>
          <div className="row">
            <div className="col-12 col-md-3 mb-3">
              <Description label={t('risk_type')} value={data?.request_type || '-'} skeleton={skeleton} />
            </div>
            <div className="col-12 col-md-3 mb-3">
              <Description label={t('product_name')} value={data?.product || '-'} skeleton={skeleton} />
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
              <Description label={t('request_number')} value={data?.policy_request_code || '-'} skeleton={skeleton} />
            </div>
            <div className="col-12 col-md-3 mb-3">
              <Description label={t('full_name')} value={data?.customer_name || '-'} skeleton={skeleton} />
            </div>
            <div className="col-12 col-md-3 mb-3">
              <Description label={t('primary_contact_number')} value={data?.customer_primary_contact || '-'} skeleton={skeleton} />
            </div>
            <div className="col-12 col-md-3 mb-3">
              <Description label={t('email')} value={data?.customer_email || '-'} skeleton={skeleton} />
            </div>
            <div className="col-12 col-md-3 mb-3">
              <Description label={t('address')} isTruncate={false} value={data?.customer_address || '-'} skeleton={skeleton} />
            </div>
            <div className="col-12 col-md-3 mb-3">
              <div className="text-muted">{t('insurer_name')}</div>
              <ProfileInfo title={data?.insurer_info_full_name || '-'} imageKey={data.insurer_info_logo} loading={skeleton} shape="square" />
            </div>
            <div className="col-12 col-md-3 mb-3">
              <Description label={t('product_name')} value={data?.product || '-'} skeleton={skeleton} />
            </div>
          </div>
        </div>
        {data.risk_types?.length > 0 && (
          <div className="panel">
            <div className="panel-title">{t('risk_details')}</div>
            <div className="il-box-tab">
              {data.risk_types.map((riskType, index) => (
                <div key={riskType.risk_type_id} className={`il-box-tab-item ${activeSelectedTab === index ? 'active' : ''}`} onClick={() => setSelectedActiveTab(index)}>
                  {capitalizeFirstLetter(riskType.risk_type_name)}
                </div>
              ))}
            </div>
            {data.risk_types.map((riskType, index) =>
              activeSelectedTab === index ? (
                <ViewRiskTypes key={riskType.risk_type_id} selectedTypeId={riskType.risk_type_id.toString()} policyBaseId={data.policy_base_id.toString()} customerId={data.customer_id.toString()} />
              ) : null,
            )}
          </div>
        )}
        <div className="panel">
          {/* <div className="panel-title">{t('policyholder_info')}</div> */}
          <div className="row">
            <div className="col-12 col-md-3 mb-3">
              <Description label={t('account_manager')} value={data?.account_manager || '-'} skeleton={skeleton} />
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
        {/* <div className="panel">
          <div className="panel-title">{t('insurer_info')}</div>
          <div className="row">
            <div className="col-12 col-md-3 mb-3">
              <Label label={t('insurer_name')} />
              <ProfileInfo title={data?.insurer_info_full_name || '-'} imageKey={data.insurer_info_logo} loading={skeleton} shape="square" />
            </div>
            <div className="col-12 col-md-3 mb-3">
              <Description label={t('primary_contact_number')} value={data?.customer_primary_contact || '-'} skeleton={skeleton} />
            </div>
            <div className="col-12 col-md-3 mb-3">
              <Description label={t('email')} value={data?.customer_email || '-'} skeleton={skeleton} />
            </div>
            <div className="col-12 col-md-3 mb-3">
              <Description label={t('remarks')} value={data?.insurer_notes || '-'} skeleton={skeleton} />
            </div>
          </div>
        </div> */}
        {/* <div className="panel">
          <div className="panel-title">{t('insurer_info')}</div>
          <div className="row">
            <div className="col-12 col-md-3 mb-3">
              <Description label={t('account_manager')} value={data?.insurer_company_name || '-'} skeleton={skeleton} />
            </div>
            <div className="col-12 col-md-3 mb-3">
              <Description label={t('sales_agent')} value={data?.customer_primary_contact || '-'} skeleton={skeleton} />
            </div>
            <div className="col-12 col-md-3 mb-3">
              <Description label={t('created_by')} value={data?.created_by || '-'} skeleton={skeleton} />
            </div>
            <div className="col-12 col-md-3 mb-3">
              <Description label={t('date')} value={formatDate(data?.created_at) || '-'} skeleton={skeleton} />
            </div>
            <div className="col-12 col-md-3 mb-3">
              <Description label={t('updated_by')} value={data?.updated_by || '-'} skeleton={skeleton} />
            </div>
            <div className="col-12 col-md-3 mb-3">
              <Description label={t('date')} value={formatDate(data?.updated_at) || '-'} skeleton={skeleton} />
            </div>
          </div>
        </div> */}
        <div className="panel">
          <div className="panel-title">{t('policy_info')}</div>
          <form id={`${form.policy_request.update}`} key={formKey}>
            <div className="row">
              <div className="col-12 col-md-3 mb-3">
                {!editable ? (
                  <Description
                    label={t('policy_request_id')}
                    value={
                      <div
                        onClick={() => {
                          data?.policy_request_id ? router.push(`/policy/a/policy-request/${data?.policy_request_id}`) : null;
                        }}
                        className={`${data?.policy_request_code ? 'clickable-text text-primary' : ''}`}
                      >
                        {data?.policy_request_code || 'N/A'}
                      </div>
                    }
                    skeleton={skeleton}
                  />
                ) : (
                  <Input label={t('policy_request_id')} value={data.policy_request_code || 'N/A'} disabled />
                )}
              </div>
              <div className="col-12 col-md-3 mb-3">
                {!editable ? (
                  <Description label={t('insurer_policy_id')} value={data?.insurer_policy_id || '-'} skeleton={skeleton} />
                ) : (
                  <Input
                    label={t('insurer_policy_id')}
                    isRequired
                    value={data.insurer_policy_id || ''}
                    onChange={(e) => onFormChange('insurer_policy_id', e.target.value)}
                    className="form-control error-insurer_policy_id"
                    name="insurer_policy_id"
                  />
                )}
              </div>
              <div className="col-12 col-md-3 mb-3">
                {!editable ? (
                  <Description label={t('insurer_invoice_id')} value={data?.insurer_invoice_id || '-'} skeleton={skeleton} />
                ) : (
                  <Input
                    label={t('insurer_invoice_id')}
                    isRequired
                    value={data.insurer_invoice_id || ''}
                    onChange={(e) => onFormChange('insurer_invoice_id', e.target.value)}
                    className="form-control error-insurer_invoice_id"
                    name="insurer_invoice_id"
                    readOnly={!editable}
                  />
                )}
              </div>
              <div className="col-12 col-md-3 mb-3">
                {!editable ? (
                  <div className="custom-description">
                    <div className="text-muted">{t('debit_note')}</div>
                    {skeleton ? <Skeleton width={'65%'} height={'24px'} /> : <FileDownloadButton s3Key={data.invoice_document ? data.invoice_document : ''} fileType="pdf" />}
                  </div>
                ) : (
                  <>
                    <Label htmlFor="invoice_documents" label={t('debit_note')} />
                    {!(invoiceResource || data.invoice_document_name) ? (
                      <InputFileUploader data={(file: File) => setInvoiceResource(file)} className="form-control error-invoice_document" name="invoice_document" />
                    ) : (
                      <FilePreviewInput
                        fileName={invoiceResource?.name || data.invoice_document_name}
                        onCancel={() => {
                          setInvoiceResource(null), onFormChange('invoice_document_name', '');
                        }}
                      />
                    )}
                  </>
                )}
              </div>
              <div className="col-12 col-md-3 mb-3">
                {!editable ? (
                  <div className="custom-description">
                    <div className="text-muted">{t('policy_document')}</div>
                    {skeleton ? <Skeleton width={'65%'} height={'24px'} /> : <FileDownloadButton s3Key={data.policy_document ? data.policy_document : ''} fileType="pdf" />}
                  </div>
                ) : (
                  <>
                    <Label htmlFor="policy_document" label={t('policy_document')} />
                    {!(policyResource || data.policy_document_name) ? (
                      <InputFileUploader data={(file: File) => setPolicyResource(file)} className="form-control error-policy_document" name="policy_document" />
                    ) : (
                      <FilePreviewInput
                        fileName={policyResource?.name || data.policy_document_name}
                        onCancel={() => {
                          setPolicyResource(null), onFormChange('policy_document_name', '');
                        }}
                      />
                    )}
                  </>
                )}
              </div>
              <div className="col-12 col-md-3 mb-3">
                {!editable ? (
                  <Description label={t('policy_issue_date')} value={formatDate(data?.policy_effective_date) || '-'} skeleton={skeleton} />
                ) : (
                  <Input
                    value={formatDate(data.policy_effective_date) || ''}
                    label={t('policy_issue_date')}
                    isRequired
                    onChange={(e) => onFormChange('policy_effective_date', e.target.value)}
                    className="form-control error-policy_effective_date"
                    name="policy_effective_date"
                    type="date"
                    readOnly={!editable}
                  />
                )}
              </div>
              <div className="col-12 col-md-3 mb-3">
                {!editable ? (
                  <Description label={t('start_date')} value={formatDate(data.start_date) || '-'} skeleton={skeleton} />
                ) : (
                  <Input
                    label={t('start_date')}
                    isRequired
                    value={formatDate(data.start_date) || ''}
                    onChange={(e) => onFormChange('start_date', e.target.value)}
                    className="form-control error-start_date"
                    name="start_date"
                    type="date"
                    readOnly={!editable}
                  />
                )}
              </div>
              <div className="col-12 col-md-3 mb-3">
                {!editable ? (
                  <Description label={t('end_date')} value={formatDate(data.end_date) || '-'} skeleton={skeleton} />
                ) : (
                  <Input
                    label={t('end_date')}
                    isRequired
                    value={formatDate(data.end_date) || ''}
                    onChange={(e) => onFormChange('end_date', e.target.value)}
                    className="form-control error-end_date"
                    name="end_date"
                    type="date"
                    readOnly={!editable}
                    min={data.start_date || undefined}
                  />
                )}
              </div>
              <div className="col-12 col-md-3 mb-3">
                {!editable ? (
                  <Description label={t('sum_insured')} value={`${currency.code} ${thousandSeparator(data?.sum_insured) || '-'}`} skeleton={skeleton} />
                ) : (
                  <Input
                    label={t('sum_insured')}
                    isRequired
                    value={data.sum_insured || ''}
                    onChange={(e) => onFormChange('sum_insured', e.target.value)}
                    className="form-control error-sum_insured"
                    name="sum_insured"
                    readOnly={!editable}
                  />
                )}
              </div>
              <div className="col-12 col-md-3 mb-3">
                {!editable ? (
                  <Description label={t('premium_amount')} value={`${currency.code} ${thousandSeparator(data?.premium_amount) || '-'}`} skeleton={skeleton} />
                ) : (
                  <Input
                    label={t('premium_amount')}
                    isRequired
                    value={data.premium_amount || ''}
                    onChange={(e) => onFormChange('premium_amount', e.target.value)}
                    className="form-control error-premium_amount"
                    name="premium_amount"
                    readOnly={!editable}
                  />
                )}
              </div>
              <div className="col-12 col-md-3 mb-3">
                {!editable ? (
                  <Description label={t('credit_period')} value={data.credit_period_days || '-'} skeleton={skeleton} />
                ) : (
                  <Input
                    label={t('credit_period')}
                    isRequired
                    value={data.credit_period_days || ''}
                    onChange={(e) => onFormChange('credit_period_days', e.target.value)}
                    className="form-control error-credit_period_days"
                    name="credit_period"
                    readOnly={!editable}
                  />
                )}
              </div>
              <div className="col-12 col-md-3 mb-3">
                {!editable ? (
                  <Description label={t('credit_age')} value={data.credit_age_days || '0'} skeleton={skeleton} />
                ) : (
                  <Input
                    label={t('credit_age')}
                    isRequired
                    value={data.credit_age_days || ''}
                    onChange={(e) => onFormChange('credit_age_days', e.target.value)}
                    className="form-control error-credit_age_days"
                    name="credit_age"
                    disabled
                  />
                )}
              </div>
            </div>
            <div className="d-flex justify-content-end gap-2">
              <Button onClick={editable ? onSubmit : () => setEditable(true)} className="d-flex align-items-center justify-content-center gap-1" width="sm" isLoading={isFormProcessing}>
                {!editable && <Flexicon icon={'edit-05'} variant="line" size={15} />}
                <span className="d-none d-sm-inline">{editable ? t('update') : t('edit')}</span>
              </Button>
              <Button text={t('cancel')} color="light" width="sm" onClick={() => router.push(`/policy/a/issued-policies/`)} />
            </div>
          </form>
        </div>
      </div>
      <EndorsementRequests setEndorsementDetailTableVersion={setEndorsementDetailTableVersion} setInvoiceKey={setInvoiceKey} statusType={data.status_type} afterSave={() => fetchData()} />
      <div className="panel">
        <div className="panel-title mb-3">{t('endorsements_details')}</div>
        {policyId && <EndorsementsDetailsList policyId={policyId} key={`listKey-${endorsementDetailTableVersion}`} />}
      </div>

      <div className="panel">
        <div className="il-box-tab mb-3">
          <div className={`il-box-tab-item ${tab === 'invoices' ? 'active' : ''}`} onClick={() => toggleTableTab('invoices')}>
            {t('debit_notes')}
          </div>
          <div className={`il-box-tab-item ${tab === 'payments' ? 'active' : ''}`} onClick={() => toggleTableTab('payments')}>
            {t('payments')}
          </div>
          <div className={`il-box-tab-item ${tab === 'policy_inheritance_history' ? 'active' : ''}`} onClick={() => toggleTableTab('policy_inheritance_history')}>
            {t('policy_inheritance_history')}
          </div>
          <div className={`il-box-tab-item ${tab === 'notes' ? 'active' : ''}`} onClick={() => toggleTableTab('notes')}>
            {t('notes')}
          </div>
          <div className={`il-box-tab-item ${tab === 'documents' ? 'active' : ''}`} onClick={() => toggleTableTab('documents')}>
            {t('documents')}
          </div>
        </div>
        <div>
          {tab === 'invoices' && <Invoices key={invoiceKey} />}
          {tab === 'payments' && <Payments />}
          {tab === 'policy_inheritance_history' && <PolicyInheritanceHistory />}
          {tab === 'notes' && data.entity_id && <Notes entityId={data.entity_id.toString()} />}
          {tab === 'documents' && data.policy_base_id && <Documents policyBaseId={data.policy_base_id.toString()} />}
        </div>
      </div>
    </>
  );
}

export default ViewIssuedPolicies;
