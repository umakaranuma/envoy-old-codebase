import S3Avatar from '@/components/others/page-related/S3Avatar';
import { local_storage } from '@/constans/StorageKeys';
import { getLocalStorage } from '@/helpers/handlers/localStorageHandler';
import { useTrans } from '@/helpers/services/lang/langService';
import { Dropdown } from '@apptimus-ui/dropdown';
import { Flexicon } from '@apptimus-ui/flexicon';
import { Button } from '@apptimus-ui/ui-element';
import React from 'react';

function ContactAgent({ reachedBreakpoint }: { reachedBreakpoint: boolean }) {
  const t = useTrans('label.profile,otr.common');

  const agentInfo = getLocalStorage(local_storage.agent_info);

  return (
    <Dropdown trigger={<Button text={t('contact_agent')} size={reachedBreakpoint ? 'sm' : undefined} width={reachedBreakpoint ? 'sm' : undefined} />}>
      {(onClose: any) => (
        <>
          <div className="p-3 px-4">
            <div style={{ width: '220px' }}>
              <div className="d-flex flex-column gap-2">
                <div className="text-end align-self-center">
                  <S3Avatar width={60} height={60} imageKey={agentInfo?.logo} />
                </div>
                <div className="align-self-center">
                  <div className="fs-18 fw-medium">{agentInfo?.display_name}</div>
                  <div className="fs-14 text-muted">{agentInfo?.email}</div>
                </div>
                <div className="d-flex flex-row justify-content-between align-items-center gap-3 my-2">
                  <Button color="primary" className="d-flex align-items-center gap-1" variant="outline" onClick={onClose}>
                    <Flexicon icon="mail-01" variant="line" size={18} />
                    <a className="d-none d-sm-inline" href={`https://wa.me/${agentInfo?.contact}`}>
                      {t('message')}
                    </a>
                  </Button>
                  <Button color="primary" className="d-flex align-items-center gap-1 px-4" onClick={onClose}>
                    <Flexicon icon="phone-call-01" variant="line" size={18} />
                    <a className="d-none d-sm-inline text-white" href={`tel:${agentInfo?.contact}`}>
                      {t('call')}
                    </a>
                  </Button>
                </div>
              </div>
            </div>
          </div>
        </>
      )}
    </Dropdown>
  );
}

export default ContactAgent;
