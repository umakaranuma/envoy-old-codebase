import { useTrans } from '@/helpers/services/lang/langService';
import { Flexicon } from '@apptimus-ui/flexicon';
import { Button, Input, Skeleton } from '@apptimus-ui/ui-element';
import React, { useEffect, useState } from 'react';
import { IUser } from '../model';
import { form } from '@/constans/Form';
import { clearError, printError } from '@/helpers/handlers/validationErrorHandler';
import { handleFileUpload } from '@/helpers/services/commonService';
import { toaster } from '@/helpers/services/toaster';
import { updateUser } from '@/app/a/users/_utils/api-service';
import { Select } from '@apptimus-ui/select';
import { InputSkeleton } from '@/components/others/InputSkeleton';
import { ImageDragAndDrop } from '@/components/others/page-related/uploader/ImageDragAndDrop';
import Image from 'next/image';
import ImageCropper from '@/components/others/page-related/ImageCropper';
import { setLocalStorage } from '@/helpers/handlers/localStorageHandler';
import { local_storage } from '@/constans/StorageKeys';
import { useRouter } from 'next/navigation';
import ReactPhoneInput from '@/components/others/page-related/ReactPhoneInput';

function MyDetails({ userData, afterSave, loading }: { userData: IUser | null; afterSave: Function; loading: boolean }) {
  const t = useTrans('label.user,otr.common');
  const tBe = useTrans('be.msg,be.error,be.attri');
  const [formData, setFormData] = useState<IUser>({} as IUser);
  // const [resource, setResource] = useState<File | null>(null);
  const [isFormProcessing, setIsFormProcessing] = useState(false);
  const [displayNames, setDisplayNames] = useState<{ label: string }[]>([]);
  const [resource, setResource] = useState<any>({ preview: '', key: 0, url: '', cropperVisible: false, croppedFile: null });
  const router = useRouter();

  useEffect(() => {
    setFormData(userData || ({} as IUser));
  }, [userData]);

  const onFormChange = (name: string, value: any) => {
    setFormData((prevFormData) => ({ ...prevFormData, [name]: value }));
  };

  const generateDisplayName = () => {
    const nameCollection = [
      { label: formData.title + ' ' + formData.first_name + ' ' + formData.last_name },
      { label: formData.last_name + ' ' + formData.first_name },
      { label: formData.first_name + ', ' + formData.last_name },
    ];
    setDisplayNames(nameCollection);
  };

  useEffect(() => {
    generateDisplayName();
  }, [formData.title, formData.first_name, formData.last_name]);

  async function onSubmit() {
    clearError(form.user.update);
    setIsFormProcessing(true);
    try {
      const docData = await handleFileUpload(resource.croppedFile, `user`);
      const responseData = await updateUser(formData.id.toString(), {
        ...formData,
        picture: docData?.key,
        picture_type: docData?.type,
        picture_name: docData?.name,
      });
      setIsFormProcessing(false);

      if (responseData.status_code === 417) {
        printError(responseData.result, form.user.update, tBe);
      }

      if (responseData.is_success) {
        setLocalStorage(local_storage.auth_user_info, {
          value: responseData.result,
        });
        afterSave();
        toaster.success(tBe(responseData.message));
        router.refresh();
      }
    } catch (error) {
      console.error('An error occurred:', error);
    }
  }

  return (
    <div className="mt-2 mt-md-4 text">
      <div className="border-bottom border-3 pb-2 border-light">
        <div className="fw-bold">{t('personal_info')}</div>
        <div className="text-muted mb-2">{t('update_your_photo_and_personal_details_here')}</div>
      </div>
      <div className="mt-4 mt-md-4 row" id={`${form.user.update}`}>
        <div className="col-12 col-md-8">
          <div className="row">
            <div className="col-12 col-md-4 mb-3">
              <div className="fw-medium">{t('salutation')}</div>
            </div>
            <div className="col-12 col-md-8 mb-3">
              {loading ? (
                <InputSkeleton />
              ) : (
                <Select
                  onChange={(value) => {
                    onFormChange('title', value), onFormChange('display_name', '');
                  }}
                  options={[
                    { label: t('mr'), value: 'Mr.' },
                    { label: t('mrs'), value: 'Mrs.' },
                    { label: t('miss'), value: 'Miss.' },
                    { label: t('rev'), value: 'Rev.' },
                  ]}
                  option={{ label: 'label', value: 'value' }}
                  isSearchable={false}
                  defaultValue={{ label: formData.title, value: formData.title }}
                  className="form-control error-title p-0"
                />
              )}
            </div>
            <div className="col-12 col-md-4 mb-3">
              <div className="fw-medium">{t('full_name')}</div>
            </div>
            <div className="col-12 col-md-8 mb-3">
              <div className="row">
                <div className="col-6">
                  {' '}
                  {loading ? (
                    <InputSkeleton />
                  ) : (
                    <Input
                      value={formData.first_name || ''}
                      onChange={(e) => {
                        onFormChange('first_name', e.target.value), onFormChange('display_name', '');
                      }}
                      className="form-control error-first_name"
                    />
                  )}
                </div>
                <div className="col-6">
                  {' '}
                  {loading ? (
                    <InputSkeleton />
                  ) : (
                    <Input
                      value={formData.last_name || ''}
                      onChange={(e) => {
                        onFormChange('last_name', e.target.value), onFormChange('display_name', '');
                      }}
                      className="form-control error-last_name"
                    />
                  )}
                </div>
              </div>
            </div>
            <div className="col-12 col-md-4 mb-3">
              <div className="fw-medium">{t('display_name')}</div>
            </div>
            <div className="col-12 col-md-8 mb-3 custom-select" key={`displayName-${formData.first_name + formData.last_name + formData.title}`}>
              {loading ? (
                <InputSkeleton />
              ) : (
                <Select
                  onChange={(value) => onFormChange('display_name', value)}
                  options={displayNames}
                  option={{ label: 'label', value: 'label' }}
                  isSearchable={false}
                  defaultValue={{ label: formData.display_name, value: formData.display_name }}
                  className="form-control error-display_name"
                />
              )}
            </div>
            <div className="col-12 col-md-4 mb-3">
              <div className="fw-medium">{t('email_address')}</div>
            </div>
            <div className="col-12 col-md-8 mb-3">
              {loading ? <InputSkeleton /> : <Input value={formData.email || ''} onChange={(e) => onFormChange('email', e.target.value)} className="form-control error-email" />}
            </div>
            <div className="col-12 col-md-4 mb-3">
              <div className="fw-medium">{t('phone_number')}</div>
            </div>
            <div className="col-12 col-md-8 mb-3">
              {loading ? (
                <InputSkeleton />
              ) : (
                // <PhoneInput
                //   country={'lk'}
                //   enableAreaCodes={true}
                //   inputStyle={{ height: '40px', width: '100%' }}
                //   containerStyle={{ height: '40px', width: '100%' }}
                //   inputClass="form-control error-primary_contact"
                //   countryCodeEditable={false}
                //   value={formData.contact_no || ''}
                //   onChange={(phone) => {
                //     onFormChange('contact_no', phone);
                //   }}
                // />
                <ReactPhoneInput
                  value={formData.contact_no || ''}
                  onChange={(phone) => onFormChange('contact_no', phone)}
                  defaultCountryCode={'lk'}
                  enableAreaCodes={false}
                  className="form-control error-contact_no"
                />
              )}
            </div>
            <div className="col-12 col-md-4 mb-3">
              <div className="fw-medium">{t('your_photo')}</div>
              <div className="text-muted fs-12">{t('this_will_be_displayed_on_your_profile')}</div>
            </div>
            <div className="col-12 col-md-8 mb-3">
              {/* {loading ? <Skeleton height='150px' /> :
              <>
              {formData.picture?<S3Avatar imageKey={formData.picture} width={150} height={150} />:
               <FilePreviewer
                onChange={(file) => {
                  setResource(file);
                }}
                initialUrl={formData.picture || ''}
              />}
              </>} */}
              {loading ? (
                <Skeleton height="100px" width="100%" />
              ) : (
                <div className="d-flex flex-row align-items-center gap-3">
                  {(resource.preview || formData.picture) && (
                    <Image src={resource.preview ? resource.preview : `${process.env.S3CDN}/${formData.picture}`} alt={'profile'} width={110} height={110} className="rounded-circle" />
                  )}
                  <div className="w-100">
                    <ImageDragAndDrop
                      htmlFor={'cover-image'}
                      fileType="image"
                      selectedImageSrc={(src: string) => {
                        setResource((prevData: any) => ({ ...prevData, url: src, cropperVisible: true }));
                      }}
                    />
                  </div>
                </div>
              )}
            </div>
            {/* <div className="col-12 col-md-4 mb-3">
              <div className="fw-medium">Cover photo</div>
              <div className="text-muted fs-12">This will be displayed on your cover.</div>
            </div>
            <div className="col-12 col-md-8 mb-3">
              <FilePreviewer
                onChange={(file) => {
                  console.log(file);
                }}
              />
            </div> */}
            {/* <div className="col-12 col-md-4 mb-3">
              <div className="fw-medium">Street address</div>
            </div>
            <div className="col-12 col-md-8 mb-3">
              <Input />
            </div>
            <div className="col-12 col-md-4 mb-3">
              <div className="fw-medium">City</div>
            </div>
            <div className="col-12 col-md-8 mb-3">
              <Input />
            </div>
            <div className="col-12 col-md-4 mb-3">
              <div className="fw-medium">State / Province</div>
            </div>
            <div className="col-12 col-md-5 mb-3">
              <div className="row">
                <div className="col-6">
                  {' '}
                  <Input />
                </div>
                <div className="col-6">
                  {' '}
                  <Input />
                </div>
              </div>
            </div>
            <div className="col-12 col-md-4 mb-3">
              <div className="fw-medium">Country</div>
            </div>
            <div className="col-12 col-md-8 mb-3">
              <Input />
            </div> */}
          </div>
        </div>
        <div className="d-flex justify-content-end gap-2 mt-3">
          <Button text={t('cancel')} color="light" width="sm" />
          <Button className="d-flex align-items-center gap-1" onClick={onSubmit} isLoading={isFormProcessing}>
            <Flexicon icon="save-01" variant="line" size={18} />
            <span>{t('save_changes')}</span>
          </Button>
        </div>
      </div>
      <ImageCropper
        key={`cover-image${resource.key}`}
        isOpen={resource.cropperVisible}
        imageSrc={resource.url ? resource.url : ''}
        size={1 / 1}
        croppedImageSrc={(url: string) => {
          setResource((prevData: any) => ({ ...prevData, preview: url, cropperVisible: false }));
        }}
        croppedImage={(image: File) => setResource((prevData: any) => ({ ...prevData, croppedFile: image }))}
      />
    </div>
  );
}

export default MyDetails;
