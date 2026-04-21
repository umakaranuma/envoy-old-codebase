'use client';
import PageHeading from '@/components/others/PageHeading';
import { useTrans } from '@/helpers/services/lang/langService';
import { Flexicon } from '@apptimus-ui/flexicon';
import { Button } from '@apptimus-ui/ui-element';
import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { deleteTemplate } from '../api-service';
import { toaster } from '@/helpers/services/toaster';
import TemplatesList from './TemplatesList';
import TemplatesCreate from './TemplatesCreate';
import { TemplatesEdit } from './TemplatesEdit';

function Templates() {
  const t = useTrans('label.template,otr.common');
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
    const responseData = await deleteTemplate(deleteId);
    setLoader(false);

    if (responseData.status_code === 409) {
      toaster.error(tBe(responseData.message));
      callback();
      onClose();
      return;
    }

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
        <PageHeading title={t('templates')} icon="core" />
        <div className="d-flex flex-row justify-content-end align-items-center gap-3">
          <Button className="d-flex align-items-center gap-1" onClick={() => setIsCreateOpen(true)}>
            <Flexicon icon="plus-circle" size={18} />
            <span className="d-none d-sm-inline">{t('add_new_template')}</span>
          </Button>
        </div>
      </div>
      <TemplatesList tableVers={tableVers} onView={(id: any) => router.push(`/a/templates/${id}`)} onEdit={(id: any) => setCurrentEditId(id)} handleOnDelete={handleOnDelete} />
      {currentEditId !== '' && <TemplatesEdit editId={currentEditId} isOpen={currentEditId !== ''} onCancel={() => setCurrentEditId('')} afterUpdate={reloadTable} />}
      {isCreateOpen && (
        <TemplatesCreate
          isOpen={isCreateOpen}
          onCancel={() => setIsCreateOpen(false)}
          afterSave={() => {
            setIsCreateOpen(false);
          }}
        />
      )}
    </>
  );
}

export default Templates;
