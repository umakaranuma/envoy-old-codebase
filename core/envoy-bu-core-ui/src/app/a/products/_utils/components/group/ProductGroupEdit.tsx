import { form } from '@/constans/Form';
import { toaster } from '@/helpers/services/toaster';
import { Modal, ModalBody, ModalFooter, ModalHeader } from '@apptimus-ui/modal';
import { Button, Input, Label } from '@apptimus-ui/ui-element';
import { FormEvent, useEffect, useState } from 'react';
import { InputSkeleton } from '@/components/others/InputSkeleton';
import { useTrans } from '@/helpers/services/lang/langService';
import { clearError, printError } from '@/helpers/handlers/validationErrorHandler';
import { initProductGroup } from '../../modal';
import { getOneProductGroups, updateProductGroups } from '../../api-service';
import { AsyncSelect } from '@apptimus-ui/select';
import { fetchallNativeProducts } from '../../services';

export const ProductGroupEdit = ({ isOpen, editId, afterUpdate, onCancel }: { isOpen: boolean; editId: string; onCancel: Function; afterUpdate: Function }) => {
  const t = useTrans('label.products,otr.common');
  const tBe = useTrans('be.msg,be.error,be.attri');
  const [isFormProcessing, setIsFormProcessing] = useState(false);
  const [formData, setFormData] = useState(initProductGroup);
  const [skeleton, setSkeleton] = useState(true);
  const [defaultProducts, setDefaultProducts] = useState<any[]>([]);
  const [defaultTeams, setDefaultTeams] = useState<any[]>([]);

  useEffect(() => {
    const fetchData = async () => {
      setSkeleton(true);
      const responseData = await getOneProductGroups(editId);
      if (responseData?.is_success) {
        const data = responseData.result[0];
        onFormChange('name', responseData.result[0].name);
        setDefaultProducts(data.native_products || []);
        setDefaultTeams(data.teams || []);
      }
      setSkeleton(false);
    };

    if (editId) {
      fetchData();
    }
  }, [editId]);

  useEffect(() => {
    const teamIds = defaultTeams.map((team) => team.id.toString());
    onFormChange('team_ids', teamIds);
    const productIds = defaultProducts.map((product) => product.id.toString());
    onFormChange('product_ids', productIds);
  }, [defaultTeams, defaultProducts]);

  useEffect(() => {
    console.log('formData', formData);
  }, [formData]);

  const onFormChange = (name: string, value: any) => {
    setFormData((prevFormData) => ({ ...prevFormData, [name]: value }));
  };

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    clearError(form.product.update);
    setIsFormProcessing(true);

    try {
      const responseData = await updateProductGroups(editId, formData);
      setIsFormProcessing(false);

      if (responseData.status_code === 417) {
        printError(responseData.result, form.product.update, tBe);
      }

      if (responseData.is_success) {
        toaster.success(tBe(responseData.message));
        setFormData(initProductGroup);
        afterUpdate();
      }
    } catch (error) {
      console.error('An error occurred:', error);
    }
  }

  return (
    <Modal isOpen={isOpen} onBackdrop={() => onCancel()}>
      <ModalHeader title={t('edit_entity', { entity: t('product_group') })} onClose={() => onCancel()} />
      <form onSubmit={onSubmit} id={`${form.product.update}`}>
        <ModalBody>
          <div className="row">
            <div className="col-12 mb-3">
              <Label htmlFor="group_name" label={t('group_name')} isRequired />
              {skeleton ? (
                <InputSkeleton />
              ) : (
                <Input
                  type="text"
                  name="name"
                  value={formData?.name}
                  onChange={(e) => {
                    onFormChange('name', e.target.value);
                  }}
                  className="form-control error-name"
                />
              )}
            </div>
            <div className="col-12 mb-3">
              <Label htmlFor="products" label={t('products')} />
              {skeleton ? (
                <InputSkeleton />
              ) : (
                <div className="custom-select">
                  <AsyncSelect
                    defaultValue={defaultProducts}
                    onChange={(value) => {
                      onFormChange('product_ids', value);
                    }}
                    className="form-control  error-product_ids"
                    option={{ label: 'name', value: 'id' }}
                    isSearchable={true}
                    loadOptions={fetchallNativeProducts}
                    multiple
                  />
                </div>
              )}
            </div>
            <div className="col-12 mb-3">
              <Label htmlFor="teams" label={t('teams')} />
              {skeleton ? (
                <InputSkeleton />
              ) : (
                <div className="custom-select">
                  <AsyncSelect
                    defaultValue={defaultTeams}
                    onChange={(value) => {
                      onFormChange('team_ids', value);
                    }}
                    className="form-control  error-team_ids"
                    option={{ label: 'name', value: 'id' }}
                    isSearchable={true}
                    loadOptions={fetchallNativeProducts}
                    multiple
                  />
                </div>
              )}
            </div>
          </div>
        </ModalBody>
        <ModalFooter>
          <div className="d-flex justify-content-end gap-2">
            <Button text={t('update')} type="submit" width="sm" isLoading={isFormProcessing} disabled={skeleton} />
            <Button text={t('cancel')} color="light" width="sm" onClick={() => onCancel()} />
          </div>
        </ModalFooter>
      </form>
    </Modal>
  );
};
