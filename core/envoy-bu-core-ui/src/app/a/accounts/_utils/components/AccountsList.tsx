import { CustomizeColumn, useCustomizeColumn } from '@/components/others/CustomizeColumn';
import Table from '@/components/table-properties/Table';
import { ITablePropertyColumn } from '@/interface/ICommon';
import { useAsyncTable } from '@apptimus-ui/table';
import { useEffect, useMemo, useReducer, useState } from 'react';
import { Dropdown, DropdownItem } from '@apptimus-ui/dropdown';
import { Flexicon } from '@apptimus-ui/flexicon';
import { fetchCustomerTableData } from '../services';
import AccountFilter from './AccountFilter';
import PageHeading from '@/components/others/PageHeading';
import { useTrans } from '@/helpers/services/lang/langService';
import DeleteConfirmPop from '@/components/others/DeleteConfirmPop';
import { useRouter } from 'next/navigation';
import { dataReducer, filterReducer } from '@/helpers/services/dataReducer';
import { convertToMap, convertToString, formatPhoneNumber } from '@/helpers/services/commonService';
import { getAllCustomers, getAllPrimaryContact } from '../api-service';
import { getAllContacts } from '@/app/a/contacts/_utils/api-service';
import { Skeleton } from '@apptimus-ui/ui-element';
import ProfileInfo from '@/components/others/page-related/ProfileInfo';

function AccountsList({ tableVers, onEdit, onConfig, handleOnDelete }: { tableVers: number; onEdit: Function; onConfig: Function; handleOnDelete: Function }) {
  const t = useTrans('label.accounts,otr.common');
  const router = useRouter();
  const tableName = 'accounts';
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [isCustColumnVisible, setIsCustColumnVisible] = useState(false);
  const [isFilterVisible, setIsFilterVisible] = useState(false);
  const [tableColumnVers, setTableColumnVers] = useState(0);
  const [filterComKey, setFilterComKey] = useState(0);
  const [contactData, cDispatch] = useReducer(dataReducer, { loadingState: true, columnKeyVers: 0, data: {} });
  const [parentData, pDispatch] = useReducer(dataReducer, { loadingState: true, columnKeyVers: 0, data: {} });
  const [primaryContactData, pcDispatch] = useReducer(dataReducer, { loadingState: true, columnKeyVers: 0, data: {} });

  const columns = useMemo<ITablePropertyColumn[]>(
    () => [
      {
        id: 'code',
        header: t('account_code'),
        accessorKey: 'code',
        sort: true,
        visibilityLock: false,
      },
      {
        id: 'type',
        header: t('account_type'),
        accessorKey: 'type',
        sort: true,
      },
      {
        id: 'name',
        header: t('name'),
        accessorKey: 'name',
        sort: true,
        size: '10rem',
      },
      // {
      //   id: 'address',
      //   header: t('address'),
      //   accessorKey: 'address',
      //   cell: ({ cell, onClick }: { cell: any; onClick: Function }) => (
      //     <div className="text" onClick={() => onClick()}>
      //       <ContactCell type="address" {...{ contactData, cell }} />
      //     </div>
      //   ),
      //   size: '10rem',
      // },
      {
        id: 'email',
        header: t('email'),
        accessorKey: 'email',
        cell: ({ cell, onClick }: { cell: any; onClick: Function }) => (
          <div className="text" onClick={() => onClick()}>
            <ContactCell type="email" {...{ contactData, cell }} />
          </div>
        ),
        size: '10rem',
      },
      {
        id: 'primary_contact',
        header: t('primary_contact'),
        accessorKey: 'primary_contact',
        cell: ({ cell, onClick }: { cell: any; onClick: Function }) => (
          <div className="text text-nowrap" onClick={() => onClick()}>
            <ContactCell type="primary_contact" {...{ contactData, cell }} />
          </div>
        ),
      },
      // {
      //   id: 'secondary_contact',
      //   header: t('secondary_contact'),
      //   accessorKey: 'secondary_contact',
      //   cell: ({ cell, onClick }: { cell: any; onClick: Function }) => (
      //     <div className="text" onClick={() => onClick()}>
      //       <ContactCell type="secondary_contact" {...{ contactData, cell }} />
      //     </div>
      //   ),
      // },
      // {
      //   id: 'website_url',
      //   header: t('website'),
      //   accessorKey: 'website_url',
      //   cell: ({ cell }: { cell: any }) => (
      //     <div className="clickable-text text-primary">
      //       <ContactCell type="website_url" {...{ contactData, cell }} />
      //     </div>
      //   ),
      // },
      // {
      //   id: 'logo',
      //   header: t('logo'),
      //   accessorKey: 'logo',
      //   sort: true,
      // },
      {
        id: 'parent_account',
        header: t('parent_account'),
        accessorKey: 'parent_account',
        cell: ({ cell, onClick }: { cell: any; onClick: Function }) => (
          <div className="text" onClick={() => onClick()}>
            <ParentCell {...{ parentData, cell }} />
          </div>
        ),
      },
      // {
      //   id: 'remarks',
      //   header: t('remarks'),
      //   accessorKey: 'remarks',
      //   sort: true,
      // },
      // {
      //   id: 'primary_contact_id',
      //   header: t('primary_contact_person'),
      //   accessorKey: 'primary_contact_id',
      //   cell: ({ cell, onClick }: { cell: any; onClick: Function }) => (
      //     <div className="text" onClick={() => onClick()}>
      //       <PrimaryContactCell {...{ primaryContactData, cell }} />
      //     </div>
      //   ),
      // },
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
                <DropdownItem onClick={() => router.push(`/a/accounts/${cell.id}`)}>
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
                <DropdownItem onClick={() => router.push(`/a/accounts/${cell.id}/hierarchy`)}>
                  <span className="d-flex gap-2">
                    <Flexicon icon="git-branch-01" variant="line" size={17} />
                    <span>{t('make_hierarchy')}</span>
                  </span>
                </DropdownItem>
                <DropdownItem onClick={() => (setIsFullscreen(false), onConfig(cell), onClose())}>
                  <span className="d-flex gap-2">
                    <Flexicon icon="settings-01" variant="line" size={17} />
                    <span>{t('configure_customer')}</span>
                  </span>
                </DropdownItem>
              </span>
            )}
          </Dropdown>
        ),
        customizable: false,
      },
    ],
    [contactData.columnKeyVers, parentData.columnKeyVers, primaryContactData.columnKeyVers],
  );

  const tableColumns = useCustomizeColumn({ ...{ tableName, columns, tableColumnVers } });

  const tableProperties = useAsyncTable({
    columns: tableColumns,
    loadData: fetchCustomerTableData,
    paginate: true,
    rowSelection: true,
    rowSelectionProp: {
      key: 'id',
      mode: 'single',
      action: (selectedId: string) => router.push(`/a/accounts/${selectedId}`),
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
    const fetchContactData = async () => {
      const primaryContactIdString = convertToString(tableProperties.tableData, 'primary_contact_id');
      if (primaryContactIdString) {
        cDispatch({ type: 'set-loader' });
        try {
          const responseData = await getAllContacts({ ids: primaryContactIdString });
          if (responseData.is_success) {
            const contactDataMap = convertToMap(responseData.result, 'id');
            cDispatch({ data: contactDataMap, type: 'set-data' });
          }
        } catch (error) {
          console.log(error);
        }
      }
    };

    const fetchCustomerData = async () => {
      const parentIdString = convertToString(tableProperties.tableData, 'parent_id');
      if (parentIdString) {
        pDispatch({ type: 'set-loader' });
        try {
          const responseData = await getAllCustomers({ ids: parentIdString });

          if (responseData.is_success) {
            const parentDataMap = convertToMap(responseData.result, 'id');
            pDispatch({ data: parentDataMap, type: 'set-data' });
          }
        } catch (error) {
          console.log(error);
        }
      }
    };

    const fetchPrimaryContactData = async () => {
      const IdString = convertToString(tableProperties.tableData, 'id');

      if (IdString) {
        pcDispatch({ type: 'set-loader' });
        try {
          const responseData = await getAllPrimaryContact({ ids: IdString });

          if (responseData.is_success) {
            pcDispatch({ type: 'set-data', data: responseData.result });
          }
        } catch (error) {
          console.log(error);
        }
      }
    };

    fetchPrimaryContactData();
    fetchContactData();
    fetchCustomerData();
  }, [tableProperties.tableData]);

  return (
    <>
      <div className={`data-table-container card custom-card ${isFullscreen ? 'dtc-fullscreen card-fullscreen' : 'mt-4'}`}>
        <Table heading={<PageHeading title={t('accounts')} icon="sun-light" />} {...{ tableProperties, isFullscreen, setIsFullscreen, setIsCustColumnVisible, setIsFilterVisible }} />
      </div>
      <CustomizeColumn
        key={tableColumnVers}
        isOpen={isCustColumnVisible}
        tableName={tableName}
        columns={tableColumns}
        onClose={() => setIsCustColumnVisible(false)}
        afterUpdate={() => setTableColumnVers((prevTableColumnVers) => prevTableColumnVers + 1)}
      />
      <AccountFilter
        key={`filter-${filterComKey}`}
        isOpen={isFilterVisible}
        onClose={() => setIsFilterVisible(false)}
        onSubmit={(filterData: any, isReset: boolean) => (setIsFilterVisible(false), tableProperties.tableDispatch({ filterData, isReset }))}
      />
    </>
  );
}

export default AccountsList;

export const ContactCell = ({ contactData, cell, type }: { contactData: any; cell: any; type: 'address' | 'email' | 'primary_contact' | 'secondary_contact' | 'website_url' }) => {
  if (contactData.loadingState && cell.primary_contact_id) {
    return <Skeleton height="20px" />;
  }

  const contact = contactData?.data?.[cell.primary_contact_id] || [];

  if (type === 'website_url') {
    return (
      <div className="text">
        {contact.website_url ? (
          <div>
            <a href={contact.website_url} target="_blank" rel="noopener noreferrer" className="clickable-text">
              {contact.website_url}
            </a>
          </div>
        ) : (
          '-'
        )}
      </div>
    );
  }

  return (
    <div className="text">
      {type === 'address'
        ? contact.address
        : type === 'email'
          ? contact.email
          : type === 'primary_contact'
            ? contact.primary_contact
              ? formatPhoneNumber(contact.primary_contact)
              : '-'
            : type === 'secondary_contact'
              ? contact.secondary_contact
              : ''}
    </div>
  );
};

export const ParentCell = ({ parentData, cell }: { parentData: any; cell: any }) => {
  if (parentData.loadingState && cell.parent_id) {
    return <Skeleton height="20px" />;
  }

  const parent = parentData?.data?.[cell.parent_id] || [];

  return <div className="text">{parent.name || ''}</div>;
};

export const PrimaryContactCell = ({ primaryContactData, cell }: { primaryContactData: any; cell: any }) => {
  if (primaryContactData.loadingState && cell.id) {
    return <Skeleton height="20px" />;
  }

  const contact = primaryContactData?.data?.[cell.id] || [];

  if (contact.length > 0) {
    const person = contact[0];
    return <ProfileInfo imageKey={person.picture} title={person.name} subtitle={person.primary_contact} />;
  }

  return null;
};
