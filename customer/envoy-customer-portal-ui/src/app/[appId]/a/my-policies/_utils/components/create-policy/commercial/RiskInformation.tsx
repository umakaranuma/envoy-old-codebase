'use client';
import { useTrans } from '@/helpers/services/lang/langService';
import Image from 'next/image';
import React, { useEffect, useState } from 'react';
import step0 from '../../../../../../../../../public/images/claim/step0.png';
import step1 from '../../../../../../../../../public/images/claim/step1.png';
import step2 from '../../../../../../../../../public/images/claim/step2.png';
import step3 from '../../../../../../../../../public/images/claim/step3.png';

import { Flexicon } from '@apptimus-ui/flexicon';
import UploadDocument from './UploadDocument';
import { Button, Skeleton } from '@apptimus-ui/ui-element';
import { form } from '@/constans/Form';
import { printError } from '@/helpers/handlers/validationErrorHandler';
import { toaster } from '@/helpers/services/toaster';
import { downloadTemplate, getOneRiskInfoTemplate, uploadCommercialRiskInfoExcel } from '../../../api-service';
import { useParams, useSearchParams } from 'next/navigation';
import { fileUploader } from '@/helpers/services/storageService';
import { Dropdown } from '@apptimus-ui/dropdown';
import S3Avatar from '@/components/others/page-related/S3Avatar';
import { getLocalStorage } from '@/helpers/handlers/localStorageHandler';
import { local_storage } from '@/constans/StorageKeys';

function RiskInformation({ setToggleTab, type, requestId }: { setToggleTab: Function; type: string; requestId: string }) {
  const t = useTrans('label.my_policy,otr.common');
  const [currentStep, setCurrentStep] = useState(1);
  const [isFormProcessing, setIsFormProcessing] = useState(false);
  const [uploadedTemplate, setUploadedTemplate] = useState<{ doc: string; name: string } | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [skeleton, setSkeleton] = useState<boolean>(false);

  useEffect(() => {
    const fetchData = async () => {
      const responseData = await getOneRiskInfoTemplate(requestId as string);
      if (responseData?.is_success) {
        if (responseData.result.document_link) {
          setUploadedTemplate({ doc: responseData.result.document_link, name: responseData.result.document_name });
          setCurrentStep(4);
        }
        setSkeleton(false);
      }
      if (responseData.status_code === 404) {
        setSkeleton(false);
      }
    };
    if (requestId) {
      setSkeleton(true);
      fetchData();
    }
  }, [requestId]);

  useEffect(() => {
    if (uploadedTemplate) {
      setError(null);
    }
  }, [uploadedTemplate]);

  const stepCardData = [
    {
      title: 'download_templates',
      description1: 'select_the_product_types_for_your_quotation_request',
      description2: 'click_the_button_below_to_download_templates',
      button: <DownloadTemplatesButton setCurrentStep={setCurrentStep} />,
    },
    {
      title: 'fill_out_the_templates',
      description1: 'open_the_downloaded_template_files_and_fill_out_the_details_form',
      description2: 'double_check_entries_for_accuracy',
      button: <ContinueButton setCurrentStep={setCurrentStep} />,
    },
    {
      title: 'upload_completed_templates',
      description1: 'upload_the_completed_templates_using_the_button_below',
      description2: 'ensure_all_required_templates_are_included',
      button: <UploadButton setCurrentStep={setCurrentStep} setUploadedTemplate={setUploadedTemplate} uploadedTemplate={uploadedTemplate} />,
    },
  ];

  const StepCircle = ({ label, status, step }: { label: string; status: string; step: number }) => {
    const color = status === 'current' ? '#116c8b' : status === 'completed' ? '#DCFAE6' : '#F2F4F7';
    const transform = step === 1 ? 'rotate(-30deg)' : step === 2 ? 'rotate(0deg)' : 'rotate(30deg)';
    const textTransform = step === 1 ? 'rotate(30deg)' : step === 2 ? 'translateX(0)' : 'rotate(-30deg)';
    return (
      <div className="d-flex flex-row align-items-center">
        <div className="step-wrapper" style={{ transform: transform, transformOrigin: 'right center' }}>
          <div className="step-circle" style={{ backgroundColor: color, transform: textTransform, color: status === 'current' ? 'white' : '#667085' }}>
            {label}
          </div>
        </div>
        <div className="position-relative " style={{ top: '-10rem', left: '4rem' }}>
          <StepCard
            title={stepCardData[step - 1].title}
            step={step === 1 ? 'step_1' : step === 2 ? 'step_2' : 'step_3'}
            description1={stepCardData[step - 1].description1}
            description2={stepCardData[step - 1].description2}
            button={stepCardData[step - 1].button}
            status={status}
          />
        </div>
      </div>
    );
  };

  async function onSubmit() {
    if (uploadedTemplate === null) {
      setError('Please upload the completed templates.');
      return;
    }
    setIsFormProcessing(true);
    try {
      const responseData = await uploadCommercialRiskInfoExcel({ request_id: requestId, type: type, document_link: uploadedTemplate?.doc, document_name: uploadedTemplate?.name });
      setIsFormProcessing(false);

      if (responseData.is_success) {
        setToggleTab('coverage_info');
      }
    } catch (error) {
      console.error('An error occurred:', error);
    }
  }

  return (
    <>
      {skeleton ? (
        <Skeleton height="200px" width="100%" />
      ) : (
        <div className="mb-4">
          <div className="pb-3 overflow-x-auto overflow-y-hidden">
            <div className="panel-title"> {t('risk_information_submission')}</div>
            <div className="fs-15 mb-2">{t('instructions_for_submitting_risk_information')}</div>
            <div className="fs-14 text-muted mb-5">{t('follow_these_steps_to_ensure_accurate_quotation_processing')}</div>
            <div className="d-flex flex-row align-items-center p-5">
              <Image
                src={currentStep === 1 ? step0.src : currentStep === 2 ? step1.src : currentStep === 3 ? step2.src : step3.src}
                alt={'claim-creation'}
                width={350}
                height={350}
                className="img-fluid"
              />
              <div className="d-none d-lg-inline flex-column mt-3 mb-5">
                <div style={{ position: 'relative', top: '4rem' }}>
                  <StepCircle label={t('step_1')} step={1} status={currentStep === 1 ? 'current' : currentStep > 1 ? 'completed' : ''} />
                </div>
                <div style={{ position: 'relative', top: '10rem', left: '6rem' }}>
                  <StepCircle label={t('step_2')} step={2} status={currentStep === 2 ? 'current' : currentStep > 2 ? 'completed' : ''} />
                </div>
                <div style={{ position: 'relative', top: '17rem', left: '1rem' }}>
                  <StepCircle label={t('step_3')} step={3} status={currentStep === 3 ? 'current' : currentStep > 3 ? 'completed' : ''} />
                </div>
              </div>
            </div>
            <div className="d-flex d-lg-none flex-column gap-4 mb-5">
              <StepCard
                title={stepCardData[0].title}
                step={'step_1'}
                description1={stepCardData[0].description1}
                description2={stepCardData[0].description2}
                button={stepCardData[0].button}
                status={currentStep === 1 ? 'current' : currentStep > 1 ? 'completed' : ''}
              />
              <StepCard
                title={stepCardData[1].title}
                step={'step_2'}
                description1={stepCardData[1].description1}
                description2={stepCardData[1].description2}
                button={stepCardData[1].button}
                status={currentStep === 2 ? 'current' : currentStep > 2 ? 'completed' : ''}
              />
              <StepCard
                title={stepCardData[2].title}
                step={'step_3'}
                description1={stepCardData[2].description1}
                description2={stepCardData[2].description2}
                button={stepCardData[2].button}
                status={currentStep === 3 ? 'current' : currentStep > 3 ? 'completed' : ''}
              />
            </div>
          </div>
          {error && (
            <span style={{ color: 'red' }} className="fs-14">
              {error}
            </span>
          )}
          <div className="d-flex justify-content-start gap-2 mt-3">
            <Button color="light" className="d-flex align-items-center gap-1" onClick={() => setToggleTab('personal_info')}>
              <Flexicon icon="chevron-left" variant="line" size={18} />
              <span className="d-none d-sm-inline">{t('back')}</span>
            </Button>
            <Button color="primary" className="d-flex align-items-center gap-1" type="submit" onClick={onSubmit} isLoading={isFormProcessing}>
              <span className="d-none d-sm-inline">{t('next')}</span>
              <Flexicon icon="chevron-right" variant="line" size={18} />
            </Button>
          </div>
        </div>
      )}
    </>
  );
}

export default RiskInformation;

const StepCard = ({
  title,
  description1,
  description2,
  button,
  step,
  status,
}: {
  title: string;
  description1: string;
  description2: string;
  button: React.ReactNode;
  step: string;
  status: string;
}) => {
  const t = useTrans('label.my_policy,label.profile,otr.common');
  const agentInfo = getLocalStorage(local_storage.agent_info);

  return (
    <div>
      <div className="d-flex flex-row align-items-center gap-2 mb-3">
        <div className="fw-medium">
          {t(`${step}`)} {t(`${title}`)}
        </div>
        <Flexicon icon="check-verified-02" variant="line" className={status === 'completed' ? 'text-success' : status === 'current' ? 'text-primary' : 'text-light'} />
      </div>
      <div className="text-muted fs-14 mb-3">
        <div>1. {t(`${description1}`)}</div>
        <div>2. {t(`${description2}`)}</div>
      </div>
      {step === 'step_2' && (
        <div className="mb-3 d-flex flex-row align-items-center gap-2">
          <span className="fw-medium">{t('tip')}</span>
          <Dropdown
            className="ms-4"
            trigger={
              <span className="clickable-text" style={{ cursor: 'pointer', color: '#63C0E3', textDecoration: 'underline' }}>
                {t('contact_us')}
              </span>
            }
          >
            {(onClose: any) => (
              <>
                <div className="p-3 px-4 mb-1">
                  <div style={{ width: '220px' }}>
                    <div className="d-flex flex-column gap-2">
                      <div className="text-end align-self-center">
                        <S3Avatar width={60} height={60} imageKey={agentInfo?.logo} />
                      </div>
                      <div className="align-self-center">
                        <div className="fs-18 fw-medium">{agentInfo?.display_name}</div>
                        <div className="fs-14 text-muted">{agentInfo?.email}</div>
                      </div>
                      <div className="d-flex flex-row justify-content-between align-items-center gap-3 my-2">
                        <Button color="primary" className="d-flex align-items-center gap-1" variant="outline" onClick={onClose}>
                          <Flexicon icon="mail-01" variant="line" size={18} />
                          <a className="d-none d-sm-inline" href={`https://wa.me/${agentInfo?.contact}`}>
                            {t('message')}
                          </a>
                        </Button>
                        <Button color="primary" className="d-flex align-items-center gap-1 px-4" onClick={onClose}>
                          <Flexicon icon="phone-call-01" variant="line" size={18} />
                          <a className="d-none d-sm-inline text-white" href={`tel:${agentInfo?.contact}`}>
                            {t('call')}
                          </a>
                        </Button>
                      </div>
                    </div>
                  </div>
                </div>
              </>
            )}
          </Dropdown>{' '}
          {t('double_check_entries_for_accuracy')}
        </div>
      )}
      <div>{button}</div>
    </div>
  );
};

const DownloadTemplatesButton = ({ setCurrentStep }: { setCurrentStep: (step: number) => void }) => {
  const t = useTrans('label.my_policy,otr.common');
  const tBe = useTrans('be.msg,be.error,be.attri');
  const searchParams = useSearchParams();
  const riskTypeIds = searchParams.get('rId') || [];

  const handleDownloadTemplate = async () => {
    try {
      const responseData = await downloadTemplate({ risk_type_ids: [riskTypeIds] });
      //setIsFormProcessing(false);

      if (responseData.status_code === 417) {
        printError(responseData.result, form.settlement.store, tBe);
      }

      if (responseData.is_success) {
        toaster.success(tBe(responseData.message));
        const fileUrl = responseData.result.download_url;
        const link = document.createElement('a');
        link.href = fileUrl;
        link.setAttribute('download', 'risk_information_template.xlsx');
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);

        setCurrentStep(2);
      }
    } catch (error) {
      console.error('An error occurred:', error);
    }
  };
  return (
    <div
      onClick={handleDownloadTemplate}
      className="d-flex flex-row align-items-center gap-2 rounded-2 p-2"
      style={{ border: '1px solid #67E3F9', color: '#0E7090', cursor: 'pointer', width: 'fit-content' }}
    >
      <svg width="27" height="21" viewBox="0 0 27 21" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path
          d="M13.8682 0.75H19.8076L25.1182 6.06055V16C25.1182 17.7949 23.6631 19.25 21.8682 19.25H13.8682C12.0732 19.25 10.6182 17.7949 10.6182 16V4C10.6182 2.20507 12.0732 0.75 13.8682 0.75Z"
          stroke="#D0D5DD"
          strokeWidth="1.5"
        />
        <path d="M19.8682 0.25V2C19.8682 4.20914 21.659 6 23.8682 6H25.6182" stroke="#D0D5DD" strokeWidth="1.5" />
        <rect x="0.368164" y="5" width="26" height="16" rx="2" fill="#079455" />
        <path
          d="M5.75453 9.72727L7.22115 12.206H7.27797L8.75169 9.72727H10.4882L8.26873 13.3636L10.5379 17H8.76944L7.27797 14.5178H7.22115L5.72967 17H3.96831L6.24458 13.3636L4.01092 9.72727H5.75453ZM11.4612 17V9.72727H12.9988V15.7322H16.1167V17H11.4612ZM21.0803 11.8189C21.0519 11.5324 20.93 11.3099 20.7146 11.1513C20.4991 10.9927 20.2068 10.9134 19.8374 10.9134C19.5865 10.9134 19.3746 10.9489 19.2018 11.0199C19.029 11.0885 18.8964 11.1844 18.8041 11.3075C18.7141 11.4306 18.6691 11.5703 18.6691 11.7266C18.6644 11.8568 18.6916 11.9704 18.7508 12.0675C18.8124 12.1645 18.8964 12.2486 19.0029 12.3196C19.1095 12.3883 19.2326 12.4486 19.3722 12.5007C19.5119 12.5504 19.6611 12.593 19.8197 12.6286L20.4731 12.7848C20.7903 12.8558 21.0815 12.9505 21.3467 13.0689C21.6118 13.1873 21.8415 13.3329 22.0356 13.5057C22.2297 13.6785 22.3801 13.8821 22.4866 14.1165C22.5955 14.3509 22.6511 14.6196 22.6535 14.9226C22.6511 15.3677 22.5375 15.7536 22.3126 16.0803C22.0901 16.4046 21.7681 16.6567 21.3467 16.8366C20.9276 17.0142 20.4222 17.103 19.8303 17.103C19.2432 17.103 18.7319 17.013 18.2963 16.8331C17.863 16.6532 17.5245 16.3868 17.2806 16.0341C17.0392 15.679 16.9125 15.2398 16.9007 14.7166H18.3886C18.4052 14.9605 18.475 15.1641 18.5981 15.3274C18.7236 15.4884 18.8905 15.6103 19.0988 15.6932C19.3095 15.7737 19.5474 15.8139 19.8126 15.8139C20.073 15.8139 20.2991 15.776 20.4909 15.7003C20.685 15.6245 20.8353 15.5192 20.9419 15.3842C21.0484 15.2493 21.1017 15.0942 21.1017 14.919C21.1017 14.7557 21.0531 14.6184 20.9561 14.5071C20.8614 14.3958 20.7217 14.3011 20.537 14.223C20.3547 14.1449 20.131 14.0739 19.8659 14.0099L19.074 13.8111C18.4608 13.6619 17.9767 13.4287 17.6215 13.1115C17.2664 12.7943 17.0901 12.367 17.0924 11.8295C17.0901 11.3892 17.2072 11.0045 17.444 10.6754C17.6831 10.3464 18.011 10.0895 18.4276 9.90483C18.8443 9.72017 19.3178 9.62784 19.8481 9.62784C20.3879 9.62784 20.859 9.72017 21.2615 9.90483C21.6663 10.0895 21.9811 10.3464 22.2061 10.6754C22.431 11.0045 22.547 11.3857 22.5541 11.8189H21.0803Z"
          fill="white"
        />
      </svg>
      <div className="fw-medium">{t('download_template')}</div>
      <Flexicon icon="download-01" variant="line" />
    </div>
  );
};

const ContinueButton = ({ setCurrentStep }: { setCurrentStep: (step: number) => void }) => {
  const t = useTrans('label.my_policy,otr.common');
  const handleContinue = () => {
    setCurrentStep(3);
  };

  return (
    <div onClick={handleContinue} className="d-flex flex-row align-items-center gap-2 rounded-2 p-2" style={{ border: '1px solid #D0D5DD', color: '#667085', cursor: 'pointer', width: 'fit-content' }}>
      <div className="fw-medium">{t('continue')}</div>
      <Flexicon icon="arrow-narrow-right" variant="line" />
    </div>
  );
};

const UploadButton = ({
  setCurrentStep,
  setUploadedTemplate,
  uploadedTemplate,
}: {
  setCurrentStep: (step: number) => void;
  setUploadedTemplate: Function;
  uploadedTemplate: { doc: string; name: string } | null;
}) => {
  const t = useTrans('label.my_policy,otr.common');
  const [isOpen, setIsOpen] = useState(false);

  const params = useParams();
  const appId = params.appId as string;

  const handleTemplateUpload = async (uploadedFile: File | null) => {
    const template = await handleFileUpload(uploadedFile ?? null);
    setUploadedTemplate(template);

    setIsOpen(false);
    setCurrentStep(4);
  };

  const handleFileUpload = async (file: File | null) => {
    const fileData = new FormData();
    if (!file) {
      return null;
    }
    fileData.append('file', file);
    const fileName = file.name;
    const fileExtension = file.name.split('.').pop();
    const key = await fileUploader(fileData, `${appId}/customer/risk-info-template`);
    return { doc: key, name: fileName, type: fileExtension };
  };

  return (
    <>
      {!uploadedTemplate ? (
        <div
          className="d-flex flex-row align-items-center gap-2 rounded-2 p-2"
          onClick={() => setIsOpen(true)}
          style={{ border: '1px solid #D0D5DD', color: '#667085', cursor: 'pointer', width: 'fit-content' }}
        >
          <Flexicon icon="upload-01" variant="line" />
          <div className="fw-medium">{t('upload_risk_info')}</div>
        </div>
      ) : (
        <div className="d-flex flex-row align-items-center gap-2 rounded-2 p-2" style={{ border: '1px solid #67E3F9', color: '#0E7090', cursor: 'pointer', width: 'fit-content' }}>
          <svg width="27" height="21" viewBox="0 0 27 21" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path
              d="M13.8682 0.75H19.8076L25.1182 6.06055V16C25.1182 17.7949 23.6631 19.25 21.8682 19.25H13.8682C12.0732 19.25 10.6182 17.7949 10.6182 16V4C10.6182 2.20507 12.0732 0.75 13.8682 0.75Z"
              stroke="#D0D5DD"
              strokeWidth="1.5"
            />
            <path d="M19.8682 0.25V2C19.8682 4.20914 21.659 6 23.8682 6H25.6182" stroke="#D0D5DD" strokeWidth="1.5" />
            <rect x="0.368164" y="5" width="26" height="16" rx="2" fill="#079455" />
            <path
              d="M5.75453 9.72727L7.22115 12.206H7.27797L8.75169 9.72727H10.4882L8.26873 13.3636L10.5379 17H8.76944L7.27797 14.5178H7.22115L5.72967 17H3.96831L6.24458 13.3636L4.01092 9.72727H5.75453ZM11.4612 17V9.72727H12.9988V15.7322H16.1167V17H11.4612ZM21.0803 11.8189C21.0519 11.5324 20.93 11.3099 20.7146 11.1513C20.4991 10.9927 20.2068 10.9134 19.8374 10.9134C19.5865 10.9134 19.3746 10.9489 19.2018 11.0199C19.029 11.0885 18.8964 11.1844 18.8041 11.3075C18.7141 11.4306 18.6691 11.5703 18.6691 11.7266C18.6644 11.8568 18.6916 11.9704 18.7508 12.0675C18.8124 12.1645 18.8964 12.2486 19.0029 12.3196C19.1095 12.3883 19.2326 12.4486 19.3722 12.5007C19.5119 12.5504 19.6611 12.593 19.8197 12.6286L20.4731 12.7848C20.7903 12.8558 21.0815 12.9505 21.3467 13.0689C21.6118 13.1873 21.8415 13.3329 22.0356 13.5057C22.2297 13.6785 22.3801 13.8821 22.4866 14.1165C22.5955 14.3509 22.6511 14.6196 22.6535 14.9226C22.6511 15.3677 22.5375 15.7536 22.3126 16.0803C22.0901 16.4046 21.7681 16.6567 21.3467 16.8366C20.9276 17.0142 20.4222 17.103 19.8303 17.103C19.2432 17.103 18.7319 17.013 18.2963 16.8331C17.863 16.6532 17.5245 16.3868 17.2806 16.0341C17.0392 15.679 16.9125 15.2398 16.9007 14.7166H18.3886C18.4052 14.9605 18.475 15.1641 18.5981 15.3274C18.7236 15.4884 18.8905 15.6103 19.0988 15.6932C19.3095 15.7737 19.5474 15.8139 19.8126 15.8139C20.073 15.8139 20.2991 15.776 20.4909 15.7003C20.685 15.6245 20.8353 15.5192 20.9419 15.3842C21.0484 15.2493 21.1017 15.0942 21.1017 14.919C21.1017 14.7557 21.0531 14.6184 20.9561 14.5071C20.8614 14.3958 20.7217 14.3011 20.537 14.223C20.3547 14.1449 20.131 14.0739 19.8659 14.0099L19.074 13.8111C18.4608 13.6619 17.9767 13.4287 17.6215 13.1115C17.2664 12.7943 17.0901 12.367 17.0924 11.8295C17.0901 11.3892 17.2072 11.0045 17.444 10.6754C17.6831 10.3464 18.011 10.0895 18.4276 9.90483C18.8443 9.72017 19.3178 9.62784 19.8481 9.62784C20.3879 9.62784 20.859 9.72017 21.2615 9.90483C21.6663 10.0895 21.9811 10.3464 22.2061 10.6754C22.431 11.0045 22.547 11.3857 22.5541 11.8189H21.0803Z"
              fill="white"
            />
          </svg>
          <div className="fw-medium">{uploadedTemplate.name}</div>
          <Flexicon
            icon="x-close"
            variant="line"
            className="text-danger action-icon"
            onClick={() => {
              setUploadedTemplate(null), setCurrentStep(3);
            }}
          />
        </div>
      )}
      {isOpen && <UploadDocument isOpen={isOpen} onCancel={() => setIsOpen(false)} setFile={(file: File) => handleTemplateUpload(file)} />}
    </>
  );
};
