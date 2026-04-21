import { form } from '@/constans/Form';
import { clearError, printError } from '@/helpers/handlers/validationErrorHandler';
import { useTrans } from '@/helpers/services/lang/langService';
import { toaster } from '@/helpers/services/toaster';
import { Modal, ModalBody, ModalFooter, ModalHeader } from '@apptimus-ui/modal';
import { Button, Label } from '@apptimus-ui/ui-element';
import React, { FormEvent, useMemo, useState } from 'react';
import 'react-phone-input-2/lib/style.css';
import { mergeContacts } from '../../api-service';
import { ITablePropertyColumn } from '@/interface/ICommon';
import ContactCard from '../group/ContactCard';
import { useCustomizeColumn } from '@/components/others/CustomizeColumn';
import { useAsyncTable } from '@apptimus-ui/table';
import Table from '@/components/table-properties/Table';
import { fetchMergeableContacts } from '../../service';

function MergeContacts({ isOpen, onCancel, afterSave, selectedContacts }: { isOpen: boolean; onCancel: Function; afterSave: Function; selectedContacts: string[] }) {
  const tableName = 'mergeable_contacts';
  const tBe = useTrans('be.msg,be.error,be.attri');
  const t = useTrans('label.contacts,otr.common');
  const [isFormProcessing, setIsFormProcessing] = useState(false);
  const [primaryContact, setPrimaryContact] = useState();
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
    loadData: (params: any) => fetchMergeableContacts(params, selectedContacts.join(',')),
    paginate: true,
    rowSelection: true,
    rowSelectionProp: {
      key: 'id',
      mode: 'single',
      actionColumn: true,
      enableSelectAll: true,
      action: (value: any, _data: any) => {
        setPrimaryContact(value);
      },
    },
  });

  async function onSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    clearError(form.contact_crud.store);
    setIsFormProcessing(true);

    try {
      const responseData = await mergeContacts({ contact_ids: selectedContacts, primary_contact_id: primaryContact });
      setIsFormProcessing(false);

      if (responseData.status_code === 417) {
        printError(responseData.result, form.contact_crud.store, tBe);
      }

      if (responseData.is_success) {
        onCancel();
        afterSave();
        toaster.success(tBe(responseData.message));
      }
    } catch (error) {
      console.error('An error occurred:', error);
    }
  }

  return (
    <Modal isOpen={isOpen} size="lg">
      <ModalHeader title={t('merge_contacts')} onClose={() => onCancel()} />
      <form onSubmit={onSubmit} id={`${form.contact_crud.store}`}>
        <ModalBody>
          <span className="error-primary_contact_id"></span>
          <Label label={t('select_the_primary_contact')} />
          <div className={`rounded-2 w-100 dark-border overflow-hidden table-header-hide`}>
            <Table {...{ tableProperties, isRowPerPageVisible: false, searchOption: false, recordControl: false }} />
          </div>
        </ModalBody>
        <ModalFooter>
          <div className="d-flex justify-content-end gap-2">
            <Button text={t('submit')} type="submit" width="sm" isLoading={isFormProcessing} />
            <Button text={t('cancel')} color="light" width="sm" onClick={() => onCancel()} />
          </div>
        </ModalFooter>
      </form>
    </Modal>
  );
}

export default MergeContacts;
