import Table from '@/components/table-properties/Table';
import { ITablePropertyColumn } from '@/interface/ICommon';
import { useAsyncTable } from '@apptimus-ui/table';
import { useMemo } from 'react';
import { useTrans } from '@/helpers/services/lang/langService';
import { fetchAllQuotationsSPTableData } from '../service';
import { Button } from '@apptimus-ui/ui-element';
import { formatDate } from '@/helpers/services/commonService';
import QuotationConfirmationPop from './QuotationConfirmationPop';
import { toaster } from '@/helpers/services/toaster';
import { confirmQuotation } from '../api-service';
import FileDownloadButton from '@/components/others/page-related/uploader/FileDownloadButton';

function QuotationServiceProviderList({ quotationId, setTableVersion }: { quotationId: string; setTableVersion: Function }) {
  const t = useTrans('label.my_quotation,otr.common');
  const tBe = useTrans('be.msg,be.error,be.attri');

  const handleOnConfirm = async (quotationId: string, callback: Function, setLoader: Function) => {
    setLoader(true);
    const responseData = await confirmQuotation(quotationId);
    setLoader(false);

    if (responseData.is_success) {
      toaster.success(tBe(responseData.message));
      tableProperties.reload();
      setTableVersion((prev: number) => prev + 1);
      callback();
    }
  };

  const columns = useMemo<ITablePropertyColumn[]>(
    () => [
      {
        id: 'service_provider_name',
        header: t('partner_name'),
        accessorKey: 'service_provider_name',
        visibilityLock: false,
        cell: ({ cell }: { cell: any }) => <div className="text-nowrap">{cell.getValue()}</div>,
      },
      {
        id: 'version',
        header: t('quotation_version'),
        accessorKey: 'version',
      },
      {
        id: 'quotation_code',
        header: t('quotation_request_number'),
        accessorKey: 'quotation_code',
      },
      {
        id: 'expiry_date',
        header: t('expiry_date'),
        accessorKey: 'expiry_date',
        nowrap: true,
        visibilityLock: false,
        cell: ({ cell }: { cell: any }) => {
          const dateValue = cell.getValue();
          return dateValue ? <span>{formatDate(dateValue)}</span> : null;
        },
      },
      {
        id: 'received_date',
        header: t('received_date'),
        accessorKey: 'received_date',
        visibilityLock: false,
        cell: ({ cell }: { cell: any }) => {
          const dateValue = cell.getValue();
          return dateValue ? <span>{formatDate(dateValue)}</span> : null;
        },
      },
      {
        id: 'total_amount',
        header: t('quotation_value'),
        accessorKey: 'total_amount',
      },
      {
        id: 'by_user_name',
        header: t('updated_by'),
        accessorKey: 'by_user_name',
      },
      {
        id: 'coverage_details',
        header: t('quotation'),
        accessorKey: 'coverage_details',
        sort: true,
        cell: ({ cell }: { cell: any }) => <>{cell.getValue() ? <FileDownloadButton s3Key={cell.getValue()} fileType="pdf" /> : '-'}</>,
        nowrap: true,
        align: 'center',
      },
      // {
      //   id: 'quotation_request_link',
      //   header: t('request_link'),
      //   accessorKey: 'quotation_request_link',
      //   cell: ({ cell }: { cell: any }) => <div className="clickable-text">{cell.getValue()}</div>,
      // },
      {
        header: t('action'),
        align: 'center',
        accessorKey: 'id',
        cell: ({ cell }: { cell: any }) => {
          if (cell.status_name === 'CONFIRMED') {
            return <Button size="sm" text={t('confirmed')} disabled />;
          }
          if (cell.status_name === 'REJECTED') {
            return <Button size="sm" color="danger" text={t('rejected')} disabled />;
          }
          return <QuotationConfirmationPop trigger={<Button size="sm" text={t('confirm')} />} quotationId={cell.vendor_quotation_id} {...{ handleOnConfirm }} />;
        },
        customizable: false,
      },
    ],
    [],
  );

  const tableProperties = useAsyncTable({
    columns: columns,
    loadData: (props: any) => fetchAllQuotationsSPTableData(props, quotationId),
    paginate: true,
    rowSelection: false,
  });

  return (
    <>
      <div className={`bg-white`}>
        <Table {...{ tableProperties, searchOption: false, recordControl: false }} />
      </div>
    </>
  );
}

export default QuotationServiceProviderList;
