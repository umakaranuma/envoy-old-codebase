'use client';
import PageHeading from '@/components/others/PageHeading';
import { useTrans } from '@/helpers/services/lang/langService';
import { Flexicon } from '@apptimus-ui/flexicon';
import { Button } from '@apptimus-ui/ui-element';
import React, { useState } from 'react';
import CreateTeam from './CreateTeam';
import TeamList from './TeamList';
import { EditTeam } from './EditTeam';
import { ViewTeam } from './ViewTeam';
import { toaster } from '@/helpers/services/toaster';
import { deleteTeam } from '../api-service';

function Teams() {
  const t = useTrans('label.teams,otr.common');
  const tBe = useTrans('be.msg,be.error,be.attri');
  const [isCreateTeamVisible, setIsCreateTeamVisible] = useState(false);
  const [currentEditId, setCurrentEditId] = useState<string>('');
  const [tableVersion, setTableVersion] = useState(0);
  const [currentViewId, setCurrentViewId] = useState('');

  const reloadTable = () => {
    setTableVersion((prev) => prev + 1);
  };
  const handleOpenEdit = (id: any) => {
    setCurrentViewId('');
    setTimeout(() => {
      setCurrentEditId(id);
    }, 100);
  };
  const handleOnDelete = async (deleteId: string, callback: Function, setLoader: Function, onClose: Function) => {
    setLoader(true);
    const responseData = await deleteTeam(deleteId);
    setLoader(false);

    if (responseData.status_code === 409) {
      toaster.error(tBe(responseData.message));
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
        <PageHeading title={t('teams')} icon="core" />
        <div className="d-flex flex-row justify-content-end align-items-center gap-3">
          <Button className="d-flex align-items-center gap-1" onClick={() => setIsCreateTeamVisible(true)}>
            <Flexicon icon="plus-circle" size={18} />
            <span className="d-none d-sm-inline">{t('create_team')}</span>
          </Button>
        </div>
      </div>
      <TeamList onEdit={(id: any) => setCurrentEditId(id)} onView={(id: any) => setCurrentViewId(id)} handleOnDelete={handleOnDelete} tableVers={tableVersion} />
      {isCreateTeamVisible && (
        <CreateTeam
          isOpen={isCreateTeamVisible}
          onCancel={() => setIsCreateTeamVisible(false)}
          afterSave={() => {
            setIsCreateTeamVisible(false), reloadTable();
          }}
        />
      )}
      {currentEditId !== '' && (
        <EditTeam
          isOpen={currentEditId !== ''}
          onCancel={() => setCurrentEditId('')}
          afterEdit={() => {
            setCurrentEditId(''), reloadTable();
          }}
          editId={currentEditId}
        />
      )}
      {currentViewId !== '' && <ViewTeam isOpen={currentViewId !== ''} onCancel={() => setCurrentViewId('')} viewId={currentViewId} handleOpenEdit={(id: any) => handleOpenEdit(id)} />}
    </>
  );
}

export default Teams;
