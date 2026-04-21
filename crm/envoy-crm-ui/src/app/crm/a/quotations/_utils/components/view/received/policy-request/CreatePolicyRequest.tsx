'use client';
import { useTrans } from '@/helpers/services/lang/langService';
import { Button, Input, Label, Skeleton } from '@apptimus-ui/ui-element';
import React, { useEffect, useRef, useState } from 'react';
import { Modal, ModalBody, ModalFooter, ModalHeader } from '@apptimus-ui/modal';
import { form } from '@/constans/Form';
import { getOneReceivedQuotation, getPolicyRiskInfoFile } from '../../../../api-service';
import { initPolicyRequestForm } from '../../../../model';
import { AsyncSelect } from '@apptimus-ui/select';
import { fetchAllPaymentTypes, fetchAllProductsByType } from '../../../../service';
import ProductDocuments from './ProductDocuments';
import { clearError, printError } from '@/helpers/handlers/validationErrorHandler';
import { createPolicyRequest } from '../../../../policy-api-service';
import { toaster } from '@/helpers/services/toaster';

function CreatePolicyRequest({
  isOpen,
  onCancel,
  setEmailData,
  quotationId,
  cusId,
  leadId,
  insurerProductName,
  insurerProductId,
  serviceProviderId,
  nativeProductId,
}: {
  isOpen: boolean;
  onCancel: Function;
  setEmailData: Function;
  quotationId: string;
  cusId: number | null;
  leadId: string | null;
  insurerProductName: string;
  insurerProductId: string;
  serviceProviderId: string;
  nativeProductId: string;
}) {
  const t = useTrans('label.policy_request,otr.common');
  const tBe = useTrans('be.msg,be.error,be.attri');
  const [formData, setFormData] = useState(initPolicyRequestForm);
  const [isFormProcessing, setIsFormProcessing] = useState(false);
  // const user = getLocalStorage(local_storage.auth_user_info);
  const productDocRef = useRef<{ onSubmit: () => Promise<any> | null }>(null);
  const [skeleton, setSkeleton] = useState(false);
  const [error, setError] = useState('');
  // console.log('formData:', formData);

  console.log('data:', { insurerProductName, insurerProductId, serviceProviderId });

  const onFormChange = (name: string, value: any) => {
    setFormData((prevFormData: any) => ({ ...prevFormData, [name]: value }));
  };

  useEffect(() => {
    const fetchData = async () => {
      const responseData = await getOneReceivedQuotation(quotationId);
      if (responseData?.is_success) {
        const data = responseData.result;
        const risk_type_id = data.opportunity_type ? data.opportunity_type.map((riskType: any) => riskType.id) : [];
        onFormChange('coverage_details_name', data.coverage_details_name);
        onFormChange('premium_amount', data.total_amount);
        onFormChange('coverage_details', data.coverage_details);
        onFormChange('quotation_code', data.code);
        onFormChange('quotation_id', data.vendor_quotation_id);
        onFormChange('quotation_expiry_date', data.expiry_date);
        onFormChange('quotation_issued_date', data.received_date);

        onFormChange('risk_type_ids', risk_type_id);
        onFormChange('insurer_name', data.service_provider_name);
        onFormChange('insurer_id', data.service_provider_id);

        onFormChange('request_by_id', data.by_user_id);
        onFormChange('request_by_name', data.by_user_name);
        onFormChange('sales_agent_id', data.sales_agent_id);
        onFormChange('sum_insured', data.total_amount);

        const grouped = data.risks?.reduce((acc: Record<string, number[]>, item: any) => {
          const typeId = item.risk_type.id;
          if (!acc[typeId]) {
            acc[typeId] = [];
          }
          acc[typeId].push(item.risk_id);
          return acc;
        }, {});

        onFormChange('risk_ids', grouped);
        setSkeleton(false);
      }
    };

    if (quotationId) {
      setSkeleton(true);
      fetchData();
      onFormChange('customer_id', cusId);
      onFormChange('product_name', insurerProductName);
      onFormChange('product_id', insurerProductId);
      onFormChange('service_provider_id', serviceProviderId);
    }
  }, [quotationId]);

  async function onSubmit() {
    clearError(form.policy_request.store);
    setError('');
    setIsFormProcessing(true);
    const productDocuments = await handleDocumentSubmit();
    let refinedEmailDocuments;
    if (productDocuments) {
      const emailDocuments = Object.values(productDocuments);
      refinedEmailDocuments = emailDocuments.length ? emailDocuments : [];
    }

    try {
      const responseData = await createPolicyRequest({
        ...formData,
        product_type: formData.risk_type_ids.length === 1 ? 'product' : 'group',
        is_policy: false,
        product_ids: [formData.product_id],
        values: productDocuments,
        lead_id: leadId,
      });

      setIsFormProcessing(false);

      if (responseData.system_code === 'validation_error') {
        setError(responseData.message);
        return;
      }

      if (responseData.system_code === 'NO_RISK_VALIDATION') {
        setError(responseData.message);
      }

      if (responseData.status_code === 417) {
        printError(responseData.result, form.policy_request.store, tBe);
      }

      if (responseData.is_success) {
        // toaster.success(tBe(responseData.message));
        // setEmailData({
        //   entity_id: responseData.result?.entity_id,
        //   policy_request_id: responseData.result?.policy_request_id,
        //   insurer: formData.insurer_name,
        //   documents: refinedEmailDocuments ?? [],
        // });
        // onCancel();
        const response = await getPolicyRiskInfoFile(responseData.result.policy_base_id);
        let document;

        document = refinedEmailDocuments ?? [];
        if (response?.is_success) {
          document = [...document, { doc: response.result.file_key, name: response.result.file_name }];
        }

        toaster.success(tBe(responseData.message));
        setEmailData({
          entity_id: responseData.result?.entity_id,
          policy_request_id: responseData.result?.policy_request_id,
          insurer: formData.insurer_name,
          documents: document,
        });
        onCancel();
      } else {
        toaster.error(tBe(responseData.message));
      }
    } catch (error) {
      console.error('An error occurred:', error);
    }
  }

  const handleDocumentSubmit = async () => {
    if (productDocRef.current) {
      const result = await productDocRef.current.onSubmit();
      if (result) {
        return result;
      } else {
        return null;
      }
    }
  };

  return (
    <Modal isOpen={isOpen} size="lg" scrollable>
      <ModalHeader title={t('add_new_entity', { entity: t('policy_request') })} onClose={() => onCancel()} />
      <ModalBody>
        {skeleton ? (
          <Skeleton width="100%" height="200px" />
        ) : (
          <div className="row" id={`${form.policy_request.store}`}>
            <div className="panel">
              <div className="panel-title mb-3">{t('product_information')}</div>
              <div className="row">
                {formData.risk_type_ids.length > 0 && (
                  <div className="col-12 col-md-6 mb-3 custom-select" key={`product-${formData.risk_type_ids}`}>
                    <Label htmlFor="product_name" label={t('product_name')} isRequired />
                    <AsyncSelect
                      onChange={(_value, data) => {
                        //onFormChange('product_type', formData.risk_type_ids.length === 1 ? 'product' : 'group');
                        onFormChange('product_id', data.id), onFormChange('product_name', data.name);
                      }}
                      className="form-control error-product_id"
                      option={{ label: 'name', value: 'id' }}
                      defaultValue={{ name: formData.product_name, id: formData.product_id }}
                      isSearchable={true}
                      loadOptions={(searchValue: any, currentPage: any) => fetchAllProductsByType(searchValue, currentPage, formData.risk_type_ids, formData.service_provider_id, nativeProductId)}
                    />
                  </div>
                )}
                {/* <div className="col-12 col-md-3 mb-3">
                  <Input
                    label={t('sum_insured')}
                    value={formData.sum_insured}
                    type="number"
                    onChange={(e) => onFormChange('sum_insured', e.target.value)}
                    className="form-control error-sum_insured"
                    name="sum_insured"
                    isRequired
                  />
                </div>
                <div className="col-12 col-md-3 mb-3 custom-select">
                  <Label htmlFor="product_name" label={t('coverages')} isRequired />
                  <AsyncSelect
                    onChange={(_value, data) => {
                      onFormChange('coverage_type_id', data.id), onFormChange('coverage_type_name', data.name);
                    }}
                    className="form-control error-coverage_type_id"
                    option={{ label: 'name', value: 'id' }}
                    isSearchable={true}
                    defaultValue={{ name: formData.coverage_type_name, id: formData.coverage_type_id }}
                    loadOptions={(searchValue: any, currentPage: any) => fetchAllCoverages(searchValue, currentPage)}
                  />
                </div> */}
                <div className="col-12 col-md-6 mb-3">
                  <Input
                    label={t('policy_period_from_date')}
                    value={formData.policy_start_date}
                    onChange={(e) => onFormChange('policy_start_date', e.target.value)}
                    className="form-control error-policy_start_date"
                    name="policy_start_date"
                    isRequired
                    type="date"
                    min={formData.quotation_issued_date}
                  />
                </div>
                <div className="col-12 col-md-6 mb-3">
                  <Input
                    label={t('policy_period_to_date')}
                    value={formData.policy_expiry_date}
                    onChange={(e) => onFormChange('policy_expiry_date', e.target.value)}
                    className="form-control error-policy_expiry_date"
                    name="policy_expiry_date"
                    isRequired
                    type="date"
                    min={formData.policy_start_date}
                  />
                </div>
                <div className="col-12 col-md-6 mb-3 custom-select custom-dropdown">
                  <Label htmlFor="product_name" label={t('payment_mode')} />
                  <AsyncSelect
                    onChange={(_value, data) => {
                      onFormChange('payment_mode_id', data.id), onFormChange('payment_mode_name', data.name);
                    }}
                    className="form-control error-payment_mode_id"
                    option={{ label: 'name', value: 'id' }}
                    defaultValue={{ name: formData.payment_mode_name, id: formData.payment_mode_id }}
                    isSearchable={true}
                    loadOptions={(searchValue: any, currentPage: any) => fetchAllPaymentTypes(searchValue, currentPage)}
                  />
                </div>
                {/* <div className="col-12 col-md-3 mb-3 custom-select">
                  <Label label={t('sales_agent')} />
                  <AsyncSelect
                    onChange={(_value, data) => {
                      onFormChange('sales_agent_id', data.id), onFormChange('sales_agent_name', data.display_name);
                    }}
                    className="form-control error-sales_agent_id"
                    option={{ label: 'display_name', value: 'id' }}
                    isSearchable={true}
                    loadOptions={(searchValue: any, currentPage: any) => fetchAllUsers(searchValue, currentPage)}
                    defaultValue={{ display_name: formData.sales_agent_name, id: formData.sales_agent_id }}
                  />
                </div> */}
              </div>
            </div>
            {/* <div className="panel">
                            <div className="panel-title mb-3">{t('insurer_info')}</div>
                            <div className="row">
                                <div className="col-12 col-md-3 mb-3 custom-select">
                                    <Label htmlFor="requested_by" label={t('requested_by')} isRequired />
                                    <AsyncSelect
                                        onChange={(_value: any, data: any) => {
                                            onFormChange('request_by_id', data.id), onFormChange('request_by_name', data.display_name);
                                        }}
                                        className="form-control error-request_by_id"
                                        option={{ label: 'display_name', value: 'id' }}
                                        defaultValue={{ display_name: formData.request_by_name, id: formData.request_by_id }}
                                        isSearchable={true}
                                        loadOptions={(searchValue, currentPage) => fetchAllUsers(searchValue, currentPage)}
                                    />
                                </div>
                                <div className="col-12 col-md-3 mb-3 custom-select">
                                    <Label label={t('sales_agent')} />
                                    <AsyncSelect
                                        onChange={(_value, data) => {
                                            onFormChange('sales_agent_id', data.id), onFormChange('sales_agent_name', data.display_name);
                                        }}
                                        className="form-control error-sales_agent_id"
                                        option={{ label: 'display_name', value: 'id' }}
                                        isSearchable={true}
                                        loadOptions={(searchValue: any, currentPage: any) => fetchAllUsers(searchValue, currentPage)}
                                        defaultValue={{ display_name: formData.sales_agent_name, id: formData.sales_agent_id }}
                                    />
                                </div>
                            </div>
                        </div> */}
            {formData.product_id && (
              <div className="panel">
                <ProductDocuments productId={formData.product_id} productType={formData.product_type} key={formData.product_id} ref={productDocRef} />
              </div>
            )}
            {error && <strong className="text-danger fs-13">{tBe(error)}</strong>}
          </div>
        )}
      </ModalBody>
      <ModalFooter>
        <div className="d-flex justify-content-end gap-2">
          <Button text={t('create')} onClick={onSubmit} width="sm" isLoading={isFormProcessing} />
          <Button text={t('cancel')} color="light" width="sm" onClick={() => onCancel()} />
        </div>
      </ModalFooter>
    </Modal>
  );
}

export default CreatePolicyRequest;
