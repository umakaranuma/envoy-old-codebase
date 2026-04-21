'use client';
import { useTrans } from '@/helpers/services/lang/langService';
import React, { useEffect, useState } from 'react';
import { Description } from '@/components/others/Description';
import { Badge, Button, PopConfirm, Skeleton } from '@apptimus-ui/ui-element';
import { findApprovalProcessAvailable, getAllServiceProviders, getOneApproval, updateApproval } from '../api-service';
import { IApproval, IServiceProvider } from '../model';
import { useParams, useRouter } from 'next/navigation';
import { Flexicon } from '@apptimus-ui/flexicon';
import { clearError, printError } from '@/helpers/handlers/validationErrorHandler';
import { form } from '@/constans/Form';
import { toaster } from '@/helpers/services/toaster';
import ApprovalConfirmation from './ApprovalConfirmation';
import { capitalizeFirstLetter, formatDate } from '@/helpers/services/commonService';
import GoBack from '@/components/others/page-related/GoBack';
import OpportunityTypes from './risk-types/OpportunityTypes';
import EmailView from './EmailView';
import { fileUploader } from '@/helpers/services/storageService';
import { useBreadcrumb } from '@/contexts/BreadcrumbContext';

export const ApprovalView = () => {
  const t = useTrans('label.approvals,otr.common');
  const tBe = useTrans('be.msg,be.error,be.attri');
  const [data, setData] = useState({} as IApproval);
  const [skeleton, setSkeleton] = useState(true);
  const params = useParams();
  const approvalId = params.approvalId?.toString() || '';
  const router = useRouter();
  const [isOpen, setIsOpen] = useState(false);
  const [allServiceProviders, setAllServiceProviders] = useState<IServiceProvider[]>([]);
  const [selectedServiceProviders, setSelectedServiceProviders] = useState<IServiceProvider[]>([]);
  const [availableServiceProviders, setAvailableServiceProviders] = useState<IServiceProvider[]>([]);
  const dropdownRef = React.useRef<HTMLDivElement>(null);
  const [isFormProcessing, setIsFormProcessing] = useState(false);
  const [isApprovalProcess, setIsApprovalProcess] = useState(false);
  const [formData, setFormData] = useState({ subject: '', body: '', documents: [], recipientNames: [], defaultTemplate: '', files: [] as File[] });
  const [activeSelectedTab, setSelectedActiveTab] = useState(0);
  const [isSubjectError, setIsSubjectError] = useState(false);
  const [selectedOperation, setSelectedOperation] = useState({ status: '', id: '' });
  const { setCustomBreadcrumb } = useBreadcrumb();

  useEffect(() => {
    setCustomBreadcrumb({
      text: data.code ? data.code : '',
      backurl: '/a/approvals',
    });
    return () => setCustomBreadcrumb(null);
  }, [data]);

  useEffect(() => {
    if (approvalId) {
      setSkeleton(true);
      fetchData();
    }
  }, [approvalId]);

  const fetchData = async () => {
    const responseData = await getOneApproval(approvalId);
    if (responseData?.is_success) {
      setData(responseData.result);
      setFormData({
        subject: responseData.result.email_data?.subject ? responseData.result.email_data.subject : '',
        body: responseData.result.email_data?.body ? responseData.result.email_data.body : '',
        documents: responseData.result.document_data ? responseData.result.document_data : [],
        recipientNames: responseData.result.email_data?.recipientNames ? responseData.result.email_data.recipientNames : [],
        defaultTemplate: responseData.result.email_data?.body ? responseData.result.email_data.body : '',
        files: [],
      });
      fetchServiceProviders();
      fetchApprovalAvailability();
      setSkeleton(false);
      if (responseData.result?.service_providers?.length) {
        setSelectedServiceProviders(
          responseData.result.service_providers.map((provider: IServiceProvider) => ({
            id: provider.service_provider_id,
            name: provider.service_provider_name,
            checked: true,
          })),
        );
      }
    }
  };

  const fetchServiceProviders = async () => {
    const responseData = await getAllServiceProviders({});
    if (responseData?.is_success) {
      const providers = responseData.result.data || [];
      setAllServiceProviders(providers);
      updateAvailableProviders(providers, selectedServiceProviders);
    }
  };

  const fetchApprovalAvailability = async () => {
    const response = await findApprovalProcessAvailable(approvalId);
    if (response.is_success) {
      if (response.result) {
        setIsApprovalProcess(true);
      } else {
        setIsApprovalProcess(false);
      }
    }
  };

  useEffect(() => {
    updateAvailableProviders(allServiceProviders, selectedServiceProviders);
  }, [selectedServiceProviders, allServiceProviders]);

  useEffect(() => {
    const handleClickOutside = (e: any) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target)) {
        setIsOpen(false);
      }
    };
    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isOpen]);

  const updateAvailableProviders = (all: IServiceProvider[], selected: IServiceProvider[]) => {
    const selectedIds = selected.map((provider) => provider.id);
    const available = all.filter((provider) => !selectedIds.includes(provider.id));
    setAvailableServiceProviders(available);
  };

  const toggleDropdown = () => {
    setIsOpen(!isOpen);
  };

  const onFormChange = (name: string, value: any) => {
    setData((prevFormData) => ({ ...prevFormData, [name]: value }));
  };

  const addServiceProvider = (provider: IServiceProvider) => {
    setSelectedServiceProviders([...selectedServiceProviders, { ...provider, checked: true }]);
    // setIsOpen(false);
  };

  const handleToggleCheck = (id: string | number) => {
    setIsOpen(false);
    setSelectedServiceProviders(selectedServiceProviders.filter((provider) => (provider.id !== id ? provider.checked : !provider.checked)));
  };

  async function handleUpdateData() {
    clearError(form.approvals.update);
    clearError(form.email.store);
    if (formData.subject.trim() === '') {
      setIsSubjectError(true);
      return;
    }
    setIsFormProcessing(true);
    try {
      let documents = data.document_data ? data.document_data : [];
      console.log('documents', documents);

      if (formData.files.length > 0) {
        const files = await handleFileUpload();
        if (files) {
          documents = [...documents, ...files];
        }
      }

      const responseData = await updateApproval(approvalId, { ...data, email_data: { ...formData, documents } });
      setIsFormProcessing(false);

      if (responseData.status_code === 417) {
        printError(responseData.result, form.approvals.update, tBe);
      }

      if (responseData.is_success) {
        toaster.success(tBe(responseData.message));
        router.push('/a/approvals');
      }
    } catch (error) {
      console.error('An error occurred:', error);
    }
  }

  useEffect(() => {
    onFormChange(
      'service_provider_ids',
      selectedServiceProviders.map((provider) => provider.id),
    );
  }, [selectedServiceProviders]);

  const handleFileUpload = async () => {
    if (formData.files.length === 0) {
      return null;
    }

    const fileData: any[] = [];

    for (const file of formData.files) {
      const s3FormData = new FormData();
      s3FormData.append('file', file);
      const key = await fileUploader(s3FormData, 'approvals');
      const fileType = file.name.split('.').pop();
      const fileName = file.name;
      fileData.push({ doc: key, name: fileName, type: fileType });
    }

    return fileData;
  };

  return (
    <>
      <GoBack goTo={() => router.push(`/a/approvals`)} title={t('approval_request_details')} />
      <div>
        <div className="panel">
          <div className="row">
            <div className="panel-title">{t('request_details')}</div>
            <div className="col-6 col-md-6 col-lg-4 mb-3">
              <Description label={t('request_id')} value={data?.code || '-'} skeleton={skeleton} />
            </div>
            <div className="col-6 col-md-6 col-lg-4 mb-3">
              <Description label={t('category')} value={<Badge text={data?.entity_type} color={data?.entity_type === 'policy' ? 'primary' : 'warning'} radius="pill" />} skeleton={skeleton} />
            </div>
            <div className="col-6 col-md-6 col-lg-4 mb-3">
              <Description label={t('transaction_type')} value={data?.request_type || '-'} skeleton={skeleton} />
            </div>
            <div className="col-6 col-md-6 col-lg-4 mb-3">
              <Description label={t('request_date')} value={formatDate(data?.request_date) || '-'} skeleton={skeleton} />
            </div>
            <div className="col-6 col-md-6 col-lg-4 mb-3">
              <Description label={t('requested_by')} value={data?.created_by_name || '-'} skeleton={skeleton} />
            </div>
            <div className="col-6 col-md-6 col-lg-4 mb-3">
              <Description label={t('customer_info')} value={data?.customer_name || '-'} skeleton={skeleton} />
            </div>
            <div className="col-6 col-md-6 col-lg-4 mb-3">
              <Description label={t('lead')} value={data?.opportunity_title || '-'} skeleton={skeleton} />
            </div>
            <div className="col-6 col-md-6 col-lg-4 mb-3">
              <Description label={t('remarks')} value={data?.notes || '-'} isTruncate={false} skeleton={skeleton} />
            </div>
            {/* <div className="col-6 col-md-6 col-lg-4 mb-3">
              <Description label={t('approved_by')} value={data?.approved_by_name || '-'} skeleton={skeleton} />
            </div>
            <div className="col-6 col-md-6 col-lg-4 mb-3">
              <Description label={t('date')} value={formatDate(data?.approval_date)} skeleton={skeleton} />
            </div> */}
          </div>
        </div>
        {/* <div className="mb-3">{data.opportunity_type_id && <RiskTypes quotationData={data} />}</div> */}

        {data.opportunity_types?.length > 0 && (
          <div className="panel">
            <div className="panel-title">{t('risk_details')}</div>
            <div className="il-box-tab">
              {data.opportunity_types.map((riskType: any, index) => (
                <div key={riskType.id} className={`il-box-tab-item ${activeSelectedTab === index ? 'active' : ''}`} onClick={() => setSelectedActiveTab(index)}>
                  {capitalizeFirstLetter(riskType.title)}
                </div>
              ))}
            </div>
            {data.opportunity_types.map((riskType: any, index) =>
              activeSelectedTab === index ? <OpportunityTypes approvalId={approvalId} riskTypeIds={riskType.id} customerId={data.customer_id?.toString()} key={riskType.id} /> : null,
            )}
          </div>
        )}

        <div className="panel">
          <div className="row">
            <div className="panel-title">{t('selected_insurers')}</div>
            {data.entity_type === 'quotation' ? (
              <div className="d-flex flex-row gap-3 flex-wrap">
                <div className="dropdown custom-select" ref={dropdownRef}>
                  <Button className="d-flex align-items-center justify-content-between" onClick={toggleDropdown} disabled={availableServiceProviders.length === 0}>
                    <div className="d-flex align-items-center">
                      <Flexicon icon="plus-circle" size={16} className="me-2" />
                      <span>{t('add_new')}</span>
                    </div>
                  </Button>
                  {isOpen && availableServiceProviders.length > 0 && (
                    <div className="dropdown-menu show position-absolute mt-1">
                      {availableServiceProviders.map((provider) => (
                        <button key={provider.id} className="dropdown-item d-flex align-items-center" onClick={() => addServiceProvider(provider)}>
                          {/* <div className="rounded me-2 d-flex align-items-center justify-content-center" style={{ width: '24px', height: '24px', backgroundColor: 'green' }}></div> */}
                          <span>{provider.name}</span>
                        </button>
                      ))}
                    </div>
                  )}
                </div>
                <div className="d-flex flex-row flex-wrap gap-3">
                  {selectedServiceProviders?.map((provider) => (
                    <div key={provider.id} className="d-flex align-items-center px-2 bg-light rounded" style={{ paddingTop: '6px', paddingBottom: '5px' }}>
                      <PopConfirm
                        trigger={
                          <div className="form-check">
                            <input
                              className="form-check-input mt-1"
                              type="checkbox"
                              id={`provider-${provider.id}`}
                              checked={provider.checked}
                              readOnly
                              // onChange={() => toggleCheck(provider.id)}
                            />
                          </div>
                        }
                        onConfirm={() => {
                          handleToggleCheck(provider.id);
                        }}
                        onCancel={(callback) => callback()}
                        placement="left"
                        title={t('confirm')}
                        body={t('service_confirmation_msg')}
                        confirmText={t('yes')}
                        cancelText={t('cancel')}
                      />
                      {/* <div className="rounded mx-2 d-flex align-items-center justify-content-center" style={{ width: '24px', height: '24px', backgroundColor: 'green' }}></div> */}
                      <label htmlFor={`provider-${provider.id}`} className="form-check-label">
                        {provider.name}
                      </label>
                    </div>
                  ))}
                </div>
              </div>
            ) : (
              <Description value={data?.service_providers ? data?.service_providers[0]?.service_provider_name : '-'} skeleton={skeleton} />
            )}
          </div>
        </div>
        <div className="panel">
          <div className="row">
            <div className="panel-title">{t('send_an_email')}</div>
            <div className="row mb-3">
              {skeleton ? (
                <Skeleton height="100px" />
              ) : (
                <EmailView
                  // defaultTemplate={data.email_data ? data.email_data.body : ''}
                  // // key={'emailFormKey'}
                  recipientNames={selectedServiceProviders.map((sp) => sp.name)}
                  // defaultSubject={data.email_data ? data.email_data.subject : ''}
                  // emailData={(data: any) => setEmailData(data)}
                  // defaultFiles={data.email_data ? data.email_data.defaultDocuments : []}
                  isSubjectError={isSubjectError}
                  formData={formData}
                  setFormData={setFormData}
                />
              )}
            </div>
          </div>
        </div>
      </div>
      {/* {data.approval_status === 'approved' && (
        <div className="panel">
          <div className="row">
            <div className="col-6 col-md-6 col-lg-4">
              <div className="fs-15 text-muted">{t('approved_by')}</div>
              {skeleton ? (
                <InputSkeleton />
              ) : (
                <div className="d-flex gap-1 align-items-center pt-1">
                  <S3Avatar imageKey={undefined} width={20} height={20} />
                  <span className="fs-15">{data?.approved_by_name || '-'}</span>
                </div>
              )}
            </div>
            <div className="col-6 col-md-6 col-lg-4 mb-3">
              <Description label={t('date')} value={formatDate(data?.approval_date ? data.approval_date : '') || '-'} skeleton={skeleton} />
            </div>
          </div>
        </div>
      )} */}
      <div className="d-flex gap-2 mb-3">
        {isApprovalProcess && data.approval_status !== 'approved' && (
          <div className="row mb-3">
            <div className="d-flex justify-content-start">
              <Button className="d-flex align-items-center gap-1" onClick={() => setSelectedOperation({ status: 'approved', id: approvalId })} width="sm">
                <Flexicon icon="check-circle" variant="line" size={15} />
                <span className="d-none d-sm-inline">{t('yes_approve')}</span>
              </Button>
            </div>
          </div>
        )}
        {isApprovalProcess && data.approval_status !== 'approved' && (
          <div className="row mb-3">
            <div className="d-flex justify-content-start">
              <Button className="d-flex align-items-center gap-1" color="danger" onClick={() => setSelectedOperation({ status: 'rejected', id: approvalId })} width="sm">
                <Flexicon icon="x-circle" variant="line" size={15} />
                <span className="d-none d-sm-inline">{t('reject')}</span>
              </Button>
            </div>
          </div>
        )}
      </div>
      <div className="d-flex justify-content-end gap-2 ">
        <Button className="d-flex align-items-center gap-1" onClick={handleUpdateData} isLoading={isFormProcessing} width="sm">
          <Flexicon icon="save-01" variant="line" size={15} />
          <span className="d-none d-sm-inline">{t('save_changes')}</span>
        </Button>
      </div>
      {selectedOperation.id !== '' && (
        <ApprovalConfirmation
          isOpen={selectedOperation.id !== ''}
          onCancel={() => setSelectedOperation({ status: '', id: '' })}
          afterSave={() => {
            setSelectedOperation({ status: '', id: '' }), router.push('/a/approvals');
          }}
          currentId={selectedOperation.id}
          status={selectedOperation.status}
        />
      )}
    </>
  );
};
