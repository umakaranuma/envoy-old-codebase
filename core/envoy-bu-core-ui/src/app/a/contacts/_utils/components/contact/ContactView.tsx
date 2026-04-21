'use client';
import { useEffect, useState } from 'react';
import { Description } from '@/components/others/Description';
import { useTrans } from '@/helpers/services/lang/langService';
import { deleteMergeAccounts, getOneContacts } from '../../api-service';
import { IContacts } from '../../model';
import Interaction from '../interaction/Interaction';
import { useParams, useRouter, useSearchParams } from 'next/navigation';
import { Button } from '@apptimus-ui/ui-element';
import { ContactEdit } from './ContactEdit';
import S3Avatar from '@/components/others/page-related/S3Avatar';
import ToggleButton from '@/components/others/page-related/ToggleButton';
import Accounts from '../accounts/Accounts';
import { Dropdown, DropdownItem } from '@apptimus-ui/dropdown';
import { Flexicon } from '@apptimus-ui/flexicon';
import DeleteConfirmPop from '@/components/others/DeleteConfirmPop';
import { toaster } from '@/helpers/services/toaster';
import GoBack from '@/components/others/page-related/GoBack';

export const ContactView = () => {
  const t = useTrans('label.contacts,otr.common');
  const tBe = useTrans('be.msg,be.error,be.attri');
  const [data, setData] = useState({} as IContacts);
  const [skeleton, setSkeleton] = useState(true);
  const [tab, setTab] = useState('interactions');
  const [isEditOpen, setIsEditOpen] = useState(false);
  const [isToggled, setIsToggled] = useState(false);
  const router = useRouter();
  const params = useParams();
  const pid = useSearchParams();
  const viewId = params.id?.toString() || '';
  const [tableVers, setTableVers] = useState(0);
  const [getPid, setGetPid] = useState('');

  useEffect(() => {
    if (viewId) {
      setSkeleton(true);
    }
  }, [viewId]);

  useEffect(() => {
    const tab = pid.get('pid') || '';
    setGetPid(tab);
  }, [pid]);

  useEffect(() => {
    if (viewId) {
      fetchData();
    }
  }, [viewId, tableVers]);

  const fetchData = async () => {
    const responseData = await getOneContacts(viewId);
    responseData?.is_success && (setData(responseData.result), setSkeleton(false));
  };

  const handleOnDelete = async (deleteId: string, callback: Function, setLoader: Function, onClose: Function) => {
    setLoader(true);
    const responseData = await deleteMergeAccounts(deleteId);
    setLoader(false);

    if (responseData.is_success) {
      toaster.success(tBe(responseData.message));
      callback();
      onClose();
      setTableVers((prevTableVers) => prevTableVers + 1);
    }
  };

  return (
    <>
      <GoBack goTo={() => router.push(pid ? `/a/contacts/${getPid}` : '/a/contacts')} title={data.name} skeleton={skeleton} />
      <div className="panel">
        <div className="row pb-2">
          <div className="col-12 col-md-6 mb-3">
            <Description label={t('contact_person_name')} value={data?.name || '-'} skeleton={skeleton} />
          </div>
          <div className="col-12 col-md-6 mb-3">
            <Description label={t('address')} value={data?.address || '-'} skeleton={skeleton} />
          </div>
          <div className="col-12 col-md-6 mb-3">
            <Description label={t('email_address')} value={data?.email || '-'} skeleton={skeleton} />
          </div>
          {/* <div className="d-flex justify-content-between mb-3 align-items-center">
          <div className="fw-semibold">{t('contact_info')}</div>
          <div className="datatable-search mb-3"></div>
        </div> */}
          <div className="col-12 col-md-6 mb-3">
            <Description label={t('primary_contact_number')} value={data?.primary_contact || '-'} skeleton={skeleton} />
          </div>
          <div className="col-12 col-md-6 mb-3">
            <Description label={t('secondary_contact_number')} value={data?.secondary_contact || '-'} skeleton={skeleton} />
          </div>
          <div className="col-12 col-md-12 mb-3">
            <Description isTruncate={false} label={t('remarks')} value={data?.remarks || '-'} skeleton={skeleton} />
          </div>
        </div>
        <div>
          {data?.merged_contacts?.length > 0 && (
            <div className="my-2 d-flex gap-2 flex-row">
              <ToggleButton isToggled={isToggled} setIsToggled={setIsToggled} />
              <div className="fw-medium">{t('show_merged_contacts')}</div>
            </div>
          )}
          {isToggled && (
            <div className="d-flex gap-2 ">
              {data.merged_contacts?.map((contact: any, index: number) => (
                <>
                  <div
                    className="d-flex flex-row align-items-center gap-2 border border-2 px-2 py-1 rounded-2 pointer"
                    key={index}
                    onClick={() => router.push(`/a/contacts/${contact.id}?pid=${viewId}`)}
                  >
                    <div>
                      <S3Avatar imageKey={undefined} width={45} height={45} />
                    </div>
                    <div className="d-flex flex-column">
                      <div className="fw-medium fs-13">{contact.name}</div>
                      <div className="fs-12">{contact.email}</div>
                      <div className="fs-11">{contact.primary_contact}</div>
                    </div>
                    <div className="" onClick={(e: any) => e.stopPropagation()}>
                      <Dropdown
                        trigger={
                          <span className="action-icon">
                            <Flexicon icon="dots-horizontal" variant="line" size={17} />
                          </span>
                        }
                      >
                        {(onClose: Function) => (
                          <span className="t-action">
                            <DropdownItem onClick={() => router.push(`/a/contacts/${contact.id}?pid=${viewId}`)}>
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
                              deleteId={contact.id}
                              {...{ handleOnDelete, onClose }}
                            />
                          </span>
                        )}
                      </Dropdown>
                    </div>
                  </div>
                </>
              ))}
            </div>
          )}
        </div>
        <div className="d-flex justify-content-end gap-2">
          {/* <Button text={t('edit_entity', { entity: t('contact_details') })} type="submit" size="sm" width="sm" onClick={() => setIsEditOpen(true)} /> */}
          <Button onClick={() => setIsEditOpen(true)}>
            <span className="d-flex gap-2">
              <Flexicon icon="pencil-line" variant="line" size={17} />
              <span>{t('edit')}</span>
            </span>
          </Button>
        </div>
      </div>

      <div className="panel">
        <div className="il-box-tab p-2">
          <div className={`il-box-tab-item ${tab === 'interactions' ? 'active' : ''}`} onClick={() => setTab('interactions')}>
            {t('interactions')}
          </div>
          <div className={`il-box-tab-item ${tab === 'accounts' ? 'active' : ''}`} onClick={() => setTab('accounts')}>
            {t('accounts')}
          </div>
        </div>

        <div className="bg-white custom-card overflow-hidden p-3 rounded-3 mt-3">
          {tab === 'interactions' && <Interaction id={viewId} onClose={() => {}} />}
          {tab === 'accounts' && <Accounts id={viewId} onClose={() => {}} />}
        </div>
      </div>

      {isEditOpen && <ContactEdit editId={viewId} isOpen={isEditOpen} onCancel={() => setIsEditOpen(false)} afterUpdate={() => fetchData()} />}
    </>
  );
};
