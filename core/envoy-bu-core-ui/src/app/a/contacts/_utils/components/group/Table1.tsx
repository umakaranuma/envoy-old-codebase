import { useCustomizeColumn } from '@/components/others/CustomizeColumn';
import Table from '@/components/table-properties/Table';
import { ITablePropertyColumn } from '@/interface/ICommon';
import { useAsyncTable } from '@apptimus-ui/table';
import { useEffect, useMemo, useState } from 'react';
import ContactCard from './ContactCard';
import { fetchContactTableData } from '../../service';

function Table1({ selectedValues }: { selectedValues: Function }) {
  const tableName = 'contacts';

  const [tableColumnVers, _setTableColumnVers] = useState(0);
  const [_filterComKey, setFilterComKey] = useState(0);

  const columns = useMemo<ITablePropertyColumn[]>(
    () => [
      {
        id: 'name',
        accessorKey: 'name',
        cell: (cell: any) => <ContactCard email={cell.cell.name} name={cell.cell.email} contactNumber={cell.cell.primary_contact} />,
      },
    ],
    [],
  );
  {
    /* <ContactCard email={cell.name} name={cell.email} /> */
  }
  const tableColumns = useCustomizeColumn({ ...{ tableName, columns, tableColumnVers } });

  const reducer = (_state: any, action: any) => {
    if (action.isReset) {
      setFilterComKey((prevFilterComKey) => prevFilterComKey + 1);
    }

    return {
      filters: action.filterData,
    };
  };

  const tableProperties = useAsyncTable({
    columns: tableColumns,
    loadData: (params: any) => fetchContactTableData(params),
    paginate: true,
    rowSelection: true,
    rowSelectionProp: {
      key: 'id',
      mode: 'multiple',
      actionColumn: true,
      enableSelectAll: true,
      action: (value: any, _data: any) => {
        selectedValues(value);
      },
    },
    customState: {
      initState: {
        filters: {},
      },
      reducer: reducer,
    },
  });

  useEffect(() => {
    tableProperties.reload();
  }, [tableColumnVers]);

  return (
    <>
      <div className={`data-table-container card custom-card p-0`}>
        <div className="d-flex justify-content-between align-items-center mb-3 mt-2">
          <div className="datatable-search">{tableProperties.SearchInput as React.ReactNode}</div>
        </div>
        <Table searchOption={false} {...{ tableProperties, isRowPerPageVisible: false }} />
      </div>
    </>
  );
}

export default Table1;
