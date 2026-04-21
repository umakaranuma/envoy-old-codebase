import { useTrans } from '@/helpers/services/lang/langService';
import React, { useState } from 'react';
import AttributeList from '../attributes/AttributeList';
import { EditAttribute } from '../attributes/EditAttribute';
import { ViewAttribute } from '../attributes/ViewAttribute';
import CreateAttribute from '../attributes/CreateAttribute';
import { toaster } from '@/helpers/services/toaster';
import { useParams } from 'next/navigation';
import { deleteAttribute } from '../../api-service';

function Attribute() {
  const tBe = useTrans('be.msg,be.error,be.attri');
  const [tableVers, setTableVers] = useState(0);
  const [currentViewId, setCurrentViewId] = useState('');
  const [currentEditId, setCurrentEditId] = useState('');
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const params = useParams();
  const formId = params.id as string;

  const reloadTable = () => {
    setTableVers((prevValue) => prevValue + 1);
  };

  const handleOnDelete = async (deleteId: string, callback: Function, setLoader: Function, onClose: Function) => {
    setLoader(true);
    const responseData = await deleteAttribute(formId, deleteId);
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
      <AttributeList tableVers={tableVers} onView={(id: any) => setCurrentViewId(id)} onEdit={(id: any) => setCurrentEditId(id)} handleOnDelete={handleOnDelete} setIsCreateOpen={setIsCreateOpen} />
      {currentEditId !== '' && <EditAttribute editId={currentEditId} isOpen={currentEditId !== ''} onCancel={() => setCurrentEditId('')} afterUpdate={reloadTable} />}
      {currentViewId !== '' && <ViewAttribute isOpen={currentViewId !== ''} viewId={currentViewId} onClose={() => setCurrentViewId('')} />}
      {isCreateOpen && <CreateAttribute isOpen={isCreateOpen} onCancel={() => setIsCreateOpen(false)} afterSave={reloadTable} />}
    </>
  );
}

export default Attribute;
