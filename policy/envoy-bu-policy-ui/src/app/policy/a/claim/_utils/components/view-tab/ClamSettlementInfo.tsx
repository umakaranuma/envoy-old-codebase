// 'use client';
// import { useEffect, useState } from 'react';
// import { Description } from '@/components/others/Description';
// import { useTrans } from '@/helpers/services/lang/langService';
// import { useParams, useRouter } from 'next/navigation';
// import { ISample } from '../../model';
// import { Button, Input, Label } from '@apptimus-ui/ui-element';
// import { Flexicon } from '@apptimus-ui/flexicon';
// import { getOneClaim } from '../../api-service';
// import { thousandSeparator } from '@/helpers/services/commonService';

// export const ClamSettlementInfo = () => {
//   const t = useTrans('label.claim,otr.common');
//   const [data, setData] = useState({} as ISample);
//   const [skeleton, setSkeleton] = useState(true);
//   const params = useParams();
//   const claimId = params.claimId?.toString() || '';
//   const router = useRouter();

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

//   return (
//     <>
//       <div className="mb-4">
//         <div className="panel-title mb-3">{t('claim_settlement_info')}</div>
//         <div className="row">
//           <div className="row">
//             <div className="col-12 col-md-6 mb-3">
//               <div className="fs-15 text-muted">{t('settlement_type')}</div>
//               <div className="">
//                 <div className="form-check form-check-inline">
//                   <Input className="form-check-input" type="radio" name="settlement_type" id="cashless" value="Cashless" defaultValue={data.settlementType === 'Cashless'} />
//                   <Label label={t('cashless')} />
//                 </div>
//                 <div className="form-check form-check-inline">
//                   <Input className="form-check-input" type="radio" name="settlement_type" id="reimbursement" value="Reimbursement" defaultValue={'Reimbursement' === 'Reimbursement'} />
//                   <Label label={t('reimbursement')} />
//                 </div>
//               </div>
//             </div>
//           </div>
//           <div className="col-12 mb-3">
//             <Description label={t('service_provider_types')} value={data?.name || '-'} skeleton={skeleton} />
//           </div>
//           {data.settlementType === 'Cashless' && (
//             <>
//               <div className="col-12 mb-3">
//                 <Description label={t('service_provider_name')} value={data?.description || '-'} skeleton={skeleton} />
//               </div>
//               <div className="col-12 col-md-6 mb-3">
//                 <Description label={t('contact_number')} value={data?.description || '-'} skeleton={skeleton} />
//               </div>
//               <div className="col-12 col-md-6 mb-3">
//                 <Description label={t('estimated_amount')} value={thousandSeparator(data?.description || 0) || '-'} skeleton={skeleton} />
//               </div>
//             </>
//           )}
//         </div>
//         <div className="panel-title">{t('bank_account_info')}</div>
//         <div className="row">
//           <div className="col-12 col-md-6 mb-3">
//             <Description label={t('account_holder_name')} value={data?.description || '-'} skeleton={skeleton} />
//           </div>
//           <div className="col-12 col-md-6 mb-3">
//             <Description label={t('bank_name')} value={data?.description || '-'} skeleton={skeleton} />
//           </div>
//           <div className="col-12 col-md-6 mb-3">
//             <Description label={t('bank_branch')} value={data?.description || '-'} skeleton={skeleton} />
//           </div>
//           <div className="col-12 col-md-6 mb-3">
//             <Description label={t('iban_swift_code')} value={data?.description || '-'} skeleton={skeleton} />
//           </div>
//           <div className="col-12 col-md-6 mb-3">
//             <Description label={t('estimated_amount')} value={data?.description || '-'} skeleton={skeleton} />
//           </div>
//           <div className="col-12 mb-3">
//             <Description label={t('account_holder_name')} value={data?.description || '-'} skeleton={skeleton} />
//           </div>
//         </div>
//         <div className="row">
//           <div className="col-12 col-md-4 mb-3">
//             <div className="fs-15 text-muted">{t('supporting_document')}</div>
//             <div className="d-flex flex-row justify-content-between gap-4 align-items-center border border-2 rounded-1 p-1 px-2">
//               <div>{data.name}</div>
//               <div className="d-flex flex-row justify-content-between gap-2">
//                 <Flexicon icon="x-square" variant="line" className="text-light action-icon" />
//               </div>
//             </div>
//           </div>
//         </div>
//       </div>
//       <div className="d-flex justify-content-start gap-2 mt-3">
//         <Button
//           color="light"
//           className="d-flex align-items-center gap-1"
//           onClick={() => {
//             router.push(`/policy/a/claim/${claimId}?t=witness_info`);
//           }}
//         >
//           <Flexicon icon="chevron-left" variant="line" size={18} />
//           <span className="d-none d-sm-inline">{t('back')}</span>
//         </Button>
//         <Button color="primary" className="d-flex align-items-center gap-1" onClick={() => router.push(`/policy/a/claim/edit/?claimId=${claimId}&t=clam_settlement_info`)}>
//           <Flexicon icon="edit-05" variant="line" size={18} />
//           <span className="d-none d-sm-inline">{t('edit')}</span>
//         </Button>
//         {/* <Button text={t('update')} type="submit" width="sm" isLoading={undefined} disabled={skeleton} />
//                   <Button text={t('cancel')} color="light" width="sm" /> */}
//       </div>
//     </>
//   );
// };
