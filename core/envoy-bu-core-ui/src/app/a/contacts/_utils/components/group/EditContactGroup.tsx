import { form } from '@/constans/Form';
import { toaster } from '@/helpers/services/toaster';
import { Modal, ModalBody, ModalFooter, ModalHeader } from '@apptimus-ui/modal';
import { Button, Input, Label } from '@apptimus-ui/ui-element';
import { FormEvent, useEffect, useState } from 'react';
import { InputSkeleton } from '@/components/others/InputSkeleton';
import { useTrans } from '@/helpers/services/lang/langService';
import { Flexicon } from '@apptimus-ui/flexicon';
import EditTable2 from './EditTable2';
import EditTable1 from './EditTable1';
import { addContactsOfGroup, deleteContactsOfGroup, getOneGroup, updateGeneralContactGroup } from '../../api-service';
import { initCreateGroupFormData } from '../../model';
import { clearError, printError } from '@/helpers/handlers/validationErrorHandler';

export const EditContactGroup = ({ isOpen, editId, afterUpdate, onCancel }: { isOpen: boolean; editId: string; onCancel: Function; afterUpdate: Function }) => {
  const t = useTrans('label.contacts,otr.common');
  const tBe = useTrans('be.msg,be.error,be.attri');
  const [isFormProcessing, setIsFormProcessing] = useState(false);
  const [formData, setFormData] = useState(initCreateGroupFormData);
  const [skeleton, setSkeleton] = useState(false);
  const [tab, setTab] = useState('general');
  const [selectedContacts, setSelectedContacts] = useState([]);
  const [selectedRemovalContacts, setSelectedRemovalContacts] = useState([]);
  const [table1Vers, setTable1Vers] = useState(0);
  const [table2Vers, setTable2Vers] = useState(0);

  useEffect(() => {
    const fetchData = async () => {
      const responseData = await getOneGroup(editId);

      if (responseData?.is_success) {
        setFormData(responseData.result);
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

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    clearError(form.contact_group.update);
    setIsFormProcessing(true);

    try {
      const responseData = await updateGeneralContactGroup(editId, formData);
      setIsFormProcessing(false);

      if (responseData.status_code === 417) {
        printError(responseData.result, form.contact_group.update, tBe);
      }
      if (responseData.is_success) {
        toaster.success(tBe(responseData.message));
        setFormData(initCreateGroupFormData);
        onCancel();
        afterUpdate();
      }
    } catch (error) {
      console.error('An error occurred:', error);
    }
  }

  const reloadTables = () => {
    setSelectedRemovalContacts([]);
    setSelectedContacts([]);
    setTable1Vers((prevValue) => prevValue + 1);
    setTable2Vers((prevValue) => prevValue + 1);
    clearError(form.contacts_change.store);
    clearError(form.contacts_change.update);
  };

  const handleAddContacts = async () => {
    clearError(form.contacts_change.store);
    try {
      const responseData = await addContactsOfGroup(editId, { contacts: selectedContacts });

      if (responseData.status_code === 417) {
        printError(responseData.result, form.contacts_change.store, tBe);
      }
      if (responseData.is_success) {
        toaster.success(tBe(responseData.message));
        reloadTables();
      }
    } catch (error) {
      console.error('An error occurred:', error);
    }
  };

  const handleDeleteContacts = async () => {
    clearError(form.contacts_change.update);
    try {
      const responseData = await deleteContactsOfGroup(editId, { contacts: selectedRemovalContacts });

      if (responseData.status_code === 417) {
        printError(responseData.result, form.contacts_change.update, tBe);
      }
      if (responseData.is_success) {
        toaster.success(tBe(responseData.message));
        reloadTables();
      }
    } catch (error) {
      console.error('An error occurred:', error);
    }
  };

  return (
    <Modal isOpen={isOpen} size="lg" scrollable>
      <ModalHeader title={t('edit_a_group')} onClose={() => onCancel()} />
      <div className="il-box-tab pb-2 mx-4">
        <div className={`il-box-tab-item ${tab === 'general' ? 'active' : ''}`} onClick={() => setTab('general')}>
          {t('general')}
        </div>
        <div className={`il-box-tab-item ${tab === 'contacts' ? 'active' : ''}`} onClick={() => setTab('contacts')}>
          {t('contacts')}
        </div>
      </div>

      {tab === 'general' && (
        <form onSubmit={onSubmit} id={`${form.contact_group.update}`}>
          <ModalBody>
            <div className="row">
              <div className="col-12 col-md-6 mb-3">
                <Label htmlFor="name" label={t('group_name')} isRequired />
                {skeleton ? <InputSkeleton /> : <Input value={formData.name} onChange={(e) => onFormChange('name', e.target.value)} className="form-control error-name" name="name" />}
              </div>
              <div className="col-12 col-md-6 mb-3">
                <Label htmlFor="description" label={t('description')} />
                {skeleton ? (
                  <InputSkeleton />
                ) : (
                  <Input value={formData.description} onChange={(e) => onFormChange('description', e.target.value)} className="form-control error-description" name="description" />
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
      )}
      {tab === 'contacts' && (
        <ModalBody>
          <div className="d-flex flex-lg-row flex-column justify-content-between">
            <div id={`${form.contacts_change.store}`}>
              <Label label={t('source_contacts')} isRequired />
              <EditTable1 tableVers={table1Vers} selectedValues={(values: any) => setSelectedContacts(values)} groupId={editId} />
              <span className="error-contacts"></span>
            </div>
            <div className="p-3 d-flex align-items-center justify-content-center">
              <div className="d-flex flex-column gap-3">
                <Flexicon icon="arrow-right" variant="line" size={24} className="action-icon bg-primary text-white" onClick={handleAddContacts} />
                <Flexicon icon="arrow-left" variant="line" size={24} className="action-icon bg-primary text-white" onClick={handleDeleteContacts} />
              </div>
            </div>
            <div id={`${form.contacts_change.update}`}>
              <Label label={t('group_contacts')} isRequired />
              <EditTable2 tableVers={table2Vers} selectedValues={(values: any) => setSelectedRemovalContacts(values)} groupId={editId} />
              <span className="error-contacts"></span>
            </div>
          </div>
        </ModalBody>
      )}
    </Modal>
  );
};
