import { form } from '@/constans/Form';
import { clearError, printError } from '@/helpers/handlers/validationErrorHandler';
import { useTrans } from '@/helpers/services/lang/langService';
import { toaster } from '@/helpers/services/toaster';
import { Modal, ModalBody, ModalFooter, ModalHeader } from '@apptimus-ui/modal';
import { Button, Input, Label } from '@apptimus-ui/ui-element';
import React, { FormEvent, useState } from 'react';
import { CreateEndorsementRequests } from '../../api-service';
import { AsyncSelect } from '@apptimus-ui/select';
import { fetchAllEndorsementTypes, fetchAllReasonCodes } from '../../service';
import { initEndorsementCreate } from '../../model';
import { useParams } from 'next/navigation';

function EndorsementRequestsCreate({ isOpen, onCancel, setEmailData, afterSave }: { isOpen: boolean; onCancel: Function; setEmailData: Function; afterSave: Function }) {
  const t = useTrans('label.issued_policies,otr.common,be.msg');
  const tBe = useTrans('be.msg,be.error,be.attri');
  const [isFormProcessing, setIsFormProcessing] = useState(false);
  const [formData, setFormData] = useState(initEndorsementCreate);
  const params = useParams();
  const policyId = params.policyId?.toString() || '';

  const onFormChange = (name: string, value: any) => {
    setFormData((prevFormData: any) => ({ ...prevFormData, [name]: value }));
  };

  async function onSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    clearError(form.endorsementRequests.store);
    setIsFormProcessing(true);
    try {
      const responseData = await CreateEndorsementRequests({ ...formData, issued_policy_id: policyId });
      setIsFormProcessing(false);

      if (responseData.status_code === 417) {
        printError(responseData.result, form.endorsementRequests.store, tBe);
      }

      if (responseData.is_success) {
        afterSave();
        setFormData(initEndorsementCreate);
        handleOpenEmail(responseData.result);
        toaster.success(tBe(responseData.message));
      } else {
        toaster.error(tBe(responseData.message));
      }
    } catch (error) {
      console.error('An error occurred:', error);
    }
  }

  const handleOpenEmail = (data: any) => {
    onCancel();
    setTimeout(() => {
      setEmailData(data);
    }, 100);
  };

  return (
    <Modal isOpen={isOpen}>
      <ModalHeader title={t('create_new_entity', { entity: t('endorsement') })} onClose={() => onCancel()} />
      <form onSubmit={onSubmit} id={`${form.endorsementRequests.store}`}>
        <ModalBody>
          <div className="row">
            <div className="col-12 mb-3 custom-select">
              <Label htmlFor="endorsement_type" label={t('endorsement_type')} isRequired />
              <AsyncSelect
                onChange={(value) => onFormChange('endorsement_type_id', value)}
                className="form-control error-endorsement_type_id"
                option={{ label: 'name', value: 'id' }}
                isSearchable={false}
                loadOptions={(searchValue: any, currentPage: any) => fetchAllEndorsementTypes(searchValue, currentPage)}
              />
            </div>
            {/* <div className={`col-12 mb-3 custom-select ${!formData.endorsement_type_id ? 'disabled' : ''}`} style={!formData.endorsement_type_id ? { pointerEvents: 'none', opacity: 0.5 } : {}}> */}
            {formData.endorsement_type_id && (
              <div className="col-12 mb-3 custom-select" key={formData.endorsement_type_id}>
                <Label label={t('reason')} isRequired />
                <AsyncSelect
                  onChange={(value) => onFormChange('reason_code_id', value)}
                  className="form-control error-reason_code_id"
                  option={{ label: 'name', value: 'id' }}
                  isSearchable={false}
                  loadOptions={(searchValue: any, currentPage: any) => fetchAllReasonCodes(searchValue, currentPage, formData.endorsement_type_id)}
                />
              </div>
            )}
            {(formData.endorsement_type_id === 1 || formData.endorsement_type_id === 2) && (
              <div className="col-12 mb-3">
                <Input
                  label={t('sum_insured')}
                  isRequired
                  value={formData.cover_value}
                  onChange={(e) => onFormChange('cover_value', e.target.value)}
                  className="form-control error-cover_value"
                  name="cover_value"
                />
              </div>
            )}
            <div className="col-12 mb-3">
              <Input label={t('remarks')} type="textarea" value={formData.remarks} onChange={(e) => onFormChange('remarks', e.target.value)} className="form-control error-remarks" name="remarks" />
            </div>
          </div>
        </ModalBody>
        <ModalFooter>
          <div className="d-flex justify-content-end gap-2">
            <Button text={t('cancel')} color="light" width="sm" onClick={() => onCancel()} />
            <Button text={t('next')} type="submit" width="sm" isLoading={isFormProcessing} />
          </div>
        </ModalFooter>
      </form>
    </Modal>
  );
}

export default EndorsementRequestsCreate;
