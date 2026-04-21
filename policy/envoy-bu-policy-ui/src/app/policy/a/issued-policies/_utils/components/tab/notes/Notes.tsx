'use client';
import React, { useState } from 'react';
import NotesList from './NotesList';
import { Button } from '@apptimus-ui/ui-element';
import { Flexicon } from '@apptimus-ui/flexicon';
import { useTrans } from '@/helpers/services/lang/langService';
import NotesCreate from './NotesCreate';
import NotesView from './NotesView';
import NotesEdit from './NotesEdit';

function Notes({ entityId }: { entityId: string }) {
  const t = useTrans('label.issued_policies,otr.common');
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

  return (
    <>
      <div className="d-flex justify-content-end mb-4">
        <Button color="primary" className="d-flex align-items-center gap-1" onClick={() => setCreateFormVisible(true)}>
          <Flexicon icon="plus-circle" size={18} />
          <span className="d-none d-sm-inline">{t('add_new')}</span>
        </Button>
      </div>

      <NotesList tableVers={tableVers} onView={(id: string) => setCurrentViewId(id)} onEdit={(id: string) => setCurrentEditId(id)} entityId={entityId} />

      {createFormVisible && <NotesCreate key={createFormKey} isOpen={createFormVisible} onCancel={handleCreateFormOnCancel} afterSave={handleAfterSave} entityId={entityId} />}

      {currentViewId !== '' && <NotesView viewId={currentViewId} isOpen={currentViewId !== ''} onClose={() => setCurrentViewId('')} entityId={entityId} />}

      {currentEditId !== '' && <NotesEdit editId={currentEditId} isOpen={currentEditId !== ''} onCancel={() => setCurrentEditId('')} afterUpdate={handleAfterUpdate} entityId={entityId} />}
    </>
  );
}

export default Notes;
