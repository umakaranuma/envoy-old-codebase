import Table from '@/components/table-properties/Table';
import { ITablePropertyColumn } from '@/interface/ICommon';
import { useAsyncTable } from '@apptimus-ui/table';
import { useMemo } from 'react';
import { useTrans } from '@/helpers/services/lang/langService';
import { fetchAllRequestTableData } from '../service';
import { formatDate, hexToRgba } from '@/helpers/services/commonService';
import { Badge } from '@apptimus-ui/ui-element';

function MyRequestList() {
  const t = useTrans('label.my_request,otr.common');

  const columns = useMemo<ITablePropertyColumn[]>(
    () => [
      {
        id: 'code',
        header: t('request_id'),
        accessorKey: 'code',
        sort: true,
        visibilityLock: false,
      },
      {
        id: 'submitted_at',
        header: t('requested_date'),
        accessorKey: 'submitted_at',
        sort: true,
        cell: ({ cell }: { cell: any }) => <>{formatDate(cell.getValue())}</>,
      },
      {
        id: 'type',
        header: t('request_type'),
        accessorKey: 'type',
        sort: true,
      },
      {
        id: 'status_name',
        header: t('request_status'),
        accessorKey: 'status_name',
        sort: true,
        visibilityLock: false,
        cell: ({ cell, onClick }: any) => {
          return (
            <div
              className={`rounded-5 fw-semibold badge`}
              style={{
                background: hexToRgba(cell.status_color ? cell.status_color : '', 0.1),
                border: `1px solid ${hexToRgba(cell.status_color ? cell.status_color : '', 0.4)}`,
                color: cell.status_color ? cell.status_color : '',
              }}
              onClick={onClick}
            >
              {cell.status_name}
            </div>
          );
        },
      },
      {
        id: 'vendor_products',
        header: t('product_types'),
        accessorKey: 'vendor_products',
        sort: true,
        cell: ({ cell }: { cell: any }) => {
          return (
            <div className="d-flex flex-wrap gap-1">
              {cell.getValue().map((item: any, index: number) => (
                <Badge key={index} color="primary" radius="pill">
                  {item.name}
                </Badge>
              ))}
            </div>
          );
        },
      },
    ],
    [],
  );

  const tableProperties = useAsyncTable({
    columns: columns,
    loadData: (props: any) => fetchAllRequestTableData(props),
    paginate: true,
    rowSelection: false,
  });

  return <Table {...{ tableProperties, searchOption: false }} />;
}

export default MyRequestList;
