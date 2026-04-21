'use client';
import PageHeading from '@/components/others/PageHeading';
import { useTrans } from '@/helpers/services/lang/langService';
import { toaster } from '@/helpers/services/toaster';
import React, { useState } from 'react';
import { deleteFlags } from '../api-service';
import MappingDataTablePreviewList from './MappingDataTablePreviewList';
import MappingDataTablePreviewCreate from './MappingDataTablePreviewCreate';
import { MappingDataTablePreviewEdit } from './MappingDataTablePreviewEdit';
import { MappingDataTablePreviewView } from './MappingDataTablePreviewView';

function MappingDataTablePreview() {
  const [tableVers, setTableVers] = useState(0);
  const [createFormKey, setCreateFormKey] = useState(0);
  const [createFormVisible, setCreateFormVisible] = useState(false);
  const [currentViewId, setCurrentViewId] = useState('');
  const [currentEditId, setCurrentEditId] = useState('');

  const handleCreateFormOnCancel = () => {
    setCreateFormVisible(false);
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

  const t = useTrans('label.mapping_data_table_preview,otr.common,be.msg');
  const tBe = useTrans('be.msg,be.error,be.attri');

  const handleOnDelete = async (deleteId: string, callback: Function, setLoader: Function, onClose: Function) => {
    setLoader(true);
    const responseData = await deleteFlags(deleteId);
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
      <div className="page-header-breadcrumb custom-page-header ">
        <PageHeading title={t('mapping_data_table_preview')} icon="core" />
      </div>
      <div className="d-flex justify-content-between align-items-center w-100 bg-white p-3 rounded-3 mt-3">
        <div className="fw-bold">{t('product_commission')}</div>
      </div>
      <MappingDataTablePreviewList tableVers={tableVers} onView={(id: string) => setCurrentViewId(id)} onEdit={(id: string) => setCurrentEditId(id)} handleOnDelete={handleOnDelete} />

      {currentViewId !== '' && <MappingDataTablePreviewView viewId={currentViewId} isOpen={currentViewId !== ''} onClose={() => setCurrentViewId('')} setEditId={(id: any) => setCurrentEditId(id)} />}

      {createFormVisible && <MappingDataTablePreviewCreate key={createFormKey} isOpen={createFormVisible} onCancel={handleCreateFormOnCancel} afterSave={handleAfterSave} />}

      {currentEditId !== '' && <MappingDataTablePreviewEdit editId={currentEditId} isOpen={currentEditId !== ''} onCancel={() => setCurrentEditId('')} afterUpdate={handleAfterUpdate} />}
    </>
  );
}

export default MappingDataTablePreview;
