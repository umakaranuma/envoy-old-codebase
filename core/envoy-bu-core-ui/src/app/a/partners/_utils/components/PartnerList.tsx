import { CustomizeColumn, useCustomizeColumn } from '@/components/others/CustomizeColumn';
import Table from '@/components/table-properties/Table';
import { ITablePropertyColumn } from '@/interface/ICommon';
import { useAsyncTable } from '@apptimus-ui/table';
import { useEffect, useMemo, useState } from 'react';
import { Dropdown, DropdownItem } from '@apptimus-ui/dropdown';
import { Flexicon } from '@apptimus-ui/flexicon';
import PageHeading from '@/components/others/PageHeading';
import { useTrans } from '@/helpers/services/lang/langService';
import DeleteConfirmPop from '@/components/others/DeleteConfirmPop';
import { fetchPartnerTableData } from '../service';
import ProfileInfo from '@/components/others/page-related/ProfileInfo';

function PartnerList({ tableVers, onView, onEdit, handleOnDelete }: { tableVers: number; onView: Function; onEdit: Function; handleOnDelete: Function }) {
  const t = useTrans('label.partners,otr.common');
  const tableName = 'partners';
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [isCustColumnVisible, setIsCustColumnVisible] = useState(false);
  const [tableColumnVers, setTableColumnVers] = useState(0);

  const columns = useMemo<ITablePropertyColumn[]>(
    () => [
      {
        id: 'partner',
        header: t('partner'),
        accessorKey: 'partner',
        visibilityLock: false,
        cell: ({ cell }: any) => {
          return (
            <div>
              <ProfileInfo imageKey={`${cell.logo}`} width={50} height={50} title={cell.name} subtitle={cell.email} shape="square" defaultImage="/images/default-profile.png" />
            </div>
          );
        },
      },
      {
        id: 'contact_no',
        header: t('contact_number'),
        accessorKey: 'contact_no',
        sort: true,
        cell: ({ cell }: any) => <div>{cell.getValue() || '-'}</div>,
      },
      {
        id: 'address',
        header: t('address'),
        accessorKey: 'address',
        sort: true,
      },
      {
        id: 'contact_no',
        header: t('primary_contact_info'),
        accessorKey: 'contact_no',
        sort: true,
        cell: ({ cell }: any) => <ProfileInfo imageKey={cell?.primary_contact?.picture} title={cell?.primary_contact?.name} subtitle={cell?.primary_contact?.primary_contact} />,
      },
      {
        id: 'number_of_products',
        header: t('number_of_products'),
        accessorKey: 'number_of_products',
        sort: true,
        align: 'right',
        cell: ({ cell }: any) => <div>{cell.getValue() || '0'}</div>,
      },
      {
        id: 'website',
        header: t('website'),
        accessorKey: 'website',
        sort: true,
        align: 'center',
        cell: ({ cell }: any) => {
          return (
            <a href={cell.website} target="_blank" rel="noopener noreferrer" className="clickable-text">
              <Flexicon icon="link-03" variant="line" size={18} />
            </a>
          );
        },
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
    [],
  );

  const tableColumns = useCustomizeColumn({ ...{ tableName, columns, tableColumnVers } });

  const tableProperties = useAsyncTable({
    columns: tableColumns,
    loadData: (props: any) => fetchPartnerTableData(props),
    paginate: true,
    rowSelection: true,
    rowSelectionProp: {
      key: 'id',
      mode: 'single',
      action: (selectedId: string) => onView(selectedId),
    },
  });

  useEffect(() => {
    tableProperties.reload();
    tableProperties.reset({ type: 'row-selection' });
  }, [tableColumnVers, tableVers]);

  return (
    <>
      <div className={`data-table-container card custom-card ${isFullscreen ? 'dtc-fullscreen card-fullscreen' : 'mt-4'}`}>
        <Table heading={<PageHeading title={t('partners')} icon="sun-light" />} {...{ tableProperties, isFullscreen, setIsFullscreen, setIsCustColumnVisible }} />
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

export default PartnerList;
