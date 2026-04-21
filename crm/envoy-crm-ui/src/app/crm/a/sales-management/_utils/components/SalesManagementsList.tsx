import { CustomizeColumn, useCustomizeColumn } from '@/components/others/CustomizeColumn';
import Table from '@/components/table-properties/Table';
import { ITablePropertyColumn } from '@/interface/ICommon';
import { useAsyncTable } from '@apptimus-ui/table';
import { useEffect, useMemo, useReducer, useState } from 'react';
import { Dropdown, DropdownItem } from '@apptimus-ui/dropdown';
import { Flexicon } from '@apptimus-ui/flexicon';
import { fetchOpportunityTableData } from '../services';
import SalesManagementsFilter from './SalesManagementsFilter';
import PageHeading from '@/components/others/PageHeading';
import { useTrans } from '@/helpers/services/lang/langService';
import { dataReducer, filterReducer } from '@/helpers/services/dataReducer';
import { convertToMap, convertToString, formatDate, hexToRgba } from '@/helpers/services/commonService';
import { getManyOpportunityTypes } from '../api-service';
import { Skeleton } from '@apptimus-ui/ui-element';
import RatingBlock from '@/components/others/page-related/RatingBlock';
import { getAllContacts, getAllCustomers, getAllEntities } from '@/api-services/common';
import Link from 'next/link';
import DeleteConfirmPop from '@/components/others/DeleteConfirmPop';
import { useRouter } from 'next/navigation';

function SalesManagementsList({ tableVers, onView, onEdit, handleOnDelete }: { tableVers: number; onView: Function; onEdit: Function; handleOnDelete: Function }) {
  const t = useTrans('label.sales_managements,otr.common');
  const tableName = 'sales_managements';
  const router = useRouter();
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [isCustColumnVisible, setIsCustColumnVisible] = useState(false);
  const [isFilterVisible, setIsFilterVisible] = useState(false);
  const [tableColumnVers, setTableColumnVers] = useState(0);
  const [filterComKey, setFilterComKey] = useState(0);
  const [opData, opDispatch] = useReducer(dataReducer, { loadingState: true, columnKeyVers: 0, data: {} });
  const [entityData, entityDispatch] = useReducer(dataReducer, { loadingState: true, columnKeyVers: 0, data: {} });
  const [cusData, cusDispatch] = useReducer(dataReducer, { loadingState: true, columnKeyVers: 0, data: {} });
  const [contData, contDispatch] = useReducer(dataReducer, { loadingState: true, columnKeyVers: 0, data: {} });

  const columns = useMemo<ITablePropertyColumn[]>(
    () => [
      {
        id: 'ref',
        header: t('sales_no'),
        accessorKey: 'code',
        sort: true,
        visibilityLock: false,
        styles: {
          body: {
            td: { textWrap: 'nowrap' },
          },
        },
      },
      {
        id: 'title',
        header: t('title'),
        accessorKey: 'title',
        size: '15rem',
        sort: true,
        visibilityLock: false,
      },
      {
        id: 'type',
        header: t('account_type'),
        accessorKey: 'type',
        sort: true,
        styles: {
          body: {
            td: { textWrap: 'nowrap' },
          },
        },
      },
      // {
      //   id: 'contact_info',
      //   header: t('contact_info'),
      //   accessorKey: 'contact_info',
      //   cell: ({ cell, onClick }: { cell: any; onClick: Function }) => {
      //     if (cell.customer_id) {
      //       return (
      //         <div className="text" onClick={() => onClick()}>
      //           <CustomerCell {...{ cusData, cell }} />
      //         </div>
      //       );
      //     } else if (cell.contact_id) {
      //       return (
      //         <div className="text" onClick={() => onClick()}>
      //           <ContactCell {...{ contData, cell }} />
      //         </div>
      //       );
      //     } else {
      //       return (
      //         <div className="text" onClick={() => onClick()}>
      //           <div>{cell.contact_number}</div>
      //           <div>{cell.email}</div>
      //         </div>
      //       );
      //     }
      //   },
      // },
      {
        id: 'channels',
        header: t('channels'),
        accessorKey: 'channel_name',
        sort: true,
        isHidden: true,
        styles: {
          body: {
            td: { textWrap: 'nowrap' },
          },
        },
      },
      // {
      //   id: 'campaign',
      //   header: t('campaign'),
      //   accessorKey: 'campaign',
      //   sort: true,
      // },
      // {
      //   id: 'opportunity_type',
      //   header: t('risk_type'),
      //   accessorKey: 'opportunity_type',
      //   cell: ({ cell, onClick }: { cell: any; onClick: Function }) => (
      //     <div className="text" onClick={() => onClick()}>
      //       <OpportunityTypesCell {...{ opData, cell }} />
      //     </div>
      //   ),
      // },
      {
        id: 'currency',
        header: t('currency'),
        accessorKey: 'currency_name',
        accessorFn: (row: any) => (
          <span>
            ({row.currency_symbol}) {row.currency_name}
          </span>
        ),
        sort: true,
        isHidden: true,
        styles: {
          body: {
            td: { textWrap: 'nowrap' },
          },
        },
      },
      {
        id: 'progress_stage',
        header: t('progress_stage'),
        accessorKey: 'sales_agent_id',
        cell: ({ cell, onClick }: any) => {
          return (
            <div
              className={`rounded-5 fw-semibold badge`}
              style={{ background: hexToRgba(cell.stage_color, 0.1), border: `1px solid ${hexToRgba(cell.stage_color, 0.4)}`, color: cell.stage_color }}
              onClick={onClick}
            >
              {cell.stage_name}
            </div>
          );
        },
        sort: true,
        visibilityLock: false,
      },
      {
        id: 'health',
        header: t('health'),
        accessorKey: 'health',
        cell: ({ cell, onClick }: any) => {
          return (
            <div onClick={onClick}>
              <RatingBlock value={cell.health_value ? cell.health_value : 0} />
            </div>
          );
        },
        sort: true,
      },
      {
        id: 'last_contacted_date',
        header: t('last_contacted_date'),
        accessorKey: 'last_contacted_date',
        sort: true,
        cell: ({ cell }: { cell: any }) => <div>{formatDate(cell.getValue()) || '-'}</div>,
      },

      {
        id: 'created_date',
        header: t('created_date'),
        accessorKey: 'created_at',
        cell: ({ cell, onClick }: { cell: any; onClick: Function }) => (
          <div className="text" onClick={() => onClick()}>
            <CreatedDateCell {...{ entityData, cell }} />
          </div>
        ),
        isHidden: true,
        styles: {
          body: {
            td: { textWrap: 'nowrap' },
          },
        },
      },
      {
        id: 'remarks',
        header: t('remarks'),
        accessorKey: 'remarks',
        sort: true,
        isHidden: true,
        size: '15rem',
      },
      {
        id: 'leads_activity_log',
        header: t('leads_activity_log'),
        accessorKey: 'leads_activity_log',
        cell: ({ cell }: any) => {
          return (
            <Link className="text-primary clickable-text-primary" href={`/crm/a/sales-managements/${cell.id}/histories`}>
              <div>{t('view_history')}</div>
            </Link>
          );
        },
        sort: true,
        isHidden: true,
        size: '15rem',
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
              <span className="t-action">
                <DropdownItem onClick={() => (setIsFullscreen(false), onView(cell.getValue()), onClose())}>
                  <span className="d-flex gap-2">
                    <Flexicon icon="eye" variant="line" size={17} />
                    <span>{t('view')}</span>
                  </span>
                </DropdownItem>
                <DropdownItem onClick={() => (setIsFullscreen(false), onEdit(cell.getValue()), onClose())}>
                  <span className="d-flex gap-2">
                    <Flexicon icon="pencil-line" variant="line" size={17} />
                    <span>{t('edit')}</span>
                  </span>
                </DropdownItem>
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
              </span>
            )}
          </Dropdown>
        ),
        customizable: false,
      },
    ],
    [opData.columnKeyVers, entityData.columnKeyVers, cusData.columnKeyVers, contData.columnKeyVers],
  );

  const tableColumns = useCustomizeColumn({ ...{ tableName, columns, tableColumnVers } });

  const tableProperties = useAsyncTable({
    columns: tableColumns,
    loadData: fetchOpportunityTableData,
    paginate: true,
    rowSelection: true,
    rowSelectionProp: {
      key: 'id',
      mode: 'single',
      action: (selectedId: string) => router.push(`/crm/a/sales-management/${selectedId}?f=list`),
    },
    customState: {
      initState: {
        filters: {},
      },
      reducer: (_: any, action: any) => filterReducer({ action, setFilterComKey }),
    },
  });

  useEffect(() => {
    tableProperties.reload();
  }, [tableColumnVers, tableVers]);

  useEffect(() => {
    const fetchOpportunityTypeData = async () => {
      const opportunityIdString = convertToString(tableProperties.tableData, 'id');

      if (opportunityIdString) {
        opDispatch({ type: 'set-loader' });
        try {
          const responseData = await getManyOpportunityTypes(opportunityIdString);

          if (responseData.is_success) {
            opDispatch({ data: responseData.result, type: 'set-data' });
          }
        } catch (error) {
          console.log(error);
        }
      }
    };

    const fetchEntityData = async () => {
      const entityIdString = convertToString(tableProperties.tableData, 'entity_id');

      if (entityIdString) {
        entityDispatch({ type: 'set-loader' });
        try {
          const responseData = await getAllEntities({ ids: entityIdString });

          if (responseData.is_success) {
            const entityDataMap = convertToMap(responseData.result, 'id');
            entityDispatch({ data: entityDataMap, type: 'set-data' });
          }
        } catch (error) {
          console.log(error);
        }
      }
    };

    const fetchContactData = async () => {
      const contactIdString = convertToString(tableProperties.tableData, 'contact_id');

      if (contactIdString) {
        contDispatch({ type: 'set-loader' });
        try {
          const responseData = await getAllContacts({ ids: contactIdString });

          if (responseData.is_success) {
            const contactDataMap = convertToMap(responseData.result, 'id');
            contDispatch({ data: contactDataMap, type: 'set-data' });
          }
        } catch (error) {
          console.log(error);
        }
      }
    };

    const fetchCustomerData = async () => {
      const customerIdString = convertToString(tableProperties.tableData, 'customer_id');

      if (customerIdString) {
        cusDispatch({ type: 'set-loader' });
        try {
          const responseData = await getAllCustomers({ ids: customerIdString });

          if (responseData.is_success) {
            const cusDataMap = convertToMap(responseData.result, 'id');
            cusDispatch({ data: cusDataMap, type: 'set-data' });
          }
        } catch (error) {
          console.log(error);
        }
      }
    };

    fetchCustomerData();
    fetchContactData();
    fetchEntityData();
    fetchOpportunityTypeData();
  }, [tableProperties.tableData]);

  return (
    <>
      <div className={`data-table-container card custom-card ${isFullscreen ? 'dtc-fullscreen card-fullscreen' : 'mt-4'}`}>
        <Table heading={<PageHeading title={t('opportunity_management')} icon="sun-light" />} {...{ tableProperties, isFullscreen, setIsFullscreen, setIsCustColumnVisible, setIsFilterVisible }} />
      </div>
      <CustomizeColumn
        key={tableColumnVers}
        isOpen={isCustColumnVisible}
        tableName={tableName}
        columns={tableColumns}
        onClose={() => setIsCustColumnVisible(false)}
        afterUpdate={() => setTableColumnVers((prevTableColumnVers) => prevTableColumnVers + 1)}
      />
      <SalesManagementsFilter
        key={`filter-${filterComKey}`}
        isOpen={isFilterVisible}
        onClose={() => setIsFilterVisible(false)}
        onSubmit={(filterData: any, isReset: boolean) => (setIsFilterVisible(false), tableProperties.tableDispatch({ filterData, isReset }))}
      />
    </>
  );
}

export default SalesManagementsList;

export const OpportunityTypesCell = ({ opData, cell }: { opData: any; cell: any }) => {
  if (opData.loadingState && cell.id) {
    return <Skeleton height="20px" />;
  }

  const opportunityTypes = opData?.data?.[cell.id] || [];

  if (opportunityTypes.length > 0) {
    return opportunityTypes.map((opportunityType: any) => (
      <div key={opportunityType.id} className="text mb-1" style={{ textWrap: 'nowrap' }}>
        {opportunityType.title}
      </div>
    ));
  }

  return null;
};

export const CreatedDateCell = ({ entityData, cell }: { entityData: any; cell: any }) => {
  if (entityData.loadingState && cell.entity_id) {
    return <Skeleton height="20px" />;
  }

  const entity = entityData?.data?.[cell.entity_id] || null;

  if (entity && entity.created_at) {
    return <span>{formatDate(entity.created_at) || ''}</span>;
  } else {
    return null;
  }
};

export const ContactCell = ({ contData, cell }: { contData: any; cell: any }) => {
  if (contData.loadingState && cell.contact_id) {
    return <Skeleton height="20px" />;
  }

  const contact = contData?.data?.[cell.contact_id] || null;

  if (contact) {
    return (
      <>
        <div className="text-muted fs-12">Contact</div>
        <div>{contact.name}</div>
      </>
    );
  } else {
    return null;
  }
};

export const CustomerCell = ({ cusData, cell }: { cusData: any; cell: any }) => {
  if (cusData.loadingState && cell.customer_id) {
    return <Skeleton height="20px" />;
  }

  const customer = cusData?.data?.[cell.customer_id] || null;

  if (customer) {
    return (
      <div className="text">
        <div className="text-muted fs-12">Account</div>
        <div>{customer.name}</div>
        {/* <div className='fs-12'>Code: {customer.code}</div> */}
      </div>
    );
  } else {
    return null;
  }
};
