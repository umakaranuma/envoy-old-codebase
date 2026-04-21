'use client';

import { useState } from 'react';
import { useTrans } from '@/helpers/services/lang/langService';
import { toaster } from '@/helpers/services/toaster';
import AssignedTasksList from './AssignedTasksList';
import { deleteAssignedTask } from '../../api-service';
import { EditAssignedTask } from './EditAssignedTask';
import CreateTask from './CreateTask';
import { useRouter } from 'next/navigation';

function AssignedTask({ createFormVisible, setCreateFormVisible }: { createFormVisible: boolean; setCreateFormVisible: Function }) {
  const [tableVers, setTableVers] = useState(0);
  const [createFormKey, setCreateFormKey] = useState(0);
  const [currentEditId, setCurrentEditId] = useState('');
  const tBe = useTrans('be.msg,be.error,be.attri');

  const router = useRouter();

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
    const responseData = await deleteAssignedTask(deleteId);
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
      <AssignedTasksList tableVers={tableVers} onView={(id: string) => router.push(`/crm/a/tasks/${id}`)} onEdit={(id: string) => setCurrentEditId(id)} handleOnDelete={handleOnDelete} />

      {createFormVisible && <CreateTask key={createFormKey} isOpen={createFormVisible} onCancel={handleCreateFormOnCancel} afterSave={handleAfterSave} />}

      {currentEditId !== '' && <EditAssignedTask editId={currentEditId} isOpen={currentEditId !== ''} onCancel={() => setCurrentEditId('')} afterUpdate={handleAfterUpdate} />}
    </>
  );
}

export default AssignedTask;
