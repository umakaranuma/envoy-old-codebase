'use client';
import PageHeading from '@/components/others/PageHeading';
import { useTrans } from '@/helpers/services/lang/langService';
import { Flexicon } from '@apptimus-ui/flexicon';
import { Button } from '@apptimus-ui/ui-element';
import React, { useState } from 'react';
import ReportList from './ReportList';
import CreateReport from './CreateReport';
import { deleteReport } from '../api-service';
import { toaster } from '@/helpers/services/toaster';
import { useRouter } from 'next/navigation';
import EditReport from './EditReport';

function CustomReports() {
  const t = useTrans('label.custom_report,otr.common,be.msg');
  const tBe = useTrans('be.msg,be.error,be.attri');
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [tableVers, setTableVers] = useState(0);
  const [currentEditId, setCurrentEditId] = useState<string>('');
  const router = useRouter();

  const reloadTable = () => {
    setTableVers((prev) => prev + 1);
  };

  const handleOnDelete = async (deleteId: string, callback: Function, setLoader: Function, onClose: Function) => {
    setLoader(true);
    const responseData = await deleteReport(deleteId);
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
        <PageHeading title={t('custom_reports')} icon="core" />
        <div className="d-flex gap-2 align-items-center">
          <Button color="primary" className="d-flex align-items-center gap-1" onClick={() => setIsCreateOpen(true)}>
            <Flexicon icon="plus-circle" size={18} />
            <span className="d-none d-sm-inline">{t('create_new_report')}</span>
          </Button>
        </div>
      </div>
      <ReportList handleOnDelete={handleOnDelete} onView={(id: any) => router.push(`/finance/a/custom-reports/${id}`)} onEdit={(id: any) => setCurrentEditId(id)} tableVers={tableVers} />
      {isCreateOpen && (
        <CreateReport
          isOpen={isCreateOpen}
          onCancel={() => setIsCreateOpen(false)}
          afterSave={() => {
            setIsCreateOpen(false);
            reloadTable();
          }}
        />
      )}
      {!!currentEditId && (
        <EditReport
          isOpen={!!currentEditId}
          onCancel={() => setCurrentEditId('')}
          afterSave={() => {
            setCurrentEditId(''), reloadTable();
          }}
          editId={currentEditId}
        />
      )}
    </>
  );
}

export default CustomReports;
