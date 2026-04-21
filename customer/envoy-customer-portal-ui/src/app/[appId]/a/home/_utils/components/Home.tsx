'use client';
import { useTrans } from '@/helpers/services/lang/langService';
import { Button } from '@apptimus-ui/ui-element';
import React, { useState } from 'react';
import { howWorksData } from '../service';
import SelectPolicy from './claim-intimation/SelectPolicy';
import { getLocalStorage } from '@/helpers/handlers/localStorageHandler';
import { local_storage } from '@/constans/StorageKeys';
import SelectInterestedProduct from '../../../my-policies/_utils/components/create-policy/individual/SelectInterestedProduct';
import SelectInterestedProductForCommercial from '../../../my-policies/_utils/components/create-policy/commercial/SelectInterestedProductForCommercial';
import { useParams, useRouter } from 'next/navigation';

function Home() {
  const t = useTrans('label.home,otr.common');
  const [isClaimOpen, setIsClaimOpen] = useState(false);
  const [isPolicyOpen, setIsPolicyOpen] = useState({ isOpen: false, key: 0 });
  const [isPolicyCommercialLineOpen, setIsPolicyCommercialLineOpen] = useState({ isOpen: false, key: 0 });
  const [quotationCommercialLine, setQuotationCommercialLine] = useState({ isOpen: false, key: 0 });
  const [isQuotationOpen, setIsQuotationOpen] = useState({ isOpen: false, key: 0 });
  const authUser = getLocalStorage(local_storage.auth_user_info);
  const router = useRouter();
  const params = useParams();
  const appId = params.appId as string;

  const handleClose = () => {
    setIsPolicyOpen({ isOpen: false, key: isPolicyOpen.key + 1 });
  };

  const handleCloseCommercialLine = () => {
    setIsPolicyCommercialLineOpen({ isOpen: false, key: isPolicyCommercialLineOpen.key + 1 });
  };

  const handleNavigateCommercial = (requestId: any, productId: any, riskTypeId: any) => {
    router.push(`/${appId}/a/my-policies/create-commercial?reqId=${requestId}&pId=${productId}&rId=${riskTypeId}`, { scroll: false });
    handleCloseCommercialLine();
  };

  const handleCloseQuotationCommercialLine = () => {
    setQuotationCommercialLine({ isOpen: false, key: quotationCommercialLine.key + 1 });
  };

  const handleCloseQuotation = () => {
    setIsQuotationOpen({ isOpen: false, key: isQuotationOpen.key + 1 });
  };

  const handleNavigateQuotationCommercial = (requestId: any, productId: any, riskTypeId: any) => {
    router.push(`/${appId}/a/my-quotations/create-commercial?reqId=${requestId}&pId=${productId}&rId=${riskTypeId}`, { scroll: false });
    handleCloseQuotationCommercialLine();
  };

  return (
    <div className="p-2 text">
      <div className="col-12 col-md-6">
        <div className="text-uppercase text-muted">{t('manage_your_insurance_effortlessly')}</div>
        <div className="fw-bold heading-text">
          {t('welcome')} <span>{authUser?.name}</span>
          <span>!</span>
        </div>
        <div className="text-muted">{t('manage_your_insurance_effortlessly_by_viewing_policies_getting_tailored_quotes_and_requesting_new_services_all_in_one_convenient_place')}</div>
      </div>
      <div className="d-flex flex-row flex-wrap flex-md-nowrap gap-4 mt-4">
        <div className="w-100 d-flex flex-column p-3 rounded-2 shadow-sm home-card-1">
          <div className="fw-medium">{t('define_action_that_you_had_like_vanguard_x_to_do')}</div>
          <div className="d-flex flex-row gap-3">
            <div
              onClick={() => {
                authUser?.type === 'Personal' ? setIsPolicyOpen({ isOpen: true, key: isPolicyOpen.key + 1 }) : setIsPolicyCommercialLineOpen({ isOpen: true, key: isPolicyCommercialLineOpen.key + 1 });
              }}
              className="bg-white d-flex border flex-column align-items-center p-3 mt-3 rounded-2 shadow-sm"
              style={{ maxWidth: '140px', cursor: 'pointer' }}
            >
              <div>
                <svg width="49" height="48" viewBox="0 0 49 48" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path
                    d="M12.4004 40.1743H17.621C18.3016 40.1743 18.9782 40.2553 19.638 40.4173L25.1542 41.7578C26.3511 42.0494 27.5979 42.0777 28.8073 41.8428L34.9063 40.6563C36.5175 40.3424 37.9996 39.5709 39.1611 38.441L43.4762 34.2435C44.7085 33.0468 44.7085 31.1049 43.4762 29.9062C42.3667 28.8269 40.6098 28.7054 39.3547 29.6207L34.3256 33.2897C33.6054 33.8162 32.729 34.0997 31.8277 34.0997H26.9714L30.0625 34.0996C31.8048 34.0996 33.2161 32.7267 33.2161 31.0319V30.4183C33.2161 29.011 32.2315 27.784 30.8285 27.4438L26.0576 26.2835C25.2812 26.0952 24.486 26 23.6867 26C21.7571 26 18.2642 27.5977 18.2642 27.5977L12.4004 30.0498M4.40039 29.2L4.40039 40.8C4.40039 41.9201 4.40039 42.4802 4.61838 42.908C4.81012 43.2843 5.11609 43.5903 5.49241 43.782C5.92023 44 6.48028 44 7.60039 44H9.20039C10.3205 44 10.8805 44 11.3084 43.782C11.6847 43.5903 11.9907 43.2843 12.1824 42.908C12.4004 42.4802 12.4004 41.9201 12.4004 40.8V29.2C12.4004 28.0799 12.4004 27.5199 12.1824 27.0921C11.9907 26.7157 11.6847 26.4098 11.3084 26.218C10.8805 26 10.3205 26 9.20039 26H7.60039C6.48029 26 5.92023 26 5.49241 26.218C5.11609 26.4098 4.81012 26.7157 4.61838 27.0921C4.40039 27.5199 4.40039 28.0799 4.40039 29.2ZM34.7831 7.18454C33.5895 4.68683 30.8376 3.3636 28.1613 4.64078C25.485 5.91796 24.3448 8.94679 25.4653 11.6057C26.1578 13.249 28.1419 16.44 29.5566 18.6381C30.0793 19.4503 30.3406 19.8563 30.7224 20.0939C31.0498 20.2977 31.4597 20.4075 31.8452 20.3947C32.2946 20.3799 32.7239 20.1589 33.5827 19.7169C35.9069 18.5207 39.2207 16.7491 40.642 15.6723C42.9419 13.9299 43.5115 10.7272 41.7897 8.29251C40.0679 5.85784 37.0657 5.61828 34.7831 7.18454Z"
                    stroke="#09729A"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                </svg>
              </div>
              <div className="text-center fw-medium text-muted fs-14 mt-2">{t('buy_new_policy')}</div>
            </div>
            {/* <div
              onClick={() => {
                authUser?.type === 'Personal' ? setIsOpen(true) : setCommercialLine((prevData) => ({ ...prevData, isOpen: true }));
              }}
              className="bg-white d-flex border flex-column align-items-center p-3 mt-3 rounded-2 shadow-sm"
              style={{ maxWidth: '140px', cursor: 'pointer' }}
            >
              <div>
                <svg width="49" height="48" viewBox="0 0 49 48" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M12.2002 12L16.2002 8M16.2002 8L12.2002 4M16.2002 8H12.2002C7.78192 8 4.2002 11.5817 4.2002 16M36.2002 36L32.2002 40M32.2002 40L36.2002 44M32.2002 40H36.2002C40.6185 40 44.2002 36.4183 44.2002 32M20.5782 13C21.9104 7.82432 26.6087 4 32.2002 4C38.8276 4 44.2002 9.37258 44.2002 16C44.2002 21.5915 40.3759 26.2897 35.2003 27.6219M28.2002 32C28.2002 38.6274 22.8276 44 16.2002 44C9.57278 44 4.2002 38.6274 4.2002 32C4.2002 25.3726 9.57278 20 16.2002 20C22.8276 20 28.2002 25.3726 28.2002 32Z" stroke="#09729A" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
              </div>
              <div className="text-center fw-medium text-muted fs-14 mt-2">{t('policy_renewal')}</div>
            </div> */}
            <div
              onClick={() => {
                authUser?.type === 'Personal' ? setIsQuotationOpen({ isOpen: true, key: isQuotationOpen.key + 1 }) : setQuotationCommercialLine((prevData) => ({ ...prevData, isOpen: true }));
              }}
              className="bg-white d-flex border flex-column align-items-center p-3 mt-3 rounded-2 shadow-sm"
              style={{ maxWidth: '140px', cursor: 'pointer' }}
            >
              <div>
                <svg width="48" height="48" viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path
                    d="M24 27V15M18 21H30M14 36V40.671C14 41.7367 14 42.2696 14.2185 42.5432C14.4084 42.7812 14.6965 42.9197 15.0011 42.9194C15.3513 42.919 15.7673 42.5861 16.5995 41.9204L21.3704 38.1037C22.345 37.324 22.8323 36.9341 23.375 36.6569C23.8564 36.411 24.3689 36.2312 24.8984 36.1225C25.4953 36 26.1194 36 27.3675 36H32.4C35.7603 36 37.4405 36 38.7239 35.346C39.8529 34.7708 40.7708 33.8529 41.346 32.7239C42 31.4405 42 29.7603 42 26.4V15.6C42 12.2397 42 10.5595 41.346 9.27606C40.7708 8.14708 39.8529 7.2292 38.7239 6.65396C37.4405 6 35.7603 6 32.4 6H15.6C12.2397 6 10.5595 6 9.27606 6.65396C8.14708 7.2292 7.2292 8.14708 6.65396 9.27606C6 10.5595 6 12.2397 6 15.6V28C6 29.8599 6 30.7899 6.20445 31.5529C6.75925 33.6235 8.37653 35.2408 10.4471 35.7956C11.2101 36 12.1401 36 14 36Z"
                    stroke="#09729A"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                </svg>
              </div>
              <div className="text-center fw-medium text-muted fs-14 mt-2">{t('get_quotation')}</div>
            </div>
          </div>
        </div>
        <div className="w-100 d-flex flex-column p-3 rounded-2 shadow-sm home-card-2">
          <div className="fw-medium">{t('experiencing_an_issue')}</div>
          <div className="d-flex flex-row align-items-center justify-content-between gap-3 mt-3">
            <div className="p-3 d-flex justify-content-center align-items-center home-card" style={{ minWidth: '140px', minHeight: '103px' }}>
              <svg width="65" height="64" viewBox="0 0 65 64" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path
                  d="M47.6004 28H17.2004C15.5202 28 14.6802 28 14.0384 28.327C13.4739 28.6146 13.015 29.0735 12.7274 29.638C12.4004 30.2798 12.4004 31.1198 12.4004 32.8V44.8C12.4004 45.9201 12.4004 46.4802 12.6184 46.908C12.8101 47.2843 13.1161 47.5903 13.4924 47.782C13.9202 48 14.4803 48 15.6004 48H19.2004C20.3205 48 20.8805 48 21.3084 47.782C21.6847 47.5903 21.9907 47.2843 22.1824 46.908C22.4004 46.4802 22.4004 45.9201 22.4004 44.8V43.8C22.4004 43.52 22.4004 43.38 22.4549 43.273C22.5028 43.1789 22.5793 43.1024 22.6734 43.0545C22.7804 43 22.9204 43 23.2004 43H41.6004C41.8804 43 42.0204 43 42.1274 43.0545C42.2215 43.1024 42.298 43.1789 42.3459 43.273C42.4004 43.38 42.4004 43.52 42.4004 43.8V44.8C42.4004 45.9201 42.4004 46.4802 42.6184 46.908C42.8101 47.2843 43.1161 47.5903 43.4924 47.782C43.9202 48 44.4803 48 45.6004 48H49.2004C50.3205 48 50.8805 48 51.3084 47.782C51.6847 47.5903 51.9907 47.2843 52.1824 46.908C52.4004 46.4802 52.4004 45.9201 52.4004 44.8V32.8C52.4004 31.1198 52.4004 30.2798 52.0734 29.638C51.7858 29.0735 51.3268 28.6146 50.7624 28.327C50.1206 28 49.2805 28 47.6004 28Z"
                  stroke="#D92D20"
                  strokeWidth="1.66667"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
                <path
                  d="M48.4004 28L45.1297 18.1881C44.8675 17.4013 44.7363 17.0078 44.4931 16.717C44.2783 16.4601 44.0025 16.2613 43.6909 16.1388C43.338 16 42.9233 16 42.094 16H22.7068C21.8774 16 21.4627 16 21.1099 16.1388C20.7983 16.2613 20.5225 16.4601 20.3077 16.717C20.0644 17.0078 19.9333 17.4013 19.671 18.1881L16.4004 28"
                  stroke="#D92D20"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
                <path d="M18.4004 34H24.4004" stroke="#D92D20" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                <path d="M40.4004 34H46.4004" stroke="#D92D20" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                <path d="M12.4004 26L16.4004 28" stroke="#D92D20" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                <path d="M48.4004 28L52.4004 26" stroke="#D92D20" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
            </div>
            <div>
              <div className="text">{t('start_your_claim_process_now_just_click_below_and_we_ll_assist_you_every_step_of_the_way_to_resolve_your_case_swiftly')}</div>
              <Button color="warning" className="d-flex align-items-center gap-1 mt-2" onClick={() => setIsClaimOpen(true)}>
                <span className="d-none d-sm-inline text-white">{t('report_a_claim')}</span>
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
          </div>
        </div>
      </div>
      <div className="mt-4">
        <div className="fw-bold heading-text">{t('how_it_works')}:</div>
        <div className="d-flex flex-row flex-wrap flex-lg-nowrap gap-3 mt-3">
          {howWorksData.map((item, index) => (
            <HowWorkCard step={item.step} title={item.title} description={item.description} key={index} />
          ))}
        </div>
      </div>
      {isClaimOpen && <SelectPolicy isOpen={isClaimOpen} onCancel={() => setIsClaimOpen(false)} />}
      {isPolicyOpen.isOpen && (
        <SelectInterestedProduct
          type="customer_policy"
          isOpen={isPolicyOpen.isOpen}
          onCancel={handleClose}
          setIds={(id: any, productId: any, riskTypeId: any) => {
            router.push(`/${appId}/a/my-policies/create?fId=${id}&pId=${productId}&rId=${riskTypeId}`, { scroll: false }), setIsPolicyOpen({ isOpen: false, key: isPolicyOpen.key + 1 });
          }}
          key={isPolicyOpen.key}
        />
      )}
      {isPolicyCommercialLineOpen.isOpen && (
        <SelectInterestedProductForCommercial
          isOpen={isPolicyCommercialLineOpen.isOpen}
          onCancel={handleCloseCommercialLine}
          type="policy"
          setIds={(requestId: any, productId: any, riskTypeId: any) => handleNavigateCommercial(requestId, productId, riskTypeId)}
          key={isPolicyCommercialLineOpen.key}
        />
      )}

      {isQuotationOpen.isOpen && (
        <SelectInterestedProduct
          type="quotation"
          isOpen={isQuotationOpen.isOpen}
          onCancel={handleCloseQuotation}
          setIds={(id: any, productId: any, riskTypeId: any) => {
            router.push(`/${appId}/a/my-quotations/create?fId=${id}&pId=${productId}&rId=${riskTypeId}`, { scroll: false }), setIsQuotationOpen({ isOpen: false, key: isQuotationOpen.key + 1 });
          }}
          key={isQuotationOpen.key}
        />
      )}

      {quotationCommercialLine.isOpen && (
        <SelectInterestedProductForCommercial
          isOpen={quotationCommercialLine.isOpen}
          onCancel={handleCloseQuotationCommercialLine}
          type="quotation"
          setIds={(requestId: any, productId: any, riskTypeId: any) => handleNavigateQuotationCommercial(requestId, productId, riskTypeId)}
          key={quotationCommercialLine.key}
        />
      )}
    </div>
  );
}

export default Home;

export const HowWorkCard = ({ step, title, description }: { step: number; title: string; description: string }) => {
  const t = useTrans('label.home,otr.common');
  return (
    <div className="card position-relative p-3 border rounded shadow-sm border border-primary w-100">
      <div className="position-absolute fw-medium top-0 end-0 bg-primary text-white rounded-bottom px-3 mx-2 py-1">{step}</div>
      <h6 className="fw-bold mb-2 text-nowrap text">{t(`${title}`)}</h6>
      <p className="text-muted fs-13 mb-0">{t(`${description}`)}</p>
    </div>
  );
};
