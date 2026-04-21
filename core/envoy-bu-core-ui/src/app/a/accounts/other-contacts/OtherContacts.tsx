import React, { useState } from 'react';
import AccountsListData from './AccountsListData';
import ContactCreate from './ContactCreate';
import { Button } from '@apptimus-ui/ui-element';
import { Flexicon } from '@apptimus-ui/flexicon';
import { useTrans } from '@/helpers/services/lang/langService';

interface ComponentsProp {
  id: string;
  afterSetPrimaryContact: Function;
  afterDelete: Function;
}

const OtherContacts = ({ id, afterSetPrimaryContact, afterDelete }: ComponentsProp) => {
  const [tableVers, setTableVers] = useState(0);
  const [createContactFormKey, setCreateContactFormKey] = useState(0);
  const [createContactVisible, setCreateContactVisible] = useState(false);
  const t = useTrans('label.accounts,otr.common');

  const handleCreateContactCancel = () => {
    setCreateContactVisible(false);
  };

  const handleAfterSaveContact = () => {
    setCreateContactVisible(false);
    setTableVers((prevTableVers) => prevTableVers + 1);
    setCreateContactFormKey((prevCreateFormKey) => prevCreateFormKey + 1);
  };

  return (
    <>
      <div className="d-flex justify-content-end  gap-2">
        <Button className="d-flex align-items-center gap-1" onClick={() => setCreateContactVisible(true)}>
          <Flexicon icon="plus-circle" size={18} />
          <span className="d-none d-sm-inline">{t('add_new_contact', { entity: t('account') })}</span>
        </Button>
      </div>
      {createContactVisible && <ContactCreate key={createContactFormKey} isOpen={createContactVisible} onCancel={handleCreateContactCancel} afterSave={handleAfterSaveContact} id={id} />}
      <AccountsListData viewId={id} {...{ tableVers, afterSetPrimaryContact, afterDelete }} />
    </>
  );
};

export default OtherContacts;
