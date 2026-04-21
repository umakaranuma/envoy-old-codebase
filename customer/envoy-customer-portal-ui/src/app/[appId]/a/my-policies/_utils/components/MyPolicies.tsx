'use client';
import React, { useState } from 'react';
import { useTrans } from '@/helpers/services/lang/langService';
import { Button } from '@apptimus-ui/ui-element';
import MyPoliciesList from './MyPoliciesList';
import { useParams, useRouter } from 'next/navigation';
import SelectInterestedProduct from './create-policy/individual/SelectInterestedProduct';
import SelectInterestedProductForCommercial from './create-policy/commercial/SelectInterestedProductForCommercial';
import { getLocalStorage } from '@/helpers/handlers/localStorageHandler';
import { local_storage } from '@/constans/StorageKeys';

function MyPolicies() {
  const t = useTrans('label.my_policy,otr.common');
  const router = useRouter();
  const params = useParams();
  const appId = params.appId as string;
  const [isOpen, setIsOpen] = useState(false);
  const [key, setKey] = useState(0);
  const [commercialLine, setCommercialLine] = useState({ isOpen: false, key: 0 });
  const authUser = getLocalStorage(local_storage.auth_user_info);

  const handleClose = () => {
    setIsOpen(false);
    setKey((prevKey) => prevKey + 1);
  };

  const handleCloseCommercialLine = () => {
    setCommercialLine({ isOpen: false, key: commercialLine.key + 1 });
  };

  const handleNavigateCommercial = (requestId: any, productId: any, riskTypeId: string[]) => {
    router.push(`/${appId}/a/my-policies/create-commercial?reqId=${requestId}&pId=${productId}&rId=${riskTypeId.join(',')}`, { scroll: false });
    handleCloseCommercialLine();
  };

  return (
    <div className="bg-white rounded-2 pt-3 px-3">
      <div className="d-flex justify-content-between mb-3">
        <div className="fs-18 fw-semibold">{t('my_policies')}</div>
        {/* <Button color="primary" className="d-flex align-items-center gap-1" onClick={() => setCommercialLine((prevData) => ({ ...prevData, isOpen: true }))}>
          <span className="d-none d-sm-inline">{t('buy_new_policy')}</span>
          <svg width="18" height="18" viewBox="0 0 18 18" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path
              d="M7.75025 10.2499L16.5003 1.4999M7.85657 10.5233L10.0467 16.155C10.2396 16.6511 10.3361 16.8991 10.4751 16.9716C10.5956 17.0343 10.7391 17.0344 10.8597 16.9718C10.9988 16.8995 11.0955 16.6516 11.2891 16.1557L16.781 2.08256C16.9557 1.63491 17.043 1.41109 16.9953 1.26807C16.9538 1.14386 16.8563 1.04639 16.7321 1.00489C16.5891 0.957112 16.3652 1.04446 15.9176 1.21915L1.84447 6.7111C1.34857 6.90462 1.10062 7.00138 1.02837 7.14047C0.965726 7.26104 0.96581 7.40458 1.02859 7.52508C1.10101 7.66408 1.34907 7.76055 1.84519 7.95349L7.47686 10.1436C7.57757 10.1827 7.62793 10.2023 7.67033 10.2326C7.70791 10.2594 7.74077 10.2922 7.76758 10.3298C7.79782 10.3722 7.81741 10.4226 7.85657 10.5233Z"
              stroke="white"
              strokeWidth="1.66667"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        </Button> */}
        <Button
          color="primary"
          className="d-flex align-items-center gap-1"
          onClick={() => {
            authUser?.type === 'Personal' ? setIsOpen(true) : setCommercialLine((prevData) => ({ ...prevData, isOpen: true }));
          }}
        >
          <span className="d-none d-sm-inline">{t('buy_new_policy')}</span>
          <svg width="18" height="18" viewBox="0 0 18 18" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path
              d="M7.75025 10.2499L16.5003 1.4999M7.85657 10.5233L10.0467 16.155C10.2396 16.6511 10.3361 16.8991 10.4751 16.9716C10.5956 17.0343 10.7391 17.0344 10.8597 16.9718C10.9988 16.8995 11.0955 16.6516 11.2891 16.1557L16.781 2.08256C16.9557 1.63491 17.043 1.41109 16.9953 1.26807C16.9538 1.14386 16.8563 1.04639 16.7321 1.00489C16.5891 0.957112 16.3652 1.04446 15.9176 1.21915L1.84447 6.7111C1.34857 6.90462 1.10062 7.00138 1.02837 7.14047C0.965726 7.26104 0.96581 7.40458 1.02859 7.52508C1.10101 7.66408 1.34907 7.76055 1.84519 7.95349L7.47686 10.1436C7.57757 10.1827 7.62793 10.2023 7.67033 10.2326C7.70791 10.2594 7.74077 10.2922 7.76758 10.3298C7.79782 10.3722 7.81741 10.4226 7.85657 10.5233Z"
              stroke="white"
              strokeWidth="1.66667"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        </Button>
      </div>
      <MyPoliciesList />
      {isOpen && (
        <SelectInterestedProduct
          type="customer_policy"
          isOpen={isOpen}
          onCancel={handleClose}
          setIds={(id: any, productId: any, riskTypeId: any) => {
            router.push(`/${appId}/a/my-policies/create?fId=${id}&pId=${productId}&rId=${riskTypeId}`, { scroll: false }), setIsOpen(false);
          }}
          key={key}
        />
      )}
      {commercialLine.isOpen && (
        <SelectInterestedProductForCommercial
          type="policy"
          isOpen={commercialLine.isOpen}
          onCancel={handleCloseCommercialLine}
          setIds={(requestId: any, productId: any, riskTypeId: any) => handleNavigateCommercial(requestId, productId, riskTypeId)}
          key={commercialLine.key}
        />
      )}
    </div>
  );
}

export default MyPolicies;
