'use client';
import PageHeading from '@/components/others/PageHeading';
import { useTrans } from '@/helpers/services/lang/langService';
import { Flexicon } from '@apptimus-ui/flexicon';
import { Button } from '@apptimus-ui/ui-element';
import React, { useState } from 'react';
import FormList from './FormList';
import { EditForm } from './EditForm';
import { useRouter } from 'next/navigation';
import CreateForm from './CreateForm';
import { deleteForm } from '../api-service';
import { toaster } from '@/helpers/services/toaster';

function Form() {
  const t = useTrans('label.form,otr.common');
  const [tableVers, setTableVers] = useState(0);
  const [currentEditId, setCurrentEditId] = useState('');
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const router = useRouter();
  const tBe = useTrans('be.msg,be.error,be.attri');

  const reloadTable = () => {
    setTableVers((prevValue) => prevValue + 1);
  };

  const handleOnDelete = async (deleteId: string, callback: Function, setLoader: Function, onClose: Function) => {
    setLoader(true);
    const responseData = await deleteForm(deleteId);
    setLoader(false);

    if (responseData.is_success) {
      toaster.success(tBe(responseData.message));
      callback();
      onClose();
      reloadTable();
    }
  };

  return (
    <>
      <div className="page-header-breadcrumb custom-page-header">
        <PageHeading title={t('forms')} icon="core" />
        <div className="d-flex flex-row justify-content-end align-items-center gap-3">
          <Button className="d-flex align-items-center gap-1" onClick={() => setIsCreateOpen(true)}>
            <Flexicon icon="plus-circle" size={18} />
            <span className="d-none d-sm-inline">{t('add_new_form')}</span>
          </Button>
        </div>
      </div>
      <FormList tableVers={tableVers} onView={(id: any) => router.push(`/a/forms/${id}`)} onEdit={(id: any) => setCurrentEditId(id)} handleOnDelete={handleOnDelete} />
      {currentEditId !== '' && <EditForm editId={currentEditId} isOpen={currentEditId !== ''} onCancel={() => setCurrentEditId('')} afterUpdate={reloadTable} />}
      {isCreateOpen && <CreateForm isOpen={isCreateOpen} onCancel={() => setIsCreateOpen(false)} afterSave={reloadTable} />}
    </>
  );
}

export default Form;
