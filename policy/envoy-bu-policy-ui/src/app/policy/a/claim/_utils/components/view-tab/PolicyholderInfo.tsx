// 'use client';
// import { useEffect, useState } from 'react';
// import { Description } from '@/components/others/Description';
// import { useTrans } from '@/helpers/services/lang/langService';
// import { useParams, useRouter } from 'next/navigation';
// import { ISample } from '../../model';
// import { Button } from '@apptimus-ui/ui-element';
// import { Flexicon } from '@apptimus-ui/flexicon';
// import EmailSentSuccessfully from './EmailSentSuccessfully';
// import { getOneClaim } from '../../api-service';

// export const PolicyholderInfo = ({ toggleTableTab }: { toggleTableTab: Function }) => {
//   const t = useTrans('label.claim,otr.common');
//   const [data, setData] = useState({} as ISample);
//   const [skeleton, setSkeleton] = useState(true);
//   const params = useParams();
//   const claimId = params.claimId?.toString() || '';
//   const router = useRouter();
//   const [_isOpenEmailForm, setIsOpenEmailForm] = useState(false);
//   const [isComformationEmailForm, setComformationEmailForm] = useState(false);
//   // const [_emailFormKey, setEmailFormKey] = useState(0);

//   useEffect(() => {
//     const fetchData = async () => {
//       const responseData = await getOneClaim(claimId);
//       responseData?.is_success && (setData(responseData.result), setSkeleton(false));
//     };

//     if (claimId) {
//       setSkeleton(true);
//       fetchData();
//     }
//   }, [claimId]);

//   const handleNextPage = () => {
//     toggleTableTab('vehicle_info');
//   };

//   // const handleCloseEmailForm = () => {
//   //   setIsOpenEmailForm(false);
//   //   setEmailFormKey((prevFormKey) => prevFormKey + 1);
//   // };

//   const handleCloseComformationEmailForm = () => {
//     setComformationEmailForm(false);
//   };

//   return (
//     <>
//       <div className="mb-4">
//         <div className="d-flex justify-content-end align-items-center">
//           <Button className="d-flex justify-content-end align-items-center gap-1" onClick={() => setIsOpenEmailForm(true)}>
//             <span className="d-none d-sm-inline">{t('send_intimation_notice')}</span>
//             <Flexicon icon="send-01" variant="line" size={18} />
//           </Button>
//         </div>
//         <div className="panel-title mb-3">{t('policyholder_information')}</div>
//         <div className="row">
//           <div className="col-12 col-md-4 mb-3">
//             <Description label={t('full_name')} value={data?.name || '-'} skeleton={skeleton} />
//           </div>
//           <div className="col-12 col-md-4 mb-3">
//             <Description label={t('contact_number')} value={data?.description || '-'} skeleton={skeleton} />
//           </div>
//         </div>
//         <div className="row">
//           <div className="col-12 col-md-4 mb-3">
//             <Description label={t('email')} value={data?.description || '-'} skeleton={skeleton} />
//           </div>
//           <div className="col-12 col-md-4 mb-3">
//             <Description label={t('date_of_birth')} value={data?.description || '-'} skeleton={skeleton} />
//           </div>
//           <div className="col-12 col-md-4 mb-3">
//             <Description label={t('driver_license_number')} value={data?.description || '-'} skeleton={skeleton} />
//           </div>
//           <div className="col-12 col-md-4 mb-3">
//             <Description label={t('city')} value={data?.description || '-'} skeleton={skeleton} />
//           </div>
//           <div className="col-12 col-md-4 mb-3">
//             <Description label={t('state_province')} value={data?.description || '-'} skeleton={skeleton} />
//           </div>
//           <div className="col-12 col-md-4 mb-3">
//             <Description label={t('zip_postal_code')} value={data?.description || '-'} skeleton={skeleton} />
//           </div>
//           <div className="col-12 col-md-6 mb-3">
//             <Description label={t('address')} value={data?.description || '-'} skeleton={skeleton} />
//           </div>
//         </div>
//         <div className="panel-title mb-3">{t('policy_information')}</div>
//         <div className="row">
//           <div className="col-12 col-md-4 mb-3">
//             <Description label={t('policy_number')} value={data?.description || '-'} skeleton={skeleton} />
//           </div>
//         </div>
//         <div className="row">
//           <div className="col-12 col-md-6 mb-3">
//             <Description label={t('start_date')} value={data?.description || '-'} skeleton={skeleton} />
//           </div>
//           <div className="col-12 col-md-6 mb-3">
//             <Description label={t('end_date')} value={data?.description || '-'} skeleton={skeleton} />
//           </div>
//         </div>
//         <div className="panel-title mb-3">{t('product_information')}</div>
//         <div className="row">
//           <div className="col-12 col-md-6 mb-3">
//             <Description label={t('product_name')} value={data?.description || '-'} skeleton={skeleton} />
//           </div>
//           <div className="col-12 col-md-6 mb-3">
//             <Description label={t('coverage_type')} value={data?.description || '-'} skeleton={skeleton} />
//           </div>
//         </div>
//         <div className="panel-title mb-3">{t('insurer_info')}</div>
//         <div className="row">
//           <div className="col-12 col-md-6 mb-3">
//             <Description label={t('insurer_name')} value={data?.description || '-'} skeleton={skeleton} />
//           </div>
//           <div className="col-12 col-md-6 mb-3">
//             <Description label={t('primary_contact_number')} value={data?.description || '-'} skeleton={skeleton} />
//           </div>
//           <div className="col-12 col-md-6 mb-3">
//             <Description label={t('policy_date')} value={data?.description || '-'} skeleton={skeleton} />
//           </div>
//           <div className="col-12 col-md-6 mb-3">
//             <Description label={t('premium_amount')} value={data?.description || '-'} skeleton={skeleton} />
//           </div>
//           <div className="col-12 col-md-6 mb-3">
//             <Description label={t('total_commission')} value={data?.description || '-'} skeleton={skeleton} />
//           </div>
//           <div className="col-12 col-md-6 mb-3">
//             <Description label={t('received_commission')} value={data?.description || '-'} skeleton={skeleton} />
//           </div>
//           <div className="col-12 col-md-6 mb-3">
//             <Description label={t('sales_agent')} value={data?.description || '-'} skeleton={skeleton} />
//           </div>
//           <div className="col-12 col-md-6 mb-3">
//             <Description label={t('account_manager')} value={data?.description || '-'} skeleton={skeleton} />
//           </div>
//           <div className="col-12 mb-3">
//             <Description label={t('remarks_notes')} value={data?.description || '-'} skeleton={skeleton} />
//           </div>
//         </div>
//       </div>
//       <div className="d-flex justify-content-start gap-2 mt-3">
//         <Button
//           color="light"
//           className="d-flex align-items-center gap-1"
//           onClick={() => {
//             router.push(`/policy/a/claim`);
//           }}
//         >
//           <Flexicon icon="chevron-left" variant="line" size={18} />
//           <span className="d-none d-sm-inline">{t('back')}</span>
//         </Button>
//         <Button color="primary" className="d-flex align-items-center gap-1" type="submit" onClick={handleNextPage}>
//           <span className="d-none d-sm-inline">{t('next')}</span>
//           <Flexicon icon="chevron-right" variant="line" size={18} />
//         </Button>
//         <Button color="primary" className="d-flex align-items-center gap-1" onClick={() => router.push(`/policy/a/claim/edit/?claimId=${claimId}&t=policyholder_info`)}>
//           <Flexicon icon="edit-05" variant="line" size={18} />
//           <span className="d-none d-sm-inline">{t('edit')}</span>
//         </Button>
//         {/* <Button text={t('update')} type="submit" width="sm" isLoading={undefined} disabled={skeleton} />
//                   <Button text={t('cancel')} color="light" width="sm" /> */}
//       </div>
//       {/* {isOpenEmailForm && (
//         <EmailForm
//           defaultTemplate={''}
//           key={emailFormKey}
//           isOpen={isOpenEmailForm}
//           onCancel={handleCloseEmailForm}
//           recipientNames={['hii']}
//           emailData={() => ''}
//           setComformationEmailForm={setComformationEmailForm}
//         />
//       )} */}
//       {isComformationEmailForm && <EmailSentSuccessfully isOpen={isComformationEmailForm} onCancel={handleCloseComformationEmailForm} />}
//     </>
//   );
// };
