import React, { useMemo } from 'react';
import { Flexicon } from '@apptimus-ui/flexicon';
import { useTrans } from '@/helpers/services/lang/langService';
import { useTable } from '@apptimus-ui/table';
import { Dropdown, DropdownItem } from '@apptimus-ui/dropdown';
import DeleteConfirmPop from '@/components/others/DeleteConfirmPop';

interface Field {
  id: string;
  label: string;
}

interface PreviewTableProps {
  rows: Array<{
    row_id: string;
    [key: string]: any;
  }>;
  fields: Field[];
  onEditRow: (rowId: string) => void;
  handleDeleteRow: (rowId: string) => void;
}

function PreviewTable({ rows, fields, onEditRow, handleDeleteRow }: PreviewTableProps) {
  const t = useTrans('label.sales_managements,otr.common,be.msg');

  const columns = useMemo(
    () => [
      ...fields.map((field) => ({
        header: field.label,
        accessorKey: field.id,
        cell: (cell: any) => cell.cell[field.id] || '',
      })),
      {
        header: t('action'),
        accessorKey: 'action',
        cell: (cell: any) => (
          <Dropdown
            trigger={
              <span className="action-icon">
                <Flexicon icon="dots-horizontal" variant="line" size={17} />
              </span>
            }
          >
            {(onClose: Function) => (
              <span className="t-action">
                <DropdownItem onClick={() => (onEditRow(cell.cell.row_id), onClose())}>
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
                  deleteId={cell.cell.row_id}
                  handleOnDelete={() => {
                    handleDeleteRow(cell.cell.row_id);
                    onClose();
                  }}
                  onClose={onClose}
                />
              </span>
            )}
          </Dropdown>
        ),
      },
    ],
    [fields, onEditRow, t],
  );

  const tableData = useMemo(() => rows, [rows]);

  const tableProperties = useTable({
    columns,
    data: tableData,
  });

  return (
    <div className="bg-white custom-card p-3 rounded-3 mb-3">
      <div className="fs-15 fw-semibold mb-3">{t('preview_edit_data')}</div>
      <div className="mt-3">{tableProperties.Table as React.ReactNode}</div>
    </div>
  );
}

export default PreviewTable;
