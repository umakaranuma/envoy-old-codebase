import { form } from '@/constans/Form';
import { clearError } from '@/helpers/handlers/validationErrorHandler';
import { useTrans } from '@/helpers/services/lang/langService';
import { Flexicon } from '@apptimus-ui/flexicon';
import { Button, Skeleton } from '@apptimus-ui/ui-element';
import React, { useEffect, useState } from 'react';
import { getTermsAndPolicyInfo } from '../../../../api-service';
import { ITermsAndConditions } from '../../../../model';
import { fileReceiver } from '@/helpers/services/storageService';

function TermsAndCondition({ setToggleTab, requestId }: { setToggleTab: Function; requestId: string }) {
  const t = useTrans('label.my_policy,otr.common');
  type Term = { vendor_product_name: string; agree: boolean };
  type FormData = { privacy: boolean; confirmAll: boolean; terms: Term[] };
  const [formData, setFormData] = useState<FormData>({ privacy: false, confirmAll: false, terms: [] });
  const [terms, setTerms] = useState<ITermsAndConditions[]>();
  const [isFormProcessing, setIsFormProcessing] = useState(false);
  const [skeleton, setSkeleton] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchData = async () => {
      const responseData = await getTermsAndPolicyInfo(requestId as string);
      if (responseData?.is_success) {
        setTerms(responseData.result);
        const products = responseData.result.map((term: any) => ({ vendor_product_name: term.vendor_product_name, agree: false }));
        setFormData(() => ({ ...formData, terms: products }));
        setSkeleton(false);
      }

      if (responseData.status_code === 404) {
        setSkeleton(false);
      }
    };
    if (requestId) {
      setSkeleton(true);
      fetchData();
    }
  }, [requestId]);

  const onFormChange = (name: string, value: any) => {
    setFormData((prevFormData) => ({ ...prevFormData, [name]: value }));
  };

  async function onSubmit() {
    clearError(form.issued_crud.store);
    setIsFormProcessing(true);

    if (!formData.privacy) {
      setError('Please accept the privacy policy');
      setIsFormProcessing(false);
      return;
    }
    if (formData.terms.some((term: any) => term.agree === false)) {
      setError('Please accept all terms and conditions');
      setIsFormProcessing(false);
      return;
    }
    if (!formData.confirmAll) {
      setError('Please confirm the accuracy of the provided information');
      setIsFormProcessing(false);
      return;
    }
    setIsFormProcessing(false);
    setToggleTab('review_and_submit');
  }

  const handleOpenFile = async (key: string) => {
    const file = await fileReceiver({ key });
    window.open(file);
  };

  const handleCheckTerms = (e: React.ChangeEvent<HTMLInputElement>, vendorProductName: string) => {
    const updatedTerms = formData.terms.map((term) => (term.vendor_product_name === vendorProductName ? { ...term, agree: e.target.checked } : term));
    setFormData({ ...formData, terms: updatedTerms });
    setError('');
  };

  useEffect(() => {
    console.log('Form Data Updated:', formData);
  }, [formData]);

  return (
    <>
      <div className="mb-4">
        <form onSubmit={onSubmit} id={`${form.terms_and_conditions.store}`}>
          <div className="panel-title">{t('policy_terms_and_conditions')}</div>
          {skeleton ? (
            <Skeleton height="200px" width="100%" />
          ) : (
            <div className="row">
              {terms &&
                terms.length > 0 &&
                terms.map((term, index) => (
                  <div key={index}>
                    <div className="fw-medium fs-15 mb-3">{term.vendor_product_name}</div>
                    <div className="d-flex flex-row gap-3 mb-3 align-items-center">
                      <input type="checkbox" onChange={(e) => handleCheckTerms(e, term.vendor_product_name)} />
                      <div>
                        {t('i_have_read_and_agree_to_the')}{' '}
                        <span className="text-primary clickable-text" onClick={() => handleOpenFile(term.documents[0].doc)}>
                          {t('terms_and_condition')}
                        </span>
                      </div>
                    </div>
                  </div>
                ))}
              <div className="d-flex flex-row gap-3 mb-3 align-items-center mt-2">
                <input
                  type="checkbox"
                  onChange={(e) => {
                    onFormChange('privacy', e.target.checked), setError('');
                  }}
                />
                <div>
                  {t('i_accept_the_use_of_cookies_in_accordance_with_the')} <span className="text-primary clickable-text">{t('privacy_policy_version_history')}</span>
                </div>
              </div>
              <div className="d-flex flex-row gap-3 mb-3 align-items-center">
                <input
                  type="checkbox"
                  onChange={(e) => {
                    onFormChange('confirmAll', e.target.checked), setError('');
                  }}
                />
                <div>{t('i_confirm_the_accuracy_of_the_provided_information')}</div>
              </div>
            </div>
          )}
        </form>
        {error && (
          <span className="fw-medium" style={{ color: '#DC3545' }}>
            {error}
          </span>
        )}
      </div>
      <div className="d-flex justify-content-start gap-2 mt-3">
        <Button color="light" className="d-flex align-items-center gap-1" onClick={() => setToggleTab('supporting_documents')}>
          <Flexicon icon="chevron-left" variant="line" size={18} />
          <span className="d-none d-sm-inline">{t('back')}</span>
        </Button>
        {/* <Button color="primary" className="d-flex align-items-center gap-1" type="submit" onClick={() => setToggleTab('terms_and_conditions')} isLoading={isFormProcessing}>
                    <span className="d-none d-sm-inline">{t('next')}</span>
                    <Flexicon icon="chevron-right" variant="line" size={18} />
                </Button> */}
        <Button color="primary" className="d-flex align-items-center gap-1" type="submit" onClick={onSubmit} isLoading={isFormProcessing}>
          <span className="d-none d-sm-inline">{t('next')}</span>
          <Flexicon icon="chevron-right" variant="line" size={18} />
        </Button>
        {/* <Button text={t('update')} type="submit" width="sm" isLoading={undefined} disabled={skeleton} />
                     <Button text={t('cancel')} color="light" width="sm" /> */}
      </div>
    </>
  );
}

export default TermsAndCondition;
