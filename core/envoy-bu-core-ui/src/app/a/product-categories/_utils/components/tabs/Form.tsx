import { useTrans } from '@/helpers/services/lang/langService';
import React, { useEffect, useState } from 'react';
import { toaster } from '@/helpers/services/toaster';
import { deleteTypeForm } from '../../api-service';
import { EditForm } from '../forms/EditForm';
import { ViewForm } from '../forms/ViewForm';
import CreateForm from '../forms/CreateForm';
import FormsList from '../forms/FormList';
import { useSearchParams } from 'next/navigation';

function Form({ viewId }: { viewId: string }) {
  const tBe = useTrans('be.msg,be.error,be.attri');
  const [tableVers, setTableVers] = useState(0);
  const [createFormVers, setCreateFormVers] = useState(0);
  const [currentViewId, setCurrentViewId] = useState('');
  const [currentEditId, setCurrentEditId] = useState('');
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const searchParams = useSearchParams();

  useEffect(() => {
    console.log('searchParams', searchParams.get('backURL'));
  }, [searchParams]);

  const reloadTable = () => {
    setTableVers((prevValue) => prevValue + 1);
    setCreateFormVers((prevValue) => prevValue + 1);
  };

  const handleOnDelete = async (deleteId: string, callback: Function, setLoader: Function, onClose: Function) => {
    setLoader(true);
    const responseData = await deleteTypeForm(deleteId, viewId);
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
      <FormsList
        tableVers={tableVers}
        onView={(id: any) => setCurrentViewId(id)}
        onEdit={(id: any) => setCurrentEditId(id)}
        handleOnDelete={handleOnDelete}
        typeId={viewId}
        setIsCreateOpen={setIsCreateOpen}
      />
      {currentEditId !== '' && <EditForm editId={currentEditId} isOpen={currentEditId !== ''} onCancel={() => setCurrentEditId('')} afterUpdate={reloadTable} />}
      {currentViewId !== '' && <ViewForm isOpen={currentViewId !== ''} viewId={currentViewId} onClose={() => setCurrentViewId('')} />}
      {isCreateOpen && <CreateForm key={createFormVers} isOpen={isCreateOpen} onCancel={() => setIsCreateOpen(false)} afterSave={reloadTable} viewId={viewId} />}
    </>
  );
}

export default Form;
