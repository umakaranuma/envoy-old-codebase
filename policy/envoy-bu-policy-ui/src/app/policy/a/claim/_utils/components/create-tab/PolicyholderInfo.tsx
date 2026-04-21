// 'use client';
// import { FormEvent, useState } from 'react';
// import { useTrans } from '@/helpers/services/lang/langService';
// import { useRouter } from 'next/navigation';
// import { initFormData } from '../../model';
// import { CreateClaim } from '../../api-service';
// import { Button, Input, Label } from '@apptimus-ui/ui-element';
// import { Flexicon } from '@apptimus-ui/flexicon';
// import { clearError, printError } from '@/helpers/handlers/validationErrorHandler';
// import { form } from '@/constans/Form';
// import { toaster } from '@/helpers/services/toaster';
// import { AsyncSelect } from '@apptimus-ui/select';
// import { thousandSeparator } from '@/helpers/services/commonService';

// export const PolicyholderInfo = ({ toggleTableTab }: { toggleTableTab: Function }) => {
//   const t = useTrans('label.claim,otr.common');
//   const router = useRouter();
//   const [formData, setFormData] = useState(initFormData);
//   const [isFormProcessing, setIsFormProcessing] = useState(false);

//   const handleNextPage = () => {
//     toggleTableTab('vehicle_info');
//   };

//   const onFormChange = (name: string, value: any) => {
//     setFormData((prevFormData) => ({ ...prevFormData, [name]: value }));
//   };

//   const tBe = useTrans('be.msg,be.error,be.attri');
//   async function onSubmit(e: FormEvent<HTMLFormElement>) {
//     e.preventDefault();
//     clearError(form.issued_crud.store);
//     setIsFormProcessing(true);

//     try {
//       const responseData = await CreateClaim(formData);
//       setIsFormProcessing(false);

//       if (responseData.status_code === 417) {
//         printError(responseData.result, form.issued_crud.store, tBe);
//       }

//       if (responseData.is_success) {
//         toaster.success(tBe(responseData.message));
//       }
//     } catch (error) {
//       console.error('An error occurred:', error);
//     }
//   }

//   return (
//     <>
//       <div className="mb-4">
//         <form onSubmit={onSubmit} id={`${form.issued_crud.store}`}>
//           <div className="panel-title mb-3">{t('policyholder_information')}</div>
//           <div className="row">
//             <div className="col-12 col-md-6 mb-3">
//               <Input isRequired label={t('full_name')} value={formData.name} onChange={(e) => onFormChange('name', e.target.value)} className="form-control error-name" name="name" />
//             </div>
//             <div className="col-12 col-md-6 mb-3">
//               <Input isRequired type="date" label={t('date_of_birth')} value={formData.name} onChange={(e) => onFormChange('name', e.target.value)} className="form-control error-name" name="name" />
//             </div>
//             <div className="col-12 col-md-4 mb-3">
//               <Input isRequired label={t('email')} value={formData.name} onChange={(e) => onFormChange('name', e.target.value)} className="form-control error-name" name="name" type="email" />
//             </div>
//             <div className="col-12 col-md-4 mb-3">
//               <Input isRequired label={t('contact_number')} value={formData.name} onChange={(e) => onFormChange('name', e.target.value)} className="form-control error-name" name="name" />
//             </div>
//             <div className="col-12 col-md-4 mb-3">
//               <Input isRequired label={t('driver_license_number')} value={formData.name} onChange={(e) => onFormChange('name', e.target.value)} className="form-control error-name" name="name" />
//             </div>
//             <div className="col-12 col-md-4 mb-3 custom-select">
//               <Label htmlFor="full_name" label={t('city')} isRequired />
//               <AsyncSelect
//                 onChange={(value) => onFormChange('select_lead', value)}
//                 className="form-control error-child_id"
//                 option={{ label: 'name', value: 'id' }}
//                 isSearchable={true}
//                 loadOptions={() => ''}
//               />
//             </div>
//             <div className="col-12 col-md-4 mb-3 custom-select">
//               <Label htmlFor="full_name" label={t('state_province')} isRequired />
//               <AsyncSelect
//                 onChange={(value) => onFormChange('select_lead', value)}
//                 className="form-control error-child_id"
//                 option={{ label: 'name', value: 'id' }}
//                 isSearchable={true}
//                 loadOptions={() => ''}
//               />
//             </div>
//             <div className="col-12 col-md-4 mb-3 custom-select">
//               <Label htmlFor="full_name" label={t('zip_postal_code')} isRequired />
//               <AsyncSelect
//                 onChange={(value) => onFormChange('select_lead', value)}
//                 className="form-control error-child_id"
//                 option={{ label: 'name', value: 'id' }}
//                 isSearchable={true}
//                 loadOptions={() => ''}
//               />
//             </div>
//             <div className="col-12 col-md-4 mb-3">
//               <Input isRequired label={t('address')} value={formData.name} onChange={(e) => onFormChange('name', e.target.value)} className="form-control error-name" name="name" type="textarea" />
//             </div>
//           </div>
//           <div className="panel-title mb-3">{t('policy_information')}</div>
//           <div className="row">
//             <div className="col-12 col-md-4 mb-3">
//               <Input isRequired label={t('policy_number')} value={formData.name} onChange={(e) => onFormChange('name', e.target.value)} className="form-control error-name" name="name" />
//             </div>
//           </div>
//           <div className="row">
//             <div className="col-12 col-md-6 mb-3">
//               <Input isRequired label={t('start_date')} value={formData.name} onChange={(e) => onFormChange('name', e.target.value)} className="form-control error-name" name="name" type="date" />
//             </div>
//             <div className="col-12 col-md-6 mb-3">
//               <Input isRequired label={t('end_date')} value={formData.name} onChange={(e) => onFormChange('name', e.target.value)} className="form-control error-name" name="name" type="date" />
//             </div>
//           </div>
//           <div className="panel-title mb-3">{t('product_information')}</div>
//           <div className="row">
//             <div className="col-12 col-md-6 mb-3 custom-select">
//               <Label htmlFor="full_name" label={t('product_name')} isRequired />
//               <AsyncSelect
//                 onChange={(value) => onFormChange('select_lead', value)}
//                 className="form-control error-child_id"
//                 option={{ label: 'name', value: 'id' }}
//                 isSearchable={true}
//                 loadOptions={() => ''}
//               />
//             </div>
//             <div className="col-12 col-md-6 mb-3 custom-select">
//               <Label htmlFor="full_name" label={t('coverage_type')} isRequired />
//               <AsyncSelect
//                 onChange={(value) => onFormChange('select_lead', value)}
//                 className="form-control error-child_id"
//                 option={{ label: 'name', value: 'id' }}
//                 isSearchable={true}
//                 loadOptions={() => ''}
//               />
//             </div>
//           </div>
//           <div className="panel-title mb-3">{t('insurer_info')}</div>
//           <div className="row">
//             <div className="col-12 col-md-6 mb-3 custom-select">
//               <Label htmlFor="full_name" label={t('insurer_name')} isRequired />
//               <AsyncSelect
//                 onChange={(value) => onFormChange('select_lead', value)}
//                 className="form-control error-child_id"
//                 option={{ label: 'name', value: 'id' }}
//                 isSearchable={true}
//                 loadOptions={() => ''}
//               />
//             </div>
//             <div className="col-12 col-md-6 mb-3">
//               <Input isRequired label={t('primary_contact_number')} value={formData.name} onChange={(e) => onFormChange('name', e.target.value)} className="form-control error-name" name="name" />
//             </div>
//             <div className="col-12 col-md-6 mb-3">
//               <Input isRequired label={t('policy_date')} value={formData.name} onChange={(e) => onFormChange('name', e.target.value)} className="form-control error-name" name="name" type="date" />
//             </div>
//             <div className="col-12 col-md-6 mb-3">
//               <Input isRequired label={t('premium_amount')} value={thousandSeparator(formData.premium_amount)} onChange={(e) => onFormChange('premium_amount', e.target.value)} className="form-control error-name" name="premium_amount" />
//             </div>
//             <div className="col-12 col-md-6 mb-3">
//               <Input isRequired label={t('total_commission')} value={formData.name} onChange={(e) => onFormChange('name', e.target.value)} className="form-control error-name" name="name" />
//             </div>
//             <div className="col-12 col-md-6 mb-3">
//               <Input isRequired label={t('received_commission')} value={formData.name} onChange={(e) => onFormChange('name', e.target.value)} className="form-control error-name" name="name" />
//             </div>
//             <div className="col-12 col-md-6 mb-3 custom-select">
//               <Label htmlFor="full_name" label={t('sales_agent')} isRequired />
//               <AsyncSelect
//                 onChange={(value) => onFormChange('select_lead', value)}
//                 className="form-control error-child_id"
//                 option={{ label: 'name', value: 'id' }}
//                 isSearchable={true}
//                 loadOptions={() => ''}
//               />
//             </div>
//             <div className="col-12 col-md-6 mb-3 custom-select">
//               <Label htmlFor="full_name" label={t('account_manager')} isRequired />
//               <AsyncSelect
//                 onChange={(value) => onFormChange('select_lead', value)}
//                 className="form-control error-child_id"
//                 option={{ label: 'name', value: 'id' }}
//                 isSearchable={true}
//                 loadOptions={() => ''}
//               />
//             </div>
//             <div className="col-12 mb-3">
//               <Input label={t('remarks_notes')} value={formData.name} onChange={(e) => onFormChange('name', e.target.value)} className="form-control error-name" name="name" type="textarea" />
//             </div>
//           </div>
//         </form>
//       </div>
//       <div className="d-flex justify-content-start gap-2 mt-3">
//         <Button
//           color="light"
//           className="d-flex align-items-center gap-1"
//           onClick={() => {
//             router.push(`/policy/a/claim/create?t=policy_information`);
//           }}
//         >
//           <Flexicon icon="chevron-left" variant="line" size={18} />
//           <span className="d-none d-sm-inline">{t('back')}</span>
//         </Button>
//         <Button color="primary" className="d-flex align-items-center gap-1" type="submit" onClick={handleNextPage} isLoading={isFormProcessing}>
//           <span className="d-none d-sm-inline">{t('next')}</span>
//           <Flexicon icon="chevron-right" variant="line" size={18} />
//         </Button>
//         {/* <Button text={t('update')} type="submit" width="sm" isLoading={undefined} disabled={skeleton} />
//                   <Button text={t('cancel')} color="light" width="sm" /> */}
//       </div>
//     </>
//   );
// };
