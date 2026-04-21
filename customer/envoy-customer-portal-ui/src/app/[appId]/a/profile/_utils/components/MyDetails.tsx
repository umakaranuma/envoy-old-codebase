import ImageCropper from '@/components/others/page-related/ImageCropper';
import { ImageDragAndDrop } from '@/components/others/page-related/ImageDragAndDrop';
import { useTrans } from '@/helpers/services/lang/langService';
import { fileUploader } from '@/helpers/services/storageService';
import { Flexicon } from '@apptimus-ui/flexicon';
import { Button, Input, Label, Skeleton } from '@apptimus-ui/ui-element';
import Image from 'next/image';
import React, { useEffect, useState } from 'react';
import PhoneInput from 'react-phone-input-2';
import 'react-phone-input-2/lib/style.css';
import { IImageUploadData, IProfileDetails } from '../model';
import { getProfileMyDetails, updateProfileInfo } from '../api-service';
import { InputSkeleton } from '@/components/others/InputSkeleton';
import { useParams, useRouter } from 'next/navigation';
import { clearError, printError } from '@/helpers/handlers/validationErrorHandler';
import { form } from '@/constans/Form';
import { toaster } from '@/helpers/services/toaster';
import { local_storage } from '@/constans/StorageKeys';
import { getLocalStorage, setLocalStorage } from '@/helpers/handlers/localStorageHandler';

function MyDetails({ reloadProfile }: { reloadProfile: Function }) {
  const t = useTrans('label.my_policy,label.profile,otr.common');
  const tBe = useTrans('be.msg,be.error,be.attri');
  const [profileImage, setProfileImage] = useState<IImageUploadData>({ preview: '', key: 0, url: '', cropperVisible: false, croppedFile: null });
  const [coverImage, setCoverImage] = useState<IImageUploadData>({ preview: '', key: 0, url: '', cropperVisible: false, croppedFile: null });
  const [passbookImage, setPassbookImage] = useState<IImageUploadData>({ preview: '', key: 0, url: '', cropperVisible: false, croppedFile: null });
  const [formData, setFormData] = useState<IProfileDetails>({} as IProfileDetails);
  const [skeleton, setSkeleton] = useState(true);
  const [isFormProcessing, setIsFormProcessing] = useState(false);
  const params = useParams();
  const appId = params.appId as string;
  const router = useRouter();
  const onFormChange = (name: string, value: any) => {
    setFormData((prevFormData) => ({ ...prevFormData, [name]: value }));
  };

  useEffect(() => {
    const fetchData = async () => {
      setSkeleton(true);
      const responseData = await getProfileMyDetails();
      if (responseData?.is_success) {
        setFormData(responseData.result);
        setSkeleton(false);
      }
    };
    fetchData();
  }, []);

  async function onSubmit() {
    clearError(form.profile.store);
    setIsFormProcessing(true);
    let data = {} as any;

    if (profileImage.croppedFile) {
      const profileImageData = await handleFileUpload(profileImage.croppedFile);
      data = { logo: profileImageData?.doc };
    }

    if (coverImage.croppedFile) {
      const coverImageData = await handleFileUpload(coverImage.croppedFile);
      data = { ...data, contact_picture: coverImageData?.doc };
    }

    if (passbookImage.croppedFile) {
      const passbookImageData = await handleFileUpload(passbookImage.croppedFile);
      data = { ...data, doc: passbookImageData?.doc, doc_type: passbookImageData?.type, doc_name: passbookImageData?.name };
    }

    try {
      const responseData = await updateProfileInfo({ ...formData, ...data });
      setIsFormProcessing(false);

      if (responseData.status_code === 417) {
        printError(responseData.result, form.profile.store, tBe);
      }

      if (responseData.is_success) {
        const userInfo = getLocalStorage(local_storage.auth_user_info);
        setLocalStorage(local_storage.auth_user_info, {
          value: { ...userInfo, logo: data.logo },
        });
        toaster.success(tBe(responseData.message));
        reloadProfile();
        router.refresh();
      }
    } catch (error) {
      console.error('An error occurred:', error);
    }
  }

  const handleFileUpload = async (file: File) => {
    const fileData = new FormData();
    if (!file) {
      return null;
    }
    fileData.append('file', file);
    const fileName = file.name;
    const fileExtension = file.name.split('.').pop();
    const key = await fileUploader(fileData, `${appId}/customer/profile`);
    return { doc: key, name: fileName, type: fileExtension };
  };

  return (
    <div className="mt-2 mt-md-4 text">
      <div className="border-bottom border-3 pb-2 border-light">
        <div className="fw-bold">{t('personal_info')}</div>
        <div className="text-muted mb-2">{t('update_your_photo_and_personal_details_here')}</div>
      </div>
      <div className="mt-4 mt-md-4 row">
        <div className="col-12 col-md-8">
          <div className="row">
            <div className="col-12 col-md-4 mb-3">
              <div className="fw-medium">{t('full_name')}</div>
            </div>
            <div className="col-12 col-md-8 mb-3">{skeleton ? <InputSkeleton /> : <Input disabled value={formData.name || ''} />}</div>
            <div className="col-12 col-md-4 mb-3">
              <div className="fw-medium">{t('email_address')}</div>
            </div>
            <div className="col-12 col-md-8 mb-3">{skeleton ? <InputSkeleton /> : <Input disabled value={formData.contact_email || ''} />}</div>
            <div className="col-12 col-md-4 mb-3">
              <div className="fw-medium">{t('phone_number')}</div>
            </div>
            <div className="col-12 col-md-8 mb-3">
              {skeleton ? (
                <InputSkeleton />
              ) : (
                <PhoneInput
                  disabled
                  country={'lk'}
                  value={formData.contact_primary_contact || ''}
                  enableAreaCodes={true}
                  inputStyle={{ height: '40px', width: '100%' }}
                  containerStyle={{ height: '40px', width: '100%' }}
                  inputClass="form-control error-primary_contact"
                  countryCodeEditable={false}
                />
              )}
            </div>
            <div className="col-12 col-md-4 mb-3">
              <div className="fw-medium">{t('your_photo')}</div>
              <div className="text-muted fs-12">{t('this_will_be_displayed_on_your_profile')}</div>
            </div>
            <div className="col-12 col-md-8 mb-3">
              {skeleton ? (
                <Skeleton height="100px" width="100%" />
              ) : (
                <div className="d-flex flex-row align-items-center gap-3">
                  {(profileImage.preview || formData.logo) && (
                    <Image src={profileImage.preview ? profileImage.preview : `${process.env.S3CDN}/${formData.logo}`} alt={'profile'} width={100} height={100} className="rounded-circle" />
                  )}
                  <div className="w-100">
                    <ImageDragAndDrop
                      htmlFor={'profile-image'}
                      fileType="image"
                      selectedImageSrc={(src: string) => {
                        setProfileImage((prevData) => ({ ...prevData, url: src, cropperVisible: true }));
                      }}
                    />
                  </div>
                </div>
              )}
            </div>
            <div className="col-12 col-md-4 mb-3">
              <div className="fw-medium">{t('cover_photo')}</div>
              <div className="text-muted fs-12">{t('this_will_be_displayed_on_your_cover')}</div>
            </div>
            <div className="col-12 col-md-8 mb-3">
              {skeleton ? (
                <Skeleton height="100px" width="100%" />
              ) : (
                <div className="d-flex flex-row align-items-center gap-3">
                  {(coverImage.preview || formData.contact_picture) && (
                    <Image src={coverImage.preview ? coverImage.preview : `${process.env.S3CDN}/${formData.contact_picture}`} alt={'profile'} width={200} height={110} />
                  )}
                  <div className="w-100">
                    <ImageDragAndDrop
                      htmlFor={'cover-image'}
                      fileType="image"
                      selectedImageSrc={(src: string) => {
                        setCoverImage((prevData) => ({ ...prevData, url: src, cropperVisible: true }));
                      }}
                    />
                  </div>
                </div>
              )}
            </div>
            <div className="col-12 col-md-4 mb-3">
              <div className="fw-medium">{t('address')}</div>
            </div>
            <div className="col-12 col-md-8 mb-3">{skeleton ? <InputSkeleton /> : <Input disabled value={formData.contact_address || ''} />}</div>
          </div>
        </div>
        <div className="row mt-3" id={`${form.profile.store}`}>
          <div className="fw-bold mb-3">{t('bank_account_info')}</div>
          <div className="col-12 col-md-6 mb-3">
            <Label label={t('account_holder_name')} isRequired />
            {skeleton ? (
              <InputSkeleton />
            ) : (
              <Input
                value={formData.account_holder_name || ''}
                className="form-control error-account_holder_name"
                name="account_holder_name"
                onChange={(e) => onFormChange('account_holder_name', e.target.value)}
              />
            )}
          </div>
          <div className="col-12 col-md-6 mb-3">
            <Label label={t('bank_name')} isRequired />
            {skeleton ? (
              <InputSkeleton />
            ) : (
              <Input value={formData.bank_name || ''} className="form-control error-bank_name" name="bank_name" onChange={(e) => onFormChange('bank_name', e.target.value)} />
            )}
          </div>
          <div className="col-12 col-md-6 mb-3">
            <Label label={t('bank_branch')} isRequired />
            {skeleton ? (
              <InputSkeleton />
            ) : (
              <Input value={formData.bank_branch || ''} className="form-control error-bank_branch" name="bank_branch" onChange={(e) => onFormChange('bank_branch', e.target.value)} />
            )}
          </div>
          <div className="col-12 col-md-6 mb-3">
            <Label label={t('account_number')} isRequired />
            {skeleton ? (
              <InputSkeleton />
            ) : (
              <Input value={formData.account_number || ''} className="form-control error-account_number" name="account_number" onChange={(e) => onFormChange('account_number', e.target.value)} />
            )}
          </div>
          <div className="col-12 col-md-6 mb-3">
            <Label label={t('iban_swift_code_for_international_if_needed')} />
            {skeleton ? (
              <InputSkeleton />
            ) : (
              <Input value={formData.iban_swift_code || ''} className="form-control error-iban_swift_code" name="iban_swift_code" onChange={(e) => onFormChange('iban_swift_code', e.target.value)} />
            )}
          </div>
          <div className="col-12 col-md-8 mb-3">
            <Label label={t('passbook_front_page')} isRequired />
            {skeleton ? (
              <Skeleton height="100px" width="100%" />
            ) : (
              <div className="d-flex flex-row align-items-center gap-3">
                {(passbookImage.preview || formData.doc) && (
                  <Image src={passbookImage.preview ? passbookImage.preview : `${process.env.S3CDN}/${formData.doc}`} alt={'PassBook'} width={200} height={110} />
                )}
                <div className="w-100">
                  <ImageDragAndDrop
                    htmlFor={'passbook'}
                    fileType="image"
                    selectedImageSrc={(src: string) => {
                      setPassbookImage((prevData) => ({ ...prevData, url: src, cropperVisible: true }));
                    }}
                  />
                </div>
              </div>
            )}
          </div>
        </div>
        <div className="d-flex justify-content-end gap-2 mt-3 px-5">
          {/* <Button text={t('cancel')} color="light" width="sm" /> */}
          <Button className="d-flex align-items-center gap-1" isLoading={isFormProcessing} onClick={onSubmit} width="sm">
            <Flexicon icon="save-01" variant="line" size={18} />
            <span>{t('save_changes')}</span>
          </Button>
        </div>
      </div>

      <ImageCropper
        key={`profile-image${profileImage.key}`}
        isOpen={profileImage.cropperVisible}
        imageSrc={profileImage.url ? profileImage.url : ''}
        croppedImageSrc={(url: string) => {
          setProfileImage((prevData) => ({ ...prevData, preview: url, cropperVisible: false }));
        }}
        croppedImage={(image: File) => setProfileImage((prevData) => ({ ...prevData, croppedFile: image }))}
      />
      <ImageCropper
        key={`cover-image${coverImage.key}`}
        isOpen={coverImage.cropperVisible}
        imageSrc={coverImage.url ? coverImage.url : ''}
        size={24 / 4}
        croppedImageSrc={(url: string) => {
          setCoverImage((prevData) => ({ ...prevData, preview: url, cropperVisible: false }));
        }}
        croppedImage={(image: File) => setCoverImage((prevData) => ({ ...prevData, croppedFile: image }))}
      />
      <ImageCropper
        key={`passbook-image${passbookImage.key}`}
        isOpen={passbookImage.cropperVisible}
        imageSrc={passbookImage.url ? passbookImage.url : ''}
        size={16 / 9}
        croppedImageSrc={(url: string) => {
          setPassbookImage((prevData) => ({ ...prevData, preview: url, cropperVisible: false }));
        }}
        croppedImage={(image: File) => setPassbookImage((prevData) => ({ ...prevData, croppedFile: image }))}
      />
    </div>
  );
}

export default MyDetails;
