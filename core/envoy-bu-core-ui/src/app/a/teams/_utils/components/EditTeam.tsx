'use client';
import { form } from '@/constans/Form';
import { Modal, ModalBody, ModalFooter, ModalHeader } from '@apptimus-ui/modal';
import { Button, Input, Label } from '@apptimus-ui/ui-element';
import React, { useEffect, useState } from 'react';
import { toaster } from '@/helpers/services/toaster';
import { useTrans } from '@/helpers/services/lang/langService';
import { clearError, printError } from '@/helpers/handlers/validationErrorHandler';
import { fileRemover } from '@/constans/storageService';
import { initTeamFormData, ITeam } from '../model';
import { InputSkeleton } from '@/components/others/InputSkeleton';
import { AsyncSelect } from '@apptimus-ui/select';
import { fetchAllNativeProducts } from '../service';
import { getAllUserDrpdown } from '@/app/a/users/_utils/service';
import { getOneTeam, updateSalesTeam } from '../api-service';

export function EditTeam({ isOpen, onCancel, afterEdit, editId }: { isOpen: boolean; onCancel: Function; afterEdit: Function; editId: string }) {
  const t = useTrans('label.teams,otr.common');
  const tBe = useTrans('be.msg,be.error,be.attri');
  const [isFormProcessing, setIsFormProcessing] = useState(false);
  const [data, setData] = useState({} as ITeam);
  const [formData, setFormData] = useState(initTeamFormData);
  const [skeleton, setSkeleton] = useState(false);
  const [deletableResource, setDeletableResource] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      const responseData = await getOneTeam(editId);
      if (responseData?.is_success) {
        const data = responseData.result;
        setData(data);
        onFormChange('name', data.name);
        onFormChange('description', data.description);
        onFormChange('manager_id', data.manager_id);
        onFormChange('manager_name', data.manager_name);
        onFormChange(
          'product_ids',
          data.products?.map((product: any) => product.id),
        );
        onFormChange(
          'user_ids',
          data.sales_agents?.map((agent: any) => agent.id),
        );
        setSkeleton(false);
      }
    };

    if (editId) {
      setSkeleton(true);
      fetchData();
    }
  }, [editId]);

  const onFormChange = (name: string, value: any) => {
    setFormData((prevFormData) => ({ ...prevFormData, [name]: value }));
  };

  async function onSubmit() {
    clearError(form.partner.update);
    setIsFormProcessing(true);

    try {
      const responseData = await updateSalesTeam(editId, formData);
      setIsFormProcessing(false);

      if (responseData.status_code === 417) {
        printError(responseData.result, form.partner.update, tBe);
      }

      if (responseData.is_success) {
        if (deletableResource) {
          const deleteResponse = await fileRemover(deletableResource);
          if (deleteResponse.success) {
            setDeletableResource(null);
          }
        }
        onCancel();
        afterEdit();
        setFormData(initTeamFormData);
        toaster.success(tBe(responseData.message));
      }
    } catch (error) {
      setIsFormProcessing(false);
      console.error('An error occurred:', error);
    }
  }

  return (
    <Modal isOpen={isOpen}>
      <ModalHeader title={t('edit_entity', { entity: t('team') })} onClose={() => onCancel()} />
      <ModalBody>
        <div id={`${form.partner.update}`}>
          <div className="row">
            <div className="col-12 col-md-6 mb-3">
              <Label label={t('team_name')} isRequired />
              {skeleton ? <InputSkeleton /> : <Input value={formData.name} onChange={(e) => onFormChange('name', e.target.value)} className="form-control error-name" name="name" />}
            </div>
            <div className="col-12 col-md-6 mb-3 custom-select">
              <Label label={t('native_product')} />
              {skeleton ? (
                <InputSkeleton />
              ) : (
                <AsyncSelect
                  onChange={(value) => onFormChange('product_ids', value)}
                  className="form-control error-product_ids"
                  option={{ label: 'name', value: 'id' }}
                  isSearchable={true}
                  loadOptions={(searchValue, currentPage) => fetchAllNativeProducts(searchValue, currentPage)}
                  multiple
                  defaultValue={data.products ? data.products : undefined}
                />
              )}
            </div>
            <div className="col-12 col-md-6 mb-3 custom-select">
              <Label isRequired label={t('team_lead')} />
              {skeleton ? (
                <InputSkeleton />
              ) : (
                <AsyncSelect
                  onChange={(value, data) => {
                    onFormChange('manager_id', value);
                    onFormChange('manager_name', data?.display_name);
                  }}
                  className="form-control error-manager_id"
                  option={{ label: 'display_name', value: 'id' }}
                  isSearchable={true}
                  loadOptions={(searchValue, currentPage) => getAllUserDrpdown(searchValue, currentPage)}
                  defaultValue={data.manager_id ? { display_name: formData.manager_name, id: formData.manager_id } : undefined}
                />
              )}
            </div>
            <div className="col-12 col-md-6 mb-3 custom-select">
              <Label isRequired label={t('team_member')} />
              {skeleton ? (
                <InputSkeleton />
              ) : (
                <AsyncSelect
                  onChange={(value) => onFormChange('user_ids', value)}
                  className="form-control error-user_ids"
                  option={{ label: 'display_name', value: 'id' }}
                  isSearchable={true}
                  loadOptions={(searchValue, currentPage) => getAllUserDrpdown(searchValue, currentPage)}
                  multiple
                  defaultValue={data.sales_agents ? data.sales_agents : undefined}
                />
              )}
            </div>
            <div className="col-12 mb-3">
              <Label label={t('description')} />
              {skeleton ? (
                <InputSkeleton />
              ) : (
                <Input
                  type="textarea"
                  rows={3}
                  value={formData.description}
                  onChange={(e) => onFormChange('description', e.target.value)}
                  className="form-control error-description"
                  name="description"
                />
              )}
            </div>
          </div>
        </div>
      </ModalBody>
      <ModalFooter>
        <div className="d-flex justify-content-end gap-2">
          <Button text={t('update')} onClick={onSubmit} width="sm" isLoading={isFormProcessing} />
          <Button text={t('cancel')} color="light" width="sm" onClick={() => onCancel()} />
        </div>
      </ModalFooter>
    </Modal>
  );
}
