import { useTrans } from '@/helpers/services/lang/langService';
import { Flexicon } from '@apptimus-ui/flexicon';
import { Button, Label } from '@apptimus-ui/ui-element';
import React, { FormEvent, useState } from 'react';
import { Modal, ModalBody, ModalFooter, ModalHeader } from '@apptimus-ui/modal';
import { AsyncSelect } from '@apptimus-ui/select';
import { fetchAllInsurerProducts } from '../../../services';
import { clearError, printError } from '@/helpers/handlers/validationErrorHandler';
import { toaster } from '@/helpers/services/toaster';
import { form } from '@/constans/Form';
import { deleteInsurerProductFromNative, updateNativeProductInsurerProducts } from '../../../api-service';
import InsureProductList from '../InsureProductList';

function InsureProduct({ viewId, isEdit = false }: { viewId: string; isEdit?: boolean }) {
  const t = useTrans('label.products,otr.common');
  const tBe = useTrans('be.msg,be.error,be.attri');
  const [isCreateTeamOpen, setIsCreateTeamOpen] = useState(false);
  const [isFormProcessing, setIsFormProcessing] = useState(false);
  const [tableVers, setTableVers] = useState(0);
  const [formData, setFormData] = useState([] as string[]);
  const [tableColumnVers, setTableColumnVers] = useState(0);

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    clearError(form.product.store);
    setIsFormProcessing(true);
    try {
      const apiData = { insurer_product_ids: formData };
      const response = await updateNativeProductInsurerProducts(viewId, apiData);
      if (response?.status_code === 417) {
        printError(response?.result, form.product.store, tBe);
      } else if (response?.is_success) {
        setTableVers((prevTableVers) => prevTableVers + 1);
        setIsCreateTeamOpen(false);
        setFormData([]);
        toaster.success(tBe(response?.message || ''));
      }
    } catch (error) {
      console.error('Submit error:', error);
    } finally {
      setIsFormProcessing(false);
    }
  }
  const handleDeleteInsurerProduct = async (deleteId: string, callback: Function, setLoader: Function, onClose: Function) => {
    try {
      setLoader(true);
      const response = await deleteInsurerProductFromNative(viewId, deleteId);
      setLoader(false);

      if (response.is_success) {
        toaster.success(t('be.msg.delete_success'));
        setTableColumnVers((prev) => prev + 1);
        callback();
        onClose();
      } else {
        toaster.error(t('be.error.delete_failed'));
      }
    } catch (error) {
      setLoader(false);
      toaster.error(t('be.error.delete_failed'));
    }
  };

  return (
    <>
      <div className="d-flex justify-content-end">
        {isEdit && (
          <Button className="d-flex align-items-center gap-1" onClick={() => setIsCreateTeamOpen(true)}>
            <Flexicon icon="plus-circle" size={18} />
            <span className="d-none d-sm-inline">{t('add_new_insurer_product')}</span>
          </Button>
        )}
      </div>
      <InsureProductList
        nativeProductId={viewId}
        isEdit={isEdit}
        tableVers={tableVers}
        handleOnDelete={handleDeleteInsurerProduct}
        tableColumnVers={tableColumnVers}
        setTableColumnVers={setTableColumnVers}
      />
      {isCreateTeamOpen && (
        <Modal isOpen={isCreateTeamOpen} onBackdrop={() => setIsCreateTeamOpen(false)}>
          <ModalHeader title={t('add_new_insurer_product', { entity: t('product') })} onClose={() => setIsCreateTeamOpen(false)} />
          <form onSubmit={onSubmit} id={`${form.product.store}`}>
            <ModalBody>
              <div className="col-12 col-md-12 mb-3 custom-select">
                <Label htmlFor="insurer_products" label={t('insurer_products')} isRequired />
                <AsyncSelect
                  onChange={(value) => setFormData(value)}
                  className="form-control error-insurer_product_ids"
                  option={{ label: 'name', value: 'id' }}
                  isSearchable={true}
                  multiple
                  loadOptions={(searchValue, currentPage) => fetchAllInsurerProducts(searchValue, currentPage)}
                />
              </div>
            </ModalBody>
            <ModalFooter>
              <div className="d-flex justify-content-end gap-2">
                <Button text={t('add')} type="submit" width="sm" isLoading={isFormProcessing} />
                <Button text={t('cancel')} color="light" width="sm" onClick={() => setIsCreateTeamOpen(false)} />
              </div>
            </ModalFooter>
          </form>
        </Modal>
      )}
    </>
  );
}

export default InsureProduct;
