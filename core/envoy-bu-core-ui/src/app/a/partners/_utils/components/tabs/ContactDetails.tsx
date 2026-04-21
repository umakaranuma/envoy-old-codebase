import React, { useState } from 'react';
import PartnerContactList from './PartnerContactList';
import { useTrans } from '@/helpers/services/lang/langService';
import { Button } from '@apptimus-ui/ui-element';
import { Flexicon } from '@apptimus-ui/flexicon';
import AddContact from './AddContact';
import EditContact from './EditContact';
import { deletePartnerContact } from '../../api-service';
import { toaster } from '@/helpers/services/toaster';
import { ViewContact } from './ViewContact';

function ContactDetails({ partnerId, setComKey }: { partnerId: string; setComKey: Function }) {
  const t = useTrans('label.partners,otr.common');
  const tBe = useTrans('be.msg,be.error,be.attri');
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [currentEditId, setCurrentEditId] = useState('');
  const [currentViewId, setCurrentViewId] = useState('');
  const [tableVers, setTableVers] = useState(0);

  const handleOnDelete = async (deleteId: string, callback: Function, setLoader: Function, onClose: Function) => {
    setLoader(true);
    const responseData = await deletePartnerContact(partnerId, deleteId);

    setLoader(false);

    if (responseData.status_code === 403) {
      toaster.error(tBe(responseData.message));
      callback();
      onClose();
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
        <Button className="d-flex align-items-center gap-1" onClick={() => setIsCreateOpen(true)}>
          <Flexicon icon="plus-circle" size={18} />
          <span className="d-none d-sm-inline">{t('add_new_entity', { entity: t('contact') })}</span>
        </Button>
      </div>

      <PartnerContactList
        onEdit={(id: string) => setCurrentEditId(id)}
        handleOnDelete={handleOnDelete}
        setCurrentViewId={(id: string) => {
          setCurrentViewId(id);
        }}
        partnerId={partnerId}
        tableVers={tableVers}
      />
      {currentViewId !== '' && <ViewContact viewId={currentViewId} isOpen={currentViewId !== ''} onClose={() => setCurrentViewId('')} setEditId={(id: any) => setCurrentEditId(id)} />}
      {isCreateOpen && (
        <AddContact
          isOpen={isCreateOpen}
          onCancel={() => setIsCreateOpen(false)}
          afterSave={() => {
            setIsCreateOpen(false);
            setTableVers((pre) => pre + 1);
            setComKey((pre: number) => pre + 1);
          }}
        />
      )}
      {currentEditId !== '' && (
        <EditContact
          isOpen={!!currentEditId}
          onCancel={() => setCurrentEditId('')}
          afterSave={() => {
            setCurrentEditId('');
            setTableVers((pre) => pre + 1);
            setComKey((pre: number) => pre + 1);
          }}
          editId={currentEditId}
        />
      )}
    </>
  );
}

export default ContactDetails;
