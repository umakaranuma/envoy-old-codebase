import { CustomizeColumn, useCustomizeColumn } from '@/components/others/CustomizeColumn';
import Table from '@/components/table-properties/Table';
import { ITablePropertyColumn } from '@/interface/ICommon';
import { useAsyncTable } from '@apptimus-ui/table';
import { useEffect, useMemo, useState } from 'react';
import { Dropdown, DropdownItem } from '@apptimus-ui/dropdown';
import { Flexicon } from '@apptimus-ui/flexicon';
import PageHeading from '@/components/others/PageHeading';
import { useTrans } from '@/helpers/services/lang/langService';
import { fetchInvoiceTableData } from '../../../service';

function PreviewList({ onEdit }: { onEdit: Function }) {
  const t = useTrans('label.invoice,otr.common');
  const tableName = 'invoice';
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [isCustColumnVisible, setIsCustColumnVisible] = useState(false);
  const [tableColumnVers, setTableColumnVers] = useState(0);

  const columns = useMemo<ITablePropertyColumn[]>(
    () => [
      {
        id: 'invoice_no',
        header: t('invoice_no'),
        accessorKey: 'invoice_no',
        sort: true,
        visibilityLock: false,
      },
      {
        id: 'invoice_date',
        header: t('invoice_date'),
        accessorKey: 'invoice_date',
        sort: true,
      },
      {
        id: 'policy_info',
        header: t('policy_info'),
        accessorKey: 'policy_info',
        sort: true,
      },
      {
        id: 'insurer_info',
        header: t('insurer_info'),
        accessorKey: 'policy_info',
        sort: true,
      },
      {
        id: 'settled_amount',
        header: t('settled_amount'),
        accessorKey: 'settled_amount',
        sort: true,
      },
      {
        id: 'outstanding_amount',
        header: t('outstanding_amount'),
        accessorKey: 'outstanding_amount',
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
                <DropdownItem onClick={() => (setIsFullscreen(false), onEdit(cell.getValue()), onClose())}>
                  <span className="d-flex gap-2">
                    <Flexicon icon="pencil-line" variant="line" size={17} />
                    <span>{t('edit')}</span>
                  </span>
                </DropdownItem>
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
    loadData: fetchInvoiceTableData,
    paginate: true,
    rowSelection: false,
  });

  useEffect(() => {
    tableProperties.reload();
  }, [tableColumnVers]);

  return (
    <>
      <div className={`data-table-container card custom-card ${isFullscreen ? 'dtc-fullscreen card-fullscreen' : 'mt-4'}`}>
        <Table heading={<PageHeading title={t('payments')} icon="sun-light" />} {...{ tableProperties, isFullscreen, setIsFullscreen, setIsCustColumnVisible }} />
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

export default PreviewList;
