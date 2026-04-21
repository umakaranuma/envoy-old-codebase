import Table from '@/components/table-properties/Table';
import { useTrans } from '@/helpers/services/lang/langService';
import { ITablePropertyColumn } from '@/interface/ICommon';
import { useAsyncTable } from '@apptimus-ui/table';
import React, { useEffect, useMemo, useState } from 'react';
import { fetchNativeProductTeamTableData } from '../_utils/services';
import { IFormData } from '../_utils/model';
import NativeTeamUserList from './NativeTeamUserList';

function NativeTeamsList({
  tableVers,
  nativeProductId,
  setIsRCommissionEditVisible,
  setCurrentTeamId,
  setCurrentTeamMemberId,
  teamUserTableVers,
  currentIProductId,
  setCurrentIProductId,
  formData,
  salesTeamIds,
  setSalesTeamIds,
}: {
  tableVers?: number;
  nativeProductId: string;
  setIsRCommissionEditVisible?: Function;
  setCurrentTeamId: Function;
  setCurrentTeamMemberId?: Function;
  teamUserTableVers: number;
  currentIProductId: number;
  setCurrentIProductId: Function;
  formData: IFormData[];
  salesTeamIds?: any[];
  setSalesTeamIds: Function;
}) {
  const t = useTrans('label.commission_setup,otr.common');
  const [defaultSelectedTeamIds, _setDefaultSelectedTeamIds] = useState<any[]>(salesTeamIds?.map((id) => ({ id })) || []);

  useEffect(() => {
    setCurrentIProductId(currentIProductId);
  }, [currentIProductId]);

  const columns = useMemo<ITablePropertyColumn[]>(
    () => [
      {
        id: 'name',
        header: t('team_name'),
        accessorKey: 'name',
        cell: ({ cell }: { cell: any }) => cell.getValue() || '-',
      },
    ],
    [],
  );

  const tableProperties = useAsyncTable({
    columns: columns,
    loadData: (props: any) => fetchNativeProductTeamTableData({ ...props, nativeProductId }),
    paginate: true,
    rowSelection: true,
    rowSelectionProp: {
      key: 'id',
      mode: 'multiple',
      actionColumn: true,
      enableSelectAll: true,
      action: (value: any, _data: any) => {
        setSalesTeamIds(value);
      },
      defaultSelectedKeys: defaultSelectedTeamIds,
    },
    rowExpandable: {
      primaryKey: 'id',
      expandableRows: () => true,
      expandedRowRender: (record: any) => {
        return (
          <NativeTeamUserList
            currentTeamId={record?.id}
            tableVers={0}
            setIsRCommissionEditVisible={setIsRCommissionEditVisible}
            setCurrentTeamMemberId={setCurrentTeamMemberId}
            setCurrentTeamId={setCurrentTeamId}
            key={teamUserTableVers}
            formData={formData}
            currentIProductId={currentIProductId.toString()}
          />
        );
      },
    },
  });

  useEffect(() => {
    tableProperties.reload();
  }, [tableVers]);

  return <Table {...{ tableProperties, searchOption: false, isRowPerPageVisible: false }} />;
}

export default React.memo(NativeTeamsList);
