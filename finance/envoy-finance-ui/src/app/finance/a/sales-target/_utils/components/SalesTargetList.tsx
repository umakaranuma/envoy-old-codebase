import { CustomizeColumn, useCustomizeColumn } from '@/components/others/CustomizeColumn';
import Table from '@/components/table-properties/Table';
import { ITablePropertyColumn } from '@/interface/ICommon';
import { useAsyncTable } from '@apptimus-ui/table';
import { useEffect, useMemo, useState } from 'react';
import PageHeading from '@/components/others/PageHeading';
import { useTrans } from '@/helpers/services/lang/langService';
import { fetchAllAgentSalesTarget, fetchAllTeamSalesTarget } from '../services';
import { Dropdown, DropdownItem } from '@apptimus-ui/dropdown';
import { Flexicon } from '@apptimus-ui/flexicon';
import DeleteConfirmPop from '@/components/others/DeleteConfirmPop';
import { thousandSeparator } from '@/helpers/services/commonService';
import { getCurrency } from '@/helpers/services/currencyService';

function SalesTargetList({
  agentTableVers,
  teamTableVers,
  activetab,
  onView,
  onEdit,
  handleOnDelete,
}: {
  agentTableVers: number;
  teamTableVers: number;
  activetab: string;
  onView?: Function;
  onEdit?: Function;
  handleOnDelete?: Function;
}) {
  const t = useTrans('label.sales_target,otr.common');
  const currency = getCurrency();
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [isCustColumnVisible, setIsCustColumnVisible] = useState(false);
  const [tableColumnVers, setTableColumnVers] = useState(0);

  function getMonthName(monthNumber: number) {
    const monthKeys = ['january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november', 'december'];

    if (monthNumber >= 1 && monthNumber <= 12) {
      return t(monthKeys[monthNumber - 1]);
    }

    return '';
  }

  const agentColumns = useMemo<ITablePropertyColumn[]>(
    () => [
      {
        id: 'agent_name',
        header: t('agent_info'),
        accessorKey: 'agent_name',
        sort: true,
        visibilityLock: false,
      },
      {
        id: 'year',
        header: t('target_period'),
        accessorKey: 'year',
        sort: true,
        cell: ({ cell }: { cell: any }) => {
          const period_type = cell.period_type;
          return period_type === 'monthly' ? (
            <>
              {getMonthName(cell.month)} {cell.year}
            </>
          ) : (
            <>{cell.year}</>
          );
        },
      },
      {
        id: 'target_amount',
        header: `${t('target_amount')} (${currency.code})`,
        accessorKey: 'target_amount',
        sort: true,
        align: 'right',
        cell: ({ cell }: { cell: any }) => <div className="amount-container">{thousandSeparator(cell.getValue()) || '-'}</div>,
      },
      {
        id: 'achieved',
        header: `${t('achieved')} (${currency.code})`,
        accessorKey: 'achieved',
        sort: true,
        align: 'right',
        cell: ({ cell }: { cell: any }) => <div className="amount-container">{thousandSeparator(cell.getValue()) || '-'}</div>,
      },
      ...(onView || onEdit || handleOnDelete
        ? [
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
                    <span className="t-action">
                      {onView && (
                        <DropdownItem onClick={() => (setIsFullscreen(false), onView(cell.getValue()), onClose())}>
                          <span className="d-flex gap-2">
                            <Flexicon icon="eye" variant="line" size={17} />
                            <span>{t('view')}</span>
                          </span>
                        </DropdownItem>
                      )}
                      {onEdit && (
                        <DropdownItem onClick={() => (setIsFullscreen(false), onEdit(cell.getValue()), onClose())}>
                          <span className="d-flex gap-2">
                            <Flexicon icon="pencil-line" variant="line" size={17} />
                            <span>{t('edit')}</span>
                          </span>
                        </DropdownItem>
                      )}
                      {handleOnDelete && (
                        <DeleteConfirmPop
                          trigger={
                            <DropdownItem onClick={() => null}>
                              <span className="d-flex gap-2 w-100">
                                <Flexicon icon="trash-03" variant="line" size={17} />
                                <span>{t('delete')}</span>
                              </span>
                            </DropdownItem>
                          }
                          deleteId={cell.id}
                          {...{ handleOnDelete, onClose }}
                        />
                      )}
                    </span>
                  )}
                </Dropdown>
              ),
              customizable: false,
            },
          ]
        : []),
    ],
    [],
  );

  const teamColumns = useMemo<ITablePropertyColumn[]>(
    () => [
      {
        id: 'team_name',
        header: t('team_name'),
        accessorKey: 'team_name',
        sort: true,
        visibilityLock: false,
      },
      {
        id: 'year',
        header: t('target_period'),
        accessorKey: 'year',
        sort: true,
        cell: ({ cell }: { cell: any }) => {
          const period_type = cell.period_type;
          return period_type === 'monthly' ? (
            <>
              {getMonthName(cell.month)} {cell.year}
            </>
          ) : (
            <>{cell.year}</>
          );
        },
      },
      {
        id: 'target_amount',
        header: `${t('target_amount')} (${currency.code})`,
        accessorKey: 'target_amount',
        sort: true,
        align: 'right',
        cell: ({ cell }: { cell: any }) => <div className="amount-container">{thousandSeparator(cell.getValue()) || '-'}</div>,
      },
      {
        id: 'achieved',
        header: `${t('achieved')} (${currency.code})`,
        accessorKey: 'achieved',
        sort: true,
        align: 'right',
        cell: ({ cell }: { cell: any }) => <div className="amount-container">{thousandSeparator(cell.getValue()) || '-'}</div>,
      },
      ...(onView || onEdit || handleOnDelete
        ? [
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
                    <span className="t-action">
                      {onView && (
                        <DropdownItem onClick={() => (setIsFullscreen(false), onView(cell.getValue()), onClose())}>
                          <span className="d-flex gap-2">
                            <Flexicon icon="eye" variant="line" size={17} />
                            <span>{t('view')}</span>
                          </span>
                        </DropdownItem>
                      )}
                      {onEdit && (
                        <DropdownItem onClick={() => (setIsFullscreen(false), onEdit(cell.getValue()), onClose())}>
                          <span className="d-flex gap-2">
                            <Flexicon icon="pencil-line" variant="line" size={17} />
                            <span>{t('edit')}</span>
                          </span>
                        </DropdownItem>
                      )}
                      {handleOnDelete && (
                        <DeleteConfirmPop
                          trigger={
                            <DropdownItem onClick={() => null}>
                              <span className="d-flex gap-2 w-100">
                                <Flexicon icon="trash-03" variant="line" size={17} />
                                <span>{t('delete')}</span>
                              </span>
                            </DropdownItem>
                          }
                          deleteId={cell.id}
                          {...{ handleOnDelete, onClose }}
                        />
                      )}
                    </span>
                  )}
                </Dropdown>
              ),
              customizable: false,
            },
          ]
        : []),
    ],
    [],
  );

  const agentTableColumns = useCustomizeColumn({ tableName: 'sales_target_agent', columns: agentColumns, tableColumnVers });
  const teamTableColumns = useCustomizeColumn({ tableName: 'sales_target_team', columns: teamColumns, tableColumnVers });

  const teamTableProperties = useAsyncTable({
    columns: teamTableColumns,
    loadData: fetchAllTeamSalesTarget,
    paginate: true,
    rowSelection: true,
    rowSelectionProp: {
      key: 'id',
      mode: 'single',
      action: (selectedId: string) => onView?.(selectedId),
    },
  });
  const agentTableProperties = useAsyncTable({
    columns: agentTableColumns,
    loadData: fetchAllAgentSalesTarget,
    paginate: true,
    rowSelection: true,
    rowSelectionProp: {
      key: 'id',
      mode: 'single',
      action: (selectedId: string) => onView?.(selectedId),
    },
  });

  useEffect(() => {
    teamTableProperties.reload();
  }, [tableColumnVers, teamTableVers]);

  useEffect(() => {
    agentTableProperties.reload();
  }, [tableColumnVers, agentTableVers]);

  return (
    <>
      <div className={`data-table-container card custom-card ${isFullscreen ? 'dtc-fullscreen card-fullscreen' : 'mt-4'}`}>
        {activetab === 'individual' ? (
          <Table heading={<PageHeading title={t('sales_target')} icon="sun-light" />} {...{ tableProperties: agentTableProperties, isFullscreen, setIsFullscreen, setIsCustColumnVisible }} />
        ) : (
          <Table heading={<PageHeading title={t('sales_target')} icon="sun-light" />} {...{ tableProperties: teamTableProperties, isFullscreen, setIsFullscreen, setIsCustColumnVisible }} />
        )}
      </div>
      <CustomizeColumn
        key={tableColumnVers}
        isOpen={isCustColumnVisible}
        tableName={activetab === 'individual' ? 'sales_target_agent' : 'sales_target_team'}
        columns={activetab === 'individual' ? agentTableColumns : teamTableColumns}
        onClose={() => setIsCustColumnVisible(false)}
        afterUpdate={() => setTableColumnVers((prevTableColumnVers) => prevTableColumnVers + 1)}
      />
    </>
  );
}

export default SalesTargetList;
