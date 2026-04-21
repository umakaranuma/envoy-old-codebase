'use client';
import { useEffect, useState } from 'react';
// import { Flexicon } from '@apptimus-ui/flexicon';
import { useRouter, useSearchParams } from 'next/navigation';
import { useTrans } from '@/helpers/services/lang/langService';
import PageHeading from '@/components/others/PageHeading';
import { toaster } from '@/helpers/services/toaster';
import { deletechartOfAccounts } from '../api-service';

// List Components
import ChartOfAccountsList from './ChartOfAccounts/ChartOfAccountsList';
import JournalEntriesList from './JournalEntries/JournalEntriesList';
import CashFlowStatementsList from './CashFlowStatements/CashFlowStatementsList';
import DebtorAgingSummaryReportList from './DebtorAgingSummaryReport/DebtorAgingSummaryReportList';

// Modal Components
import PolicyMadeList from './DailyTransactions/PolicyMadeList';
import CommissionEarnedList from './DailyTransactions/CommissionEarnedList';
import CommissionGivenList from './DailyTransactions/CommissionGivenList';
import GeneralLedgerList from './GeneralLedger/GeneralLedgerList';
import ChartOfAccountsCreate from './ChartOfAccounts/ChartOfAccountsCreate';
import { ChartOfAccountsEdit } from './ChartOfAccounts/ChartOfAccountsEdit';
import { ChartOfAccountsView } from './ChartOfAccounts/ChartOfAccountsView';

const MODULES = {
  COA: 'chart_of_accounts',
  JOURNAL: 'journal_entries',
  CASHFLOW: 'cash_flow_statements',
  DEBTORAGING: 'debtor_aging_summary_report_lists',
  DAILYTRANSACTION: 'daily_transactions',
  GENERALLEDGER: 'general_ledger',
};

const DAILY_SUBMODULES = {
  POLICYMADELIST: 'policy_made',
  COMMISSIONGIVENLIST: 'commission_given',
  COMMISSIONEARNEDLIST: 'commission_earned',
};

const MODULE_KEYS = Object.values(MODULES);

export default function Contacts() {
  const t = useTrans('label.general_ledger,otr.common');
  const router = useRouter();
  const searchParams = useSearchParams();
  const [tab, setTab] = useState(MODULES.COA);
  const [tableVers, setTableVers] = useState(0);
  const [subTab, setSubTab] = useState(DAILY_SUBMODULES.POLICYMADELIST);

  const [modalState, setModalState] = useState({
    module: '',
    type: '',
    id: null,
    key: 0,
    open: false,
  });

  useEffect(() => {
    const urlTab = searchParams.get('t') || MODULES.COA;
    setTab(urlTab);
  }, [searchParams]);

  const openModal = (type: any, module: any, id = null) => {
    setModalState({
      module,
      type,
      id,
      key: type === 'create' ? modalState.key + 1 : modalState.key,
      open: true,
    });
  };

  const closeModal = () => setModalState((prev) => ({ ...prev, open: false, id: null, type: '' }));

  const handleAfterSaveOrUpdate = () => {
    setTableVers((prev) => prev + 1);
    closeModal();
  };

  const handleOnDelete = async (deleteId: any, callback: any, setLoader: any, onClose: any) => {
    setLoader(true);
    const responseData = await deletechartOfAccounts(deleteId);
    setLoader(false);
    if (responseData.is_success) {
      toaster.success(t(responseData.message));
      callback();
      onClose();
    }
  };

  const handleTabClick = (key: any) => {
    setTab(key);
    router.push(`/finance/a/general-ledger?t=${key}`);
  };

  const renderTabButtons = () =>
    MODULE_KEYS.map((key) => (
      <div className={`il-box-tab-item ${tab === key ? 'active' : ''}`} onClick={() => handleTabClick(key)} key={key}>
        {t(key)}
      </div>
    ));

  const renderSubTabs = () => {
    if (tab !== MODULES.DAILYTRANSACTION) return null;

    const subTabs = Object.values(DAILY_SUBMODULES);

    return (
      <div className="mt-2 il-tab pb-2 p-2 d-flex gap-4 ms-2">
        {subTabs.map((sKey) => (
          <div key={sKey} className={`il-tab-item ${subTab === sKey ? 'active' : ''}`} onClick={() => setSubTab(sKey)}>
            {t(sKey)}
          </div>
        ))}
      </div>
    );
  };

  const renderListComponent = () => {
    const props = {
      tableVers,
      onView: (id: any) => openModal('view', tab, id),
      onEdit: (id: any) => openModal('edit', tab, id),
      handleOnDelete,
    };

    switch (tab) {
      case MODULES.COA:
        return <ChartOfAccountsList {...props} />;
      case MODULES.JOURNAL:
        return <JournalEntriesList {...props} />;
      case MODULES.CASHFLOW:
        return <CashFlowStatementsList {...props} />;
      case MODULES.DEBTORAGING:
        return <DebtorAgingSummaryReportList {...props} />;
      case MODULES.DAILYTRANSACTION:
        switch (subTab) {
          case DAILY_SUBMODULES.POLICYMADELIST:
            return <PolicyMadeList {...props} />;
          case DAILY_SUBMODULES.COMMISSIONGIVENLIST:
            return <CommissionGivenList {...props} />;
          case DAILY_SUBMODULES.COMMISSIONEARNEDLIST:
            return <CommissionEarnedList {...props} />;

          default:
            return null;
        }
      case MODULES.GENERALLEDGER:
        return <GeneralLedgerList {...props} />;
      default:
        return null;
    }
  };

  const renderModal = () => {
    const { module, type, id, key, open } = modalState;
    const commonProps = { isOpen: open, onCancel: closeModal, key };

    if (!open) return null;

    const viewEditProps = {
      viewId: id,
      editId: id,
      onClose: closeModal,
      setEditId: (eid: any) => openModal('edit', module, eid),
    };

    switch (`${type}-${module}`) {
      case `create-${MODULES.COA}`:
        return <ChartOfAccountsCreate {...commonProps} afterSave={handleAfterSaveOrUpdate} />;
      case `edit-${MODULES.COA}`:
        return <ChartOfAccountsEdit {...commonProps} editId={id || ''} afterUpdate={handleAfterSaveOrUpdate} />;
      case `view-${MODULES.COA}`:
        return <ChartOfAccountsView {...viewEditProps} isOpen={open} viewId={id || ''} />;
      default:
        return null;
    }
  };

  return (
    <>
      {/* Header */}
      <div className="page-header-breadcrumb custom-page-header">
        <PageHeading title={t('finance_management')} icon="core" />
      </div>

      <div className="panel mt-4">
        {/* Tabs */}
        <div className="il-box-tab">{renderTabButtons()}</div>

        {/* Sub Tabs (only for Daily Transactions) */}
        {renderSubTabs()}

        {/* List View */}
        {renderListComponent()}
      </div>

      {/* Modal */}
      {renderModal()}
    </>
  );
}
