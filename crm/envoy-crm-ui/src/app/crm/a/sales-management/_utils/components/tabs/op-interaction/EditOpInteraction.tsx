import { form } from '@/constans/Form';
import { Modal, ModalBody, ModalFooter, ModalHeader } from '@apptimus-ui/modal';
import { Button, Input, Label } from '@apptimus-ui/ui-element';
import { FormEvent, useEffect, useState } from 'react';
import { InputSkeleton } from '@/components/others/InputSkeleton';
import { useTrans } from '@/helpers/services/lang/langService';
import { AsyncSelect } from '@apptimus-ui/select';
import { initInteractionData } from '../../../model';
import { fetchAllChannel, fetchAllUsers } from '../../../services';
import { getOneOpInteraction, updateOpInteraction } from '../../../api-service';
import { useParams } from 'next/navigation';
import { toaster } from '@/helpers/services/toaster';

export const EditOpInteraction = ({ isOpen, editId, afterUpdate, onCancel }: { isOpen: boolean; editId: string; onCancel: Function; afterUpdate: Function }) => {
  const t = useTrans('label.sales_managements,otr.common');
  const [isFormProcessing, setIsFormProcessing] = useState(false);
  const [formData, setFormData] = useState(initInteractionData);
  const [skeleton, setSkeleton] = useState(true);
  const params = useParams();
  const opportunityId = params.managementId?.toString() || '';
  const [defalutUser, setDefalutUser] = useState({ id: '', display_name: '' });

  useEffect(() => {
    console.log('formData', formData);
  }, [formData]);

  useEffect(() => {
    const fetchData = async () => {
      const responseData = await getOneOpInteraction(opportunityId, editId);

      if (responseData?.is_success) {
        const data = responseData.result;
        setFormData(data);
        setDefalutUser({ id: data.contact_by_id, display_name: data.contact_by_display_name });
        setSkeleton(false);
        onFormChange('contact_by_id', data.contact_by_id);
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

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsFormProcessing(true);
    try {
      const responseData = await updateOpInteraction(opportunityId, formData, editId);
      setIsFormProcessing(false);

      if (responseData.is_success) {
        toaster.success(t(responseData.message));
        setFormData(initInteractionData);
        afterUpdate();
      }
    } catch (error) {
      console.error('An error occurred:', error);
    }
  }

  return (
    <Modal isOpen={isOpen}>
      <ModalHeader title={t('edit_interaction')} onClose={() => onCancel()} />
      <form onSubmit={onSubmit} id={`${form.opportunity_interaction.update}`}>
        <ModalBody>
          <div className="row">
            <div className="col-12 col-md-6 mb-3">
              <Label htmlFor="date" label={t('date')} isRequired />
              {skeleton ? <InputSkeleton /> : <Input value={formData.date} onChange={(e) => onFormChange('date', e.target.value)} className="form-control error-date" name="date" type="date" />}
            </div>
            <div className="col-12 col-md-6 mb-3 custom-select">
              <Label htmlFor="contacts" label={t('contacts')} isRequired />
              {skeleton ? (
                <InputSkeleton />
              ) : (
                <AsyncSelect
                  onChange={(value) => onFormChange('contact_by_id', value)}
                  className="form-control error-contact_by_id"
                  isSearchable={true}
                  loadOptions={(searchValue, currentPage) => fetchAllUsers(searchValue, currentPage)}
                  defaultValue={defalutUser}
                  option={{
                    label: 'display_name',
                    value: 'id',
                  }}
                />
              )}
            </div>
            <div className="col-12 col-md-6 mb-3 custom-select">
              <Label htmlFor="channels" label={t('channels')} isRequired />
              {skeleton ? (
                <InputSkeleton />
              ) : (
                <AsyncSelect
                  onChange={(_value: any, data: any) => {
                    onFormChange('channel_id', data.id);
                    onFormChange('channel_name', data.name);
                  }}
                  className="form-control error-channel_id"
                  option={{
                    label: 'name',
                    value: 'id',
                  }}
                  defaultValue={{
                    id: formData.channel_id,
                    name: formData.channel_name,
                  }}
                  isSearchable={true}
                  loadOptions={(searchValue, currentPage) => fetchAllChannel(searchValue, currentPage)}
                />
              )}
            </div>
            <div className="col-12 col-md-6 mb-3">
              <Label label={t('remarks')} />
              {skeleton ? (
                <InputSkeleton />
              ) : (
                <Input type="textarea" value={formData.notes} onChange={(e) => onFormChange('notes', e.target.value)} className="form-control error-notes" name="notes" />
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
