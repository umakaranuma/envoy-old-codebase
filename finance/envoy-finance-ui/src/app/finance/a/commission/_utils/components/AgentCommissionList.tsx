import { CustomizeColumn, useCustomizeColumn } from '@/components/others/CustomizeColumn';
import Table from '@/components/table-properties/Table';
import { ITablePropertyColumn } from '@/interface/ICommon';
import { useAsyncTable } from '@apptimus-ui/table';
import { useEffect, useMemo, useState } from 'react';
import PageHeading from '@/components/others/PageHeading';
import { useTrans } from '@/helpers/services/lang/langService';
import { fetchAgentCommissionTableData } from '../services';
import { hexToRgba, thousandSeparator } from '@/helpers/services/commonService';
import { getCurrency } from '@/helpers/services/currencyService';
import ProfileInfo from '@/components/others/page-related/ProfileInfo';
import { Dropdown, DropdownItem } from '@apptimus-ui/dropdown';
import { Flexicon } from '@apptimus-ui/flexicon';

function AgentCommissionList({ tableVers, onView, onSettle }: { tableVers: number; onView: Function; onEdit: Function; handleOnDelete: Function; onSettle: Function }) {
  const t = useTrans('label.commission,otr.common');
  const tableName = 'channel';
  const currency = getCurrency();
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [isCustColumnVisible, setIsCustColumnVisible] = useState(false);
  const [tableColumnVers, setTableColumnVers] = useState(0);
  const [_filterComKey, setFilterComKey] = useState(0);

  const columns = useMemo<ITablePropertyColumn[]>(
    () => [
      {
        id: 'user_name',
        header: t('agent_details'),
        accessorKey: 'user_name',
        sort: true,
        visibilityLock: false,
        cell: ({ cell }: { cell: any }) => {
          return <ProfileInfo title={cell.agent_name} subtitle={cell.agent_email} imageKey={cell.agent_picture} />;
        },
      },
      {
        id: 'invoice_number',
        header: t('dr_cr_note_number'),
        accessorKey: 'invoice_number',
        sort: true,
        visibilityLock: false,
        align: 'right',
        cell: ({ cell }: { cell: any }) => cell.getValue() || '-',
      },
      {
        id: 'invoice_amount',
        header: `${t('amount')} (${currency.code})`,
        accessorKey: 'invoice_amount',
        sort: true,
        align: 'right',
        cell: ({ cell }: { cell: any }) => <div className="amount-container">{thousandSeparator(cell.getValue()) || '-'}</div>,
      },
      {
        id: 'agent_commission_percent',
        header: t('agent_commission_persentage'),
        accessorKey: 'agent_commission_percent',
        sort: true,
        align: 'right',
        cell: ({ cell }: { cell: any }) => {
          if (cell.agent_commission_type === 'percentage') {
            return <div className="amount-container">{cell.getValue()} %</div>;
          } else {
            return <div className="amount-container">{thousandSeparator(cell.getValue())}</div>;
          }
        },
      },
      {
        id: 'revenue_recognized',
        header: `${t('recognized_amount')} (${currency.code})`,
        accessorKey: 'revenue_recognized',
        sort: true,
        align: 'right',
        cell: ({ cell }: { cell: any }) => <div className="amount-container">{thousandSeparator(cell.getValue()) || '-'}</div>,
      },
      {
        id: 'revenue_realized',
        header: `${t('revenue_realized_amount')} (${currency.code})`,
        accessorKey: 'revenue_realized',
        sort: true,
        align: 'right',
        cell: ({ cell }: { cell: any }) => <div className="amount-container">{thousandSeparator(cell.getValue()) || '-'}</div>,
      },
      {
        id: 'revised_amount_percent',
        header: `${t('revised_amount')}`,
        accessorKey: 'revised_amount_percent',
        sort: true,
        align: 'right',
        cell: ({ cell }: { cell: any }) => {
          if (cell.revised_amount_type === 'percentage') {
            return <div className="amount-container">{cell.getValue()} %</div>;
          } else {
            return <div className="amount-container">{`${currency.code} ${thousandSeparator(cell.getValue())}`}</div>;
          }
        },
      },
      {
        id: 'commission_deductible ',
        header: `${t('deductible')} (${currency.code})`,
        accessorKey: 'commission_deductible',
        sort: true,
        align: 'right',
        cell: ({ cell }: { cell: any }) => <div className="amount-container">{thousandSeparator(cell.getValue()) || '-'}</div>,
      },
      {
        id: 'paid_amount',
        header: `${t('paid_amount')} (${currency.code})`,
        accessorKey: 'paid_amount',
        sort: true,
        align: 'right',
        cell: ({ cell }: { cell: any }) => <div className="amount-container">{thousandSeparator(cell.getValue()) || '-'}</div>,
      },
      {
        id: 'outstanding',
        header: `${t('outstanding_amount')} (${currency.code})`,
        accessorKey: 'outstanding',
        sort: true,
        align: 'right',
        cell: ({ cell }: { cell: any }) => <div className="amount-container">{thousandSeparator(cell.getValue()) || '-'}</div>,
      },
      {
        id: 'status',
        header: t('status'),
        accessorKey: 'status',
        sort: true,
        cell: ({ cell, onClick }: any) => (
          <div
            className="rounded-5 fw-semibold badge"
            style={{ background: hexToRgba(cell?.status_color || '', 0.1), border: `1px solid ${cell?.status_color}`, color: cell?.status_color }}
            onClick={onClick}
          >
            {cell?.status}
          </div>
        ),
      },
      {
        header: t('action'),
        align: 'center',
        accessorKey: 'id',
        cell: ({ cell }: { cell: any }) => (
          <Dropdown
            trigger={
              <span className="action-icon">
                <Flexicon icon="dots-horizontal" variant="line" size={17} />
              </span>
            }
          >
            {(onClose: Function) => (
              <>
                <DropdownItem onClick={() => (setIsFullscreen(false), onSettle(cell.getValue()), onClose())}>
                  <span className="d-flex gap-2">
                    <span>{t('add_settlement')}</span>
                  </span>
                </DropdownItem>
              </>
            )}
          </Dropdown>
        ),
        customizable: false,
      },
    ],
    [],
  );

  const tableColumns = useCustomizeColumn({ ...{ tableName, columns, tableColumnVers } });

  const reducer = (_state: any, action: any) => {
    if (action.isReset) {
      setFilterComKey((prevFilterComKey) => prevFilterComKey + 1);
    }

    return {
      filters: action.filterData,
    };
  };

  const tableProperties = useAsyncTable({
    columns: tableColumns,
    loadData: fetchAgentCommissionTableData,
    paginate: true,
    rowSelection: true,
    rowSelectionProp: {
      key: 'id',
      mode: 'single',
      action: (selectedId: string) => onView(selectedId),
    },
    customState: {
      initState: {
        filters: {},
      },
      reducer: reducer,
    },
  });

  useEffect(() => {
    tableProperties.reload();
  }, [tableColumnVers, tableVers]);

  return (
    <>
      <div className={`data-table-container card custom-card ${isFullscreen ? 'dtc-fullscreen card-fullscreen' : 'mt-2'}`}>
        <Table heading={<PageHeading title={t('agent_commission')} icon="sun-light" />} {...{ tableProperties, isFullscreen, setIsFullscreen, setIsCustColumnVisible }} />
      </div>
      <CustomizeColumn
        key={tableColumnVers}
        isOpen={isCustColumnVisible}
        tableName={tableName}
        columns={tableColumns}
        onClose={() => setIsCustColumnVisible(false)}
        afterUpdate={() => setTableColumnVers((prevTableColumnVers) => prevTableColumnVers + 1)}
      />
    </>
  );
}

export default AgentCommissionList;
