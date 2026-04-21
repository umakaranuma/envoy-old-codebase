import { useCustomizeColumn } from '@/components/others/CustomizeColumn';
import Table from '@/components/table-properties/Table';
import { ITablePropertyColumn } from '@/interface/ICommon';
import { useAsyncTable } from '@apptimus-ui/table';
import { useEffect, useMemo, useState } from 'react';
import { Dropdown, DropdownItem } from '@apptimus-ui/dropdown';
import { Flexicon } from '@apptimus-ui/flexicon';
import PageHeading from '@/components/others/PageHeading';
import { useTrans } from '@/helpers/services/lang/langService';
import { formatDate, hexToRgba } from '@/helpers/services/commonService';
import { fetchCustomerRequestQuotationTableData } from '../../service';

function QuotationList({ onView, setCurrentApprovalId, tableVer }: { onView: Function; setCurrentApprovalId: Function; tableVer: number }) {
  const t = useTrans('label.customer_request,otr.common');
  const tableName = 'quotation_list';
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [tableColumnVers, _setTableColumnVers] = useState(0);
  // const router = useRouter();

  const columns = useMemo<ITablePropertyColumn[]>(
    () => [
      {
        id: 'code',
        header: t('quotation_request_id'),
        accessorKey: 'code',
        sort: true,
        visibilityLock: false,
      },
      {
        id: 'customer_name',
        header: t('customer'),
        accessorKey: 'customer_name',
        sort: true,
        visibilityLock: false,
      },
      {
        id: 'vendor_products',
        header: t('product'),
        accessorKey: 'vendor_products',
        sort: true,
        cell: ({ cell }: { cell: any }) => <div>{cell.vendor_products[0]?.vendor_product_name}</div>,
      },
      {
        id: 'submitted_at',
        header: t('requested_on'),
        accessorKey: 'submitted_at',
        sort: true,
        align: 'center',
        cell: ({ cell }: { cell: any }) => <div>{formatDate(cell.getValue()) || '-'}</div>,
      },
      {
        id: 'status_name',
        header: t('stage'),
        accessorKey: 'status_name',
        sort: true,
        visibilityLock: false,
        cell: ({ cell, onClick }: any) => {
          return (
            <div className="d-flex justify-content-between align-items-center gap-3" onClick={onClick}>
              <div
                className={`d-flex flex-row align-items-center gap-1 rounded-1 fs-10 fw-bold badge`}
                style={{ background: hexToRgba(cell.status_color, 0.1), border: `1px solid ${cell.status_color}`, color: cell.status_color }}
              >
                <svg width="9" height="8" viewBox="0 0 9 8" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <circle cx="4.375" cy="4" r="3" fill={cell.status_color} />
                </svg>
                {cell.status_name}
              </div>
            </div>
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
                <DropdownItem onClick={() => (setIsFullscreen(false), setCurrentApprovalId(cell.getValue()), onClose())}>
                  <span className="d-flex gap-2">
                    <Flexicon icon="check-circle" variant="line" size={17} />
                    <span>{t('approve')}</span>
                  </span>
                </DropdownItem>
                {/* <DeleteConfirmPop
                  trigger={
                    <DropdownItem onClick={() => null}>
                      <span className="d-flex gap-2 w-100">
                        <Flexicon icon="trash-03" variant="line" size={17} />
                        <span>{t('delete')}</span>
                      </span>
                    </DropdownItem>
                  }
                  deleteId={cell.approval_id}
                  {...{ handleOnDelete, onClose }}
                /> */}
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
    loadData: (props: any) => fetchCustomerRequestQuotationTableData(props),
    paginate: true,
    rowSelection: true,
    rowSelectionProp: {
      key: 'id',
      mode: 'single',
      enableSelectAll: true,
      action: (selectedId: string) => onView(selectedId),
    },
  });

  useEffect(() => {
    tableProperties.reload();
  }, [tableColumnVers, tableVer]);

  return (
    <>
      <div className={`data-table-container card custom-card ${isFullscreen ? 'dtc-fullscreen card-fullscreen' : ''}`}>
        <Table heading={<PageHeading title={t('partners')} icon="sun-light" />} {...{ tableProperties, isFullscreen, setIsFullscreen }} />
      </div>
      {/* <CustomizeColumn
        key={tableColumnVers}
        isOpen={isCustColumnVisible}
        tableName={tableName}
        columns={tableColumns}
        onClose={() => setIsCustColumnVisible(false)}
        afterUpdate={() => setTableColumnVers((prevTableColumnVers) => prevTableColumnVers + 1)}
      /> */}
    </>
  );
}

export default QuotationList;
