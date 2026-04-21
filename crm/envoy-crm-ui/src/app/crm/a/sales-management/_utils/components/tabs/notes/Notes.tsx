'use client';

import { useState } from 'react';
import { useTrans } from '@/helpers/services/lang/langService';
import NoteList from './NoteList';
import { toaster } from '@/helpers/services/toaster';
import CreateNotes from './CreateNotes';
import EditNotes from './EditNotes';
import ViewNotes from './ViewNotes';
import { deleteNotes } from '../../../api-service';

function Notes({ entityId }: { entityId: number }) {
  const tBe = useTrans('be.msg,be.error,be.attri');
  const [currentViewId, setCurrentViewId] = useState('');
  const [currentEditId, setCurrentEditId] = useState('');
  const [createFormVisible, setCreateFormVisible] = useState(false);
  const [tableVers, setTableVers] = useState(0);
  const [createFormKey, setCreateFormKey] = useState(0);

  const handleOnDelete = async (deleteId: string, callback: Function, setLoader: Function) => {
    setLoader(true);
    const responseData = await deleteNotes(entityId.toString(), deleteId);
    setLoader(false);

    if (responseData.is_success) {
      toaster.success(tBe(responseData.message));
      callback();
      setTableVers((prevValue) => prevValue + 1);
    }
  };

  const handleOnEdit = (editId: string) => {
    setCurrentEditId(editId);
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
      <NoteList tableVers={tableVers} onEdit={handleOnEdit} onDelete={() => {}} handleOnDelete={handleOnDelete} setCreateFormVisible={setCreateFormVisible} entityId={entityId.toString()} />
      {createFormVisible && <CreateNotes key={createFormKey} isOpen={createFormVisible} onCancel={() => setCreateFormVisible(false)} afterSave={handleAfterSave} entityId={entityId.toString()} />}
      {currentEditId !== '' && <EditNotes editId={currentEditId} isOpen={currentEditId !== ''} onCancel={() => setCurrentEditId('')} afterUpdate={handleAfterUpdate} entityId={entityId.toString()} />}
      {currentViewId !== '' && <ViewNotes viewId={currentViewId} isOpen={currentViewId !== ''} onClose={() => setCurrentViewId('')} entityId={entityId.toString()} />}
    </>
  );
}

export default Notes;
