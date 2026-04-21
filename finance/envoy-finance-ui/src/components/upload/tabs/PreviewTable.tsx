import React, { useMemo, useEffect } from 'react';
import { Button } from '@apptimus-ui/ui-element';
import { Flexicon } from '@apptimus-ui/flexicon';
import Table from '@/components/table-properties/Table';
import { useAsyncTable } from '@apptimus-ui/table';

interface PreviewTableProps {
  rows: any[];
  fields: string[];
  flexFields: { name: string }[];
  onEditRow: (rowId: string) => void;
}

function PreviewTable({ rows, fields, flexFields, onEditRow }: PreviewTableProps) {
  const tableData = useMemo(() => {
    return rows.map((row) => {
      const rowData: any = {
        id: row.row_id,
        row_id: row.row_id,
      };

      fields.forEach((field) => {
        const key = field.toLowerCase().replace(/\s+/g, '_');
        rowData[key] = row[key] || '';
      });

      flexFields.forEach((field) => {
        const key = field.name.toLowerCase().replace(/\s+/g, '_');
        rowData[key] = row.flex_fields?.[key] || '';
      });

      return rowData;
    });
  }, [rows, fields, flexFields]);

  const columns = useMemo<any[]>(() => {
    const systemFieldColumns: any[] = fields.map((field) => ({
      id: field.toLowerCase().replace(/\s+/g, '_'),
      header: field,
      accessorKey: field.toLowerCase().replace(/\s+/g, '_'),
      sort: false,
    }));

    const flexFieldColumns: any[] = flexFields.map((field) => ({
      id: field.name.toLowerCase().replace(/\s+/g, '_'),
      header: field.name,
      accessorKey: field.name.toLowerCase().replace(/\s+/g, '_'),
      sort: false,
    }));

    const actionColumn: any = {
      id: 'action',
      header: 'Action',
      accessorKey: 'action',
      sort: false,
      cell: ({ cell }: { cell: any }) => (
        <Button size="sm" color="primary" className="d-flex align-items-center gap-1" onClick={() => onEditRow(cell.row_id)}>
          <Flexicon icon="pencil-line" size={16} /> Edit
        </Button>
      ),
    };

    return [...systemFieldColumns, ...flexFieldColumns, actionColumn];
  }, [fields, flexFields, onEditRow]);

  // Create table properties
  const tableProperties = useAsyncTable({
    columns: columns,
    loadData: () => Promise.resolve({ data: tableData, dataLength: tableData.length }),
    paginate: false,
    rowSelection: false,
  });

  // Reload table data when rows change
  useEffect(() => {
    tableProperties.reload();
  }, [tableData, tableProperties]);

  return (
    <div className="bg-white custom-card p-3 rounded-3 mb-3">
      <div className="fs-15 fw-semibold mb-3">Preview & Edit Data</div>
      <div className="data-table-container card custom-card">
        <Table tableProperties={tableProperties} recordControl={false} searchOption={false} />
      </div>
    </div>
  );
}

export default PreviewTable;
