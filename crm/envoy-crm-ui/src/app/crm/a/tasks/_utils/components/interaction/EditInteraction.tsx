// import { form } from '@/constans/Form';
// import { toaster } from '@/helpers/services/toaster';
// import { Modal, ModalBody, ModalFooter, ModalHeader } from '@apptimus-ui/modal';
// import { Button, Input, Label } from '@apptimus-ui/ui-element';
// import { FormEvent, useEffect, useState } from 'react';
// import { InputSkeleton } from '@/components/others/InputSkeleton';
// import { useTrans } from '@/helpers/services/lang/langService';
// import { AsyncSelect } from '@apptimus-ui/select';
// import { getOneSample, updateSample } from '@/app/crm/a/sample-crud/_utils/api-service';
// import { initFormData, ISample } from '@/app/crm/a/sample-crud/_utils/model';

// export const EditInteraction = ({ isOpen, editId, afterUpdate, onCancel }: { isOpen: boolean; editId: string; onCancel: Function; afterUpdate: Function }) => {
//   const t = useTrans('label.tasks,otr.common');

//   const [isFormProcessing, setIsFormProcessing] = useState(false);
//   const [formData, setFormData] = useState(initFormData);
//   const [skeleton, setSkeleton] = useState(true);

//   useEffect(() => {
//     const fetchData = async () => {
//       const responseData = await getOneSample(editId);

//       if (responseData?.is_success) {
//         const data: ISample = responseData.result;
//         onFormChange('name', data.name);
//         onFormChange('description', data.description);
//         setSkeleton(false);
//       }
//     };

//     if (editId) {
//       setSkeleton(true);
//       fetchData();
//     }
//   }, [editId]);

//   const onFormChange = (name: string, value: any) => {
//     setFormData((prevFormData) => ({ ...prevFormData, [name]: value }));
//   };

//   async function onSubmit(event: FormEvent<HTMLFormElement>) {
//     event.preventDefault();
//     setIsFormProcessing(true);

//     try {
//       const responseData = await updateSample(editId, formData);
//       setIsFormProcessing(false);

//       if (responseData.is_success) {
//         toaster.success(t(responseData.message));
//         setFormData(initFormData);
//         afterUpdate();
//       }
//     } catch (error) {
//       console.error('An error occurred:', error);
//     }
//   }

//   return (
//     <Modal isOpen={isOpen}>
//       <ModalHeader title={t('edit_customers_interactions')} onClose={() => onCancel()} />
//       <form onSubmit={onSubmit} id={`${form.sample_crud.update}`}>
//         <ModalBody>
//           <div className="row">
//             <div className="col-12 col-md-6 mb-3">
//               <Label htmlFor="name" label={t('task_type')} isRequired />
//               {skeleton ? <InputSkeleton /> : <AsyncSelect loadOptions={() => {}} onChange={() => {}} />}
//             </div>
//             <div className="col-12 col-md-6 mb-3">
//               <Label label={t('assigned_stage')} isRequired />
//               {skeleton ? (
//                 <InputSkeleton />
//               ) : (
//                 <Input value={formData.description} onChange={(e) => onFormChange('description', e.target.value)} className="form-control error-description" id="description" name="description" />
//               )}
//             </div>
//             <div className="col-12 col-md-6 mb-3">
//               <Label label={t('task')} />
//               {skeleton ? (
//                 <InputSkeleton />
//               ) : (
//                 <Input value={formData.description} onChange={(e) => onFormChange('description', e.target.value)} className="form-control error-description" id="description" name="description" />
//               )}
//             </div>
//             <div className="col-12 col-md-6 mb-3">
//               <Label label={t('expected_time_period_to_complete')} isRequired />
//               {skeleton ? <InputSkeleton /> : <AsyncSelect loadOptions={() => {}} onChange={() => {}} />}
//             </div>
//             <div className="col-12 col-md-6 mb-3">
//               <Label label={t('expected_time_to_send_reminder')} isRequired />
//               {skeleton ? <InputSkeleton /> : <AsyncSelect loadOptions={() => {}} onChange={() => {}} />}
//             </div>
//           </div>
//         </ModalBody>
//         <ModalFooter>
//           <div className="d-flex justify-content-end gap-2">
//             <Button text={t('update')} type="submit" width="sm" isLoading={isFormProcessing} disabled={skeleton} />
//             <Button text={t('cancel')} color="light" width="sm" onClick={() => onCancel()} />
//           </div>
//         </ModalFooter>
//       </form>
//     </Modal>
//   );
// };
