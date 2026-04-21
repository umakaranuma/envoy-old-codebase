'use client';
import PageHeading from '@/components/others/PageHeading';
import { useTrans } from '@/helpers/services/lang/langService';
import React, { useState } from 'react';
import { Button } from '@apptimus-ui/ui-element';
import { Flexicon } from '@apptimus-ui/flexicon';
import PolicyRequestList from './PolicyRequestList';
import SelectPolicyRequestType from './create/SelectPolicyRequestType';
import AccountsCreate from '@/components/others/common/accounts/AccountsCreate';
import SalesManagementsCreate from '@/components/others/common/lead/SalesManagementsCreate';
import IssuePolicy from './IssuePolicy';
import { INewCustomerInfo } from '../model';

function PolicyRequest({ settingId }: { settingId: string }) {
  const t = useTrans('label.policy_request,otr.common,be.msg');
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [createNewCustomer, setIsCreateNewCustomer] = useState(false);
  const [createNewLead, setIsCreateNewLead] = useState(false);
  const [issuePolicyId, setIssuePolicyId] = useState<string | null>(null);
  const [tableVersion, setTableVersion] = useState(0);
  // const [isDocExtractionOpen, setIsDocExtractionOpen] = useState(false);
  // const [createKey, setCreateKey] = useState(0);
  // const [docExtractionData, setDocExtractionData] = useState<any>(null);
  // const [currentPolicyRequestId, setCurrentPolicyRequestId] = useState<string | null>(null);
  const [newCustomerInfo, setNewCustomerInfo] = useState<INewCustomerInfo | null>(null);

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

  return (
    <>
      <div className="page-header-breadcrumb custom-page-header">
        <PageHeading title={t('policy_request')} icon="core" />
        <div className="d-flex gap-2 align-items-center">
          <Button color="primary" className="d-flex align-items-center gap-1" onClick={() => setIsCreateOpen(true)}>
            <Flexicon icon="plus-circle" size={18} />
            <span className="d-none d-sm-inline">{t('request_policy')}</span>
          </Button>
        </div>
      </div>
      {isCreateOpen && (
        <SelectPolicyRequestType newCustomerInfo={newCustomerInfo} isOpen={true} onCancel={() => setIsCreateOpen(false)} issuedPolicy={false} handleOpenCreateCustomer={handleOpenCreateCustomer} />
      )}
      {createNewCustomer && (
        <AccountsCreate onCreatedCustomer={(data: any) => handleOpenCreatePolicy(data)} isOpen={createNewCustomer} onCancel={() => setIsCreateNewCustomer(false)} afterSave={() => {}} />
      )}
      <PolicyRequestList
        onIssue={(id: string) => setIssuePolicyId(id)}
        tableVersion={tableVersion}
        // handleDocExtraction={(_data: any) => {
        //   // setDocExtractionData(data);
        //   // setIsDocExtractionOpen(true);
        // }}
        // setCurrentPolicyRequestId={()=>{}}
      />
      {createNewLead && <SalesManagementsCreate {...{ defaultStageId: null }} settingId={settingId} isOpen={createNewLead} onCancel={() => setIsCreateNewLead(false)} afterSave={() => {}} />}
      {issuePolicyId && <IssuePolicy isOpen={!!issuePolicyId} policyId={issuePolicyId} onCancel={() => setIssuePolicyId(null)} afterSave={() => setTableVersion((prev) => prev + 1)} />}

      {/* <DocExtractionModal
        isOpen={isDocExtractionOpen}
        onCancel={() => {
          setIsDocExtractionOpen(false);
          setCreatKey((prev) => prev + 1);
        }}
        afterSave={() => {
          setIsDocExtractionOpen(false);
          setCreatKey((prev) => prev + 1);
        }}
        policyRequestId={currentPolicyRequestId || ''}
        docExtractionData={docExtractionData || null}
        key={creatKey}
      /> */}
      {issuePolicyId && (
        <IssuePolicy
          isOpen={!!issuePolicyId}
          policyId={issuePolicyId}
          onCancel={() => setIssuePolicyId(null)}
          afterSave={() => {
            setIssuePolicyId(null), setTableVersion((prev) => prev + 1);
          }}
        />
      )}
    </>
  );
}

export default PolicyRequest;
