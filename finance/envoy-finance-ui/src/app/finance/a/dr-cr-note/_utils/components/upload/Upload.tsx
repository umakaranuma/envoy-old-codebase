'use client';

import { useTrans } from '@/helpers/services/lang/langService';
import { Flexicon } from '@apptimus-ui/flexicon';
import { Button, Input } from '@apptimus-ui/ui-element';
import { useRouter } from 'next/navigation';
import React, { useState } from 'react';
import PreviewList from './tabs/PreviewList';
import Summary from './tabs/Summary';
import Mapping from './tabs/Mapping';
import EditMapping from './tabs/EditMapping';
import GoBack from '@/components/others/page-related/GoBack';

function Upload() {
  const router = useRouter();
  const t = useTrans('label.invoice,otr.common,be.msg');
  const [currentTabId, setCurrentTabId] = useState(1);
  const [resource, setResource] = useState<File | null>(null);
  const [currentEditId, setCurrentEditId] = useState<string>('');

  console.log(resource);

  const steps = [
    { id: 1, title: t('file_upload') },
    { id: 2, title: t('map_fields') },
    { id: 3, title: t('summary') },
    { id: 4, title: t('preview_and_submit') },
  ];

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      const file = e.target.files[0];
      setResource(file);
      setCurrentTabId(1);
    }
  };

  const onBack = () => {
    if (currentTabId > 0) {
      setCurrentTabId(currentTabId - 1);
    } else {
      router.push('/finance/a/invoices');
    }
  };

  const handleNextPage = () => {
    console.log('steps.length', steps.length, 'currentTabId', currentTabId);

    //clearError(form.upload.store);
    if (currentTabId < steps.length + 1) {
      setCurrentTabId(currentTabId + 1);
    }
  };

  return (
    <>
      <GoBack goTo={() => router.push('/finance/a/invoices')} title={t('mapping_payment')} />
      <div className="card-body bg-white p-3 rounded-3 mb-3">
        <ul className="d-flex justify-content-center gap-5 list-unstyled mb-0 crm-recent-activity">
          {steps.map((step, index) => (
            <li key={index} className="crm-recent-activity-content">
              <div className="align-items-center">
                <div className="d-flex justify-content-center me-3">
                  {step.id <= currentTabId ? (
                    <>
                      <span className={`avatar avatar-xs bg-primary-transparent avatar-rounded`}>
                        <Flexicon icon="check-circle" variant="solid" size={50} />
                      </span>
                    </>
                  ) : (
                    <>
                      <span className="avatar claim-avatar claim-transparent claim-avatar-rounded">
                        <i className="bi bi-circle-fill fs-8"></i>
                      </span>
                    </>
                  )}
                </div>
                <div className="mt-2">
                  <div className="fw-medium mb-1 fs-12">{step.title}</div>
                </div>
              </div>
            </li>
          ))}
        </ul>
      </div>
      {currentTabId === 1 && (
        <div className="panel">
          <div className="fs-15 fw-semibold mb-3">{t('upload_payment_data_file')}</div>
          <div className="col-12 col-md-3 mb-3">
            <Input label={t('select_file')} isRequired type="file" onChange={(e: any) => handleFileChange(e)} className="form-control error-invoice_document" name="invoice_document" />
          </div>
        </div>
      )}
      {currentTabId === 2 && <Mapping />}
      {currentTabId === 3 && <Summary />}
      {currentTabId === 4 && <PreviewList onEdit={(id: string) => setCurrentEditId(id)} />}

      <div className="d-flex justify-content-start gap-2 mt-3">
        <Button color="light" className="d-flex align-items-center gap-1" onClick={() => onBack()}>
          <Flexicon icon="chevron-left" variant="line" size={18} />
          <span className="d-none d-sm-inline">{t('back')}</span>
        </Button>
        {currentTabId === 4 ? (
          <Button color="primary" text={t('upload')} onClick={() => {}} />
        ) : (
          <Button color="primary" className="d-flex align-items-center gap-1" onClick={() => handleNextPage()}>
            <span className="d-none d-sm-inline">{t('next')}</span>
            <Flexicon icon="chevron-right" variant="line" size={18} />
          </Button>
        )}
      </div>
      {currentEditId !== '' && <EditMapping isOpen={currentEditId !== ''} onCancel={() => setCurrentEditId('')} />}
    </>
  );
}

export default Upload;
