import Table from '@/components/table-properties/Table';
import { ITablePropertyColumn } from '@/interface/ICommon';
import { useAsyncTable } from '@apptimus-ui/table';
import { useEffect, useMemo } from 'react';
import { Dropdown, DropdownItem } from '@apptimus-ui/dropdown';
import { Flexicon } from '@apptimus-ui/flexicon';
import { useTrans } from '@/helpers/services/lang/langService';
import { formatDate, hexToRgba, thousandSeparator } from '@/helpers/services/commonService';
import { fetchAllVendorQuotationTableData } from '../../../service';
import DeleteConfirmPop from '@/components/others/DeleteConfirmPop';
import FileDownloadButton from '@/components/others/page-related/uploader/FileDownloadButton';
import { useCurrency } from '@/contexts/CurrencyContext';
import { toaster } from '@/helpers/services/toaster';
import { confirmReceivedQuotation } from '../../../api-service';

function ReceivedList({
  onEdit,
  tableVers,
  selectedIds,
  handleOnDelete,
  quotationId,
  onPolicyRequest,
  setShareData,
}: {
  quotationId: string;
  onEdit: Function;
  tableVers: number;
  selectedIds: Function;
  handleOnDelete: Function;
  onPolicyRequest: Function;
  setShareData: Function;
}) {
  const t = useTrans('label.quotations,otr.common');
  const tBe = useTrans('be.msg,be.error,be.attri');
  const { currency } = useCurrency();

  const handleConfirmQuotation = async (id: string, callback: Function, setLoader: Function, onClose?: Function) => {
    setLoader(true);
    const responseData = await confirmReceivedQuotation(id);
    setLoader(false);

    if (responseData.is_success) {
      toaster.success(tBe(responseData.message));
      callback();
      onClose?.();
      tableProperties.reload();
    }
  };

  const columns = useMemo<ITablePropertyColumn[]>(
    () => [
      {
        id: 'service_provider_name',
        header: t('insurer_company_name'),
        accessorKey: 'service_provider_name',
        sort: true,
        visibilityLock: false,
      },
      {
        id: 'version',
        header: t('quotation_version'),
        accessorKey: 'version',
        sort: true,
      },
      {
        id: 'code',
        header: t('quotation_id'),
        accessorKey: 'code',
        sort: true,
      },
      {
        id: 'total_amount',
        header: `${t('quotation_value')} (${currency.code})`,
        accessorKey: 'total_amount',
        sort: true,
        align: 'right',
        cell: ({ cell }: { cell: any }) => <div className="amount-container">{thousandSeparator(cell.getValue()) || '-'}</div>,
      },
      {
        id: 'status',
        header: t('status'),
        accessorKey: 'status',
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
                {cell.status}
              </div>
            </div>
          );
        },
      },
      {
        id: 'received_date',
        header: t('received_date'),
        accessorKey: 'received_date',
        sort: true,
        cell: ({ cell }: { cell: any }) => <div>{formatDate(cell.getValue()) || '-'}</div>,
      },
      {
        id: 'expiry_date',
        header: t('expiry_date'),
        accessorKey: 'expiry_date',
        sort: true,
        cell: ({ cell }: { cell: any }) => <div>{formatDate(cell.getValue()) || '-'}</div>,
      },
      {
        id: 'remaining_days',
        header: t('remaining_days'),
        accessorKey: 'remaining_days',
        sort: true,
      },
      {
        id: 'by_user_name',
        header: t('requested_by'),
        accessorKey: 'by_user_name',
        sort: true,
      },
      {
        id: 'coverage_details_name',
        header: t('quotation'),
        accessorKey: 'coverage_details_name',
        align: 'center',
        cell: ({ cell }: { cell: any }) => <FileDownloadButton s3Key={cell.coverage_details} fileType="pdf" />,
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
                {cell.status !== 'REJECTED' && cell.status !== 'CONFIRMED' ? (
                  <>
                    {cell.status !== 'EXPIRED' && (
                      <DeleteConfirmPop
                        msg="quotation_confirm_msg"
                        trigger={
                          <DropdownItem onClick={() => null}>
                            <span className="d-flex gap-2 w-100">
                              <Flexicon icon="check-circle" variant="line" size={17} />
                              <span>{t('confirm')}</span>
                            </span>
                          </DropdownItem>
                        }
                        deleteId={cell.vendor_quotation_id}
                        {...{ handleOnDelete: handleConfirmQuotation, onClose }}
                      />
                    )}
                    <DropdownItem onClick={() => (onEdit(cell.getValue()), onClose())}>
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
                  </>
                ) : (
                  <>
                    {cell.status === 'CONFIRMED' && (
                      <DropdownItem onClick={() => (onPolicyRequest(cell.getValue(), cell?.insurer_product_id, cell?.insurer_product_name, cell?.service_provider_id, cell?.product_id), onClose())}>
                        <span className="d-flex gap-2">
                          <Flexicon icon="pencil-line" variant="line" size={17} />
                          <span>{t('request_policy')}</span>
                        </span>
                      </DropdownItem>
                    )}
                  </>
                )}
                <DropdownItem
                  onClick={() => (setShareData({ id: cell.customer_id, name: cell.customer_name, documents: [{ name: cell.coverage_details_name, doc: cell.coverage_details }] }), onClose())}
                >
                  <span className="d-flex gap-2">
                    <Flexicon icon="share-07" variant="line" size={17} />
                    <span>{t('share')}</span>
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

  const tableProperties = useAsyncTable({
    columns: columns,
    loadData: (props: any) => fetchAllVendorQuotationTableData(props, quotationId, 'received'),
    paginate: true,
    rowSelection: true,
    rowSelectionProp: {
      key: 'id',
      mode: 'multiple',
      actionColumn: true,
      enableSelectAll: true,
      action: (value: any, _data: any) => {
        selectedIds(value);
      },
    },
  });

  useEffect(() => {
    tableProperties.reload();
    tableProperties.reset({ type: 'row-selection' });
  }, [tableVers]);

  return <Table {...{ tableProperties, searchOption: false, recordControl: false }} />;
}

export default ReceivedList;
