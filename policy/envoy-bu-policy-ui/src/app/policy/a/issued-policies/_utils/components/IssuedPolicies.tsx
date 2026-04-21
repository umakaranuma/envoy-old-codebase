'use client';
import PageHeading from '@/components/others/PageHeading';
import { useTrans } from '@/helpers/services/lang/langService';
import React, { useState } from 'react';
import { Button } from '@apptimus-ui/ui-element';
import { Flexicon } from '@apptimus-ui/flexicon';
import SelectPolicyRequestType from '../../../policy-request/_utils/components/create/SelectPolicyRequestType';
import AccountsCreate from '@/components/others/common/accounts/AccountsCreate';
import IssuedPoliciesList from './IssuedPoliciesList';
import { useRouter } from 'next/navigation';
import SalesManagementsCreate from '@/components/others/common/lead/SalesManagementsCreate';
import { INewCustomerInfo } from '../../../policy-request/_utils/model';

function IssuedPolicies({ settingId }: { settingId: string }) {
  const t = useTrans('label.issued_policies,otr.common,be.msg');
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [createNewCustomer, setIsCreateNewCustomer] = useState(false);
  const [createNewLead, setIsCreateNewLead] = useState(false);
  const [newCustomerInfo, setNewCustomerInfo] = useState<INewCustomerInfo | null>(null);

  const router = useRouter();

  const handleOpenCreateCustomer = () => {
    setIsCreateOpen(false);
    setTimeout(() => {
      setIsCreateNewCustomer(true);
    }, 100);
  };

  const handleOpenCreatePolicy = (data: INewCustomerInfo) => {
    setNewCustomerInfo(data);
    setIsCreateNewCustomer(false);
    setTimeout(() => {
      setIsCreateOpen(true);
    }, 100);
  };
  // const handleCreateLead = () => {
  //   setIsCreateOpen(false);
  //   setTimeout(() => {
  //     setIsCreateNewLead(true);
  //   }, 100);
  // };

  return (
    <>
      <div className="page-header-breadcrumb custom-page-header">
        <PageHeading title={t('policy_management')} icon="core" />
        <div className="d-flex gap-2 align-items-center">
          <Button color="primary" className="d-flex align-items-center gap-1" onClick={() => setIsCreateOpen(true)}>
            <Flexicon icon="plus-circle" size={18} />
            <span className="d-none d-sm-inline">{t('add_new_entity', { entity: t('policy') })}</span>
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
      <IssuedPoliciesList
        onView={(approval_id: string) => {
          router.push(`/policy/a/issued-policies/${approval_id}`);
        }}
      />
      {isCreateOpen && (
        <SelectPolicyRequestType isOpen={true} onCancel={() => setIsCreateOpen(false)} issuedPolicy={true} handleOpenCreateCustomer={handleOpenCreateCustomer} newCustomerInfo={newCustomerInfo} />
      )}
      {createNewCustomer && (
        <AccountsCreate onCreatedCustomer={(data: any) => handleOpenCreatePolicy(data)} isOpen={createNewCustomer} onCancel={() => setIsCreateNewCustomer(false)} afterSave={() => {}} />
      )}
      {createNewLead && <SalesManagementsCreate {...{ defaultStageId: null }} settingId={settingId} isOpen={createNewLead} onCancel={() => setIsCreateNewLead(false)} afterSave={() => {}} />}
    </>
  );
}

export default IssuedPolicies;
