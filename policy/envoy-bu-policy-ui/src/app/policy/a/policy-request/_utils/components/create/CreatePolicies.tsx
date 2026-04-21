'use client';
import { form } from '@/constans/Form';
import { Button, Input, Label } from '@apptimus-ui/ui-element';
import React, { useEffect, useRef, useState } from 'react';
import { useTrans } from '@/helpers/services/lang/langService';
import { initPolicyData } from '../../model';
import { AsyncSelect } from '@apptimus-ui/select';
import 'react-phone-input-2/lib/style.css';
import OpportunityTypes from './risk-type/OpportunityTypes';
import { useRouter } from 'next/navigation';
import GoTo from '@/components/others/page-related/GoTo';

import {
  fetchAllAccountManagers,
  fetchAllInsurers,
  fetchAllPaymentTypes,
  fetchAllProductsByType,
  fetchAllProductTypes,
  fetchAllSalesAgent,
  fetchAllUsers,
  getDefaultPolicyRequestEmailTemplateForInsurer,
} from '../../services';
import { clearError, printError } from '@/helpers/handlers/validationErrorHandler';
import { toaster } from '@/helpers/services/toaster';
import { createIssuedPolicy, createPolicyRequest, getAccountManager, getAllInsurers, getAllOpportunities, getIssuedPolicyData, getPolicyRiskInfoFile, policyRequestEmail } from '../../api-service';
import { getLocalStorage } from '@/helpers/handlers/localStorageHandler';
import { local_storage } from '@/constans/StorageKeys';
import InputFileUploader from '@/components/others/page-related/uploader/InputFileUploader';
import ProductDocuments from './ProductDocuments';
import FilePreviewInput from '@/components/others/page-related/uploader/FilePreviewInput';
import { capitalizeFirstLetter, formatDate, handleFileUpload } from '@/helpers/services/commonService';
import EmailForm from '@/components/others/page-related/email-form/EmailForm';
import { Description } from '@/components/others/Description';
import { Flexicon } from '@apptimus-ui/flexicon';
import BulkUpload from './risk-type/BulkUpload';
import { getOneDraftPolicy } from '@/app/policy/a/draft-policies/_utils/api-service';
import DraftConfirmPopup from './DraftConfirmPopup';
import { InputSkeleton } from '@/components/others/InputSkeleton';

function CreatePolicies({
  fromIssuedPolicies,
  is_renewal,
  policy_base_id,
  cusId,
  leadId,
  customerType,
  draftId,
  fromReRequest,
}: {
  fromIssuedPolicies: boolean;
  is_renewal: boolean;
  policy_base_id?: string;
  cusId?: string;
  leadId?: string;
  customerType: number | null;
  draftId?: string | null;
  fromReRequest?: boolean;
}) {
  const tBe = useTrans('be.msg,be.error,be.attri');
  const t = useTrans('label.policy_request,label.risks,otr.common,be.msg');
  const [isFormProcessing, setIsFormProcessing] = useState(false);
  const [formData, setFormData] = useState(initPolicyData);
  const [resource, setResource] = useState<File | null>(null);
  const router = useRouter();
  const user = getLocalStorage(local_storage.auth_user_info);
  const [key, setKey] = useState(0);
  const [invoiceResource, setInvoiceResource] = useState<File | null>(null);
  const [policyResource, setPolicyResource] = useState<File | null>(null);
  const [activeSelectedTab, setSelectedActiveTab] = useState(0);
  const productDocRef = useRef<{ onSubmit: () => Promise<any> | null }>(null);
  const [emailData, setEmailData] = useState({ entity_id: '', policy_request_id: '', insurer: '', documents: [] as any[] });
  const [error, setError] = useState('');
  const [riskIdsByType, setRiskIdsByType] = useState<{ [riskTypeId: string]: any[] }>({});
  const [skeleton, setSkeleton] = useState(false);
  const [isBulkUploadOpen, setIsBulkUploadOpen] = useState(false);
  const [riskTableKey, setRiskTableKey] = useState(0);
  const [validationError, setValidationError] = useState('');
  const [populateLoading, setPopulateLoading] = useState({ insurerLoading: false, accountManagerLoading: false, initialLoading: false });

  useEffect(() => {
    if (user) {
      fetchAccountManager(user.id);
      onFormChange('request_by_id', user.id), onFormChange('request_by_name', user.display_name);
      onFormChange('sales_agent_id', user.id), onFormChange('sales_agent_name', user.display_name);
    }
  }, []);

  useEffect(() => {
    if (formData.sales_agent_id) {
      fetchAccountManager(formData.sales_agent_id);
    }
  }, [formData.sales_agent_id, formData.product_id]);

  useEffect(() => {
    fetchInsurer();
  }, [formData.risk_type_ids, formData.product_id]);

  useEffect(() => {
    onFormChange('is_renewal', is_renewal ? 1 : 0);
    onFormChange('customer_id', cusId);
    onFormChange('lead_id', leadId);

    if (policy_base_id) {
      onFormChange('policy_base_id', policy_base_id);
    }

    if (policy_base_id || leadId) {
      fetchData(policy_base_id, leadId);
    }
    if (draftId) {
      onFormChange('draft_policy_base_id', draftId);
      fetchDraftPolicy();
    }
  }, []);
  console.log('formData.sales_agent_id', formData.sales_agent_id);
  console.log('formData.product_id', formData.product_id);
  const fetchAccountManager = async (userId: any) => {
    setPopulateLoading((prev) => ({ ...prev, accountManagerLoading: true }));
    const response = await getAccountManager({
      agent_Id: userId,
      product_id: formData.product_type === 'product' ? formData.product_id : '',
      product_group_id: formData.product_type === 'group' ? formData.product_id : '',
    });
    if (response.is_success) {
      const managerData = response?.result?.data[0];
      onFormChange('account_manager_id', managerData?.manager_id), onFormChange('account_manager_name', managerData?.manager_name);
    }
    setPopulateLoading((prev) => ({ ...prev, accountManagerLoading: false }));
  };

  const fetchInsurer = async () => {
    setPopulateLoading((prev) => ({ ...prev, insurerLoading: true }));
    const response = await getAllInsurers({
      risk_type_ids: formData.risk_type_ids,
      product_id: formData.product_type === 'product' ? formData.product_id : '',
      group_id: formData.product_type === 'group' ? formData.product_id : '',
    });
    if (response.is_success) {
      const data = response?.result[0];
      onFormChange('insurer_id', data.id), onFormChange('insurer_name', data.name);
    }
    setPopulateLoading((prev) => ({ ...prev, insurerLoading: false }));
  };

  const fetchDraftPolicy = async () => {
    setSkeleton(true);
    const response = await getOneDraftPolicy(draftId!);
    if (response.is_success) {
      const data = response.result ?? {};
      // const quotation = data.quotation_info?.length > 0 ? (data.quotation_info[0] ?? {}) : {};

      onFormChange('policy_draft_documents', data.policy_document_value.length > 0 ? data.policy_document_value : []);
      onFormChange('risk_draft_documents', data.risk_document_value.length > 0 ? data.risk_document_value : []);

      onFormChange('quotation_issued_date', data.quotation_issued_date ? data.quotation_issued_date : '');
      onFormChange('quotation_expiry_date', data.quotation_expiry_date ? data.quotation_expiry_date : '');
      onFormChange('quotation_id', data.quotation_id ? data.quotation_id : '');
      onFormChange('coverage_details_name', data?.quotation_document_name ? data?.quotation_document_name : '');
      onFormChange('coverage_details', data?.quotation_document ? data?.quotation_document : '');

      onFormChange('quotation_code', data.quotation_code ? data.quotation_code : '');
      onFormChange('premium_amount', data.premium_amount ? data.premium_amount : '');
      onFormChange('policy_document', data?.policy_document ? data?.policy_document : '');
      onFormChange('policy_document_name', data?.policy_document_name ? data?.policy_document_name : '');

      onFormChange('risks', data.risk_types?.length > 0 ? data.risk_types : []);
      const riskTypeIds = data.risk_types?.length ? data.risk_types.map((risk: any) => risk.risk_type_id) : [];
      onFormChange('risk_type_ids', riskTypeIds);

      onFormChange('product_type', riskTypeIds.length === 1 ? 'product' : 'group');
      onFormChange('product_name', data?.product?.name ? data?.product?.name : '');
      onFormChange('product_id', data?.product?.id ? data?.product?.id : '');

      onFormChange('insurer_id', data.insurer_id ? data.insurer_id : '');
      onFormChange('insurer_name', data.insurer_company_name ? data.insurer_company_name : '');
      onFormChange('sales_agent_id', data.sales_agent_id ? data.sales_agent_id : '');
      onFormChange('sales_agent_name', data.sales_agent_name ? data.sales_agent_name : '');
      onFormChange('account_manager_id', data.account_manager_id ? data.account_manager_id : '');
      onFormChange('account_manager_name', data.account_manager_name ? data.account_manager_name : '');
      onFormChange('request_by_id', data.requested_by_id ? data.requested_by_id : '');
      onFormChange('request_by_name', data.requested_by ? data.requested_by : '');

      onFormChange('sum_insured', data.sum_insured ? data.sum_insured : '');

      onFormChange('payment_mode_name', data.payment_plan ? data.payment_plan : '');
      onFormChange('payment_mode_id', data.payment_plan_id ? data.payment_plan_id : '');
      onFormChange('insurer_invoice_id', data.insurer_invoice_id ? data.insurer_invoice_id : '');
      onFormChange('insurer_policy_id', data.insurer_policy_id ? data.insurer_policy_id : '');
      onFormChange('invoice_document_name', data.invoice_document_name ? data.invoice_document_name : '');
      onFormChange('invoice_document', data.invoice_document ? data.invoice_document : '');
      onFormChange('policy_effective_date', data.policy_effective_date ? data.policy_effective_date : '');
      onFormChange('credit_period_days', data.credit_period_days ? data.credit_period_days : '');

      onFormChange('policy_start_date', data.policy_start_date ? data.policy_start_date : '');
      onFormChange('policy_expiry_date', data.policy_expiry_date ? data.policy_expiry_date : '');
      const riskInfo = data.risk_configs ? data.risk_configs : {};
      setRiskIdsByType(riskInfo);
    }
    setSkeleton(false);
  };

  const handleSentEmail = async (data: any) => {
    try {
      // const uploadedFiles = data.files ? data.files.map((file: any) => process.env.NEXT_PUBLIC_S3CDN + '/' + file.doc_link) : [];

      const responseData = await policyRequestEmail({
        entity_type: 'common_approval',
        action: 'approval',
        entity_data: {
          id: emailData.entity_id,
        },
        email_data: data,
      });

      if (responseData.is_success) {
        //handleCloseEmailForm();
        setEmailData({ entity_id: '', policy_request_id: '', insurer: '', documents: [] });
        toaster.success(tBe(responseData.message));
        router.back();
      }
    } catch (error) {
      console.error('An error occurred:', error);
    }
  };

  const fetchData = async (pId?: string, lId?: string) => {
    setSkeleton(true);
    const response = pId ? await getIssuedPolicyData({ base_id: pId, fields: 'additional' }) : await getAllOpportunities({ lead_id: lId, fields: 'additional' });
    if (response?.is_success) {
      const data = response.result.data[0] ?? {};
      const quotation = data.quotations?.length > 0 ? (data.quotations[0].crmq_vendor_response ?? {}) : {};
      const policyBase = data?.issued_policies?.[0]?.policy_base ?? {};
      const issuedPolicy = data?.issued_policies?.[0] ?? {};
      onFormChange('brokerage_policy_number', issuedPolicy?.brokerage_policy_id ? issuedPolicy?.brokerage_policy_id : '');
      onFormChange('end_date', issuedPolicy?.policy_expiry_date ? issuedPolicy?.policy_expiry_date : '');
      onFormChange('start_date', issuedPolicy?.policy_start_date ? issuedPolicy?.policy_start_date : '');
      onFormChange('insurer_policy_id', issuedPolicy?.insurer_policy_id ? issuedPolicy?.insurer_policy_id : '');
      onFormChange('issued_policy_sum_insured', issuedPolicy?.sum_insured ? issuedPolicy?.sum_insured : '');

      onFormChange('customer_name', data.customer?.name ? data.customer.name : '');
      onFormChange('customer_primary_contact', data.customer?.primary_contact ? data.customer.primary_contact : '94');
      onFormChange('customer_email', data.customer?.email ? data.customer.email : '');
      onFormChange('customer_address', data.customer?.address ? data.customer.address : '');

      onFormChange('quotation_issued_date', quotation.received_date ? quotation.received_date : '');
      onFormChange('quotation_expiry_date', quotation.expiry_date ? quotation.expiry_date : '');
      onFormChange('quotation_id', quotation.id ? quotation.id : '');
      onFormChange('quotation_code', quotation.code ? quotation.code : '');
      onFormChange('coverage_details_name', quotation?.coverage_details_name ? quotation?.coverage_details_name : '');
      onFormChange('coverage_details', quotation?.coverage_details ? quotation?.coverage_details : '');
      if (pId) {
        onFormChange('policy_document', data?.policy_document ? data?.policy_document : '');
        onFormChange('policy_document_name', data?.policy_document_name ? data?.policy_document_name : '');
      } else {
        onFormChange('policy_document', issuedPolicy?.policy_document ? issuedPolicy?.policy_document : '');
        onFormChange('policy_document_name', issuedPolicy?.policy_document_name ? issuedPolicy?.policy_document_name : '');
      }

      onFormChange('risks', data.lead_risks?.length > 0 ? data.lead_risks : []);
      const riskTypeIds = data.lead_risks?.length ? data.lead_risks.map((risk: any) => risk.risk_type_id) : [];
      onFormChange('risk_type_ids', riskTypeIds);

      onFormChange('product_type', riskTypeIds.length === 1 ? 'product' : 'group');
      onFormChange('insurer_id', policyBase.insurer_id ? policyBase.insurer_id : '');
      onFormChange('insurer_name', policyBase.insurer_name ? policyBase.insurer_name : '');

      if (data.sales_agent_id && data.sales_agent_name) {
        onFormChange('sales_agent_id', data.sales_agent_id);
        onFormChange('sales_agent_name', data.sales_agent_name);
      }
      console.log('data.account_manager_name', data.account_manager_name);
      if (data.account_manager_id) {
        onFormChange('account_manager_id', data.account_manager_id);
        onFormChange('account_manager_name', data.account_manager_name);
      }
      if (data.requested_by_id && data.requested_by) {
        onFormChange('request_by_id', data.requested_by_id);
        onFormChange('request_by_name', data.requested_by);
      }

      onFormChange('sum_insured', policyBase.sum_insured ? policyBase.sum_insured : '');
      if (leadId) {
        onFormChange('premium_amount', quotation.total_amount ? quotation.total_amount : '');
        if (riskTypeIds.length === 1) {
          onFormChange('product_name', data?.product_name ? data?.product_name : '');
          onFormChange('product_id', data?.product_id ? data?.product_id : '');
        } else {
          onFormChange('product_name', data?.product_group_name ? data?.product_group_name : '');
          onFormChange('product_id', data?.product_group_id ? data?.product_group_id : '');
        }
      } else {
        onFormChange('premium_amount', policyBase.premium_amount ? policyBase.premium_amount : '');
        if (riskTypeIds.length === 1) {
          onFormChange('product_name', policyBase?.product_name ? policyBase?.product_name : '');
          onFormChange('product_id', policyBase?.product_id ? policyBase?.product_id : '');
        } else {
          onFormChange('product_name', policyBase?.product_group_name ? policyBase?.product_group_name : '');
          onFormChange('product_id', policyBase?.product_group_id ? policyBase?.product_group_id : '');
        }
      }
      onFormChange('issued_policy_premium_amount', issuedPolicy.premium_amount ? issuedPolicy.premium_amount : '');
      onFormChange('start_date', issuedPolicy.start_date ? issuedPolicy.start_date : '');
      onFormChange('end_date', issuedPolicy.end_date ? issuedPolicy.end_date : '');
      setSkeleton(false);
    }
  };

  const onFormChange = (name: string, value: any) => {
    setFormData((prevFormData) => ({ ...prevFormData, [name]: value }));
  };

  useEffect(() => {
    setResource(null);
  }, [formData.lead_id]);

  async function onSubmit(isDraft?: boolean) {
    clearError(form.policy_request.store);
    setError('');
    setValidationError('');
    setIsFormProcessing(true);
    const productDocuments = await handleDocumentSubmit();
    let refinedEmailDocuments;
    // if (!productDocuments) {
    //   setIsFormProcessing(false);
    //   return null;
    // }
    if (productDocuments) {
      const emailDocuments = Object.values(productDocuments);
      console.log('emailDocuments', emailDocuments);

      // refinedEmailDocuments = emailDocuments.length ? emailDocuments.map((doc: any) => ({ coverage_details_name: doc.name, coverage_details: doc.doc })) : [];
      refinedEmailDocuments = emailDocuments.length ? emailDocuments : [];
    }

    if (fromIssuedPolicies) {
      try {
        const docData = resource ? await handleFileUpload(resource, `quotation_${formData.quotation_code ? `QT${formData.quotation_code}` : `CUS${formData.customer_id}`}`) : null;
        const invoiceFileData = invoiceResource
          ? await handleFileUpload(invoiceResource, `invoice_${formData.insurer_policy_id ? `IP${formData.insurer_policy_id}` : `CUS${formData.customer_id}`}`)
          : null;
        const policyFileData = policyResource
          ? await handleFileUpload(policyResource, `policy_${formData.insurer_policy_id ? `IP${formData.insurer_policy_id}` : `CUS${formData.customer_id}`}`)
          : null;
        const responseData = await createIssuedPolicy({
          ...formData,
          quotation_document: docData?.key,
          quotation_document_name: docData?.name,
          policy_document: policyFileData?.key,
          policy_document_name: policyFileData?.name,
          invoice_document: invoiceFileData?.key,
          invoice_document_name: invoiceFileData?.name,
          product_ids: [formData.product_id],
          risk_ids: riskIdsByType,
          values: productDocuments,
          product_group_id: formData.product_type === 'group' ? formData.product_id : undefined,
          product_id: formData.product_type === 'product' ? formData.product_id : undefined,
          is_draft: fromReRequest ? false : isDraft,
        });
        setIsFormProcessing(false);

        if (responseData.status_code === 417) {
          printError(responseData.result, form.policy_request.store, tBe);
        }

        if (responseData.system_code === 'NO_RISK_VALIDATION') {
          setError(responseData.message.replace(/[\[\]]/g, ''));
        }

        if (responseData.system_code === 'validation_error') {
          setValidationError(responseData.message);
        }

        if (responseData.is_success) {
          toaster.success(tBe(responseData.message));
          router.push(`/policy/a/issued-policies`);
        }
      } catch (error) {
        console.error('An error occurred:', error);
      }
    } else {
      try {
        const docData = resource ? await handleFileUpload(resource, `doc_QT${formData.quotation_code || ''}`) : null;
        const responseData = await createPolicyRequest({
          ...formData,
          is_policy: formData.is_policy,
          quotation_document: docData?.key,
          quotation_document_name: docData?.name,
          quotation_document_type: docData?.type,
          product_ids: [formData.product_id],
          values: productDocuments,
          risk_ids: riskIdsByType,
          product_group_id: formData.product_type === 'group' ? formData.product_id : undefined,
          product_id: formData.product_type === 'product' ? formData.product_id : undefined,
          is_draft: fromReRequest ? false : isDraft,
        });
        refinedEmailDocuments = [...(refinedEmailDocuments ?? []), ...(docData ? [{ doc: docData?.key, name: docData?.name }] : [])];
        setIsFormProcessing(false);

        if (responseData.status_code === 417) {
          printError(responseData.result, form.policy_request.store, tBe);
        }

        if (responseData.system_code === 'NO_RISK_VALIDATION') {
          setError(responseData.message.replace(/[\[\]]/g, ''));
        }

        if (responseData.system_code === 'validation_error') {
          setValidationError(responseData.message);
        }
        if (responseData.is_success) {
          const response = await getPolicyRiskInfoFile(responseData.result.policy_base_id);
          let document;

          document = refinedEmailDocuments ?? [];
          if (response?.is_success) {
            document = [...document, { doc: response.result.file_key, name: response.result.file_name }];
          }
          if (formData.policy_document && formData.policy_document_name) {
            document = [...document, { doc: formData.policy_document, name: formData.policy_document_name }];
          }

          setKey((prevKey) => prevKey + 1);
          onFormChange('request_by_id', user.id), onFormChange('request_by_name', user.display_name);
          toaster.success(tBe(responseData.message));
          if (isDraft) {
            router.push('/policy/a/policy-request');
          } else {
            setEmailData({
              entity_id: responseData.result?.entity_id,
              policy_request_id: responseData.result?.policy_request_id,
              insurer: formData.insurer_name,
              documents: document,
            });
          }
          setFormData(initPolicyData);
        }
      } catch (error) {
        console.error('An error occurred:', error);
      }
    }
  }

  const handleDocumentSubmit = async () => {
    if (productDocRef.current) {
      const result = await productDocRef.current.onSubmit();
      if (result) {
        return result;
      } else {
        return null;
      }
    }
  };

  useEffect(() => {
    console.log('riskIdsByType', riskIdsByType);
  }, [riskIdsByType]);

  const handleRiskIds = (riskTypeId: string, ids: any[]) => {
    setRiskIdsByType((prev) => ({
      ...prev,
      [riskTypeId]: ids,
    }));
  };

  const onRiskTypeChange = (ids: number[]) => {
    const updatedRiskIds = ids.reduce<Record<string, number[]>>((acc, id) => {
      acc[id] = riskIdsByType[id] || [];
      return acc;
    }, {});
    setRiskIdsByType(updatedRiskIds);
  };

  const handleOnDraft = async (setLoader: Function, onClose: Function) => {
    setLoader(true);
    await onSubmit(true);
    onClose();
  };

  return (
    <div>
      <DraftConfirmPopup
        trigger={
          <GoTo
            goTo={() => {
              //fromIssuedPolicies ? router.push('/policy/a/issued-policies') : router.push('/policy/a/policy-request');
            }}
            title={fromIssuedPolicies ? t('create_policy') : t('create_policy_request')}
          />
        }
        handleOnDraft={handleOnDraft}
        onClose={() => {
          fromIssuedPolicies ? router.push('/policy/a/issued-policies') : router.push('/policy/a/policy-request');
        }}
      />

      {is_renewal && (
        <div className="panel">
          <div className="panel-title mb-3">{t('current_policy_info')}</div>
          <div className="row">
            <div className="col-12 col-md-3 mb-3">
              <Description label={t('brokerage_policy_number')} value={formData?.brokerage_policy_number || 'N/A'} skeleton={skeleton} />
            </div>
            <div className="col-12 col-md-3 mb-3">
              <Description label={t('insurer')} value={formData?.insurer_name || '-'} skeleton={skeleton} />
            </div>
            <div className="col-12 col-md-3 mb-3">
              <Description label={t('product_name')} value={formData?.product_name || '-'} skeleton={skeleton} />
            </div>
            <div className="col-12 col-md-3 mb-3">
              <Description label={t('insurer_policy_number')} value={formData?.insurer_policy_id || '-'} skeleton={skeleton} />
            </div>
            <div className="col-12 col-md-3 mb-3">
              <Description label={t('policy_start_date')} value={formatDate(formData?.start_date ?? '') || '-'} skeleton={skeleton} />
            </div>
            <div className="col-12 col-md-3 mb-3">
              <Description label={t('policy_end_date')} value={formatDate(formData?.end_date ?? '') || '-'} skeleton={skeleton} />
            </div>
            <div className="col-12 col-md-3 mb-3">
              <Description label={t('sum_insured')} value={formData?.issued_policy_sum_insured || '-'} skeleton={skeleton} />
            </div>
            <div className="col-12 col-md-3 mb-3">
              <Description label={t('premium_amount')} value={formData?.issued_policy_premium_amount || '-'} skeleton={skeleton} />
            </div>
          </div>
        </div>
      )}
      <div id={`${form.policy_request.store}`} key={key}>
        {!is_renewal && (
          <div className="panel" key={`quotation-${formData.lead_id}`}>
            <div className="panel-title">{t('quotation_info')}</div>
            <div className="row">
              <div className="col-12 col-md-3 mb-3">
                <Label label={t('quotation_id')} />
                {skeleton ? (
                  <InputSkeleton />
                ) : (
                  <Input value={formData.quotation_code} onChange={(e) => onFormChange('quotation_code', e.target.value)} className="form-control error-quotation_id" name="quotation_id" />
                )}
              </div>
              <div className="col-12 col-md-3 mb-3">
                <Label label={t('confirmed_quotation')} />
                {skeleton ? (
                  <InputSkeleton />
                ) : (
                  <>
                    {!(resource || formData.coverage_details) ? (
                      <InputFileUploader data={(file: File) => setResource(file)} className="form-control error-quotation_document" name="quotation_document" />
                    ) : (
                      <FilePreviewInput
                        fileName={resource?.name || formData.coverage_details_name}
                        onCancel={() => {
                          setResource(null), onFormChange('coverage_details_name', '');
                        }}
                        s3Key={formData.coverage_details}
                        downloadable
                      />
                    )}
                  </>
                )}
              </div>
              <div className="col-12 col-md-3 mb-3">
                <Label label={t('premium_amount')} />
                {skeleton ? (
                  <InputSkeleton />
                ) : (
                  <Input
                    type="number"
                    value={formData.premium_amount}
                    onChange={(e) => onFormChange('premium_amount', e.target.value)}
                    className="form-control error-premium_amount"
                    name="premium_amount"
                  />
                )}
              </div>
              <div className="col-12 col-md-3 mb-3">
                <Label label={t('quotation_issued_date')} />
                {skeleton ? (
                  <InputSkeleton />
                ) : (
                  <Input
                    value={formData.quotation_issued_date}
                    onChange={(e) => onFormChange('quotation_issued_date', e.target.value)}
                    className="form-control error-quotation_issued_date"
                    name="quotation_issued_date"
                    type="date"
                  />
                )}
              </div>
              <div className="col-12 col-md-3 mb-3">
                <Label label={t('quotation_expiry_date')} />
                {skeleton ? (
                  <InputSkeleton />
                ) : (
                  <Input
                    value={formData.quotation_expiry_date}
                    onChange={(e) => onFormChange('quotation_expiry_date', e.target.value)}
                    className="form-control error-quotation_expiry_date"
                    name="quotation_expiry_date"
                    type="date"
                  />
                )}
              </div>
              {/* <div className="col-12 mb-3">
              <Input
                label={t('notes')}
                type="textarea"
                rows={3}
                value={formData.quotation_notes}
                onChange={(e) => onFormChange('quotation_notes', e.target.value)}
                className="form-control error-quotation_notes"
                name="quotation_notes"
              />
            </div> */}
            </div>
          </div>
        )}
        <div className="panel" key={`policy-related-${formData.lead_id}`}>
          <div className="panel-title mb-3">{t('product_information')}</div>
          <div className="row">
            <div className="col-12 col-md-3 mb-3 custom-select">
              <Label htmlFor="risk_type" label={t('risk_type')} isRequired />
              {skeleton ? (
                <InputSkeleton />
              ) : (
                <AsyncSelect
                  multiple={customerType === 1 ? true : false}
                  isSearchable
                  className="form-control error-risk_type_ids"
                  option={{ label: 'name', value: 'id' }}
                  onChange={(_, selectedData) => {
                    if (customerType === 1) {
                      const selectedRiskIds = selectedData.map((data: any) => data.id);
                      setSelectedActiveTab(0);
                      onRiskTypeChange(selectedRiskIds || []);
                      onFormChange('product_id', ''), onFormChange('product_name', '');
                      onFormChange('risk_type_ids', selectedRiskIds || []);
                      onFormChange('risks', selectedData.map((risk: any) => ({ risk_type_name: risk.name, risk_type_id: risk.id })) || []);
                    } else {
                      onRiskTypeChange([selectedData.id]);
                      onFormChange('product_id', ''), onFormChange('product_name', '');
                      onFormChange('risk_type_ids', [selectedData.id]);
                      onFormChange('risks', [{ risk_type_name: selectedData.name, risk_type_id: selectedData.id }]);
                    }
                  }}
                  defaultValue={
                    formData?.risks
                      ? customerType === 1
                        ? formData.risks.map((risk: any) => ({ name: risk.risk_type_name, id: risk.risk_type_id }))
                        : formData.risks.map((risk: any) => ({ name: risk.risk_type_name, id: risk.risk_type_id }))[0]
                      : []
                  }
                  loadOptions={(searchStr: string, page: number) => fetchAllProductTypes(searchStr, page)}
                />
              )}
            </div>
            {formData.risk_type_ids.length > 0 && (
              <div className="col-12 col-md-3 mb-3 custom-select" key={`product-${formData.risk_type_ids}`}>
                <Label htmlFor="product_name" label={t('product_name')} isRequired />
                <AsyncSelect
                  onChange={(_value, data) => {
                    onFormChange('product_type', formData.risk_type_ids.length === 1 ? 'product' : 'group');
                    onFormChange('product_id', data.id), onFormChange('product_name', data.name);
                    onFormChange('insurer_id', ''), onFormChange('insurer_name', '');
                  }}
                  className="form-control error-product_id"
                  option={{ label: 'name', value: 'id' }}
                  defaultValue={{ name: formData.product_name, id: formData.product_id }}
                  isSearchable={true}
                  loadOptions={(searchValue: any, currentPage: any) => fetchAllProductsByType(searchValue, currentPage, formData.risk_type_ids)}
                />
              </div>
            )}
            {formData.product_id && (
              <div className="col-12 col-md-3 mb-3 custom-select" key={`insurer-${formData.product_id}`}>
                <Label htmlFor="insurer" label={t('insurer')} isRequired />
                {populateLoading.insurerLoading ? (
                  <InputSkeleton />
                ) : (
                  <AsyncSelect
                    onChange={(_value, data) => {
                      onFormChange('insurer_id', data.id), onFormChange('insurer_name', data.name);
                    }}
                    className="form-control error-insurer_id"
                    option={{ label: 'name', value: 'id' }}
                    isSearchable={true}
                    loadOptions={(searchValue: any, currentPage: any) =>
                      fetchAllInsurers(
                        searchValue,
                        currentPage,
                        formData.risk_type_ids,
                        formData.risk_type_ids.length > 1 ? formData.product_id : undefined,
                        formData.risk_type_ids.length === 1 ? formData.product_id : undefined,
                      )
                    }
                    defaultValue={{ name: formData.insurer_name, id: formData.insurer_id }}
                  />
                )}
              </div>
            )}
            <div className="col-12 col-md-3 mb-3">
              <Label label={t('sum_insured')} isRequired />
              {skeleton ? (
                <InputSkeleton />
              ) : (
                <Input value={formData.sum_insured} type="number" onChange={(e) => onFormChange('sum_insured', e.target.value)} className="form-control error-sum_insured" name="sum_insured" />
              )}
            </div>
            {/* <div className="col-12 col-md-3 mb-3 custom-select">
              <Label htmlFor="product_name" label={t('coverages')} isRequired />
              <AsyncSelect
                onChange={(_value, data) => {
                  onFormChange('coverage_type_id', data.id), onFormChange('coverage_type_name', data.name);
                }}
                className="form-control error-coverage_type_id"
                option={{ label: 'name', value: 'id' }}
                isSearchable={true}
                defaultValue={{ name: formData.coverage_type_name, id: formData.coverage_type_id }}
                loadOptions={(searchValue: any, currentPage: any) => fetchAllCoverages(searchValue, currentPage)}
              />
            </div> */}
            <div className="col-12 col-md-3 mb-3">
              <Label label={t('policy_start_date')} isRequired />
              {skeleton ? (
                <InputSkeleton />
              ) : (
                <Input
                  value={formData.policy_start_date}
                  onChange={(e) => onFormChange('policy_start_date', e.target.value)}
                  className="form-control error-policy_start_date"
                  name="policy_start_date"
                  type="date"
                  min={is_renewal ? formatDate(formData?.end_date) : undefined}
                />
              )}
            </div>
            <div className="col-12 col-md-3 mb-3">
              <Label label={t('policy_end_date')} isRequired />
              {skeleton ? (
                <InputSkeleton />
              ) : (
                <Input
                  value={formData.policy_expiry_date}
                  onChange={(e) => onFormChange('policy_expiry_date', e.target.value)}
                  className="form-control error-policy_expiry_date"
                  name="policy_expiry_date"
                  type="date"
                  min={formData.policy_start_date}
                />
              )}
            </div>
            <div className="col-12 col-md-3 mb-3">
              <Label label={t('no_of_days')} />
              {skeleton ? (
                <InputSkeleton />
              ) : (
                <Input
                  value={
                    formData.policy_expiry_date && formData.policy_start_date
                      ? Math.ceil((new Date(formData.policy_expiry_date).getTime() - new Date(formData.policy_start_date).getTime()) / (1000 * 3600 * 24))
                      : ''
                  }
                  disabled
                />
              )}
            </div>
            {fromIssuedPolicies && (
              <div className="col-12 col-md-3 mb-3 custom-select custom-dropdown">
                <Label htmlFor="payment_term" label={t('payment_term')} />
                <AsyncSelect
                  onChange={(_value, data) => {
                    onFormChange('payment_mode_id', data.id), onFormChange('payment_mode_name', data.name);
                  }}
                  className="form-control error-payment_mode_id"
                  option={{ label: 'name', value: 'id' }}
                  defaultValue={{ name: formData.payment_mode_name, id: formData.payment_mode_id }}
                  isSearchable={true}
                  loadOptions={(searchValue: any, currentPage: any) => fetchAllPaymentTypes(searchValue, currentPage)}
                />
              </div>
            )}
            <div className="col-12 col-md-3 mb-3 custom-select">
              <Label htmlFor="requested_by" label={t('requested_by')} isRequired />
              {skeleton ? (
                <InputSkeleton />
              ) : (
                <AsyncSelect
                  onChange={(_value: any, data: any) => {
                    onFormChange('request_by_id', data.id), onFormChange('request_by_name', data.display_name);
                  }}
                  className="form-control error-request_by_id"
                  option={{ label: 'display_name', value: 'id' }}
                  defaultValue={{ display_name: formData.request_by_name, id: formData.request_by_id }}
                  isSearchable={true}
                  loadOptions={(searchValue, currentPage) => fetchAllUsers(searchValue, currentPage)}
                />
              )}
            </div>

            <div className="col-12 col-md-3 mb-3 custom-select">
              <Label label={t('sales_agent')} isRequired />
              {populateLoading.initialLoading || skeleton ? (
                <InputSkeleton />
              ) : (
                <AsyncSelect
                  onChange={(_value, data) => {
                    onFormChange('sales_agent_id', data.user_id), onFormChange('sales_agent_name', data.user_name);
                  }}
                  className="form-control error-sales_agent_id"
                  option={{ label: 'user_name', value: 'user_id' }}
                  isSearchable={true}
                  loadOptions={(searchValue: any, currentPage: any) =>
                    fetchAllSalesAgent(
                      searchValue,
                      currentPage,
                      '',
                      '',
                      '',
                      //  formData.account_manager_id,
                      // formData.product_type === 'product' ? formData.product_id : '',
                      // formData.product_type === 'group' ? formData.product_id : '',
                    )
                  }
                  defaultValue={{ user_name: formData.sales_agent_name, user_id: formData.sales_agent_id }}
                />
              )}
            </div>
            <div className="col-12 col-md-3 mb-3 custom-select">
              <Label label={t('account_manager')} isRequired />
              {populateLoading.accountManagerLoading || skeleton ? (
                <InputSkeleton />
              ) : (
                <AsyncSelect
                  onChange={(_value, data) => {
                    onFormChange('account_manager_id', data.manager_id), onFormChange('account_manager_name', data.manager_name);
                  }}
                  className="form-control error-account_manager_id"
                  option={{ label: 'manager_name', value: 'manager_id' }}
                  isSearchable={true}
                  loadOptions={(searchValue: any, currentPage: any) =>
                    fetchAllAccountManagers(
                      searchValue,
                      currentPage,
                      '',
                      '',
                      '',
                      // formData.sales_agent_id,
                      // formData.product_type === 'product' ? formData.product_id : '',
                      // formData.product_type === 'group' ? formData.product_id : '',
                    )
                  }
                  defaultValue={{ manager_name: formData.account_manager_name, manager_id: formData.account_manager_id }}
                />
              )}
            </div>
          </div>
        </div>
        {fromIssuedPolicies && (
          <div className="panel">
            <div className="panel-title mb-3">{t('policy_information')}</div>
            <div className="row">
              <div className="col-12 col-md-3 mb-3">
                <Input
                  isRequired
                  label={t('insurer_policy_number')}
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
                <Label htmlFor="debit_note" label={t('debit_note')} />
                {!(invoiceResource || formData.invoice_document_name) ? (
                  <InputFileUploader data={(file: File) => setInvoiceResource(file)} className="form-control error-invoice_document" name="invoice_document" />
                ) : (
                  <FilePreviewInput
                    fileName={invoiceResource?.name || formData.invoice_document_name}
                    onCancel={() => {
                      setInvoiceResource(null), onFormChange('invoice_document_name', '');
                    }}
                  />
                )}
              </div>
              <div className="col-12 col-md-3 mb-3">
                <Label htmlFor="policy_document" label={t('policy_document')} />
                {!(policyResource || formData.policy_document_name) ? (
                  <InputFileUploader data={(file: File) => setPolicyResource(file)} className="form-control error-policy_document" name="policy_document" />
                ) : (
                  <FilePreviewInput
                    fileName={policyResource?.name || formData.policy_document_name}
                    onCancel={() => {
                      setPolicyResource(null), onFormChange('policy_document_name', '');
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
              {/* <div className="col-12 col-md-3 mb-3">
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
              </div> */}
              {/* <div className="col-12 col-md-3 mb-3">
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
              </div> */}
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
              {/* <div className="col-12 col-md-3 mb-3">
                <Input
                  isRequired
                  label={t('credit_age')}
                  value={formData.credit_age_days}
                  onChange={(e) => onFormChange('credit_age_days', e.target.value)}
                  className="form-control error-credit_age_days"
                  name="credit_age"
                />
              </div> */}
            </div>
          </div>
        )}
        {/* <div className="panel mt-3">
          <div className="panel-title mb-3">{t('insurer_info')}</div>
          <div className="row">
            {formData.risk_type_ids.length > 0 && (
              <div className="col-12 col-md-3 mb-3 custom-select" key={`insurer-${formData.product_id}`}>
                <Label htmlFor="insurer" label={t('insurer')} isRequired />
                <AsyncSelect
                  onChange={(_value, data) => {
                    onFormChange('insurer_id', data.id), onFormChange('insurer_name', data.name);
                  }}
                  className="form-control error-insurer_id"
                  option={{ label: 'name', value: 'id' }}
                  isSearchable={true}
                  loadOptions={(searchValue: any, currentPage: any) =>
                    fetchAllInsurers(
                      searchValue,
                      currentPage,
                      formData.risk_type_ids,
                      formData.risk_type_ids.length > 1 ? formData.product_id : undefined,
                      formData.risk_type_ids.length === 1 ? formData.product_id : undefined,
                    )
                  }
                  defaultValue={{ name: formData.insurer_name, id: formData.insurer_id }}
                />
              </div>
            )}
            <div className="col-12 col-md-3 mb-3 custom-select">
              <Label htmlFor="requested_by" label={t('requested_by')} isRequired />
              <AsyncSelect
                onChange={(_value: any, data: any) => {
                  onFormChange('request_by_id', data.id), onFormChange('request_by_name', data.display_name);
                }}
                className="form-control error-request_by_id"
                option={{ label: 'display_name', value: 'id' }}
                defaultValue={{ display_name: formData.request_by_name, id: formData.request_by_id }}
                isSearchable={true}
                loadOptions={(searchValue, currentPage) => fetchAllUsers(searchValue, currentPage)}
              />
            </div>
            <div className="col-12 col-md-3 mb-3 custom-select">
              <Label label={t('sales_agent')} />
              <AsyncSelect
                onChange={(_value, data) => {
                  onFormChange('sales_agent_id', data.id), onFormChange('sales_agent_name', data.display_name);
                }}
                className="form-control error-sales_agent_id"
                option={{ label: 'display_name', value: 'id' }}
                isSearchable={true}
                loadOptions={(searchValue: any, currentPage: any) => fetchAllUsers(searchValue, currentPage)}
                defaultValue={{ display_name: formData.sales_agent_name, id: formData.sales_agent_id }}
              />
            </div>
            <div className="col-12 mb-3">
              <Input
                label={t('notes_to_insurer')}
                type="textarea"
                rows={3}
                value={formData.insurer_notes}
                onChange={(e) => onFormChange('insurer_notes', e.target.value)}
                className="form-control error-insurer_notes"
                name="insurer_notes"
              />
            </div>
          </div>
        </div> */}
      </div>

      {formData.risks.length > 0 && (
        <div className="panel" key={`risks-${riskTableKey}`}>
          <div className="d-flex justify-content-between align-items-center">
            <div className="panel-title">{t('risk_details')}</div>
            <Button color="light" className="d-flex align-items-center gap-1 me-2" onClick={() => setIsBulkUploadOpen(true)}>
              <Flexicon icon="upload-01" size={18} />
              <span className="d-none d-sm-inline">{t('upload_risk_info')}</span>
            </Button>
          </div>
          <div className="il-box-tab">
            {formData.risks.map((riskType: any, index) => (
              <div key={riskType.risk_type_id} className={`il-box-tab-item ${activeSelectedTab === index ? 'active' : ''}`} onClick={() => setSelectedActiveTab(index)}>
                {capitalizeFirstLetter(riskType.risk_type_name)}
              </div>
            ))}
          </div>
          {formData.risks.map((riskType: any, index) =>
            activeSelectedTab === index ? (
              <OpportunityTypes
                key={riskType.risk_type_id}
                selectedTypeId={riskType.risk_type_id}
                customerId={formData.customer_id}
                leadId={formData.lead_id}
                selectedRiskIds={(ids: any) => handleRiskIds(riskType.risk_type_id, ids)}
                defaultRiskIds={riskIdsByType[riskType.risk_type_id] || []}
                // defaultRiskIds={[116]}
              />
            ) : null,
          )}
          {error && <strong className="text-danger fs-13">{tBe(error)}</strong>}
        </div>
      )}

      {formData.product_id !== '' && (
        <div className="panel">
          <ProductDocuments
            productId={formData.product_id}
            productType={formData.product_type}
            key={formData.product_id}
            ref={productDocRef}
            defaultDocuments={[...formData.policy_draft_documents, ...formData.risk_draft_documents]}
            isDraft={draftId !== ''}
          />
        </div>
      )}
      {validationError && <span className="err-msg">{tBe(validationError)}</span>}
      <div className="d-flex justify-content-end gap-2 mt-4">
        <Button text={t('submit')} onClick={() => onSubmit()} width="sm" isLoading={isFormProcessing} />
        {/* <Button text={t('cancel')} color="light" width="sm" onClick={() => router.push(`/policy/a/${fromIssuedPolicies ? `issued-policies` : 'policy-request'}`)} /> */}
        <DraftConfirmPopup
          trigger={<Button text={t('cancel')} color="light" width="sm" />}
          handleOnDraft={handleOnDraft}
          onClose={() => {
            fromIssuedPolicies ? router.push('/policy/a/issued-policies') : router.push('/policy/a/policy-request');
          }}
          placement="left"
        />
      </div>
      {emailData?.entity_id && (
        <EmailForm
          isOpen={emailData.entity_id !== ''}
          onCancel={() => {
            setEmailData({ entity_id: '', policy_request_id: '', insurer: '', documents: [] });
            router.push(`/policy/a/${fromIssuedPolicies ? `issued-policies` : 'policy-request'}`);
          }}
          recipientNames={[emailData.insurer]}
          defaultTemplate={getDefaultPolicyRequestEmailTemplateForInsurer(emailData.insurer)}
          emailData={(data: any) => handleSentEmail(data)}
          defaultFiles={emailData.documents}
        />
      )}
      {isBulkUploadOpen && formData.risk_type_ids.length > 0 && (
        <BulkUpload
          isOpen={isBulkUploadOpen}
          onCancel={() => setIsBulkUploadOpen(false)}
          afterSave={() => {
            setIsBulkUploadOpen(false), setRiskTableKey((prev) => prev + 1);
          }}
          riskTypeIds={formData.risk_type_ids}
          leadId={formData.lead_id}
          customerId={formData.customer_id}
        />
      )}
    </div>
  );
}

export default CreatePolicies;
