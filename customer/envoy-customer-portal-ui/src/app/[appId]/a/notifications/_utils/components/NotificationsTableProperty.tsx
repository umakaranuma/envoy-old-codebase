import { useAsyncTable } from '@apptimus-ui/table';
import { useEffect, useMemo } from 'react';
import { fetchAllNotificationTableData } from '../service';

export const useNotificationTableProperty = ({ read_status, filter }: { read_status: string; filter: string }) => {
  const columns = useMemo(() => [], []);

  const tableProps = {
    columns: columns,
    loadData: (props: any) => fetchAllNotificationTableData(props, read_status, filter),
  };

  const tableProperties = useAsyncTable(tableProps);

  useEffect(() => {
    tableProperties.reload();
  }, [read_status, filter]);

  return { tableProperties };
};
