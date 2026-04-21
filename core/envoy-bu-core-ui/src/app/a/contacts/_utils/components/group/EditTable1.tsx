import { useCustomizeColumn } from '@/components/others/CustomizeColumn';
import Table from '@/components/table-properties/Table';
import { ITablePropertyColumn } from '@/interface/ICommon';
import { useAsyncTable } from '@apptimus-ui/table';
import { useEffect, useMemo, useState } from 'react';
import ContactCard from './ContactCard';
import { fetchAvailableContacts } from '../../service';

function EditTable1({ tableVers, selectedValues, groupId }: { tableVers: number; selectedValues: Function; groupId: string }) {
  const tableName = 'available_contacts';

  const [tableColumnVers, _setTableColumnVers] = useState(0);

  const columns = useMemo<ITablePropertyColumn[]>(
    () => [
      {
        id: 'name',
        accessorKey: 'name',
        cell: (cell: any) => <ContactCard email={cell.cell.email} name={cell.cell.name} contactNumber={cell.cell.primary_contact} />,
      },
    ],
    [],
  );

  const tableColumns = useCustomizeColumn({ ...{ tableName, columns, tableColumnVers } });

  const tableProperties = useAsyncTable({
    columns: tableColumns,
    loadData: (params: any) => fetchAvailableContacts(params, groupId),
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
  });

  useEffect(() => {
    tableProperties.reload();
    tableProperties.reset({ type: 'row-selection' });
  }, [tableColumnVers, tableVers]);

  return (
    <>
      <div className={`rounded-2 w-100 dark-border overflow-hidden table-header-hide`}>
        <Table {...{ tableProperties, isRowPerPageVisible: false }} />
      </div>
    </>
  );
}

export default EditTable1;
