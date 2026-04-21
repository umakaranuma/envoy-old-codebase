// import { useCustomizeColumn } from '@/components/others/CustomizeColumn';
// import Table from '@/components/table-properties/Table';
// import { ITablePropertyColumn } from '@/interface/ICommon';
// import { useAsyncTable } from '@apptimus-ui/table';
// import { useEffect, useMemo, useState } from 'react';
// import PageHeading from '@/components/others/PageHeading';
// import { useTrans } from '@/helpers/services/lang/langService';
// import { fetchPoliciesOfCustomerTableData } from '../../services';

// function PolicyHolderPolicyList({ customerId, setSelectedPolicyId }: { customerId: string; setSelectedPolicyId: Function }) {
//   const t = useTrans('label.claim,otr.common');
//   const tableName = 'policyInformation';
//   const [isFullscreen, _setIsFullscreen] = useState(false);
//   const [tableColumnVers, _setTableColumnVers] = useState(0);

//   const columns = useMemo<ITablePropertyColumn[]>(
//     () => [
//       {
//         id: 'brokerage_policy_id',
//         header: t('policy_id'),
//         accessorKey: 'brokerage_policy_id',
//         sort: true,
//         visibilityLock: false,
//       },
//       {
//         id: 'risk_type_title',
//         header: t('policy_name'),
//         accessorKey: 'risk_type_title',
//         sort: true,
//       },
//       {
//         id: 'start_date',
//         header: t('start_date'),
//         accessorKey: 'start_date',
//         sort: true,
//         accessorFn: (row: any) => row.start_date.split('T')[0],
//       },
//       {
//         id: 'end_date',
//         header: t('end_date'),
//         accessorKey: 'end_date',
//         sort: true,
//         accessorFn: (row: any) => row.start_date.split('T')[0],
//       },
//       {
//         id: 'status',
//         header: t('status'),
//         accessorKey: 'status',
//         sort: true,
//         cell: ({ cell }: any) => <div>{cell.getValue() || '-'}</div>,
//       },
//     ],
//     [],
//   );

//   const tableColumns = useCustomizeColumn({ ...{ tableName, columns, tableColumnVers } });

//   const tableProperties = useAsyncTable({
//     columns: tableColumns,
//     loadData: (props: any) => fetchPoliciesOfCustomerTableData(props, customerId),
//     paginate: true,
//     rowSelection: true,
//     rowSelectionProp: {
//       key: 'id',
//       mode: 'single',
//       actionColumn: true,
//       enableSelectAll: false,
//       action: (value: any, _data: any) => {
//         setSelectedPolicyId(value);
//       },
//     },
//   });

//   useEffect(() => {
//     tableProperties.reload();
//     tableProperties.reset({ type: 'row-selection' });
//   }, [tableColumnVers]);

//   return (
//     <>
//       <div className={`data-table-container card custom-card ${isFullscreen ? 'dtc-fullscreen card-fullscreen' : 'mt-4'}`}>
//         <Table heading={<PageHeading title={t('roles')} icon="sun-light" />} searchOption={false} isRowPerPageVisible={false} {...{ tableProperties }} />
//       </div>
//     </>
//   );
// }

// export default PolicyHolderPolicyList;
