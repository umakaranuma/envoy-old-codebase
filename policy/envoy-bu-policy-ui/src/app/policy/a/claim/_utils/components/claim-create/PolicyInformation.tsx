// 'use client';
// import { useTrans } from '@/helpers/services/lang/langService';
// import { useRouter } from 'next/navigation';
// import { Button, Label } from '@apptimus-ui/ui-element';
// import { Flexicon } from '@apptimus-ui/flexicon';
// import { AsyncSelect } from '@apptimus-ui/select';
// import { form } from '@/constans/Form';
// import PolicyInformationList from './PolicyHolderPolicyList';
// import 'react-phone-input-2/lib/style.css';
// import { fetchAllCustomersForClaim } from '../../services';

// export const PolicyInformation = ({ toggleTableTab, formData, setFormData }: { toggleTableTab: Function; formData: any; setFormData: Function }) => {
//   const t = useTrans('label.claim,otr.common');
//   const router = useRouter();
//   // const [isFormProcessing, setIsFormProcessing] = useState(false);

//   const handleNextPage = () => {
//     toggleTableTab('policy_info');
//   };

//   const onFormChange = (name: string, value: any) => {
//     setFormData((prevFormData: any) => ({ ...prevFormData, [name]: value }));
//   };

//   // const tBe = useTrans('be.msg,be.error,be.attri');
//   // async function onSubmit(e: FormEvent<HTMLFormElement>) {
//   //   e.preventDefault();
//   //   clearError(form.claim.store);
//   //   setIsFormProcessing(true);

//   //   try {
//   //     const responseData = await CreateClaim(formData);
//   //     setIsFormProcessing(false);

//   //     if (responseData.status_code === 417) {
//   //       printError(responseData.result, form.claim.store, tBe);
//   //     }

//   //     if (responseData.is_success) {
//   //       toaster.success(tBe(responseData.message));
//   //     }
//   //   } catch (error) {
//   //     console.error('An error occurred:', error);
//   //   }
//   // }

//   return (
//     <>
//       <div className="bg-white custom-card p-3 rounded-3 mb-3">
//         <form id={`${form.claim.store}`}>
//           {/* <div className="panel-title mb-3">{t('reporter_information')}</div>
//           <div className="row">
//             <div className="d-flex flex-row gap-3 mb-3">
//               <Label label={t('myself')} />
//               <input type="checkbox" className="mb-2" onChange={(e) => onFormChange('is_myself', e.target.checked)} />
//             </div>
//             <div className="col-12 col-md-4 mb-3">
//               <Input label={t('full_name')} value={formData.name} onChange={(e) => onFormChange('reporter_name', e.target.value)} className="form-control error-name" name="name" />
//             </div>
//             <div className="col-12 col-md-4 mb-3">
//               <Label label={t('contact_number')} />
//               <PhoneInput
//                 country={'lk'}
//                 enableAreaCodes={true}
//                 value={formData.contact_number}
//                 inputStyle={{ height: '40px', width: '100%' }}
//                 containerStyle={{ height: '40px', width: '100%' }}
//                 onChange={(phone) => onFormChange('reporter_contact', phone)}
//                 inputClass="form-control error-primary_contact"
//                 countryCodeEditable={false}
//               />
//             </div>
//             <div className="col-12 col-md-4 mb-3">
//               <Input label={t('relationship')} value={formData.name} onChange={(e) => onFormChange('reporter_relationship', e.target.value)} className="form-control error-name" name="name" />
//             </div>
//           </div> */}
//           <div className="panel-title mb-3">{t('policy_information')}</div>
//           <div className="row">
//             <div className="col-12 col-md-4 mb-3 custom-select custom-dropdown">
//               <Label label={t('search_by_customer_name_mobile_no')} />
//               <AsyncSelect
//                 onChange={(value) => onFormChange('customer_id', value)}
//                 className="form-control error-child_id"
//                 option={{ label: 'name', value: 'id' }}
//                 isSearchable={true}
//                 loadOptions={(searchValue, currentPage) => fetchAllCustomersForClaim(searchValue, currentPage)}
//               />
//             </div>
//           </div>
//           {formData.customer_id && (
//             <div>
//               <div className="panel-title mb-3">{t('policies')}</div>
//               <PolicyInformationList customerId={formData.customer_id} key={formData.customer_id} setSelectedPolicyId={(value: string) => onFormChange('policy_id', value)} />
//             </div>
//           )}
//         </form>
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
//         {formData.policy_id && (
//           <Button color="primary" className="d-flex align-items-center gap-1" type="submit" onClick={handleNextPage}>
//             <span className="d-none d-sm-inline">{t('next')}</span>
//             <Flexicon icon="chevron-right" variant="line" size={18} />
//           </Button>
//         )}
//       </div>
//     </>
//   );
// };
