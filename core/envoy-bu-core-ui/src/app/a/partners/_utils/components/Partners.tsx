'use client';
import PageHeading from '@/components/others/PageHeading';
import { useTrans } from '@/helpers/services/lang/langService';
import React, { useState } from 'react';
import PartnerList from './PartnerList';
import { toaster } from '@/helpers/services/toaster';
import { Button } from '@apptimus-ui/ui-element';
import { Flexicon } from '@apptimus-ui/flexicon';
import { CreatePartner } from './CreatePartner';
import { EditPartner } from './EditPartner';
import { deletePartner } from '../api-service';
import { useRouter } from 'next/navigation';

function Partners() {
  const t = useTrans('label.partners,otr.common');
  const tBe = useTrans('be.msg,be.error,be.attri');
  const [tableVers, setTableVers] = useState(0);
  const [createFormKey, setCreateFormKey] = useState(0);
  const [currentEditId, setCurrentEditId] = useState('');
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const router = useRouter();

  const reloadTable = () => {
    setTableVers((prevValue) => prevValue + 1);
  };
  const handleOnDelete = async (deleteId: string, callback: Function, setLoader: Function, onClose: Function) => {
    setLoader(true);
    const responseData = await deletePartner(deleteId);
    setLoader(false);

    if (responseData.is_success) {
      toaster.success(tBe(responseData.message));
      reloadTable();
      callback();
      onClose();
    }
  };

  const handleCreateFormCancel = () => {
    setIsCreateOpen(false);
    setCreateFormKey((prevCreateFormKey) => prevCreateFormKey + 1);
  };

  const handleAfterSave = () => {
    handleCreateFormCancel();
    reloadTable();
  };

  return (
    <>
      <div className="page-header-breadcrumb custom-page-header">
        <PageHeading title={t('partners')} icon="core" />
        <div className="d-flex flex-row justify-content-end align-items-center gap-3">
          <Button className="d-flex align-items-center gap-1" onClick={() => setIsCreateOpen(true)}>
            <Flexicon icon="plus-circle" size={18} />
            <span className="d-none d-sm-inline">{t('add_new_entity', { entity: t('partner') })}</span>
          </Button>
          {/* <Dropdown
            trigger={
              <Button color="primary" variant="outline" className="d-flex align-items-center gap-1">
                <Flexicon icon="dots-vertical" variant="line" size={15} />
              </Button>
            }
          >
            {(onClose: Function) => (
              <>
                <DropdownItem onClick={() => onClose()}>
                  <div className="d-flex align-items-center gap-2">
                    <Flexicon icon="download-cloud-02" variant="line" size={14} />
                    <span>{t('export')}</span>
                  </div>
                </DropdownItem>
              </>
            )}
          </Dropdown> */}
        </div>
      </div>
      <PartnerList tableVers={tableVers} onView={(id: any) => router.push(`/a/partners/${id}`)} onEdit={(id: any) => setCurrentEditId(id)} handleOnDelete={handleOnDelete} />
      {isCreateOpen && <CreatePartner key={createFormKey} isOpen={isCreateOpen} onCancel={handleCreateFormCancel} afterSave={handleAfterSave} />}
      {currentEditId !== '' && <EditPartner isOpen={currentEditId !== ''} onCancel={() => setCurrentEditId('')} afterEdit={reloadTable} editId={currentEditId} />}
    </>
  );
}

export default Partners;
