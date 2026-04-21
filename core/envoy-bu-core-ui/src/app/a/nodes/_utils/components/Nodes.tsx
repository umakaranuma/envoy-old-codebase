'use client';
import React, { useEffect, useState } from 'react';
import OrgHierarchyView from './OrgHierarchyView';
import { getAllCustomersHierarchies } from '@/app/a/accounts/_utils/api-service';
import { Dropdown, DropdownItem } from '@apptimus-ui/dropdown';
import { Button } from '@apptimus-ui/ui-element';
import { Flexicon } from '@apptimus-ui/flexicon';
import { useTrans } from '@/helpers/services/lang/langService';
import StaffHierarchyView from './StaffHierarchyView';
import TeamView from './TeamView';
import PageHeading from '@/components/others/PageHeading';

function Nodes() {
  const t = useTrans('label.org_nodes,otr.common');
  const [data, setData] = useState<any>(null);
  const [name, setName] = useState<string | undefined>(undefined);
  const [type, setType] = useState<string | undefined>(undefined);
  const [_skeleton, setSkeleton] = useState(true);
  const [viewType, setViewType] = useState('organization_view');
  const [_createFormVisible, setCreateFormVisible] = useState(false);

  const fetchData = async () => {
    try {
      const response = await getAllCustomersHierarchies('1');
      if (response?.is_success && response.result.length > 0) {
        const rootNode = response.result[0]; // Taking the first item as root
        setData(rootNode);
        setName(rootNode?.name ?? '');
        setType(rootNode?.type ?? '');
      }
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setSkeleton(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  useEffect(() => {}, [data]);
  return (
    <>
      <div className="page-header-breadcrumb custom-page-header">
        <div>
          {viewType === 'organization_view' && <PageHeading title={t('organizational_view')} icon="core" />}
          {viewType === 'staff_hierarchy_view' && <PageHeading title={t('staff_hierarchy_view')} icon="core" />}
          {viewType === 'team_view' && <PageHeading title={t('team_view')} icon="core" />}
        </div>
        <div className="d-flex flex-row gap-2 align-items-center">
          <Dropdown
            trigger={
              <Button color="primary" variant="outline" className="d-flex align-items-center gap-1">
                <Flexicon icon={'git-branch-01'} variant="line" size={15} />
                <span className="d-none d-sm-inline">
                  {viewType === 'organization_view' && t('organizational_view')}
                  {viewType === 'staff_hierarchy_view' && t('staff_hierarchy_view')}
                  {viewType === 'team_view' && t('team_view')}
                </span>
                <Flexicon icon="chevron-down" variant="line" size={15} />
              </Button>
            }
          >
            {(onClose: Function) => (
              <div style={{ minWidth: '200px' }}>
                <DropdownItem onClick={() => (setViewType('organization_view'), onClose())}>
                  <span className="d-flex gap-2">
                    <Flexicon icon="git-branch-01" variant="line" size={15} />
                    <span>{t('organizational_view')}</span>
                  </span>
                </DropdownItem>
                <DropdownItem onClick={() => (setViewType('staff_hierarchy_view'), onClose())}>
                  <span className="d-flex gap-2">
                    <Flexicon icon="git-branch-01" variant="line" size={15} />
                    <span>{t('staff_hierarchy_view')}</span>
                  </span>
                </DropdownItem>
                <DropdownItem onClick={() => (setViewType('team_view'), onClose())}>
                  <span className="d-flex gap-2">
                    <Flexicon icon="git-branch-01" variant="line" size={15} />
                    <span>{t('team_view')}</span>
                  </span>
                </DropdownItem>
              </div>
            )}
          </Dropdown>

          <Button color="primary" className="d-flex align-items-center gap-1" onClick={() => setCreateFormVisible(true)}>
            <Flexicon icon="plus-circle" size={18} />
            <span className="d-none d-sm-inline">{t('add_new_entity', { entity: t('nodes') })}</span>
          </Button>
        </div>
      </div>
      <div className="mt-4">
        {data && viewType === 'organization_view' && <OrgHierarchyView data={data} name={name} afterNodeCreation={() => fetchData()} id={1} type={type} />}
        {data && viewType === 'staff_hierarchy_view' && <StaffHierarchyView data={data} name={name} afterNodeCreation={() => fetchData()} id={1} type={type} />}
        {data && viewType === 'team_view' && <TeamView data={data} name={name} afterNodeCreation={() => fetchData()} id={1} type={type} />}
      </div>
    </>
  );
}

export default Nodes;
