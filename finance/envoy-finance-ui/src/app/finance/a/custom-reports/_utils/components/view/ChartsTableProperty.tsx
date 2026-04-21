import { useAsyncTable } from '@apptimus-ui/table';
import { useEffect, useMemo } from 'react';
import { fetchOneReportChartTableData } from '../../service';

export const useChartTableProperty = (id: any) => {
  const columns = useMemo(() => [], []);

  const tableProps = {
    columns: columns,
    loadData: (props: any) => fetchOneReportChartTableData(props, id),
  };

  const tableProperties = useAsyncTable(tableProps);

  useEffect(() => {
    tableProperties.reload();
  }, []);

  return { tableProperties };
};
