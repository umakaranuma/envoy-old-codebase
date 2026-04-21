import { useTrans } from '@/helpers/services/lang/langService';
import React, { useState } from 'react';
import AssignedTasksList from '@/app/crm/a/tasks/_utils/components/assigned-tasks/AssignedTasksList';
import { useParams, useRouter } from 'next/navigation';
import { deleteAssignedTask } from '@/app/crm/a/tasks/_utils/api-service';
import { toaster } from '@/helpers/services/toaster';
import { EditAssignedTask } from '@/app/crm/a/tasks/_utils/components/assigned-tasks/EditAssignedTask';
import { Button } from '@apptimus-ui/ui-element';
import { Flexicon } from '@apptimus-ui/flexicon';
import CreateTask from '@/app/crm/a/tasks/_utils/components/assigned-tasks/CreateTask';

const Tasks = ({ opData }: { opData: any }) => {
  const tBe = useTrans('be.msg,be.error,be.attri');
  const t = useTrans('label.tasks,otr.common');
  const [tableVers, setTableVers] = useState(0);
  const [currentEditId, setCurrentEditId] = useState('');
  const router = useRouter();
  const params = useParams();
  const opportunityId = params.managementId?.toString() || '';
  const [createFormKey, setCreateFormKey] = useState(0);
  const [createFormVisible, setCreateFormVisible] = useState(false);

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

  const handleCreateFormOnCancel = () => {
    setCreateFormVisible(false);
    setCreateFormKey((prevCreateFormKey) => prevCreateFormKey + 1);
  };

  const handleAfterSave = () => {
    setTableVers((prevTableVers) => prevTableVers + 1);
    setCreateFormKey((prevCreateFormKey) => prevCreateFormKey + 1);
  };

  return (
    <>
      <div className="d-flex justify-content-end">
        <Button color="primary" className="d-flex align-items-center gap-1" onClick={() => setCreateFormVisible(true)}>
          <Flexicon icon="plus-circle" size={18} />
          <span className="d-none d-sm-inline">{t('add_new_entity', { entity: t('task') })}</span>
        </Button>
      </div>
      <AssignedTasksList
        opId={opportunityId}
        tableVers={tableVers}
        onView={(id: string) => router.push(`/crm/a/tasks/${id}?f=op&opId=${opportunityId}`)}
        onEdit={(id: string) => setCurrentEditId(id)}
        handleOnDelete={handleOnDelete}
      />
      {currentEditId !== '' && <EditAssignedTask editId={currentEditId} isOpen={currentEditId !== ''} onCancel={() => setCurrentEditId('')} afterUpdate={handleAfterUpdate} />}
      {createFormVisible && <CreateTask opData={opData} key={createFormKey} isOpen={createFormVisible} onCancel={handleCreateFormOnCancel} afterSave={handleAfterSave} />}
    </>
  );
};

export default Tasks;
