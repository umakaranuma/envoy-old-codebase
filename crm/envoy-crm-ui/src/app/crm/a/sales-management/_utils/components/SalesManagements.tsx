'use client';
import { Button } from '@apptimus-ui/ui-element';
import { useState } from 'react';
import { Flexicon } from '@apptimus-ui/flexicon';
import { useTrans } from '@/helpers/services/lang/langService';
import SalesManagementsList from './SalesManagementsList';
import PageHeading from '@/components/others/PageHeading';
import SalesManagementsCreate from './SalesManagementsCreate';
import { useRouter } from 'next/navigation';
import { Dropdown, DropdownItem } from '@apptimus-ui/dropdown';
import KanbanView from './kanban-view/KanbanView';
import { SalesManagementsEdit } from './SalesManagementsEdit';
import { toaster } from '@/helpers/services/toaster';
import { deleteOpportunity } from '../api-service';

function SalesManagements({ settingId, act }: { settingId: string; act: any }) {
  const [tableVers, setTableVers] = useState(0);
  const [createFormKey, setCreateFormKey] = useState(0);
  const [createFormVisible, setCreateFormVisible] = useState(false);
  const [defaultStageId, setDefaultStageId] = useState(null);
  const [currentEditId, setCurrentEditId] = useState('');
  const [viewType, setViewType] = useState<'list_view' | 'kanban_view'>(act);
  const [kanbanColumnReloadVers, _setKanbanColumnReloadVers] = useState(0);
  const router = useRouter();
  const t = useTrans('label.sales_managements,otr.common');
  const tBe = useTrans('be.msg,be.error,be.attri');

  const handleCreateFormOnCancel = () => {
    setCreateFormVisible(false);
    setCreateFormKey((prev) => prev + 1);
    setDefaultStageId(null);
  };

  const handleAfterSave = (id: any) => {
    router.push(`/crm/a/sales-management/${id}?t=opp-type&f=board`);
    // setTableVers((prev) => prev + 1);
    // setCreateFormKey((prev) => prev + 1);
    // setCreateFormVisible(false);
    // setDefaultStageId(null);
    // setKanbanColumnReloadVers((prev) => prev + 1);
  };

  const handleAfterUpdate = () => {
    setCurrentEditId('');
    setTableVers((prev) => prev + 1);
  };

  const handleOnDelete = async (deleteId: string, callback: Function, setLoader: Function, onClose: Function) => {
    setLoader(true);
    const responseData = await deleteOpportunity(deleteId);
    setLoader(false);
    if (responseData.status_code === 417) {
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
        <PageHeading title={t('sales_management')} icon="crm" />
        <div className="d-flex gap-2 align-items-center">
          <Dropdown
            trigger={
              <Button color="primary" variant="outline" className="d-flex align-items-center gap-1">
                <Flexicon icon={viewType === 'kanban_view' ? 'git-branch-01' : 'dotpoints-01'} variant="line" size={15} />
                <span className="d-none d-sm-inline">
                  {viewType === 'list_view' && t('list_view')}
                  {viewType === 'kanban_view' && t('kanban_view')}
                </span>
                <Flexicon icon="chevron-down" variant="line" size={15} />
              </Button>
            }
          >
            {(onClose: Function) => (
              <>
                <DropdownItem onClick={() => (setViewType('list_view'), onClose())}>
                  <span className="d-flex gap-2">
                    <Flexicon icon="dotpoints-01" variant="line" size={15} />
                    <span>{t('list_view')}</span>
                  </span>
                </DropdownItem>
                <DropdownItem onClick={() => (setViewType('kanban_view'), onClose())}>
                  <span className="d-flex gap-2">
                    <Flexicon icon="git-branch-01" variant="line" size={15} />
                    <span>{t('kanban_view')}</span>
                  </span>
                </DropdownItem>
              </>
            )}
          </Dropdown>
          {viewType !== 'kanban_view' && (
            <Button color="primary" className="d-flex align-items-center gap-1" onClick={() => setCreateFormVisible(true)}>
              <Flexicon icon="plus-circle" size={18} />
              <span className="d-none d-sm-inline">{t('add_new_leads')}</span>
            </Button>
          )}
          {/* {viewType !== 'kanban_view' && (
            <Dropdown
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
            </Dropdown>
          )} */}
        </div>
      </div>

      {viewType === 'list_view' && (
        <SalesManagementsList tableVers={tableVers} onView={(id: any) => router.push(`/crm/a/sales-management/${id}`)} onEdit={(id: string) => setCurrentEditId(id)} handleOnDelete={handleOnDelete} />
      )}
      {viewType === 'kanban_view' && (
        <KanbanView
          {...{ kanbanColumnReloadVers, settingId }}
          onAdd={(column: any) => {
            setDefaultStageId(column.id);
            setCreateFormVisible(true);
          }}
        />
      )}
      {createFormVisible && <SalesManagementsCreate {...{ defaultStageId }} key={createFormKey} isOpen={createFormVisible} onCancel={handleCreateFormOnCancel} afterSave={handleAfterSave} />}
      {currentEditId && <SalesManagementsEdit editId={currentEditId} isOpen={!!currentEditId} onCancel={() => setCurrentEditId('')} afterUpdate={handleAfterUpdate} />}
    </>
  );
}

export default SalesManagements;
