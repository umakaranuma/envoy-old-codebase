import React, { useEffect, useMemo, useState } from 'react';
import { useTrans } from '@/helpers/services/lang/langService';
import { useAsyncTable } from '@apptimus-ui/table';
import { ITablePropertyColumn } from '@/interface/ICommon';
import { NativeProduct } from '../../types';
import Table from '@/components/table-properties/Table';
import PageHeading from '@/components/others/PageHeading';
import { fetchNativeProductsTableData } from '../../services';
import { Dropdown, DropdownItem } from '@apptimus-ui/dropdown';
import { Flexicon } from '@apptimus-ui/flexicon';
import DeleteConfirmPop from '@/components/others/DeleteConfirmPop';
import InsureProductList from './InsureProductList';

interface Props {
  onEdit: (id: string) => void;
  onView: (id: string) => void;
  handleOnDelete: (deleteId: string, callback: Function, setLoader: Function, onClose: Function) => void;
  tableVers: number;
}

const NativeProductsList: React.FC<Props> = ({ onEdit, onView, handleOnDelete, tableVers }) => {
  const t = useTrans('label.products,otr.common');
  const [isFullscreen, setIsFullscreen] = useState(false);

  const columns = useMemo<ITablePropertyColumn[]>(
    () => [
      {
        id: 'code',
        header: t('product_code'),
        accessorKey: 'code',
        sort: true,
      },
      {
        id: 'name',
        header: t('product_name'),
        accessorKey: 'name',
        sort: true,
        visibilityLock: false,
      },
      {
        id: 'risk_type',
        header: t('risk_type'),
        accessorKey: 'type',
        sort: true,
      },
      {
        header: t('action'),
        align: 'center',
        accessorKey: 'id',
        cell: ({ cell }: { cell: any }) => (
          <Dropdown
            trigger={
              <span className="action-icon">
                <Flexicon icon="dots-horizontal" variant="line" size={17} />
              </span>
            }
          >
            {(onClose: Function) => (
              <span className="t-action">
                <DropdownItem onClick={() => (setIsFullscreen(false), onView(cell.getValue()), onClose())}>
                  <span className="d-flex gap-2">
                    <Flexicon icon="eye" variant="line" size={17} />
                    <span>{t('view')}</span>
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
                  deleteId={cell.getValue()}
                  {...{ handleOnDelete, onClose }}
                />
              </span>
            )}
          </Dropdown>
        ),
      },
    ],
    [t, onEdit, onView, handleOnDelete],
  );

  const tableProperties = useAsyncTable({
    columns: columns,
    loadData: (props: any) => fetchNativeProductsTableData(props),
    paginate: true,
    rowExpandable: {
      primaryKey: 'id',
      expandableRows: () => true,
      expandedRowRender: (record: NativeProduct) => {
        return (
          <div className="p-1 bg-grey">
            <InsureProductList nativeProductId={record?.id} tableVers={tableVers} isEdit={false} />
          </div>
        );
      },
    },
    rowSelection: true,
    rowSelectionProp: {
      key: 'id',
      mode: 'single',
      action: (selectedId: string) => onView(selectedId),
    },
  });

  useEffect(() => {
    tableProperties.reload();
  }, [tableVers]);

  return (
    <>
      <div className={`data-table-container card custom-card ${isFullscreen ? 'dtc-fullscreen card-fullscreen' : 'mt-2'}`}>
        <Table heading={<PageHeading title={t('native_products')} icon="sun-light" />} tableProperties={tableProperties} isFullscreen={isFullscreen} setIsFullscreen={setIsFullscreen} />
      </div>
    </>
  );
};

export default NativeProductsList;
