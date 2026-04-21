'use client';
import { useCustomizeColumn } from '@/components/others/CustomizeColumn';
import Table from '@/components/table-properties/Table';
import { ITablePropertyColumn } from '@/interface/ICommon';
import { useAsyncTable } from '@apptimus-ui/table';
import { useEffect, useMemo, useState } from 'react';
import { useTrans } from '@/helpers/services/lang/langService';
import { hexToRgba } from '@/helpers/services/commonService';
import { fetchAllServiceProvidersOfQuotationTableData } from '../../service';
import { useParams } from 'next/navigation';
import ProfileInfo from '@/components/others/page-related/ProfileInfo';
import Chat from '@/components/others/page-related/chat/Chat';
import { createMsg, getAllChatMsg, getDocumentData, getSyncChatMsg } from '../../api-service';
import AddQuotation from './received/AddQuotation';
import { IFileData } from '@/components/others/page-related/chat/_utils/model';

function ServiceProviderList({ setReceivedTabKey }: { setReceivedTabKey?: Function }) {
  const t = useTrans('label.quotations,otr.common');
  const tableName = 'quotation_service_provider';
  const [tableColumnVers, _setTableColumnVers] = useState(0);
  const [data, setData] = useState<IFileData | null>(null);
  const [loading, setLoading] = useState(false);
  const params = useParams();
  const quotationId = params.quotationId?.toString() || '';

  const handleAddQuotation = async (id: string) => {
    setLoading(true);
    const response = await getDocumentData(id);
    if (response.is_success) {
      setData(response.result);
    }
    setLoading(false);
  };
  const columns = useMemo<ITablePropertyColumn[]>(
    () => [
      {
        id: 'name',
        header: t('insurer_company_name'),
        accessorKey: 'name',
        sort: true,
        visibilityLock: false,
        cell: ({ cell }: any) => <ProfileInfo imageKey={`${cell.insurer_image}`} title={cell.name} subtitle={cell.insurer_email} defaultImage="/images/default-profile.png" />,
      },
      {
        id: 'quotation_id',
        header: t('insurer_request_id'),
        accessorKey: 'quotation_id',
        sort: true,
      },
      {
        id: 'status',
        header: t('status'),
        accessorKey: 'status',
        sort: true,
        visibilityLock: false,
        cell: ({ cell, onClick }: any) => {
          return (
            <div className="d-flex justify-content-between align-items-center gap-3" onClick={onClick}>
              <div
                className={`d-flex flex-row align-items-center gap-1 rounded-1 fs-10 fw-bold badge`}
                style={{ background: hexToRgba('#28a745', 0.1), border: `1px solid #28a745`, color: '#28a745' }}
              >
                <svg width="9" height="8" viewBox="0 0 9 8" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <circle cx="4.375" cy="4" r="3" fill={'#28a745'} />
                </svg>
                {cell.received_status}
              </div>
            </div>
          );
        },
      },
      {
        id: 're_requested',
        header: t('re_requested'),
        accessorKey: 're_requested',
        sort: true,
        cell: ({ cell }: { cell: any }) => <>{cell.getValue() === 'new' ? <>Yes</> : <>No</>}</>,
      },
    ],
    [],
  );

  const tableColumns = useCustomizeColumn({ ...{ tableName, columns, tableColumnVers } });

  const tableProperties = useAsyncTable({
    columns: tableColumns,
    loadData: (props: any) => fetchAllServiceProvidersOfQuotationTableData(props, quotationId),
    paginate: true,
    rowExpandable: {
      primaryKey: 'service_provider_id',
      expandableRows: () => true,
      expandedRowRender: (record: any) => {
        return (
          <>
            <Chat
              id={quotationId}
              getAllChatMsg={(params: any) => getAllChatMsg(params, false, quotationId, record.service_provider_id.toString())}
              createMsgFn={createMsg}
              getSyncChatMsg={getSyncChatMsg}
              handleAddQuotation={handleAddQuotation}
              loading={loading}
            />
          </>
        );
      },
    },
  });

  useEffect(() => {
    tableProperties.reload();
  }, [tableColumnVers]);

  return (
    <>
      <Table {...{ tableProperties, searchOption: false, recordControl: false }} />
      {data?.document_url && (
        <AddQuotation
          defaultData={data}
          isOpen={!!data.document_url}
          onCancel={() => setData(null)}
          afterSave={() => {
            setData(null), setReceivedTabKey && setReceivedTabKey((prev: number) => prev + 1);
          }}
          quotationId={quotationId}
        />
      )}
    </>
  );
}

export default ServiceProviderList;
