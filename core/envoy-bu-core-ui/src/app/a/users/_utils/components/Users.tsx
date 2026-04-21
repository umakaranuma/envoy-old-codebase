'use client';

import PageHeading from '@/components/others/PageHeading';
import { useTrans } from '@/helpers/services/lang/langService';
import { Flexicon } from '@apptimus-ui/flexicon';
import { Button } from '@apptimus-ui/ui-element';
import React, { useState } from 'react';
import IndexTable from './IndexTable';
import ViewUser from './ViewUser';
import { Dropdown, DropdownItem } from '@apptimus-ui/dropdown';
import InvitationList from './InvitationList';
import Invite from './Invite';
import Edit from './Edit';
import HierarchyView from '../../hierarchy/HierarchyView';
import SalesTeamCreate from './sales-team/SalesTeamCreate';
import AddMemberInTeam from './sales-team/AddMemberInTeam';

function Users() {
  const t = useTrans('label.user,otr.common');
  const [currentViewId, setCurrentViewId] = useState('');
  const [currentEditId, setCurrentEditId] = useState('');
  const [viewType, setViewType] = useState('list_view');
  const [inviteVisible, setInviteVisible] = useState(false);
  const [inviteListVisible, setInviteListVisible] = useState(false);
  const [tableVers, setTableVers] = useState(0);
  const [inviteKey, setInviteKey] = useState(0);
  const [editKey, setEditKey] = useState(0);
  const [createSalesTeamKey, setSalesTeamKey] = useState(0);
  const [AddSalesTeamKey, setAddSalesTeamKey] = useState(0);
  const [createSaleTeamVisible, setCreateSaleTeamVisible] = useState(false);
  const [addMembersInTeamVisible, setAddMembersInTeamVisible] = useState(false);
  const [selectedUserId, setSelectedUserId] = useState('');

  const handleAfterAddTeamSave = () => {
    setTableVers((prevTableVers) => prevTableVers + 1);
    setSalesTeamKey((prevCreateFormKey) => prevCreateFormKey + 1);
    setAddSalesTeamKey((prevCreateFormKey) => prevCreateFormKey + 1);
    setAddMembersInTeamVisible(false);
    setSelectedUserId('');
  };
  const handleTeamFormOnCancel = () => {
    setSalesTeamKey((prevCreateFormKey) => prevCreateFormKey + 1);
    setAddSalesTeamKey((prevCreateFormKey) => prevCreateFormKey + 1);
    setCreateSaleTeamVisible(false);
    setAddMembersInTeamVisible(false);
    setSelectedUserId('');
  };

  const handleAfterUpdate = () => {
    setCurrentEditId('');
    setTableVers((prevTableVers) => prevTableVers + 1);
  };

  const onCancelInvite = () => {
    setInviteVisible(false);
    setInviteKey((prevValue) => prevValue + 1);
  };

  const handleAfterSave = () => {
    setTableVers((prevTableVers) => prevTableVers + 1);
    setInviteKey((prevCreateFormKey) => prevCreateFormKey + 1);
  };

  const getPageTitle = () => {
    switch (viewType) {
      case 'hierarchy_view':
        return t('staff_hierarchy_view');
      case 'team_view':
        return t('team_hierarchy_view');
      case 'list_view':
      default:
        return t('user_staff');
    }
  };

  return (
    <>
      <div className="page-header-breadcrumb custom-page-header">
        <PageHeading title={getPageTitle()} icon="core" />
        <div className="d-flex flex-row justify-content-end align-items-center gap-3">
          <Dropdown
            width="180px"
            trigger={
              <Button className="d-flex align-items-center gap-1">
                <Flexicon icon={viewType === 'team_view' ? 'git-branch-01' : viewType === 'hierarchy_view' ? 'git-branch-01' : 'dotpoints-01'} variant="line" size={15} />
                <span className="d-none d-sm-inline">
                  {viewType === 'list_view' && t('list_view')}
                  {viewType === 'hierarchy_view' && t('staff_hierarchy_view')}
                  {viewType === 'team_view' && t('team_view')}
                </span>
                <Flexicon icon="chevron-down" variant="line" size={18} />
              </Button>
            }
          >
            {(onClose: Function) => (
              <>
                <DropdownItem onClick={() => (setViewType('list_view'), onClose())}>
                  <span className="d-flex gap-2">
                    <Flexicon icon="dotpoints-01" variant="line" size={18} />
                    <span>{t('list_view')}</span>
                  </span>
                </DropdownItem>
                <DropdownItem onClick={() => (setViewType('hierarchy_view'), onClose())}>
                  <span className="d-flex gap-2">
                    <Flexicon icon="git-branch-01" variant="line" size={18} />
                    <span>{t('staff_hierarchy_view')}</span>
                  </span>
                </DropdownItem>
                <DropdownItem onClick={() => (setViewType('team_view'), onClose())}>
                  <span className="d-flex gap-2">
                    <Flexicon icon="git-branch-01" variant="line" size={18} />
                    <span>{t('team_view')}</span>
                  </span>
                </DropdownItem>
              </>
            )}
          </Dropdown>
          <Button className="d-flex align-items-center gap-1" onClick={() => setInviteListVisible(true)}>
            <Flexicon icon="dotpoints-01" variant="line" size={18} />
            <span className="d-none d-sm-inline">{t('invitation_list')}</span>
          </Button>
          <Button className="d-flex align-items-center gap-1" onClick={() => setInviteVisible(true)}>
            <Flexicon icon="plus-circle" size={18} />
            <span className="d-none d-sm-inline">{t('invite_user')}</span>
          </Button>
          <Button
            className="d-flex align-items-center gap-1"
            onClick={() => {
              setCreateSaleTeamVisible(true);
            }}
          >
            <Flexicon icon="plus-circle" size={18} />
            <span className="d-none d-sm-inline">{t('create_sales_team')}</span>
          </Button>
        </div>
      </div>

      {viewType === 'list_view' && (
        <IndexTable
          tableVers={tableVers}
          onView={(id: any) => setCurrentViewId(id)}
          onEdit={(id: any) => setCurrentEditId(id)}
          setSelectedUserId={setSelectedUserId}
          setAddMembersInTeamVisible={setAddMembersInTeamVisible}
        />
      )}
      {viewType === 'hierarchy_view' && <HierarchyView />}
      {viewType === 'team_view' && <HierarchyView />}

      <ViewUser viewId={currentViewId} isOpen={currentViewId !== ''} onCancel={() => setCurrentViewId('')} setEditId={(id: any) => setCurrentEditId(id)} />

      {inviteListVisible && <InvitationList isOpen={inviteListVisible} onCancel={() => setInviteListVisible(false)} />}
      <Invite isOpen={inviteVisible} onCancel={onCancelInvite} afterSave={handleAfterSave} key={inviteKey} />
      <Edit
        key={`edit-${editKey}`}
        viewId={currentEditId}
        isOpen={currentEditId !== ''}
        onCancel={() => {
          setCurrentEditId(''), setEditKey((prevValue) => prevValue + 1);
        }}
        afterSave={handleAfterUpdate}
      />

      {createSaleTeamVisible && <SalesTeamCreate key={createSalesTeamKey} isOpen={createSaleTeamVisible} onCancel={handleTeamFormOnCancel} afterSave={handleAfterAddTeamSave} />}
      {addMembersInTeamVisible && (
        <AddMemberInTeam key={`add-member-${AddSalesTeamKey}`} isOpen={addMembersInTeamVisible} onCancel={handleTeamFormOnCancel} afterSave={handleAfterAddTeamSave} userId={selectedUserId} />
      )}
    </>
  );
}

export default Users;
