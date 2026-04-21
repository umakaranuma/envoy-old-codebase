'use client';
import PageHeading from '@/components/others/PageHeading';
import { useTrans } from '@/helpers/services/lang/langService';
import { Flexicon } from '@apptimus-ui/flexicon';
import { Button } from '@apptimus-ui/ui-element';
import React, { useState } from 'react';
import { deleteReportType } from '../api-service';
import { toaster } from '@/helpers/services/toaster';
import ReportTypeList from './ReportTypeList';
import CreateReportType from './CreateReportType';
import { EditReportType } from './EditReportType';

function ReportTypes() {
  const t = useTrans('label.report_type,otr.common,be.msg');
  const tBe = useTrans('be.msg,be.error,be.attri');
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [editId, setEditId] = useState<string>('');
  const [tableVers, setTableVers] = useState(0);

  const reloadTable = () => {
    setTableVers((prev) => prev + 1);
  };

  const handleOnDelete = async (deleteId: string, callback: Function, setLoader: Function, onClose: Function) => {
    setLoader(true);
    const responseData = await deleteReportType(deleteId);
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
        <PageHeading title={t('report_types')} icon="core" />
        <div className="d-flex gap-2 align-items-center">
          <Button color="primary" className="d-flex align-items-center gap-1" onClick={() => setIsCreateOpen(true)}>
            <Flexicon icon="plus-circle" size={18} />
            <span className="d-none d-sm-inline">{t('create_new_report_type')}</span>
          </Button>
        </div>
      </div>
      <ReportTypeList handleOnDelete={handleOnDelete} onView={() => {}} onEdit={(id: string) => setEditId(id)} tableVers={tableVers} />
      {isCreateOpen && <CreateReportType isOpen={isCreateOpen} onCancel={() => setIsCreateOpen(false)} afterSave={reloadTable} />}
      {editId !== '' && <EditReportType isOpen={!!editId} editId={editId} onCancel={() => setEditId('')} afterUpdate={reloadTable} />}
    </>
  );
}

export default ReportTypes;
