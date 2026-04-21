'use client';

import { Button } from '@apptimus-ui/ui-element';
import { useState } from 'react';
import { Flexicon } from '@apptimus-ui/flexicon';
import { useTrans } from '@/helpers/services/lang/langService';
import SampleList from './SampleList';
import PageHeading from '@/components/others/PageHeading';
import { SampleDelete } from './SampleDelete';
import { SampleView } from './SampleView';
import SampleCreate from './SampleCreate';
import { SampleEdit } from './SampleEdit';

function Sample() {
  const [tableVers, setTableVers] = useState(0);
  const [createFormKey, setCreateFormKey] = useState(0);
  const [createFormVisible, setCreateFormVisible] = useState(false);
  const [currentViewId, setCurrentViewId] = useState('');
  const [currentEditId, setCurrentEditId] = useState('');
  const [currentDeleteId, setCurrentDeleteId] = useState('');

  const handleCreateFormOnCancel = () => {
    setCreateFormVisible(false);
    setCreateFormKey((prevCreateFormKey) => prevCreateFormKey + 1);
  };

  const handleAfterSave = () => {
    setTableVers((prevTableVers) => prevTableVers + 1);
    setCreateFormKey((prevCreateFormKey) => prevCreateFormKey + 1);
  };

  const handleAfterUpdate = () => {
    setCurrentEditId('');
    setTableVers((prevTableVers) => prevTableVers + 1);
  };

  const t = useTrans('label.sample,otr.common');

  return (
    <>
      <div className="page-header-breadcrumb custom-page-header">
        <PageHeading title={t('samples')} icon="sun-light" />
        <Button color="light" className="d-flex align-items-center gap-1" onClick={() => setCreateFormVisible(true)}>
          <Flexicon icon="plus" size={15} />
          <span className="d-none d-sm-inline">{t('add_new_entity', { entity: t('sample') })}</span>
        </Button>
      </div>

      <SampleList tableVers={tableVers} onView={(id: string) => setCurrentViewId(id)} onEdit={(id: string) => setCurrentEditId(id)} onDelete={(id: string) => setCurrentDeleteId(id)} />

      <SampleView viewId={currentViewId} isOpen={currentViewId !== ''} onClose={() => setCurrentViewId('')} />

      <SampleCreate key={createFormKey} isOpen={createFormVisible} onCancel={handleCreateFormOnCancel} afterSave={handleAfterSave} />

      <SampleEdit editId={currentEditId} isOpen={currentEditId !== ''} onCancel={() => setCurrentEditId('')} afterUpdate={handleAfterUpdate} />

      <SampleDelete
        isOpen={currentDeleteId !== ''}
        deleteId={currentDeleteId}
        afterDelete={() => (setCurrentDeleteId(''), setTableVers((prevTableVers) => prevTableVers + 1))}
        onCancel={() => setCurrentDeleteId('')}
      />
    </>
  );
}

export default Sample;
