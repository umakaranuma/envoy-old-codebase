'use client';

import { Button } from '@apptimus-ui/ui-element';
import { useEffect, useState } from 'react';
import { Flexicon } from '@apptimus-ui/flexicon';
import { useTrans } from '@/helpers/services/lang/langService';
import PageHeading from '@/components/others/PageHeading';
import ContactList from './contact/ContactList';
import GroupIndexTable from './group/GroupIndexTable';
import CreateContact from './contact/ContactCreate';
import { ContactEdit } from './contact/ContactEdit';
import CreateContactGroup from './group/CreateContactGroup';
import { EditContactGroup } from './group/EditContactGroup';
import { toaster } from '@/helpers/services/toaster';
import { deleteContactGroup, deleteContacts } from '../api-service';
import { useRouter, useSearchParams } from 'next/navigation';
import MergeContacts from './contact/MergeContacts';

function Contacts() {
  const t = useTrans('label.contacts,otr.common');
  const tBe = useTrans('be.msg,be.error,be.attri');
  const router = useRouter();
  const searchParams = useSearchParams();
  const [tableVers, setTableVers] = useState(0);
  const [createFormKey, setCreateFormKey] = useState(0);
  const [currentEditId, setCurrentEditId] = useState('');
  const [createContactVisible, setCreateContactVisible] = useState(false);
  const [selectedMergeableContacts, setSelectedMergeableContacts] = useState([]);
  const [isMergeVisible, setIsMergeVisible] = useState(false);
  const [createGroupVisible, setCreateGroupVisible] = useState(false);
  const [currentGroupEditId, setCurrentGroupEditId] = useState('');
  const [createGroupKey, setCreateGroupKey] = useState(0);
  const [groupTableVers, setGroupTableVers] = useState(0);
  const [tab, setTab] = useState('all-contacts');

  useEffect(() => {
    const tab = searchParams.get('t') || 'all-contacts';
    setTab(tab);
  }, [searchParams]);

  const toggleTableTab = (activeTab: string) => {
    setSelectedMergeableContacts([]);
    setTab(activeTab);
    router.push(`/a/contacts?t=${activeTab}`);
  };

  const handleCreateFormOnCancel = () => {
    setCreateContactVisible(false);
    setCreateFormKey((prevCreateFormKey) => prevCreateFormKey + 1);
  };

  const handleAfterSave = () => {
    setTableVers((prevTableVers) => prevTableVers + 1);
    setCreateFormKey((prevCreateFormKey) => prevCreateFormKey + 1);
  };

  const handleAfterUpdate = () => {
    setCurrentEditId('');
    setTableVers((prevTableVers) => prevTableVers + 1);
  };

  const onReloadGroupTable = () => {
    setGroupTableVers((prevKey) => prevKey + 1);
  };

  const onReloadAllContactTable = () => {
    setTableVers((prevKey) => prevKey + 1);
  };

  const handleOnDelete = async (deleteId: string, callback: Function, setLoader: Function, onClose: Function) => {
    setLoader(true);
    const responseData = await deleteContactGroup(deleteId);
    setLoader(false);

    if (responseData.is_success) {
      toaster.success(tBe(responseData.message));
      callback();
      onClose();
      onReloadGroupTable();
    }
  };

  const handleAllContactOnDelete = async (deleteId: string, callback: Function, setLoader: Function, onClose: Function) => {
    setLoader(true);
    const responseData = await deleteContacts(deleteId);
    setLoader(false);

    if (responseData.is_success) {
      toaster.success(tBe(responseData.message));
      callback();
      onClose();
      onReloadAllContactTable();
    } else {
      toaster.error(tBe(responseData.message));
    }
  };

  return (
    <>
      <div className="page-header-breadcrumb custom-page-header">
        <PageHeading title={t('contacts_management')} icon="core" />
        {tab === 'all-contacts' && (
          <div className="d-flex gap-4 align-items-center">
            {selectedMergeableContacts.length > 1 && (
              <Button className="d-flex align-items-center gap-1" onClick={() => setIsMergeVisible(true)}>
                <span className="d-none d-sm-inline">{t('merge_contacts')}</span>
              </Button>
            )}

            <Button className="d-flex align-items-center gap-1" onClick={() => setCreateContactVisible(true)}>
              <Flexicon icon="plus-circle" size={18} />
              <span className="d-none d-sm-inline">{t('add_new_contact')}</span>
            </Button>
          </div>
        )}
        {tab === 'contact-groups' && (
          <div className="d-flex gap-4 align-items-center">
            <Button className="d-flex align-items-center gap-1" onClick={() => setCreateGroupVisible(true)}>
              <Flexicon icon="plus-circle" size={18} />
              <span className="d-none d-sm-inline">{t('add_new_group')}</span>
            </Button>
          </div>
        )}
      </div>
      <div className="panel mt-4">
        <div className="il-box-tab pb-2">
          <div className={`il-box-tab-item ${tab === 'all-contacts' ? 'active' : ''}`} onClick={() => toggleTableTab('all-contacts')}>
            {t('all_contacts')}
          </div>
          <div className={`il-box-tab-item ${tab === 'contact-groups' ? 'active' : ''}`} onClick={() => toggleTableTab('contact-groups')}>
            {t('contact_groups')}
          </div>
        </div>
        {tab === 'all-contacts' && (
          <ContactList
            tableVers={tableVers}
            onView={(id: string) => router.push(`/a/contacts/${id}`)}
            onEdit={(id: string) => setCurrentEditId(id)}
            handleOnDelete={handleAllContactOnDelete}
            selectedContacts={(values: any) => setSelectedMergeableContacts(values)}
          />
        )}

        {tab === 'contact-groups' && <GroupIndexTable tableVers={groupTableVers} onEdit={(id: string) => setCurrentGroupEditId(id)} handleOnDelete={handleOnDelete} />}
      </div>
      <CreateContact key={createFormKey} isOpen={createContactVisible} onCancel={handleCreateFormOnCancel} afterSave={handleAfterSave} />
      {currentEditId !== '' && <ContactEdit editId={currentEditId} isOpen={currentEditId !== ''} onCancel={() => setCurrentEditId('')} afterUpdate={handleAfterUpdate} />}
      {isMergeVisible && <MergeContacts selectedContacts={selectedMergeableContacts} isOpen={isMergeVisible} onCancel={() => setIsMergeVisible(false)} afterSave={onReloadAllContactTable} />}

      {createGroupVisible && (
        <CreateContactGroup
          isOpen={createGroupVisible}
          onCancel={() => {
            setCreateGroupVisible(false), setCreateGroupKey((prevKey) => prevKey + 1);
          }}
          key={`createKey-${createGroupKey}`}
          afterSave={onReloadGroupTable}
        />
      )}

      {currentGroupEditId !== '' && <EditContactGroup editId={currentGroupEditId} isOpen={currentGroupEditId !== ''} onCancel={() => setCurrentGroupEditId('')} afterUpdate={onReloadGroupTable} />}
    </>
  );
}

export default Contacts;
