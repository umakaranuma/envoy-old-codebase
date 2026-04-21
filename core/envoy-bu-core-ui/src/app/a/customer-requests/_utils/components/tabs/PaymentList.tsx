import { useCustomizeColumn } from '@/components/others/CustomizeColumn';
import Table from '@/components/table-properties/Table';
import { ITablePropertyColumn } from '@/interface/ICommon';
import { useAsyncTable } from '@apptimus-ui/table';
import { useEffect, useMemo, useState } from 'react';
import PageHeading from '@/components/others/PageHeading';
import { useTrans } from '@/helpers/services/lang/langService';
import { formatDate, hexToRgba } from '@/helpers/services/commonService';
import { fetchCustomerPaymentRequestTableData } from '../../service';
import FileDownloadButton from '@/components/others/page-related/uploader/FileDownloadButton';
import { toaster } from '@/helpers/services/toaster';
import { approveCustomerPaymentRequest } from '../../api-service';
import { Dropdown, DropdownItem } from '@apptimus-ui/dropdown';
import { Flexicon } from '@apptimus-ui/flexicon';

function PaymentList() {
  const t = useTrans('label.customer_request,otr.common');
  const tBe = useTrans('be.msg,be.error,be.attri');
  const tableName = 'payment_list';
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [tableColumnVers, _setTableColumnVers] = useState(0);
  const [tableVer, setTableVer] = useState(0);
  // const router = useRouter();
  async function onApprovePayment(id: string) {
    try {
      const responseData = await approveCustomerPaymentRequest(id);

      if (responseData.is_success) {
        toaster.success(tBe(responseData.message));
        setTableVer((prev) => prev + 1);
      }
    } catch (error) {
      console.error('An error occurred:', error);
    }
  }

  const columns = useMemo<ITablePropertyColumn[]>(
    () => [
      {
        id: 'reference_id',
        header: t('payment_id'),
        accessorKey: 'reference_id',
        sort: true,
        visibilityLock: false,
      },
      {
        id: 'invoice_number',
        header: t('policy_request_id'),
        accessorKey: 'invoice_number',
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
      // {
      //   id: 'insurers',
      //   header: t('insurer'),
      //   accessorKey: 'insurers',
      //   sort: true,
      //   cell: ({ cell }: { cell: any }) => <div>{cell.insurers[0]?.name}</div>,
      // },
      {
        id: 'created_at',
        header: t('requested_on'),
        accessorKey: 'created_at',
        sort: true,
        align: 'center',
        cell: ({ cell }: { cell: any }) => <div>{formatDate(cell.getValue()) || '-'}</div>,
      },
      {
        id: 'status',
        header: t('stage'),
        accessorKey: 'status',
        sort: true,
        visibilityLock: false,
        cell: ({ cell, onClick }: any) => {
          return (
            <div className="d-flex justify-content-between align-items-center gap-3" onClick={onClick}>
              <div
                className={`d-flex flex-row align-items-center gap-1 rounded-1 fs-10 fw-bold badge`}
                style={{ background: hexToRgba(cell.status_color || '#188f50', 0.1), border: `1px solid ${cell.status_color || '#188f50'}`, color: cell.status_color || '#188f50' }}
              >
                <svg width="9" height="8" viewBox="0 0 9 8" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <circle cx="4.375" cy="4" r="3" fill={cell.status_color || '#188f50'} />
                </svg>
                {cell.status}
              </div>
            </div>
          );
        },
      },
      {
        id: 'created_at',
        header: t('payment_slip'),
        accessorKey: 'created_at',
        sort: true,
        align: 'center',
        cell: ({ cell }: { cell: any }) => <FileDownloadButton s3Key={cell.receipt} fileName={cell.receipt_name} />,
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
                <DropdownItem onClick={() => (setIsFullscreen(false), onApprovePayment(cell.getValue()), onClose())}>
                  <span className="d-flex gap-2">
                    <Flexicon icon="eye" variant="line" size={17} />
                    <span>{t('approve')}</span>
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
    loadData: (props: any) => fetchCustomerPaymentRequestTableData(props),
    paginate: true,
    rowSelection: false,
    // rowSelectionProp: {
    //   key: 'approval_id',
    //   mode: 'single',
    //   enableSelectAll: true,
    //   action: (selectedId: string) => router.push(`/a/approvals/${selectedId}`),
    // },
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

export default PaymentList;
