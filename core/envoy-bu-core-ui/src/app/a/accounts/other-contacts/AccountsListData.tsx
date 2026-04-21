import { CustomizeColumn, useCustomizeColumn } from '@/components/others/CustomizeColumn';
import Table from '@/components/table-properties/Table';
import { ITablePropertyColumn } from '@/interface/ICommon';
import { useAsyncTable } from '@apptimus-ui/table';
import { useEffect, useMemo, useState } from 'react';
import { Dropdown, DropdownItem } from '@apptimus-ui/dropdown';
import { Flexicon } from '@apptimus-ui/flexicon';
import PageHeading from '@/components/others/PageHeading';
import { useTrans } from '@/helpers/services/lang/langService';
import { fetchCustomerContactTableData } from '../_utils/services';
import DeleteConfirmPop from '@/components/others/DeleteConfirmPop';
import { toaster } from '@/helpers/services/toaster';
import { deleteCustomerContact, setAsPrimaryCustomerContact } from '../_utils/api-service';
import { PopConfirm } from '@apptimus-ui/ui-element';

function AccountsListData({
  tableVers,
  viewId,
  afterSetPrimaryContact,
  afterDelete,
}: {
  tableVers?: number;
  onView?: Function;
  onEdit?: Function;
  handleOnDelete?: Function;
  viewId: string;
  afterSetPrimaryContact: Function;
  afterDelete: Function;
}) {
  const t = useTrans('label.accounts,otr.common');
  const tBe = useTrans('be.msg,be.error,be.attri');
  const tableName = 'other_contacts';
  const [isFullscreen, _setIsFullscreen] = useState(false);
  const [tableColumnVers, setTableColumnVers] = useState(0);
  const [_filterComKey, setFilterComKey] = useState(0);
  const [isCustColumnVisible, setIsCustColumnVisible] = useState(false);

  const handleOnDelete = async (deleteId: string, callback: Function, setLoader: Function, onClose: Function) => {
    setLoader(true);
    const responseData = await deleteCustomerContact(viewId, deleteId);
    setLoader(false);

    if (responseData.is_success) {
      toaster.success(tBe(responseData.message));
      callback();
      tableProperties.reload();
      afterDelete();
      onClose();
    }
  };

  const handleOnMarkAsPrimary = async (contactId: string, callback: Function, setLoader: Function, onClose: Function) => {
    setLoader(true);
    const responseData = await setAsPrimaryCustomerContact(viewId, contactId);
    setLoader(false);

    if (responseData.is_success) {
      toaster.success(tBe(responseData.message));
      callback();
      tableProperties.reload();
      afterSetPrimaryContact();
      onClose();
    }
  };

  const columns = useMemo<ITablePropertyColumn[]>(
    () => [
      // {
      //   id: 'title',
      //   header: t('title'),
      //   accessorKey: 'title',
      //   sort: true,
      // },
      {
        id: 'name',
        header: t('contact_person_name'),
        accessorKey: 'name',
        sort: true,
        visibilityLock: false,
      },
      {
        id: 'email',
        header: t('email'),
        accessorKey: 'email',
        sort: true,
      },
      {
        id: 'primary_contact',
        header: t('primary_contact'),
        accessorKey: 'primary_contact',
        sort: true,
      },
      {
        id: 'secondary_contact',
        header: t('secondary_contact'),
        accessorKey: 'secondary_contact',
        sort: true,
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
                {cell.is_primary === 0 && (
                  <PopConfirm
                    trigger={
                      <DropdownItem onClick={() => null}>
                        <span className="d-flex gap-2 w-100">
                          <Flexicon icon="check-verified-01" variant="line" size={17} />
                          <span>{t('mark_as_primary')}</span>
                        </span>
                      </DropdownItem>
                    }
                    onConfirm={(callback, setLoader) => {
                      handleOnMarkAsPrimary(cell.id, callback, setLoader, onClose);
                    }}
                    onCancel={(callback) => callback()}
                    placement="left"
                    title={t('confirm')}
                    body={t('are_you_sure_mark_as_primary')}
                    confirmText={t('yes')}
                    cancelText={t('cancel')}
                  />
                )}
              </span>
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
    loadData: async (props: any) => {
      return await fetchCustomerContactTableData({ ...props, id: viewId });
    },
    paginate: true,
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
      <div className={`data-table-container card custom-card ${isFullscreen ? 'dtc-fullscreen card-fullscreen' : 'mt-4'}`}>
        <Table heading={<PageHeading title={t('samples')} icon="sun-light" />} {...{ tableProperties, searchOption: false }} />
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

export default AccountsListData;
