import Table from '@/components/table-properties/Table';
import { useAsyncTable } from '@apptimus-ui/table';
import { useState } from 'react';
import { fetchOneReportTableData } from '../../service';
import { Skeleton } from '@apptimus-ui/ui-element';

function ReportTable({ reportId, tableColumns, loading }: { reportId: string; tableColumns: any[]; loading: boolean }) {
  const [isFullscreen, setIsFullscreen] = useState(false);

  const tableProperties = useAsyncTable({
    columns: tableColumns,
    loadData: (props: any) => fetchOneReportTableData(props, reportId),
    paginate: true,
    rowSelection: false,
  });

  return (
    <>
      {!loading ? (
        <>
          {tableColumns?.length > 0 ? (
            <div className={`data-table-container card custom-card ${isFullscreen && 'dtc-fullscreen card-fullscreen'}`}>
              <Table {...{ tableProperties, isFullscreen, setIsFullscreen }} />
            </div>
          ) : (
            <div className="text-muted text-center fs-16 fw-semibold">No records found!</div>
          )}
        </>
      ) : (
        <Skeleton width="100%" height="400px" />
      )}
    </>
  );
}

export default ReportTable;
