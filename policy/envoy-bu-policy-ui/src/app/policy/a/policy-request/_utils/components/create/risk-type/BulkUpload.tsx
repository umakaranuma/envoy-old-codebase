import { Modal, ModalBody, ModalFooter, ModalHeader } from '@apptimus-ui/modal';
import React, { useEffect, useState } from 'react';
import { toaster } from '@/helpers/services/toaster';
import { useTrans } from '@/helpers/services/lang/langService';
import { Button, Label } from '@apptimus-ui/ui-element';
import { bulkUpload, getBulkUploadExcel } from '../../../api-service';
import FilePreviewInput from '@/components/others/page-related/uploader/FilePreviewInput';
import InputFileUploader from '@/components/others/page-related/uploader/InputFileUploader';
import { Flexicon } from '@apptimus-ui/flexicon';
import { InputSkeleton } from '@/components/others/InputSkeleton';
import { handleFileUpload } from '@/helpers/services/commonService';
import { clearError, printError } from '@/helpers/handlers/validationErrorHandler';
import { form } from '@/constans/Form';

function BulkUpload({
  isOpen,
  onCancel,
  afterSave,
  riskTypeIds,
  leadId,
  customerId,
}: {
  isOpen: boolean;
  onCancel: Function;
  afterSave: Function;
  riskTypeIds: string[];
  leadId: string;
  customerId: string;
}) {
  const [isFormProcessing, setIsFormProcessing] = useState(false);
  const t = useTrans('label.policy_request,otr.common,be.msg');
  const tBe = useTrans('be.msg,be.error,be.attri');
  const [loading, setLoading] = useState(true);
  const [formData, setFormData] = useState({ excelFile: '', file_key: '', customer_id: '', lead_id: '' });
  const [resource, setResource] = useState<File | null>();
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        const responseData = await getBulkUploadExcel({ risk_type_ids: riskTypeIds.join(',') });
        if (responseData?.is_success) {
          onFormChange('excelFile', responseData.result.download_url);
        }
      } catch (error) {
        console.error('Error fetching bulk upload Excel:', error);
      } finally {
        setLoading(false);
      }
    };

    if (riskTypeIds.length > 0) {
      fetchData();
    }
  }, [riskTypeIds]);

  const onFormChange = (name: string, value: any) => {
    setFormData((prevFormData) => ({ ...prevFormData, [name]: value }));
  };

  async function onSubmit() {
    setError('');
    clearError(form.bulk_upload.store);
    setIsFormProcessing(true);
    try {
      const docData = resource ? await handleFileUpload(resource) : null;
      const responseData = await bulkUpload({
        customer_id: customerId,
        lead_id: leadId,
        file_key: docData?.key,
      });
      setIsFormProcessing(false);
      if (responseData.status_code === 417) {
        printError(responseData.result, form.bulk_upload.store, tBe);
      }
      if (responseData.system_code === 'VALIDATION_ERROR') {
        setError(responseData.message);
      }
      if (responseData.is_success) {
        toaster.success(tBe(responseData.message));
        afterSave();
      }
    } catch (error) {
      console.error('An error occurred:', error);
      setIsFormProcessing(false);
    }
  }

  async function handleDownloadTemplate(url: string) {
    const link = document.createElement('a');
    link.href = url;
    link.target = '_blank';
    link.rel = 'noopener noreferrer';
    link.download = url || '';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }

  return (
    <Modal isOpen={isOpen} onBackdrop={() => onCancel()} scrollable={true}>
      <ModalHeader title={t('upload')} onClose={() => onCancel()} />
      <ModalBody>
        <div className="row">
          <div className="col-12 mb-3">
            <Label label={t('download_template')} />
            {/* {<FileDownloadButton s3Key={formData.excelFile} fileType="xlsx" />} */}
            {loading ? (
              <InputSkeleton />
            ) : (
              <div
                onClick={() => handleDownloadTemplate(formData.excelFile)}
                className="file-download-btn"
                //style={{ border: '1px solid #67E3F9', color: '#0E7090', cursor: 'pointer', width: 'fit-content' }}
              >
                <svg width="18" height="18" viewBox="0 0 27 21" fill="none" xmlns="http://www.w3.org/2000/svg">
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

                <div className="text-truncate text fs-13">{t('download')}</div>
                <Flexicon icon="download-01" variant="line" size={15} className="text-primary" />
              </div>
            )}
          </div>
          <div className="col-12" id={`${form.bulk_upload.store}`}>
            <Label label={t('upload_file')} />
            {!resource ? (
              <InputFileUploader fileType="excel" data={(file: File) => setResource(file)} className="form-control error-file_key" name="file_key" />
            ) : (
              <FilePreviewInput
                fileName={resource?.name}
                onCancel={() => {
                  setResource(null);
                }}
              />
            )}
          </div>
          {error && (
            <div className="col-12 mt-2">
              <strong style={{ color: '#dc3545' }} className="fs-13">
                {error}
              </strong>
            </div>
          )}
        </div>
      </ModalBody>
      <ModalFooter>
        <div className="d-flex justify-content-end gap-2">
          <Button text={t('cancel')} color="light" width="sm" onClick={() => onCancel()} />
          <Button text={t('submit')} type="submit" width="sm" isLoading={isFormProcessing} onClick={onSubmit} />
        </div>
      </ModalFooter>
    </Modal>
  );
}

export default BulkUpload;
