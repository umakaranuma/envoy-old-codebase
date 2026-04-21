'use client';
import { form } from '@/constans/Form';
import { Modal, ModalBody, ModalFooter, ModalHeader } from '@apptimus-ui/modal';
import { Button, Input, Label } from '@apptimus-ui/ui-element';
import React, { useState } from 'react';
import { useTrans } from '@/helpers/services/lang/langService';
import { clearError } from '@/helpers/handlers/validationErrorHandler';
import { initNode } from '../model';
import { AsyncSelect } from '@apptimus-ui/select';
import { fetchAllCustomers } from '@/app/a/accounts/_utils/services';
import ReactPhoneInput from '@/components/others/page-related/ReactPhoneInput';

export function CreateNode({ isOpen, onCancel, afterSave }: { isOpen: boolean; onCancel: Function; afterSave: Function }) {
  const t = useTrans('label.org_nodes,otr.common');
  // const tBe = useTrans('be.msg,be.error,be.attri');
  const [isFormProcessing, setIsFormProcessing] = useState(false);
  const [formData, setFormData] = useState(initNode);
  // const [resource, setResource] = useState<File | null>();
  console.log(afterSave);

  const onFormChange = (name: string, value: any) => {
    setFormData((prevFormData) => ({ ...prevFormData, [name]: value }));
  };

  async function onSubmit() {
    clearError(form.partner.store);
    setIsFormProcessing(true);

    // try {
    //   // const docData = await handleFileUpload();
    //   const responseData = await createPartner(formData);
    //   setIsFormProcessing(false);

    //   if (responseData.status_code === 417) {
    //     printError(responseData.result, form.partner.store, tBe);
    //   }

    //   if (responseData.is_success) {
    //     afterSave();
    //     setFormData(initPartner);
    //     toaster.success(tBe(responseData.message));
    //   }
    // } catch (error) {
    //   console.error('An error occurred:', error);
    // }
  }

  return (
    <Modal isOpen={isOpen} scrollable>
      <ModalHeader title={t('add_new_entity', { entity: t('organizational_node') })} onClose={() => onCancel()} />
      <ModalBody>
        <div id={`${form.org_node.store}`}>
          <div className="row">
            <div className="col-12 col-md-6 mb-3 custom-select">
              <Label label={t('level_name')} isRequired />
              <AsyncSelect
                onChange={(value) => onFormChange('level_name', value)}
                className="form-control error-child_id"
                option={{ label: 'name', value: 'id' }}
                isSearchable={true}
                loadOptions={(searchValue, currentPage) => fetchAllCustomers(searchValue, currentPage)}
              />
            </div>
            <div className="col-12 col-md-6 mb-3 custom-select">
              <Label label={t('parent_node')} isRequired />
              <AsyncSelect
                onChange={(value) => onFormChange('parent_node_id', value)}
                className="form-control error-parent_node_id"
                option={{ label: 'name', value: 'id' }}
                isSearchable={true}
                loadOptions={(searchValue, currentPage) => fetchAllCustomers(searchValue, currentPage)}
              />
            </div>
            <div className="col-12 col-md-6 mb-3">
              <Input label={t('code')} isRequired value={formData.code} onChange={(e) => onFormChange('code', e.target.value)} className="form-control error-code" name="code" />
            </div>
            <div className="col-12 col-md-6 mb-3">
              <Input
                label={t('node_name')}
                isRequired
                value={formData.node_name}
                onChange={(e) => onFormChange('node_name', e.target.value)}
                className="form-control error-node_name"
                name="node_name"
              />
            </div>
            <div className="col-12 col-md-6 mb-3">
              <Input
                label={t('branch_name_code')}
                value={formData.branch_name_code}
                onChange={(e) => onFormChange('branch_name_code', e.target.value)}
                className="form-control error-branch_name_code"
                name="branch_name_code"
              />
            </div>
            <div className="col-12 col-md-6 mb-3">
              <Input
                label={t('physical_address')}
                value={formData.physical_address}
                onChange={(e) => onFormChange('physical_address', e.target.value)}
                className="form-control error-physical_address"
                name="physical_address"
              />
            </div>
            <div className="col-12 col-md-6 mb-3">
              <Input
                label={t('primary_email')}
                value={formData.primary_email}
                onChange={(e) => onFormChange('primary_email', e.target.value)}
                className="form-control error-primary_email"
                name="primary_email"
              />
            </div>
            <div className="col-12 col-md-6 mb-3">
              <Label label={t('contact_number')} />
              {/* <PhoneInput
                country={'lk'}
                enableAreaCodes={true}
                value={formData.contact_number}
                inputStyle={{ height: '40px', width: '100%' }}
                containerStyle={{ height: '40px', width: '100%' }}
                onChange={(phone) => onFormChange('contact_number', phone)}
                inputClass="form-control error-contact_number"
                countryCodeEditable={false}
              /> */}
              <ReactPhoneInput
                value={formData.contact_number}
                onChange={(phone) => onFormChange('contact_number', phone)}
                defaultCountryCode={'lk'}
                enableAreaCodes={false}
                className="form-control error-contact_number"
              />
            </div>
          </div>
        </div>
      </ModalBody>
      <ModalFooter>
        <div className="d-flex justify-content-end gap-2">
          <Button text={t('create')} onClick={onSubmit} width="sm" isLoading={isFormProcessing} />
          <Button text={t('cancel')} color="light" width="sm" onClick={() => onCancel()} />
        </div>
      </ModalFooter>
    </Modal>
  );
}
export default CreateNode;
