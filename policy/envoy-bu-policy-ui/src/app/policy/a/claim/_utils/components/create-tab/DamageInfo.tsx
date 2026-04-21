'use client';
import { useTrans } from '@/helpers/services/lang/langService';
import { useRouter } from 'next/navigation';
import { Button, Input, Label } from '@apptimus-ui/ui-element';
import { Flexicon } from '@apptimus-ui/flexicon';
import { FormEvent, useState } from 'react';
import { initFormData } from '../../model';
import { clearError, printError } from '@/helpers/handlers/validationErrorHandler';
import { form } from '@/constans/Form';
import { CreateClaim } from '../../api-service';
import { toaster } from '@/helpers/services/toaster';
import { AsyncSelect } from '@apptimus-ui/select';
import { ImageDragAndDrop } from '@/components/others/page-related/uploader/ImageDragAndDrop';

export const DamageInfo = ({ toggleTableTab }: { toggleTableTab: Function }) => {
  const t = useTrans('label.claim,otr.common');
  const router = useRouter();
  const [isFormProcessing, setIsFormProcessing] = useState(false);
  const [formData, setFormData] = useState(initFormData);
  const [resource, setResource] = useState<File | null>(null);

  const handleNextPage = () => {
    toggleTableTab('other_party_info');
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
          <div className="panel-title mb-3">{t('damage_to_the_vehicle')}</div>
          <div className="row">
            <div className="col-12 mb-3">
              <Input label={t('describe_dmage_vehicle')} value={formData.name} onChange={(e) => onFormChange('name', e.target.value)} className="form-control error-name" name="name" type="textarea" />
            </div>
            <div className="col-12 col-md-6 mb-3">
              <Input label={t('estimate_of_repair_costs')} value={formData.name} onChange={(e) => onFormChange('name', e.target.value)} className="form-control error-name" name="name" />
            </div>
            <div className="col-12 col-md-6 mb-3 custom-select">
              <Label htmlFor="was_the_vehicle_towed" label={t('was_the_vehicle_towed')} />
              <AsyncSelect
                onChange={(value) => onFormChange('select_lead', value)}
                className="form-control error-child_id"
                option={{ label: 'name', value: 'id' }}
                isSearchable={true}
                loadOptions={() => ''}
              />
            </div>
            <div className="col-12 col-md-6 mb-3">
              <Input label={t('repair_shop_name')} value={formData.name} onChange={(e) => onFormChange('name', e.target.value)} className="form-control error-name" name="name" />
            </div>
            <div className="col-12 col-md-6 mb-3">
              <Input label={t('repair_shop_address')} value={formData.name} onChange={(e) => onFormChange('name', e.target.value)} className="form-control error-name" name="name" />
            </div>
            <div className="col-12 col-md-4 mb-3">
              <Label htmlFor="photos_of_damage" label={t('photos_of_damage')} isRequired />
              <div className="fs-10 fw-normal mb-2 text-muted">{t('images_showing_the_damage_vehicle')}</div>
              {!resource ? (
                <ImageDragAndDrop htmlFor={'document'} selectedImage={(file: File) => setResource(file)} className="form-control error-coverage_details" />
              ) : (
                <div className="d-flex flex-row justify-content-between gap-4 align-items-center border border-2 rounded-1 p-1 px-2">
                  <div>{resource.name}</div>
                  <div className="d-flex flex-row justify-content-between gap-2">
                    <Flexicon icon="x-square" variant="line" className="text-danger action-icon" onClick={() => setResource(null)} />
                  </div>
                </div>
              )}
            </div>
            <div className="row">
              <div className="col-12 col-md-4 mb-3">
                <Label htmlFor="repair_estimates" label={t('repair_estimates')} isRequired />
                <div className="fs-10 fw-normal mb-2 text-muted">{t('documentation_repair_costs')}</div>
                {!resource ? (
                  <ImageDragAndDrop htmlFor={'document'} selectedImage={(file: File) => setResource(file)} className="form-control error-coverage_details" />
                ) : (
                  <div className="d-flex flex-row justify-content-between gap-4 align-items-center border border-2 rounded-1 p-1 px-2">
                    <div>{resource.name}</div>
                    <div className="d-flex flex-row justify-content-between gap-2">
                      <Flexicon icon="x-square" variant="line" className="text-danger action-icon" onClick={() => setResource(null)} />
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </form>
      </div>
      <div className="d-flex justify-content-start gap-2 mt-3">
        <Button
          color="light"
          className="d-flex align-items-center gap-1"
          onClick={() => {
            router.push(`/policy/a/claim/create?t=incident_info`);
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
