'use client';
import { useTrans } from '@/helpers/services/lang/langService';
import { useRouter } from 'next/navigation';
import { Button, Input, Label } from '@apptimus-ui/ui-element';
import { Flexicon } from '@apptimus-ui/flexicon';
import { FormEvent, useState } from 'react';
import { initFormData } from '../../model';
import { form } from '@/constans/Form';
import { clearError, printError } from '@/helpers/handlers/validationErrorHandler';
import { CreateClaim } from '../../api-service';
import { toaster } from '@/helpers/services/toaster';
import { AsyncSelect } from '@apptimus-ui/select';

export const OtherPartyInfo = ({ toggleTableTab }: { toggleTableTab: Function }) => {
  const t = useTrans('label.claim,otr.common');
  const router = useRouter();
  const [isFormProcessing, setIsFormProcessing] = useState(false);
  const [formData, setFormData] = useState(initFormData);

  const handleNextPage = () => {
    toggleTableTab('witness_info');
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
          <div className="panel-title mb-3">{t('other_parties_involved')}</div>
          <div className="row">
            <div className="col-12 col-md-3 mb-3 custom-select">
              <Label htmlFor="was_another_vehicle_involved" label={t('was_another_vehicle_involved')} />
              <AsyncSelect
                onChange={(value) => onFormChange('select_lead', value)}
                className="form-control error-child_id"
                option={{ label: 'name', value: 'id' }}
                isSearchable={true}
                loadOptions={() => ''}
              />
            </div>
            <div className="col-12 mb-3">
              <Input label={t('driver_name')} value={formData.name} onChange={(e) => onFormChange('name', e.target.value)} className="form-control error-name" name="name" />
            </div>
            <div className="col-12 col-md-4 mb-3">
              <Input label={t('vehicle_type')} value={formData.name} onChange={(e) => onFormChange('name', e.target.value)} className="form-control error-name" name="name" />
            </div>
            <div className="col-12 col-md-4 mb-3">
              <Input label={t('vehicle_make')} value={formData.name} onChange={(e) => onFormChange('name', e.target.value)} className="form-control error-name" name="name" />
            </div>
            <div className="col-12 col-md-4 mb-3">
              <Input label={t('vehicle_model')} value={formData.name} onChange={(e) => onFormChange('name', e.target.value)} className="form-control error-name" name="name" />
            </div>
            <div className="col-12 col-md-4 mb-3">
              <Input isRequired label={t('license_plate_number')} value={formData.name} onChange={(e) => onFormChange('name', e.target.value)} className="form-control error-name" name="name" />
            </div>
            <div className="col-12 col-md-4 mb-3">
              <Input label={t('year_of_manufacture')} value={formData.name} onChange={(e) => onFormChange('name', e.target.value)} className="form-control error-name" name="name" />
            </div>
            <div className="col-12 col-md-4 mb-3">
              <Input label={t('registered_year')} value={formData.name} onChange={(e) => onFormChange('name', e.target.value)} className="form-control error-name" name="name" />
            </div>
            <div className="col-12 col-md-4 mb-3">
              <Input label={t('vehicle_identification_number')} value={formData.name} onChange={(e) => onFormChange('name', e.target.value)} className="form-control error-name" name="name" />
            </div>
            <div className="col-12 col-md-4 mb-3">
              <Input label={t('other_driver_insurance_company')} value={formData.name} onChange={(e) => onFormChange('name', e.target.value)} className="form-control error-name" name="name" />
            </div>
            <div className="col-12 col-md-4 mb-3">
              <Input label={t('used_for')} value={formData.name} onChange={(e) => onFormChange('name', e.target.value)} className="form-control error-name" name="name" />
            </div>
          </div>
        </form>
      </div>
      <div className="d-flex justify-content-start gap-2 mt-3">
        <Button
          color="light"
          className="d-flex align-items-center gap-1"
          onClick={() => {
            router.push(`/policy/a/claim/create?t=damage_info`);
          }}
        >
          <Flexicon icon="chevron-left" variant="line" size={18} />
          <span className="d-none d-sm-inline">{t('back')}</span>
        </Button>
        <Button color="light" className="d-flex align-items-center gap-1" onClick={handleNextPage}>
          <span className="d-none d-sm-inline">{t('skip')}</span>
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
