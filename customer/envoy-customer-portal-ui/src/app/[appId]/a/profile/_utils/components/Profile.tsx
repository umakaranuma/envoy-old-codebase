'use client';
import { useTrans } from '@/helpers/services/lang/langService';
import Image from 'next/image';
import React, { useEffect, useState } from 'react';
import MyDetails from './MyDetails';
import Password from './Password';
import PaymentMethod from './PaymentMethod';
import { Flexicon } from '@apptimus-ui/flexicon';
import { useParams, useRouter, useSearchParams } from 'next/navigation';
import { getLocalStorage } from '@/helpers/handlers/localStorageHandler';
import { local_storage } from '@/constans/StorageKeys';
import { Dropdown } from '@apptimus-ui/dropdown';
import S3Avatar from '@/components/others/page-related/S3Avatar';
import { Button, Skeleton } from '@apptimus-ui/ui-element';
import { NotificationSettings } from './NotificationSettings';
import { IProfileDetails } from '../model';
import { getProfileMyDetails } from '../api-service';
import dummyCoverPic from '../../../../../../../public/images/dummyCoverPic.webp';

function Profile() {
  const t = useTrans('label.profile,otr.common');
  const [activeTab, setActiveTab] = useState('my-details');
  const [isDismissed, setIsDismissed] = useState(false);
  const [formData, setFormData] = useState<IProfileDetails>({} as IProfileDetails);
  const [skeleton, setSkeleton] = useState(true);
  const searchParams = useSearchParams();
  const router = useRouter();
  const params = useParams();
  const appId = params.appId as string;
  const authUser = getLocalStorage(local_storage.auth_user_info);
  const agentInfo = getLocalStorage(local_storage.agent_info);

  useEffect(() => {
    const tab = searchParams.get('t') || 'my-details';
    toggleTableTab(tab);
  }, []);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setSkeleton(true);
    const responseData = await getProfileMyDetails();
    if (responseData?.is_success) {
      setFormData(responseData.result);
      setSkeleton(false);
    }
  };

  const toggleTableTab = (activeTab: string) => {
    setActiveTab(activeTab);
    router.push(`/${appId}/a/profile?t=${activeTab}`, { scroll: false });
  };

  return (
    <div className="card custom-card text">
      <div className="d-flex flex-column align-items-center justify-content-center">
        {skeleton ? (
          <Skeleton width="100%" height="200px" />
        ) : (
          <div>
            <Image
              src={`${formData.contact_picture ? `${process.env.S3CDN}/${formData.contact_picture}` : dummyCoverPic.src}`}
              alt="Profile banner"
              className="w-100 img-fluid"
              height={400}
              width={2400}
            />
          </div>
        )}
        <div className="d-flex flex-row flex-wrap align-items-center justify-content-between gap-3 p-3 col-md-8 col-12 z-2" style={{ alignSelf: 'center', marginTop: '-2.5rem', zIndex: 10 }}>
          <div className="d-flex flex-row align-items-center justify-content-between gap-3">
            <div className="z-2">
              {skeleton ? (
                <Skeleton width="100px" height="100px" className="rounded-circle border border-2 border-white shadow img-fluid" />
              ) : (
                <S3Avatar imageKey={formData.logo} height={100} width={100} />
                //<Image src={`${formData.iban_swift_code ? `${process.env.S3CDN}/${formData.logo}` : dummyCoverPic.src}`} alt="Profile" width={100} height={100} className="rounded-circle border border-2 border-white shadow img-fluid" />
              )}
            </div>

            <div className="z-2">
              <div className="fw-semibold fs-24">{authUser.name}</div>
              <div className="text-muted">{authUser.email}</div>
            </div>
          </div>
          {/* <div className="d-flex flex-row align-items-center justify-content-between gap-3 z-2">
            <Button variant="light" className="border border-2 border-light text-muted">
              <span className="d-flex flex-row align-items-center gap-2">
                <Flexicon icon="user-plus-01" variant="line" size={18} />
                <span>{t('share')}</span>
              </span>
            </Button>
            <Button text={t('view_profile')} />
          </div> */}
        </div>
      </div>

      {!isDismissed && (
        <div className="border border-2 border-light d-inline-block rounded-3 mb-4 mx-3">
          <div className="d-md-flex gap-3 p-3">
            <div className="mb-3 mb-md-2">
              <Flexicon icon="alert-square" variant="line" />
            </div>
            <div>
              <div className="mb-3 mb-md-2">
                <div className="fw-medium">{t('important_notice_verified_information')}</div>
                <div className="text-muted">
                  {t(
                    'please_note_any_information_verified_by_the_insurer_or_brokerage_such_as_name_address_and_phone_number_cannot_be_modified_directly_by_you_through_the_customer_portal_if_you_believe_there_is_an_error_or_require_updates_please_contact_insurer_brokerage_support_contact_for_assistance',
                  )}
                </div>
              </div>

              <div className="d-flex gap-3">
                <div className="fw-semibold pointer" onClick={() => setIsDismissed(true)}>
                  {t('dismiss')}
                </div>

                <Dropdown className="ms-4" trigger={<div className="text-primary pointer">{t('contact')}</div>}>
                  {(onClose: any) => (
                    <>
                      <div className="p-3 px-4 mb-1">
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
              </div>
            </div>
          </div>
        </div>
      )}

      <div className="mt-3 px-3 bg-light py-2">
        <div className="il-tab pb-2 overflow-x-auto text-nowrap" style={{ scrollbarWidth: 'none' }}>
          <div className={`il-tab-item ${activeTab === 'my-details' ? 'active' : ''}`} onClick={() => toggleTableTab('my-details')}>
            {t('my_details')}
          </div>
          {/* <div className={`il-tab-item ${activeTab === 'password' ? 'active' : ''}`} onClick={() => toggleTableTab('password')}>
            {t('password')}
          </div> */}
          <div className={`il-tab-item ${activeTab === 'payment-method' ? 'active' : ''}`} onClick={() => toggleTableTab('payment-method')}>
            {t('payment_method')}
          </div>
          {/* <div className={`il-tab-item ${activeTab === 'notification-settings' ? 'active' : ''}`} onClick={() => toggleTableTab('notification-settings')}>
            {t('notifications_settings')}
          </div> */}
        </div>
      </div>

      <div className="p-3 px-md-4 py-md-3">
        {activeTab === 'my-details' && <MyDetails reloadProfile={() => fetchData()} />}
        {activeTab === 'password' && <Password />}
        {activeTab === 'payment-method' && <PaymentMethod />}
        {activeTab === 'notification-settings' && <NotificationSettings />}
      </div>
    </div>
  );
}

export default Profile;
