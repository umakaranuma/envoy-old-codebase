'use client';
import { FormEvent, useState } from 'react';
import { useTrans } from '@/helpers/services/lang/langService';
import { useRouter } from 'next/navigation';
import { initFormData } from '../../model';
import { Button, Input } from '@apptimus-ui/ui-element';
import { Flexicon } from '@apptimus-ui/flexicon';
import { clearError, printError } from '@/helpers/handlers/validationErrorHandler';
import { CreateClaim } from '../../api-service';
import { form } from '@/constans/Form';
import { toaster } from '@/helpers/services/toaster';

export const VehicleInfo = ({ toggleTableTab }: { toggleTableTab: Function }) => {
  const t = useTrans('label.claim,otr.common');
  const router = useRouter();
  const [isFormProcessing, setIsFormProcessing] = useState(false);
  const [formData, setFormData] = useState(initFormData);

  const handleNextPage = () => {
    toggleTableTab('incident_info');
  };

  const onFormChange = (name: string, value: any) => {
    setFormData((prevFormData) => ({ ...prevFormData, [name]: value }));
  };

  const tBe = useTrans('be.msg,be.error,be.attri');
  async function onSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    clearError(form.issued_crud.store);
    setIsFormProcessing(true);

    try {
      const responseData = await CreateClaim(formData);
      setIsFormProcessing(false);

      if (responseData.status_code === 417) {
        printError(responseData.result, form.issued_crud.store, tBe);
      }

      if (responseData.is_success) {
        toaster.success(tBe(responseData.message));
      }
    } catch (error) {
      console.error('An error occurred:', error);
    }
  }

  return (
    <>
      <div className="mb-4">
        <form onSubmit={onSubmit} id={`${form.issued_crud.store}`}>
          <div className="panel-title mb-3">{t('vehicle_information')}</div>
          <div className="row">
            <div className="col-12 col-md-4 mb-3">
              <Input isRequired label={t('vehicle_type')} value={formData.name} onChange={(e) => onFormChange('name', e.target.value)} className="form-control error-name" name="name" />
            </div>
            <div className="col-12 col-md-4 mb-3">
              <Input isRequired label={t('vehicle_make')} value={formData.name} onChange={(e) => onFormChange('name', e.target.value)} className="form-control error-name" name="name" />
            </div>
            <div className="col-12 col-md-4 mb-3">
              <Input isRequired label={t('vehicle_model')} value={formData.name} onChange={(e) => onFormChange('name', e.target.value)} className="form-control error-name" name="name" />
            </div>
            <div className="col-12 col-md-4 mb-3">
              <Input isRequired label={t('year_of_manufacture')} value={formData.name} onChange={(e) => onFormChange('name', e.target.value)} className="form-control error-name" name="name" />
            </div>
            <div className="col-12 col-md-4 mb-3">
              <Input isRequired label={t('registered_year')} value={formData.name} onChange={(e) => onFormChange('name', e.target.value)} className="form-control error-name" name="name" />
            </div>
            <div className="col-12 col-md-4 mb-3">
              <Input
                isRequired
                label={t('vehicle_identification_number')}
                value={formData.name}
                onChange={(e) => onFormChange('name', e.target.value)}
                className="form-control error-name"
                name="name"
              />
            </div>
            <div className="col-12 col-md-6 mb-3">
              <Input isRequired label={t('license_plate_number')} value={formData.name} onChange={(e) => onFormChange('name', e.target.value)} className="form-control error-name" name="name" />
            </div>
            <div className="col-12 col-md-6 mb-3">
              <Input isRequired label={t('mileage')} value={formData.name} onChange={(e) => onFormChange('name', e.target.value)} className="form-control error-name" name="name" />
            </div>
          </div>
        </form>
      </div>
      <div className="d-flex justify-content-start gap-2 mt-3">
        <Button
          color="light"
          className="d-flex align-items-center gap-1"
          onClick={() => {
            router.push(`/policy/a/claim/create?t=policyholder_info`);
          }}
        >
          <Flexicon icon="chevron-left" variant="line" size={18} />
          <span className="d-none d-sm-inline">{t('back')}</span>
        </Button>
        <Button color="primary" className="d-flex align-items-center gap-1" onClick={handleNextPage} isLoading={isFormProcessing}>
          <span className="d-none d-sm-inline">{t('next')}</span>
          <Flexicon icon="chevron-right" variant="line" size={18} />
        </Button>
        {/* <Button text={t('update')} type="submit" width="sm" isLoading={undefined} disabled={skeleton} />
                  <Button text={t('cancel')} color="light" width="sm" /> */}
      </div>
    </>
  );
};
