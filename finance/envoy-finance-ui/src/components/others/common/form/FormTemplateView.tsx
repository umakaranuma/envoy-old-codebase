// import React, { useEffect, useState } from 'react';
// import { useRouter } from 'next/navigation';
// import { Flexicon } from '@apptimus-ui/flexicon';
// import { useTrans } from '@/helpers/services/lang/langService';
// import { Button, Skeleton } from '@apptimus-ui/ui-element';
// import { IClaimTemplate, IElement, Step } from './template-modal';
// import FormStepper from './FormStepper';
// import { Description } from '../../Description';
// import { getOneClaim } from '@/app/finance/a/claim/_utils/api-service';
// import { fileReceiver } from '@/helpers/services/storageService';

// function FormTemplateView({ claimId, onBack, currentPath, handleNextPage }: { claimId: string; onBack: Function; currentPath: string; handleNextPage?: Function }) {
//   const t = useTrans('label.claim,otr.common');
//   const router = useRouter();
//   const [currentTab, setCurrentTab] = useState({} as Step);
//   const [currentTabIndex, setCurrentTabIndex] = useState(0);
//   const [formData, setFormData] = useState([] as IElement[]);
//   const [templateData, setTemplateData] = useState<IClaimTemplate>({} as IClaimTemplate);
//   const [skeleton, setSkeleton] = useState(false);

//   const fetchTemplateData = async () => {
//     if (claimId) {
//       const responseData = await getOneClaim(claimId);
//       if (responseData?.is_success) {
//         setTemplateData(responseData.result);
//         setFormData(responseData.result.elements);
//         const templateResponseData = responseData.result as IClaimTemplate;
//         if (templateResponseData.steps && templateResponseData.steps.length > 0) {
//           const defaultTabSlug = templateResponseData.steps[0].title.toLowerCase().replace(/\s+/g, '_');
//           const foundIndex = templateResponseData.steps.findIndex((step) => step.title.toLowerCase().replace(/\s+/g, '_') === defaultTabSlug);

//           if (foundIndex !== -1) {
//             const step = templateResponseData.steps[foundIndex];
//             setCurrentTab(step);
//             setCurrentTabIndex(foundIndex);
//           }
//         }
//         setSkeleton(false);
//       }
//     }
//   };

//   useEffect(() => {
//     if (claimId) {
//       setSkeleton(true);
//       fetchTemplateData();
//       router.push(`${currentPath}`);
//     }
//   }, [claimId]);

//   const handleNext = () => {
//     const nextIndex = currentTabIndex + 1;
//     const nextStep = templateData.steps[nextIndex];
//     setCurrentTab(nextStep);
//     setCurrentTabIndex(nextIndex);
//   };

//   return (
//     <>
//       {skeleton ? (
//         <Skeleton className="w-100" height={'400px'} />
//       ) : (
//         <div>
//           <>{templateData.steps && templateData.steps.length > 0 && <FormStepper templateName={templateData.template.name} steps={templateData.steps} currentTabId={currentTab.id} />}</>
//           <>
//             {templateData.panels &&
//               templateData.panels.length > 0 &&
//               templateData.panels.map((panel, index) => (
//                 <div key={panel.id} className={templateData.template?.type === 'multi_step_form' ? `d-${currentTab.id && currentTab.id === panel.step_id ? 'block' : 'none'}` : 'd-block'}>
//                   <div className="card-body bg-white p-3 rounded-3 mb-3" key={index}>
//                     <div className="fs-13 fw-semibold mb-3">{panel.title}</div>
//                     {
//                       <div className="row">
//                         {formData
//                           .filter((element) => element.panel_id === panel.id)
//                           .map((element: any, index) => {
//                             const value =
//                               element.code === 'MULTI_SELECT' || element.code === 'MULTI_CHOICE'
//                                 ? element.value && JSON.parse(element.value.replace(/'/g, '"')).join(',')
//                                 : element.code === 'CURRENCY' && element.value
//                                   ? `amount: ${JSON.parse(element.value.replace(/'/g, '"')).amount}, currency: ${JSON.parse(element.value.replace(/'/g, '"')).currency}`
//                                   : element.value;
//                             return (
//                               <div className="col-12 col-md-3 mb-3" key={index}>
//                                 {element.code !== 'SUBMISSION_PICKER' ? (
//                                   <Description label={element.label as string} value={value || '-'} skeleton={skeleton} isTruncate={false} />
//                                 ) : (
//                                   <Description
//                                     label={element.label as string}
//                                     value={
//                                       (
//                                         <>
//                                           {element.value && (
//                                             <div className="d-flex flex-row justify-content-between gap-4 align-items-center border border-2 border-primary rounded-1 p-1 px-2">
//                                               <div>{JSON.parse(element.value.replace(/'/g, '"'))[1] || '-'}</div>
//                                               <div className="d-flex flex-row justify-content-between gap-1">
//                                                 {JSON.parse(element.value.replace(/'/g, '"'))[1] && (
//                                                   <Flexicon icon="eye" variant="line" className="action-icon" onClick={() => handleFileViewer(JSON.parse(element.value.replace(/'/g, '"'))[1])} />
//                                                 )}
//                                               </div>
//                                             </div>
//                                           )}
//                                         </>
//                                       ) || '-'
//                                     }
//                                     skeleton={skeleton}
//                                     isTruncate={false}
//                                   />
//                                 )}
//                               </div>
//                             );
//                           })}
//                       </div>
//                     }
//                   </div>
//                 </div>
//               ))}
//           </>
//           {(templateData.template && templateData.template.type) === 'multi_step_form' ? (
//             <div className="d-flex justify-content-start gap-2 mt-3">
//               <Button
//                 color="light"
//                 className="d-flex align-items-center gap-1"
//                 onClick={() => {
//                   if (currentTabIndex > 0) {
//                     const prevIndex = currentTabIndex - 1;
//                     const prevStep = templateData.steps[prevIndex];
//                     setCurrentTab(prevStep);
//                     setCurrentTabIndex(prevIndex);
//                   } else {
//                     onBack();
//                   }
//                 }}
//               >
//                 <Flexicon icon="chevron-left" variant="line" size={18} />
//                 <span className="d-none d-sm-inline">{t('back')}</span>
//               </Button>

//               {currentTabIndex < templateData.steps.length - 1 && (
//                 <Button
//                   color="primary"
//                   className="d-flex align-items-center gap-1"
//                   onClick={() => {
//                     handleNext();
//                   }}
//                 >
//                   <span className="d-none d-sm-inline">{t('next')}</span>
//                   <Flexicon icon="chevron-right" variant="line" size={18} />
//                 </Button>
//               )}
//               {currentTabIndex === templateData.steps.length - 1 && handleNextPage && (
//                 <Button color="primary" className="d-flex align-items-center gap-1" onClick={() => handleNextPage()}>
//                   <span className="d-none d-sm-inline">{t('next')}</span>
//                   <Flexicon icon="chevron-right" variant="line" size={18} />
//                 </Button>
//               )}
//             </div>
//           ) : (
//             <div className="d-flex justify-content-start gap-2 mt-3">
//               <Button color="light" className="d-flex align-items-center gap-1" onClick={() => onBack()}>
//                 <Flexicon icon="chevron-left" variant="line" size={18} />
//                 <span className="d-none d-sm-inline">{t('back')}</span>
//               </Button>
//               {/* <Button color="primary" onClick={() => {}} text={t('save')} /> */}
//               {handleNextPage && (
//                 <Button color="primary" className="d-flex align-items-center gap-1" onClick={() => handleNextPage()}>
//                   <span className="d-none d-sm-inline">{t('next')}</span>
//                   <Flexicon icon="chevron-right" variant="line" size={18} />
//                 </Button>
//               )}
//             </div>
//           )}
//         </div>
//       )}
//     </>
//   );
// }

// export default FormTemplateView;

// const handleFileViewer = async (key: string) => {
//   const file = await fileReceiver({ key });
//   window.open(file);
// };
