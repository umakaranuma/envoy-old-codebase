import { form } from '@/constans/Form';
import { clearError, printError } from '@/helpers/handlers/validationErrorHandler';
import { useTrans } from '@/helpers/services/lang/langService';
import { Modal, ModalBody, ModalFooter, ModalHeader } from '@apptimus-ui/modal';
import { Button, Label } from '@apptimus-ui/ui-element';
import React, { FormEvent, useState } from 'react';
import { toaster } from '@/helpers/services/toaster';
import { createOpportunityType } from '../../../api-service';
import { AsyncSelect } from '@apptimus-ui/select';
import { fetchAllOpportunityTypes } from '../../../services';
import { useParams } from 'next/navigation';

function AddType({ isOpen, onCancel, afterSave }: { isOpen: boolean; onCancel: Function; afterSave: Function }) {
  const tBe = useTrans('be.msg,be.error,be.attri');
  const t = useTrans('label.sales_managements,otr.common,be.msg');
  const [isFormProcessing, setIsFormProcessing] = useState(false);
  const [formData, setFormData] = useState({ type_id: '' });
  const params = useParams();
  const opportunityId = params.managementId?.toString() || '';
  const onFormChange = (name: string, value: any) => {
    setFormData((prevFormData) => ({ ...prevFormData, [name]: value }));
  };

  async function onSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    clearError(form.opportunity_type.store);
    setIsFormProcessing(true);

    try {
      const responseData = await createOpportunityType(formData, opportunityId);
      setIsFormProcessing(false);

      if (responseData.status_code === 417) {
        printError(responseData.result, form.opportunity_type.store, tBe);
      }

      if (responseData.is_success) {
        onCancel();
        afterSave();
        toaster.success(tBe(responseData.message));
      }
    } catch (error) {
      console.error('An error occurred:', error);
    }
  }
  return (
    <Modal isOpen={isOpen}>
      <ModalHeader title={t('add_new', { entity: t('risk_type') })} onClose={() => onCancel()} />
      <form onSubmit={onSubmit} id={`${form.opportunity_type.store}`}>
        <ModalBody>
          <div className="row">
            <div className="col-12 mb-3 custom-select">
              <Label htmlFor="channel" label={t('risk_type')} isRequired />
              <AsyncSelect
                onChange={(value) => onFormChange('type_id', value)}
                className="form-control error-type_id"
                option={{ label: 'title', value: 'id' }}
                isSearchable={true}
                loadOptions={(searchValue, currentPage) => fetchAllOpportunityTypes(searchValue, currentPage, opportunityId)}
              />
            </div>
          </div>
        </ModalBody>
        <ModalFooter>
          <div className="d-flex justify-content-end gap-2">
            <Button text={t('add')} type="submit" width="sm" isLoading={isFormProcessing} />
            <Button text={t('cancel')} color="light" width="sm" onClick={() => onCancel()} />
          </div>
        </ModalFooter>
      </form>
    </Modal>
  );
}

export default AddType;
