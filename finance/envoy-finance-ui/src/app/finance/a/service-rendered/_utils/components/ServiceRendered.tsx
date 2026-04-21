'use client';

import PageHeading from '@/components/others/PageHeading';
import { useTrans } from '@/helpers/services/lang/langService';
import React, { useState } from 'react';
import ServiceRenderedList from './ServiceRenderedList';
import { Button } from '@apptimus-ui/ui-element';
import { Flexicon } from '@apptimus-ui/flexicon';
import { toaster } from '@/helpers/services/toaster';
import { deleteServiceRendered } from '../api-service';
import ServiceRenderedCreate from './ServiceRenderedCreate';
import { useRouter } from 'next/navigation';

function ServiceRendered() {
  const t = useTrans('label.service_rendered,otr.common,be.msg');
  const [tableVers, setTableVers] = useState(0);
  const [createFormKey, setCreateFormKey] = useState(0);
  const [createFormVisible, setCreateFormVisible] = useState(false);
  const router = useRouter();

  const handleCreateFormOnCancel = () => {
    setCreateFormVisible(false);
    setCreateFormKey((prevCreateFormKey) => prevCreateFormKey + 1);
  };

  const handleAfterSave = () => {
    setTableVers((prevTableVers) => prevTableVers + 1);
    setCreateFormKey((prevCreateFormKey) => prevCreateFormKey + 1);
  };

  // const handleAfterUpdate = () => {
  //   setCurrentEditId('');
  //   setTableVers((prevTableVers) => prevTableVers + 1);
  // };

  const tBe = useTrans('be.msg,be.error,be.attri');

  const handleOnDelete = async (deleteId: string, callback: Function, setLoader: Function, onClose: Function) => {
    setLoader(true);
    const responseData = await deleteServiceRendered(deleteId);
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
        <PageHeading title={t('service_rendered')} icon="core" />
        <div className="d-flex gap-2">
          {/* <Button className="d-flex align-items-center gap-1" onClick={() => { }} size="md" color="light">
            <Flexicon icon="download-01" size={18} />
            <span>{t('export')}</span>
          </Button> */}
          <Button className="d-flex align-items-center gap-1" onClick={() => setCreateFormVisible(true)}>
            <Flexicon icon="plus-circle" size={18} />
            <span className="d-none d-sm-inline">{t('add_new_entity', { entity: t('service_rendered') })}</span>
          </Button>
        </div>
      </div>

      <ServiceRenderedList tableVers={tableVers} onView={(id: string) => router.push(`/finance/a/service-rendered/${id}`)} handleOnDelete={handleOnDelete} />

      {/* {currentViewId !== '' && <ServiceRenderedView viewId={currentViewId} isOpen={currentViewId !== ''} onClose={() => setCurrentViewId('')} setEditId={(id: any) => setCurrentEditId(id)} />} */}

      {createFormVisible && <ServiceRenderedCreate key={createFormKey} isOpen={createFormVisible} onCancel={handleCreateFormOnCancel} afterSave={handleAfterSave} />}

      {/* {currentEditId !== '' && <ServiceRenderedEdit editId={currentEditId} isOpen={currentEditId !== ''} onCancel={() => setCurrentEditId('')} afterUpdate={handleAfterUpdate} />} */}
    </>
  );
}

export default ServiceRendered;
