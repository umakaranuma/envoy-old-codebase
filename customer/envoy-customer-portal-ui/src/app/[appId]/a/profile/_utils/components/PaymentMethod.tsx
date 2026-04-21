import { useTrans } from '@/helpers/services/lang/langService';
import React, { useEffect, useState } from 'react';
import AddCardDetails from './AddCardDetails';
import EditCardDetails from './EditCardDetails';
import BillingDetailList from './BillingDetailList';
import { getUserEmailInfo } from '../api-service';

function PaymentMethod() {
  const t = useTrans('label.profile,otr.common');
  // const tBe = useTrans('be.msg,be.error,be.attri');
  const [_formData, setFormData] = useState({
    email_account: '',
    email: '',
    current_email: '',
  });
  const [addCardOpen, setAddCardOpen] = useState(false);
  const [editCardOpen, setEditCardOpen] = useState(false);
  const [_selectedBills, setSelectedBills] = useState([]);
  const [_skeleton, setSkeleton] = useState<boolean>(false);
  // const [_isFormProcessing, setIsFormProcessing] = useState(false);
  const [_selectedFiles, setSelectedFiles] = useState<string[]>([]);
  // const [loading, setLoading] = useState(false);

  const onFormChange = (name: string, value: any) => {
    setFormData((prevFormData) => ({ ...prevFormData, [name]: value }));
  };

  useEffect(() => {
    const fetchData = async () => {
      setSkeleton(true);
      const responseData = await getUserEmailInfo();
      if (responseData?.is_success) {
        onFormChange('email', responseData.result.email);
        onFormChange('current_email', responseData.result.email);
        setSkeleton(false);
      }
    };
    fetchData();
  }, []);

  // async function onSubmit() {
  //   clearError(form.profile.update);
  //   setIsFormProcessing(true);

  //   try {
  //     const responseData = await updateEmailInfo({ email: formData.email });
  //     setIsFormProcessing(false);

  //     if (responseData.status_code === 417) {
  //       printError(responseData.result, form.profile.update, tBe);
  //     }

  //     if (responseData.is_success) {
  //       toaster.success(tBe(responseData.message));
  //     }
  //   } catch (error) {
  //     console.error('An error occurred:', error);
  //   }
  // }

  // const handleDownloadSelectedFiles = async () => {
  //   try {
  //     setLoading(true);
  //     const downloadPromises = selectedFiles.map(async (fileKey) => {
  //       const fileUrl = await fileReceiver({ key: fileKey });
  //       window.open(fileUrl, '_blank');
  //     });
  //     await Promise.all(downloadPromises);
  //     setLoading(false);
  //   } catch (error) {
  //     console.error('Error downloading files:', error);
  //     toaster.error(t('file_download_error'));
  //   }
  // };

  return (
    <div className="mt-2 mt-md-4">
      {/* <div className="border-bottom border-3 pb-2 border-light"> */}
      <div className="fw-bold">{t('payment_record')}</div>
      {/* <div className="text-muted mb-2">{t('update_your_billing_details_and_email_address')}</div> */}
      {/* </div> */}
      {/* <div className="row border-bottom border-3 pb-2 border-light mt-4 mt-md-4">
        <div className="col-12 col-md-8">
          <div className="row ">
            <div className="col-12 col-md-4 mb-3">
              <div className="fw-medium">{t('contact_email')}</div>
              <div className="text-muted">{t('where_should_invoices_be_sent')}</div>
            </div>
            <div className="col-12 col-md-8 d-flex flex-column">
              <div className="d-flex flex-column">
                <div className="d-flex flex-row gap-2 align-items-center">
                  <input type="radio" id="my_email" name="email_account" value="my_email" onChange={(e) => onFormChange('email_account', e.target.value)} />
                  <label htmlFor="my_email" className="fw-medium text-muted">
                    {t('send_to_my_account_email')}
                  </label>
                </div>
                <div className="ms-4" style={{ marginTop: '-5px', marginBottom: '0px' }}>
                  {skeleton ? <Skeleton width={'50%'} height={'10px'} className="mt-1" /> : <Label label={formData.email} />}
                </div>
              </div>

              <div className="d-flex flex-column gap-2" id={`${form.profile.update}`}>
                <div className="d-flex flex-row gap-2">
                  <input type="radio" id="other_email" name="email_account" value="other_email" onChange={(e) => onFormChange('email_account', e.target.value)} />
                  <label htmlFor="other_email" className="fw-medium text-muted">
                    {t('send_to_an_alternative_email')}
                  </label>
                </div>
                {formData.email_account === 'other_email' && (
                  <Input
                    className="flex-grow-1 form-control error-email"
                    placeholder={t('enter_email_address')}
                    value={formData.email}
                    onChange={(e) => onFormChange('email', e.target.value)}
                    name="email"
                  />
                )}
              </div>
            </div>
          </div>
        </div>
      </div> */}
      {/* <div className="row border-bottom border-3 pb-2 border-light mt-4 mt-md-4">
        <div className="col-12 col-md-8">
          <div className="row ">
            <div className="col-12 col-md-4 mb-3">
              <div className="fw-medium">{t('card_details')}</div>
              <div className="text-muted">{t('select_default_payment_method')}</div>
            </div>
            <div className="col-12 col-md-8 d-flex flex-column gap-2">
              {paymentMethods.map((method, index) => (
                <PaymentMethodCard key={index} icon={method.icon} cardNumber={method.cardNumber} expiryDate={method.expiryDate} cardName={method.cardName} onEdit={() => setEditCardOpen(true)} />
              ))}
              <div className="d-flex flex-row gap-2 align-items-center text-muted fw-medium pointer">
                <Flexicon icon="plus" variant="line" size={18} />
                <div onClick={() => setAddCardOpen(true)}>{t('add_new_payment_method')}</div>
              </div>
            </div>
          </div>
        </div>
      </div> */}
      {/* <div className="d-flex justify-content-end gap-2 mt-3">
        <Button className="d-flex align-items-center gap-1" isLoading={isFormProcessing} onClick={() => onSubmit()}>
          <Flexicon icon="save-01" variant="line" size={18} />
          <span>{t('save_changes')}</span>
        </Button>
      </div> */}
      <div>
        {/* <div className="d-flex flex-row align-items-start justify-content-between gap-2">
          <div className="fw-bold">{t('billing_history')}</div>
          {selectedBills.length > 1 && (
            <Button variant="outline" onClick={handleDownloadSelectedFiles} className="d-flex flex-row align-items-center gap-2" isLoading={loading}>
              <Flexicon icon="download-cloud-02" variant="line" size={18} />
              <span>{t('download')}</span>
            </Button>
          )}
        </div> */}
        <BillingDetailList selectedIds={(ids: any) => setSelectedBills(ids)} selectedFiles={(files: any) => setSelectedFiles(files)} />
      </div>
      {addCardOpen && <AddCardDetails isOpen={addCardOpen} onCancel={() => setAddCardOpen(false)} />}
      {editCardOpen && <EditCardDetails isOpen={editCardOpen} onCancel={() => setEditCardOpen(false)} />}
    </div>
  );
}

export default PaymentMethod;

// const paymentMethods = [
//   {
//     icon: (
//       <svg width="33" height="12" viewBox="0 0 33 12" fill="none" xmlns="http://www.w3.org/2000/svg">
//         <path
//           fillRule="evenodd"
//           clipRule="evenodd"
//           d="M8.33406 11.1451H5.58774L3.52833 3.05728C3.43058 2.68524 3.22304 2.35634 2.91774 2.20132C2.15584 1.81176 1.31628 1.50172 0.400391 1.34536V1.03398H4.8245C5.43509 1.03398 5.89303 1.50172 5.96936 2.04495L7.03789 7.87898L9.78287 1.03398H12.4529L8.33406 11.1451ZM13.9794 11.1451H11.3857L13.5214 1.03398H16.1151L13.9794 11.1451ZM19.4707 3.83507C19.547 3.29049 20.0049 2.9791 20.5392 2.9791C21.3788 2.90092 22.2933 3.05729 23.0565 3.4455L23.5145 1.26853C22.7512 0.957146 21.9117 0.800781 21.1498 0.800781C18.6324 0.800781 16.8007 2.20132 16.8007 4.1451C16.8007 5.62383 18.0982 6.40026 19.0141 6.868C20.0049 7.3344 20.3865 7.64578 20.3102 8.11218C20.3102 8.81178 19.547 9.12316 18.7851 9.12316C17.8692 9.12316 16.9533 8.88996 16.1151 8.5004L15.6571 10.6787C16.573 11.0669 17.5639 11.2233 18.4798 11.2233C21.3024 11.3001 23.0565 9.90094 23.0565 7.8008C23.0565 5.15608 19.4707 5.00106 19.4707 3.83507ZM32.1337 11.1451L30.0743 1.03398H27.8623C27.4043 1.03398 26.9464 1.34536 26.7937 1.81176L22.9802 11.1451H25.6502L26.1831 9.66774H29.4637L29.769 11.1451H32.1337ZM28.2439 3.75689L29.0058 7.56761H26.8701L28.2439 3.75689Z"
//           fill="#172B85"
//         />
//       </svg>
//     ),
//     cardNumber: '1234',
//     expiryDate: '12/25',
//     cardName: 'Visa',
//   },
//   {
//     icon: (
//       <svg width="30" height="19" viewBox="0 0 30 19" fill="none" xmlns="http://www.w3.org/2000/svg">
//         <path
//           fillRule="evenodd"
//           clipRule="evenodd"
//           d="M14.9053 16.4396C13.3266 17.7704 11.2787 18.5737 9.04092 18.5737C4.04776 18.5737 0 14.5741 0 9.64036C0 4.70662 4.04776 0.707031 9.04092 0.707031C11.2787 0.707031 13.3266 1.51036 14.9053 2.84109C16.484 1.51036 18.5319 0.707031 20.7697 0.707031C25.7628 0.707031 29.8106 4.70662 29.8106 9.64036C29.8106 14.5741 25.7628 18.5737 20.7697 18.5737C18.5319 18.5737 16.484 17.7704 14.9053 16.4396Z"
//           fill="#ED0006"
//         />
//         <path
//           fillRule="evenodd"
//           clipRule="evenodd"
//           d="M14.9053 16.4396C16.8492 14.8011 18.0818 12.363 18.0818 9.64036C18.0818 6.91776 16.8492 4.47962 14.9053 2.84108C16.484 1.51036 18.5319 0.707031 20.7697 0.707031C25.7628 0.707031 29.8106 4.70662 29.8106 9.64036C29.8106 14.5741 25.7628 18.5737 20.7697 18.5737C18.5319 18.5737 16.484 17.7704 14.9053 16.4396Z"
//           fill="#F9A000"
//         />
//         <path
//           fillRule="evenodd"
//           clipRule="evenodd"
//           d="M14.905 16.4403C16.8489 14.8018 18.0815 12.3636 18.0815 9.64105C18.0815 6.91846 16.8489 4.48033 14.905 2.8418C12.9611 4.48033 11.7285 6.91846 11.7285 9.64105C11.7285 12.3636 12.9611 14.8018 14.905 16.4403Z"
//           fill="#FF5E00"
//         />
//       </svg>
//     ),
//     cardNumber: '5678',
//     expiryDate: '11/24',
//     cardName: 'MasterCard',
//   },
// ];
