'use client';
import { Button } from '@apptimus-ui/ui-element';
import { useState } from 'react';
import { Flexicon } from '@apptimus-ui/flexicon';
import { useTrans } from '@/helpers/services/lang/langService';
import AccountsList from './AccountsList';
import PageHeading from '@/components/others/PageHeading';
import AccountsCreate from './AccountsCreate';
import { AccountsEdit } from './AccountsEdit';
import { deleteCustomers } from '../api-service';
import { toaster } from '@/helpers/services/toaster';
import { AccountConfig } from './AccountConfig';

function Accounts() {
  const [tableVers, setTableVers] = useState(0);
  const [createFormKey, setCreateFormKey] = useState(0);
  const [createFormVisible, setCreateFormVisible] = useState(false);
  const [currentEditId, setCurrentEditId] = useState('');
  const [currentConfigId, setCurrentConfigId] = useState('');
  const [currentConfigData, setCurrentConfigData] = useState({});

  const handleCreateFormOnCancel = () => {
    setCreateFormVisible(false);
    setCreateFormKey((prevCreateFormKey) => prevCreateFormKey + 1);
  };

  const handleAfterSave = () => {
    setCreateFormVisible(false);
    setTableVers((prevTableVers) => prevTableVers + 1);
    setCreateFormKey((prevCreateFormKey) => prevCreateFormKey + 1);
  };

  const handleAfterUpdate = () => {
    setCurrentEditId('');
    setTableVers((prevTableVers) => prevTableVers + 1);
  };
  const handleAfterConfig = () => {
    setCurrentConfigId('');
    setTableVers((prevTableVers) => prevTableVers + 1);
    setCurrentConfigData({});
  };

  const t = useTrans('label.accounts,otr.common,be.msg');
  const tBe = useTrans('be.msg,be.error,be.attri');

  const handleOnDelete = async (deleteId: string, callback: Function, setLoader: Function, onClose: Function) => {
    setLoader(true);
    const responseData = await deleteCustomers(deleteId);
    setLoader(false);

    if (responseData.is_success) {
      toaster.success(tBe(responseData.message));
      callback();
      onClose();
      setTableVers((prevTableVers) => prevTableVers + 1);
    }
  };

  return (
    <>
      <div className="page-header-breadcrumb custom-page-header">
        <PageHeading title={t('accounts_management')} icon="core" />
        <Button className="d-flex align-items-center gap-1" onClick={() => setCreateFormVisible(true)}>
          <Flexicon icon="plus-circle" size={15} />
          <span className="d-none d-sm-inline">{t('add_new_entity', { entity: t('accounts') })}</span>
        </Button>
      </div>

      <AccountsList
        tableVers={tableVers}
        onEdit={(id: string) => setCurrentEditId(id)}
        onConfig={(cell: any) => {
          setCurrentConfigId(cell.id);
          setCurrentConfigData(cell);
        }}
        handleOnDelete={handleOnDelete}
      />

      {createFormVisible && <AccountsCreate key={createFormKey} isOpen={createFormVisible} onCancel={handleCreateFormOnCancel} afterSave={handleAfterSave} />}

      {currentEditId !== '' && <AccountsEdit editId={currentEditId} isOpen={currentEditId !== ''} onCancel={() => setCurrentEditId('')} afterUpdate={handleAfterUpdate} />}
      {currentConfigId !== '' && (
        <AccountConfig
          currentConfigId={currentConfigId}
          isOpen={currentConfigId !== ''}
          onCancel={() => setCurrentConfigId('')}
          afterConfig={handleAfterConfig}
          currentConfigData={currentConfigData}
        />
      )}
    </>
  );
}

export default Accounts;
