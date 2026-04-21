import Table from '@/components/table-properties/Table';
import { ITablePropertyColumn } from '@/interface/ICommon';
import { useAsyncTable } from '@apptimus-ui/table';
import { useEffect, useMemo, useState } from 'react';
import PageHeading from '@/components/others/PageHeading';
import { useTrans } from '@/helpers/services/lang/langService';
import { Badge } from '@apptimus-ui/ui-element';
import { fetchPInsurerroductDocumentTableData } from '../../../../services';
import { Dropdown, DropdownItem } from '@apptimus-ui/dropdown';
import { Flexicon } from '@apptimus-ui/flexicon';
import DeleteConfirmPop from '@/components/others/DeleteConfirmPop';

function DocumentList({
  viewId,
  type,
  isView = true,
  handleOnDelete,
  setCurrentEditData,
  tableVers,
}: {
  viewId: string;
  type: string;
  isView: boolean;
  handleOnDelete: Function;
  setCurrentEditData: Function;
  tableVers: number;
}) {
  const t = useTrans('label.products,otr.common');
  const [isFullscreen, setIsFullscreen] = useState(false);

  const columns = useMemo<ITablePropertyColumn[]>(
    () => [
      {
        id: 'name',
        header: t('document_type'),
        accessorKey: 'name',
        sort: true,
      },
      {
        id: 'is_mandatory',
        header: t('is_mandatory'),
        accessorKey: 'is_mandatory',
        sort: true,
        cell: ({ cell }: any) => {
          const value = cell.getValue();
          if (value === 0) return <Badge text={t('optional')} color="warning" variant="light" />;
          if (value === 1) return <Badge text={t('yes')} color="success" variant="light" />;
          return <div>{value}</div>;
        },
      },
      ...(!isView
        ? [
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
                      <DropdownItem onClick={() => (setIsFullscreen(false), setCurrentEditData(cell), onClose())}>
                        <span className="d-flex gap-2">
                          <Flexicon icon="pencil-line" variant="line" size={17} />
                          <span>{t('edit')}</span>
                        </span>
                      </DropdownItem>
                      {handleOnDelete && (
                        <DeleteConfirmPop
                          trigger={
                            <DropdownItem onClick={() => null}>
                              <span className="d-flex gap-2 w-100">
                                <Flexicon icon="trash-03" variant="line" size={17} />
                                <span>{t('delete')}</span>
                              </span>
                            </DropdownItem>
                          }
                          deleteId={cell.id}
                          {...{ handleOnDelete, onClose }}
                        />
                      )}
                    </span>
                  )}
                </Dropdown>
              ),
              customizable: false,
            },
          ]
        : []),
    ],
    [],
  );

  const tableProperties = useAsyncTable({
    columns: columns,
    loadData: (params: any) => fetchPInsurerroductDocumentTableData({ ...params, type: type }, viewId),
    paginate: true,
  });

  useEffect(() => {
    tableProperties.reload();
  }, [viewId, tableVers]);

  return (
    <>
      <div className={`data-table-container card custom-card ${isFullscreen ? 'dtc-fullscreen card-fullscreen' : 'mt-3'}`}>
        <Table heading={<PageHeading title={t('team_details')} icon="sun-light" />} {...{ tableProperties, isFullscreen, setIsFullscreen, searchOption: false, enableTopContent: false }} />
      </div>
    </>
  );
}

export default DocumentList;
