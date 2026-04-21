import { useTrans } from '@/helpers/services/lang/langService';
import { Modal, ModalBody, ModalFooter, ModalHeader } from '@apptimus-ui/modal';
import { Button } from '@apptimus-ui/ui-element';
import React, { useMemo } from 'react';
import InvitationListCard from './InvitationListCard';
import { getAllInvitations } from '../api-service';
import { IInvitation } from '../model';
import { useAsyncTable } from '@apptimus-ui/table';
import RecordController from '@/components/table-properties/RecordController';

function InvitationList({ isOpen, onCancel }: { isOpen: boolean; onCancel: Function }) {
  const t = useTrans('label.user,otr.common');
  const columns = useMemo(() => [], []);

  const tableProperties = useAsyncTable({
    columns,
    loadData: async ({ searchValue, currentPage, itemsPerPage }) => {
      const response = await getAllInvitations({
        search: searchValue,
        page: currentPage,
        limit: itemsPerPage,
      });

      if (response.is_success) {
        return {
          data: response.result.data,
          dataLength: response.result.total_records,
        };
      }

      return { data: [], dataLength: 0 };
    },
    paginate: true,
  });

  const { SearchInput }: any = tableProperties;

  return (
    <Modal isOpen={isOpen} size="lg" scrollable onBackdrop={() => onCancel()}>
      <ModalHeader title={t('invitation_list')} onClose={() => onCancel()} />
      <ModalBody>
        <div className="mb-3">
          <div className="d-flex justify-content-between align-items-center">
            <div className="w-25">{SearchInput}</div>
            <RecordController tableProperties={tableProperties} isRowPerPageVisible={false} isPaginationTextVisible={false} />
          </div>
        </div>

        {tableProperties.tableInitiated && (
          <div className="d-flex flex-row justify-content-between flex-wrap gap-3">
            {tableProperties?.tableData?.map((invitation: IInvitation) => <InvitationListCard data={invitation} onReload={tableProperties.reload} key={invitation.uid} />)}
          </div>
        )}

        {tableProperties.tableInitiated && tableProperties.dataLength === 0 && <div className="text-muted">{t('no_records_found')}</div>}
      </ModalBody>

      <ModalFooter>
        <div className="d-flex justify-content-end gap-2">
          <Button text={t('close')} color="light" width="sm" onClick={() => onCancel()} />
        </div>
      </ModalFooter>
    </Modal>
  );
}

export default InvitationList;
