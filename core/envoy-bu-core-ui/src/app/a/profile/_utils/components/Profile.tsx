'use client';
import { useTrans } from '@/helpers/services/lang/langService';
import Image from 'next/image';
import React, { useEffect, useState } from 'react';
import MyDetails from './MyDetails';
import Password from './Password';
import PaymentMethod from './PaymentMethod';
import AutomationSettings from './AutomationSettings';
import { getLocalStorage } from '@/helpers/handlers/localStorageHandler';
import { local_storage } from '@/constans/StorageKeys';
import { Skeleton } from '@apptimus-ui/ui-element';
import { IUser } from '../model';
import S3Avatar from '@/components/others/page-related/S3Avatar';
import { getOneUser } from '@/app/a/users/_utils/api-service';

function Profile() {
  const [activetab, setActiveTab] = useState('my-details');
  const t = useTrans('label.profile,otr.common');
  const authUser = getLocalStorage(local_storage.auth_user_info);
  const [userData, setUserData] = useState<IUser | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (authUser?.id) {
      fetchUserData();
    }
  }, []);

  const fetchUserData = async () => {
    setLoading(true);
    try {
      const responseData = await getOneUser(authUser?.id);
      if (responseData?.is_success) {
        setUserData(responseData.result);
      }
    } catch (error) {
      console.error('Error fetching user data:', error);
    } finally {
      setLoading(false);
    }
  };

  const toggleTableTab = (activeTab: string) => {
    setActiveTab(activeTab);
  };

  const user = {
    bannerImage: '/images/banner.jpg',
  };

  return (
    <div className="card custom-card text">
      {/* banner & profile image */}
      <div className="profile-pg-container">
        {/* Banner */}
        <div className="banner-container position-relative rounded-5">
          <div className="banner-image-wrapper ">
            <Image src={user.bannerImage} alt="Profile banner" fill className="img-fluid" style={{ objectFit: 'cover' }} priority />
          </div>
        </div>

        {/* Profile Content */}
        <div className="profile-pg-content">
          <div className="profile-content-container">
            {/* Profile Image */}
            <div className="profile-image-wrapper">
              <div className="profile-image-inner">
                {loading ? <Skeleton height="140px" width="140px" className="rounded-circle" /> : <S3Avatar width={140} height={140} imageKey={userData?.picture ?? ''} />}
                {/* <Image src={user.profileImage} alt="Profile" fill className="profile-image rounded-circle border border-4 border-white shadow" style={{ objectFit: 'cover' }} /> */}
              </div>
            </div>

            {/* User Details */}
            <div className="user-details-wrapper">
              <div className="user-details">
                {loading ? <Skeleton height="30px" width="100px" className="mb-2" /> : <h3 className="user-name fw-bold mb-1">{userData?.display_name}</h3>}
                {loading ? <Skeleton height="20px" width="100px" /> : <p className="user-email text-muted mb-2">{userData?.email}</p>}
              </div>
            </div>
          </div>
        </div>
      </div>
      {/* warning msg */}
      {/* <div className="border border-2 border-light d-inline-block rounded-3 mb-4 mx-3">
        <div className="d-md-flex gap-3 p-3">
          <div className="mb-3 mb-md-2">
            <Flexicon icon="alert-square" variant="line" />
          </div>
          <div>
            <div className="mb-3 mb-md-2">
              <div className="fw-medium">Important Notice: Verified Information</div>
              <div className="text-muted">
                Please note, any information verified by the Vanguard X (such as name, address, and phone number) cannot be modified directly by you through the portal. If you believe there is an
                error or require updates, please contact Support Team for assistance.
              </div>
            </div>

            <div className="d-flex gap-3">
              <div className="fw-semibold">Dismiss</div>
              <div className="text-primary">Contact</div>
            </div>
          </div>
        </div>
      </div> */}

      <div className="px-3">
        <div className="il-box-tab pb-2">
          <div className={`il-box-tab-item ${activetab === 'my-details' ? 'active' : ''}`} onClick={() => toggleTableTab('my-details')}>
            {t('my_details')}
          </div>
          {/* <div className={`il-box-tab-item ${activetab === 'password' ? 'active' : ''}`} onClick={() => toggleTableTab('password')}>
            {t('password')}
          </div>
          <div className={`il-box-tab-item ${activetab === 'payment-method' ? 'active' : ''}`} onClick={() => toggleTableTab('payment-method')}>
            {t('payment_method')}
          </div>
          <div className={`il-box-tab-item ${activetab === 'automation-settings' ? 'active' : ''}`} onClick={() => toggleTableTab('automation-settings')}>
            {t('workflows_automation_settings')}
          </div> */}
        </div>
      </div>

      <div className="p-3 px-md-4 py-md-3">
        {activetab === 'my-details' && <MyDetails userData={userData} afterSave={() => fetchUserData()} loading={loading} />}
        {activetab === 'password' && <Password />}
        {activetab === 'payment-method' && <PaymentMethod />}
        {activetab === 'automation-settings' && <AutomationSettings />}
      </div>
    </div>
  );
}

export default Profile;
