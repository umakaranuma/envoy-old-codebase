import { useAsyncTable } from '@apptimus-ui/table';
import { useEffect, useMemo } from 'react';
import { fetchPoliciesTableData } from '../service';

export const useTableProperty = () => {
  const columns = useMemo(() => [], []);

  const tableProps = {
    columns: columns,
    loadData: (props: any) => fetchPoliciesTableData(props),
  };

  const tableProperties = useAsyncTable(tableProps);

  useEffect(() => {
    tableProperties.reload();
  }, []);

  return { tableProperties };
};
