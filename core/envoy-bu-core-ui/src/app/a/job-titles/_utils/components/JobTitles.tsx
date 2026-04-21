'use client';

import { Button } from '@apptimus-ui/ui-element';
import { useState } from 'react';
import { Flexicon } from '@apptimus-ui/flexicon';
import { useTrans } from '@/helpers/services/lang/langService';
import JobTitlesList from './JobTitlesList';
import PageHeading from '@/components/others/PageHeading';
import { deleteJobTitle } from '../api-service';
import { toaster } from '@/helpers/services/toaster';
import { JobTitlesView } from './JobTitlesView';
import JobTitlesCreate from './JobTitlesCreate';
import { JobTitlesEdit } from './JobTitlesEdit';

function JobTitles() {
  const t = useTrans('label.job_titles,otr.common,be.msg');
  const tBe = useTrans('be.msg,be.error,be.attri');
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

  const handleOnDelete = async (deleteId: string, callback: Function, setLoader: Function, onClose: Function) => {
    setLoader(true);
    const responseData = await deleteJobTitle(deleteId);
    setLoader(false);

    if (responseData.status_code === 409) {
      toaster.error(tBe(responseData.message));
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
      <div className="page-header-breadcrumb custom-page-header">
        <PageHeading title={t('job_titles')} icon="core" />
        <Button className="d-flex align-items-center gap-1" onClick={() => setCreateFormVisible(true)}>
          <Flexicon icon="plus-circle" size={18} />
          <span className="d-none d-sm-inline">{t('add_new_title', { entity: t('job_titles') })}</span>
        </Button>
      </div>

      <JobTitlesList tableVers={tableVers} onView={(id: string) => setCurrentViewId(id)} onEdit={(id: string) => setCurrentEditId(id)} handleOnDelete={handleOnDelete} />

      {currentViewId !== '' && <JobTitlesView viewId={currentViewId} isOpen={currentViewId !== ''} onClose={() => setCurrentViewId('')} setEditId={(id: any) => setCurrentEditId(id)} />}

      {createFormVisible && <JobTitlesCreate key={createFormKey} isOpen={createFormVisible} onCancel={handleCreateFormOnCancel} afterSave={handleAfterSave} />}

      {currentEditId !== '' && <JobTitlesEdit editId={currentEditId} isOpen={currentEditId !== ''} onCancel={() => setCurrentEditId('')} afterUpdate={handleAfterUpdate} />}
    </>
  );
}

export default JobTitles;
