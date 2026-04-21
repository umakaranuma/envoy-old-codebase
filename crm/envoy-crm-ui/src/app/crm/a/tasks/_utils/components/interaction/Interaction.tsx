import React, { useState } from 'react';
import InteractionList from './InteractionList';
import { useTrans } from '@/helpers/services/lang/langService';
import CreateInteraction from './CreateInteraction';
import { toaster } from '@/helpers/services/toaster';
import { deleteTaskInteraction } from '../../api-service';
import { useParams } from 'next/navigation';
import { ViewOpInteraction } from '@/app/crm/a/sales-management/_utils/components/tabs/op-interaction/ViewOpInteraction';

function Interaction({ opportunityId }: { opportunityId: string }) {
  const tBe = useTrans('be.msg,be.error,be.attri');
  const [currentViewId, setCurrentViewId] = useState('');
  const [createFormVisible, setCreateFormVisible] = useState(false);
  const [tableVers, setTableVers] = useState(0);
  const params = useParams();
  const taskId = params.taskId?.toString() || '';

  const handleOnDelete = async (deleteId: string, callback: Function, setLoader: Function) => {
    setLoader(true);
    const responseData = await deleteTaskInteraction(taskId, deleteId);
    setLoader(false);

    if (responseData.is_success) {
      toaster.success(tBe(responseData.message));
      callback();
      setTableVers((prevValue) => prevValue + 1);
    }
  };

  return (
    <>
      <InteractionList tableVers={tableVers} handleOnDelete={handleOnDelete} setCreateFormVisible={setCreateFormVisible} onView={(id: string) => setCurrentViewId(id)} />
      {currentViewId !== '' && <ViewOpInteraction isOpen={currentViewId !== ''} viewId={currentViewId} onClose={() => setCurrentViewId('')} opportunityId={opportunityId} />}
      {createFormVisible && (
        <CreateInteraction isOpen={createFormVisible} onCancel={() => setCreateFormVisible(false)} afterSave={() => (setTableVers((prevValue) => prevValue + 1), setCreateFormVisible(false))} />
      )}
    </>
  );
}

export default Interaction;
