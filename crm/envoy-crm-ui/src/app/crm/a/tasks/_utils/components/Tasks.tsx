'use client';

import { Button } from '@apptimus-ui/ui-element';
import { useEffect, useState } from 'react';
import { Flexicon } from '@apptimus-ui/flexicon';
import { useTrans } from '@/helpers/services/lang/langService';
import PageHeading from '@/components/others/PageHeading';
import KanbanView from './assigned-tasks/kanban-view/KanbanView';
import AssignedTask from './assigned-tasks/AssignedTask';
import { Dropdown, DropdownItem } from '@apptimus-ui/dropdown';
import { useRouter, useSearchParams } from 'next/navigation';

function Tasks() {
  const t = useTrans('label.tasks,otr.common');
  const [createFormVisible, setCreateFormVisible] = useState(false);
  const [viewType, setViewType] = useState('list_view');
  const searchParams = useSearchParams();
  const router = useRouter();

  useEffect(() => {
    const tab = searchParams.get('t') || 'list_view';
    toggleTableTab(tab);
  }, []);

  const toggleTableTab = (activeTab: string) => {
    setViewType(activeTab);
    router.push(`/crm/a/tasks?t=${activeTab}`);
  };

  return (
    <>
      <div className="page-header-breadcrumb custom-page-header">
        <PageHeading title={t('task_management')} icon="crm" />
        {
          <div className="d-flex gap-2 align-items-center">
            <Dropdown
              trigger={
                <Button color="primary" variant="outline" className="d-flex align-items-center gap-1">
                  <Flexicon icon={viewType === 'team_view' ? 'git-branch-01' : viewType === 'kanban_view' ? 'git-branch-01' : 'dotpoints-01'} variant="line" size={15} />
                  <span className="d-none d-sm-inline">
                    {viewType === 'list_view' && t('list_view')}
                    {viewType === 'kanban_view' && t('kanban_view')}
                    {/* {viewType === 'calender_view' && t('calendar_view')} */}
                  </span>
                  <Flexicon icon="chevron-down" variant="line" size={15} />
                </Button>
              }
            >
              {(onClose: Function) => (
                <>
                  <DropdownItem onClick={() => (toggleTableTab('list_view'), onClose())}>
                    <span className="d-flex gap-2">
                      <Flexicon icon="dotpoints-01" variant="line" size={15} />
                      <span>{t('list_view')}</span>
                    </span>
                  </DropdownItem>
                  <DropdownItem onClick={() => (toggleTableTab('kanban_view'), onClose())}>
                    <span className="d-flex gap-2">
                      <Flexicon icon="git-branch-01" variant="line" size={15} />
                      <span>{t('kanban_view')}</span>
                    </span>
                  </DropdownItem>
                  {/* <DropdownItem onClick={() => (setViewType('calender_view'), onClose())}>
                    <span className="d-flex gap-2">
                      <Flexicon icon="git-branch-01" variant="line" size={15} />
                      <span>{t('calendar_view')}</span>
                    </span>
                  </DropdownItem> */}
                </>
              )}
            </Dropdown>
            {viewType === 'list_view' && (
              <Button color="primary" className="d-flex align-items-center gap-1" onClick={() => setCreateFormVisible(true)}>
                <Flexicon icon="plus-circle" size={18} />
                <span className="d-none d-sm-inline">{t('add_new_entity', { entity: t('task') })}</span>
              </Button>
            )}
          </div>
        }
      </div>
      <div>
        {viewType === 'list_view' && <AssignedTask setCreateFormVisible={setCreateFormVisible} createFormVisible={createFormVisible} />}
        {/* {viewType === 'calender_view' && <CalendarView />} */}
        {viewType === 'kanban_view' && <KanbanView />}
      </div>
    </>
  );
}

export default Tasks;
