import React, { useState } from 'react';
import { useTrans } from '@/helpers/services/lang/langService';
import { ViewOpInteraction } from './ViewOpInteraction';
import { useParams } from 'next/navigation';
import OpInteractionList from './OpInteractionList';
import CreateOpInteraction from './CreateOpInteraction';
import { EditOpInteraction } from './EditOpInteraction';
import { deleteOpInteraction } from '../../../api-service';
import { toaster } from '@/helpers/services/toaster';

function OpportunityInteraction() {
  const tBe = useTrans('be.msg,be.error,be.attri');
  const [currentViewId, setCurrentViewId] = useState('');
  const [currentEditId, setCurrentEditId] = useState('');
  const [createFormVisible, setCreateFormVisible] = useState(false);
  const [tableVers, setTableVers] = useState(0);
  const params = useParams();
  const opportunityId = params.managementId?.toString() || '';

  const handleOnDelete = async (deleteId: string, callback: Function, setLoader: Function) => {
    setLoader(true);
    const responseData = await deleteOpInteraction(opportunityId, deleteId);
    setLoader(false);

    if (responseData.is_success) {
      toaster.success(tBe(responseData.message));
      callback();
      setTableVers((prevValue) => prevValue + 1);
    }
  };

  const handleAfterUpdate = () => {
    setCurrentEditId('');
    setTableVers((prev) => prev + 1);
  };

  return (
    <>
      <OpInteractionList
        tableVers={tableVers}
        onView={(id: any) => setCurrentViewId(id)}
        handleOnDelete={handleOnDelete}
        onEdit={(id: any) => setCurrentEditId(id)}
        setCreateFormVisible={setCreateFormVisible}
      />
      {currentViewId !== '' && <ViewOpInteraction isOpen={currentViewId !== ''} viewId={currentViewId} onClose={() => setCurrentViewId('')} opportunityId={opportunityId} />}
      {currentEditId !== '' && <EditOpInteraction isOpen={currentEditId !== ''} editId={currentEditId} onCancel={() => setCurrentEditId('')} afterUpdate={handleAfterUpdate} />}
      {createFormVisible && (
        <CreateOpInteraction isOpen={createFormVisible} onCancel={() => setCreateFormVisible(false)} afterSave={() => (setTableVers((prevValue) => prevValue + 1), setCreateFormVisible(false))} />
      )}
    </>
  );
}

export default OpportunityInteraction;
