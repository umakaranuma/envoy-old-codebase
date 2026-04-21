import { useTrans } from '@/helpers/services/lang/langService';
import { Modal, ModalBody, ModalFooter, ModalHeader } from '@apptimus-ui/modal';
import { AsyncSelect } from '@apptimus-ui/select';
import { Button, Label } from '@apptimus-ui/ui-element';
import React, { useState } from 'react';
import { form } from '@/constans/Form';
import { clearError, printError } from '@/helpers/handlers/validationErrorHandler';
import { useParams, useRouter } from 'next/navigation';
import { fetchAllRiskTypes } from '../../../my-policies/_utils/service';

function SelectRiskType({ isOpen, onCancel }: { isOpen: boolean; onCancel: Function }) {
  const t = useTrans('label.my_quotation,label.my_policy,otr.common,be.msg');
  const tBe = useTrans('be.msg,be.error,be.attri');
  const [isFormProcessing, setIsFormProcessing] = useState(false);
  const [formData, setFormData] = useState({ risk_type: '' });
  const router = useRouter();
  const params = useParams();
  const appId = params.appId as string;

  const onFormChange = (name: string, value: any) => {
    setFormData((prevFormData) => ({ ...prevFormData, [name]: value }));
  };

  async function onSubmit() {
    clearError(form.select_risk_type.store);
    const error: { [key: string]: Array<{ error_type: string; tokens: { _attribute: string } }> } = {};
    if (!formData.risk_type) {
      error['risk_type'] = [
        {
          error_type: 'required',
          tokens: {
            _attribute: 'risk_type',
          },
        },
      ];
    }

    if (Object.keys(error).length > 0) {
      printError(error, form.select_risk_type.store, tBe);
    } else {
      setIsFormProcessing(true);
      router.push(`/${appId}/a/my-quotations/create?rId=${formData.risk_type}`);
    }
  }

  return (
    <Modal isOpen={isOpen}>
      <ModalHeader title={t('request_quotation')} onClose={() => onCancel()} />
      <ModalBody>
        <div className="row" id={`${form.select_risk_type.store}`}>
          <div className="col-12 mb-3 custom-select">
            <Label label={t('risk_type')} isRequired />
            <AsyncSelect
              onChange={(value) => onFormChange('risk_type', value)}
              className="form-control error-risk_type"
              option={{ label: 'title', value: 'id' }}
              isSearchable={false}
              loadOptions={(searchValue: any, currentPage: any) => fetchAllRiskTypes(searchValue, currentPage)}
            />
          </div>
        </div>
      </ModalBody>
      <ModalFooter>
        <div className="d-flex justify-content-end gap-2">
          <Button text={t('cancel')} color="light" width="sm" onClick={() => onCancel()} />
          <Button text={t('continue')} type="submit" width="sm" isLoading={isFormProcessing} onClick={onSubmit} />
        </div>
      </ModalFooter>
    </Modal>
  );
}

export default SelectRiskType;
