import { useTrans } from '@/helpers/services/lang/langService';
import { Flexicon } from '@apptimus-ui/flexicon';
import { Button, Label } from '@apptimus-ui/ui-element';
import React, { FormEvent, useState } from 'react';
import TeamsList from './TeamsList';
import { Modal, ModalBody, ModalFooter, ModalHeader } from '@apptimus-ui/modal';
import { AsyncSelect } from '@apptimus-ui/select';
import { fetchAllTeamsDropdown } from '../../../services';
import { clearError, printError } from '@/helpers/handlers/validationErrorHandler';
import { toaster } from '@/helpers/services/toaster';
import { form } from '@/constans/Form';
import { createProductTeam, deleteProductTeam } from '../../../api-service';

function Teams({ viewId, isEdit = false }: { viewId: string; isEdit?: boolean }) {
  const t = useTrans('label.products,otr.common');
  const tBe = useTrans('be.msg,be.error,be.attri');
  const [isCreateTeamOpen, setIsCreateTeamOpen] = useState(false);
  const [isFormProcessing, setIsFormProcessing] = useState(false);
  const [tableVers, setTableVers] = useState(0);
  const [formData, setFormData] = useState({ team_id: '' });

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    clearError(form.product.store);
    setIsFormProcessing(true);
    try {
      const response = await createProductTeam(viewId, formData);
      if (response?.status_code === 417) {
        printError(response?.result, form.product.store, tBe);
      } else if (response?.is_success) {
        setTableVers((prevTableVers) => prevTableVers + 1);
        setIsCreateTeamOpen(false);
        setFormData({ team_id: '' });
        toaster.success(tBe(response?.message || ''));
      }
    } catch (error) {
      console.error('Submit error:', error);
    } finally {
      setIsFormProcessing(false);
    }
  }

  const handleOnDelete = async (deleteId: string, callback: Function, setLoader: Function, onClose: Function) => {
    setLoader(true);
    const responseData = await deleteProductTeam(viewId, deleteId);
    setLoader(false);

    if (responseData.status_code === 409) {
      toaster.error(tBe(responseData.message));
    }

    if (responseData.is_success) {
      toaster.success(tBe(responseData.message));
      callback();
      onClose();
      setTableVers((prevTableVers) => prevTableVers + 1);
    }
  };
  return (
    <>
      <div className="d-flex justify-content-end">
        {isEdit && (
          <Button className="d-flex align-items-center gap-1" onClick={() => setIsCreateTeamOpen(true)}>
            <Flexicon icon="plus-circle" size={18} />
            <span className="d-none d-sm-inline">{t('add_new_team')}</span>
          </Button>
        )}
      </div>
      <TeamsList viewId={viewId} tableVers={tableVers} handleOnDelete={handleOnDelete} isEdit={isEdit} />
      {isCreateTeamOpen && (
        <Modal isOpen={isCreateTeamOpen} onBackdrop={() => setIsCreateTeamOpen(false)}>
          <ModalHeader title={t('add_new_team', { entity: t('product') })} onClose={() => setIsCreateTeamOpen(false)} />
          <form onSubmit={onSubmit} id={`${form.product.store}`}>
            <ModalBody>
              <div className="col-12 col-md-12 mb-3 custom-select">
                <Label htmlFor="team" label={t('teams')} isRequired />
                <AsyncSelect
                  onChange={(_, data) => setFormData({ team_id: data?.id ?? '' })}
                  className="form-control error-team_id"
                  option={{ label: 'name', value: 'id' }}
                  isSearchable={true}
                  loadOptions={(searchValue, currentPage) => fetchAllTeamsDropdown(searchValue, currentPage)}
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

export default Teams;
