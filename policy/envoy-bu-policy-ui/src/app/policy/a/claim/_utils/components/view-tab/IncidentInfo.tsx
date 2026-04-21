// 'use client';
// import { useEffect, useState } from 'react';
// import { Description } from '@/components/others/Description';
// import { useTrans } from '@/helpers/services/lang/langService';
// import { useParams, useRouter } from 'next/navigation';
// import { ISample } from '../../model';
// import { Button, Input, Label } from '@apptimus-ui/ui-element';
// import { Flexicon } from '@apptimus-ui/flexicon';
// import { getOneClaim } from '../../api-service';

// export const IncidentInfo = ({ toggleTableTab }: { toggleTableTab: Function }) => {
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

//   const handleNextPage = () => {
//     toggleTableTab('damage_info');
//   };

//   return (
//     <>
//       <div className="mb-4">
//         <div className="panel-title mb-3">{t('incident_information')}</div>
//         <div className="row">
//           <div className="col-12 col-md-6 mb-3">
//             <Description label={t('date_of_incident')} value={data?.name || '-'} skeleton={skeleton} />
//           </div>
//           <div className="col-12 col-md-6 mb-3">
//             <Description label={t('time_of_incident')} value={data?.description || '-'} skeleton={skeleton} />
//           </div>
//           <div className="col-12 mb-3">
//             <Description label={t('location_of_incident')} value={data?.description || '-'} skeleton={skeleton} />
//           </div>
//           <div className="col-12  mb-3">
//             <Description label={t('description_of_incident')} value={data?.description || '-'} skeleton={skeleton} />
//           </div>
//           <div className="col-12 col-md-6 mb-3">
//             <Description label={t('weather_conditions')} value={data?.description || '-'} skeleton={skeleton} />
//           </div>
//           <div className="col-12 col-md-6 mb-3">
//             <Description label={t('was_a_police_report_filed')} value={data?.description || '-'} skeleton={skeleton} />
//           </div>
//           <div className="col-12 col-md-6 mb-3">
//             <Description label={t('police_report_number')} value={data?.description || '-'} skeleton={skeleton} />
//           </div>
//           <div className="col-12 col-md-6 mb-3">
//             <Description label={t('officer_name')} value={data?.description || '-'} skeleton={skeleton} />
//           </div>
//           <div className="col-12 col-md-4 mb-3">
//             <div className="fs-15 text-muted">{t('police_reports')}</div>
//             <div className="fs-10 fw-normal mb-2 text-muted">{t('copy_of_police_reports')}</div>
//             <div className="d-flex flex-row justify-content-between gap-4 align-items-center border border-2 rounded-1 p-1 px-2">
//               <div>{data.name}</div>
//               <div className="d-flex flex-row justify-content-between gap-2">
//                 <Flexicon icon="x-square" variant="line" className="text-light action-icon" />
//               </div>
//             </div>
//           </div>
//           <div className="row">
//             <div className="col-12 col-md-6 mb-3">
//               <div className="fs-15 text-muted">{t('are_you_okay_injuries')}</div>
//               <div className="">
//                 <div className="form-check form-check-inline">
//                   <Input className="form-check-input" type="radio" name="injuryStatus" id="injuryYes" value="yes" defaultValue={data.injuryStatus === 'yes'} />
//                   <Label label={t('yes')} />
//                 </div>
//                 <div className="form-check form-check-inline">
//                   <Input className="form-check-input" type="radio" name="injuryStatus" id="injuryNo" value="no" defaultValue={data.injuryStatus === 'no'} />
//                   <Label label={t('no')} />
//                 </div>
//               </div>
//             </div>
//           </div>
//           <div className="col-12 mb-3">
//             <Description label={t('description_of_injuries')} value={data?.description || '-'} skeleton={skeleton} />
//           </div>
//           <div className="row">
//             <div className="col-12 col-md-6 mb-3">
//               <div className="fs-15 text-muted">{t('if_admitted_in_hospital')}</div>
//               <div className="">
//                 <div className="form-check form-check-inline">
//                   <Input className="form-check-input" type="radio" name="admittedStatus" id="injuryYes" value="yes" defaultValue={data.admittedStatus === 'yes'} />
//                   <Label label={t('yes')} />
//                 </div>
//                 <div className="form-check form-check-inline">
//                   <Input className="form-check-input" type="radio" name="admittedStatus" id="injuryNo" value="no" defaultValue={data.admittedStatus === 'no'} />
//                   <Label label={t('no')} />
//                 </div>
//               </div>
//             </div>
//           </div>
//           <div className="col-12 mb-3">
//             <Description label={t('hospital_name')} value={data?.description || '-'} skeleton={skeleton} />
//           </div>
//           <div className="col-12 col-md-4 mb-3">
//             <Description label={t('contact_number')} value={data?.description || '-'} skeleton={skeleton} />
//           </div>
//           <div className="col-12 col-md-4 mb-3">
//             <Description label={t('estimated_amount')} value={data?.description || '-'} skeleton={skeleton} />
//           </div>
//           <div className="row">
//             <div className="col-12 col-md-4 mb-3">
//               <div className="fs-15 text-muted">{t('medical_reports')}</div>
//               <div className="fs-10 fw-normal mb-2 text-muted">{t('please_provide_medical_documentation')}</div>
//               <div className="d-flex flex-row justify-content-between gap-4 align-items-center border border-2 rounded-1 p-1 px-2">
//                 <div>{data.name}</div>
//                 <div className="d-flex flex-row justify-content-between gap-2">
//                   <Flexicon icon="x-square" variant="line" className="text-light action-icon" />
//                 </div>
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
//             router.push(`/policy/a/claim/${claimId}?t=vehicle_info`);
//           }}
//         >
//           <Flexicon icon="chevron-left" variant="line" size={18} />
//           <span className="d-none d-sm-inline">{t('back')}</span>
//         </Button>
//         <Button color="primary" className="d-flex align-items-center gap-1" onClick={handleNextPage}>
//           <span className="d-none d-sm-inline">{t('next')}</span>
//           <Flexicon icon="chevron-right" variant="line" size={18} />
//         </Button>
//         <Button color="primary" className="d-flex align-items-center gap-1" onClick={() => router.push(`/policy/a/claim/edit/?claimId=${claimId}&t=incident_info`)}>
//           <Flexicon icon="edit-05" variant="line" size={18} />
//           <span className="d-none d-sm-inline">{t('edit')}</span>
//         </Button>
//         {/* <Button text={t('update')} type="submit" width="sm" isLoading={undefined} disabled={skeleton} />
//                   <Button text={t('cancel')} color="light" width="sm" /> */}
//       </div>
//     </>
//   );
// };
