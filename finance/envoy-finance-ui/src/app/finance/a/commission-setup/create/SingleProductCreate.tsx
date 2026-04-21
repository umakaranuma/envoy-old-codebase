'use client';
import { useTrans } from '@/helpers/services/lang/langService';
import React, { useState, FormEvent, useEffect } from 'react';
import { Button, Input, Label } from '@apptimus-ui/ui-element';
import { AsyncSelect } from '@apptimus-ui/select';
import { useRouter } from 'next/navigation';
import { fetchAllProductsData, fetchAllTransationTypeData } from '../_utils/services';
import { CommissionSetupFormData, IFormData, ICommon, initCommissionData } from '../_utils/model';
import { form } from '@/constans/Form';
import InsurerProductsList from './InsurerProductsList';
import { clearError, printError } from '@/helpers/handlers/validationErrorHandler';
import RevisedCommission from './RevisedCommission';
import { createCommissionSetup } from '../_utils/api-service';
import { toaster } from '@/helpers/services/toaster';
import InsurerProductWithTeamList from './InsurerProductWithTeamList';
import AddCommison from './AddCommison';
import NativeTeamsList from './NativeTeamsList';

export default function SingleProductCreate({ currentPg, setcurrentPg }: { currentPg: string; setcurrentPg: Function }) {
  const t = useTrans('label.commission_setup,label.mapping_data_table_preview,otr.common');
  const tBe = useTrans('be.msg,be.error,be.attri');
  const router = useRouter();
  const [isFormProcessing, setIsFormProcessing] = useState(false);
  const [uiFormData, setUIFormData] = useState<ICommon>(initCommissionData);
  const [defaultNativeProduct, setDefaultNativeProduct] = useState({ id: '', name: '' });
  const [salesTeamIds, setSalesTeamIds] = useState<string[]>([]);
  const [error, setError] = useState('');
  const [selectedInsurerProductData, setSelectedInsurerProductData] = useState<any[]>([]);
  const [insurerTableKey, setinsurerTableKey] = useState(0);
  const [iProductTableVers, setIProductTableVers] = useState(0);
  const [isAddCommissionVisible, setIsAddCommissionVisible] = useState(false);
  const [isRCommissionEditVisible, setIsRCommissionEditVisible] = useState(false);
  const [currentTeamId, setCurrentTeamId] = useState('');
  const [currentTeamMemberId, setCurrentTeamMemberId] = useState('');
  const [currentIProductId, setCurrentIProductId] = useState('');
  const [teamUserTableVers, setTeamUserTableVers] = useState(0);
  const [formData, setFormData] = useState<IFormData[]>([]);
  const [currenttab, setCurrentTab] = useState('first');
  const [defaultTeamIds, setDefaultTeamIds] = useState<string[]>([]);

  useEffect(() => {
    setCurrentTab(currentPg);
    console.log('currentPg', setcurrentPg);
  }, [currentPg]);

  useEffect(() => {
    setError('');
  }, [selectedInsurerProductData]);

  // useEffect(() => {
  //   setSelectedInsurerProductData([]);
  // }, [defaultNativeProduct]);

  // useEffect(() => {
  //   setSelectedInsurerProductData([]);
  //   setinsurerTableKey((pre) => pre + 1);
  // }, [defaultNativeProduct]);

  useEffect(() => {
    console.log('selectedInsurerProductData', selectedInsurerProductData);
  }, [selectedInsurerProductData]);

  useEffect(() => {
    if (formData.length > 0) {
      const selectedData = formData.map((product: any) => ({
        id: product.id,
        vendor_id: product.vendor_id,
        product_name: product.name,
        transaction_type: uiFormData.transaction_type,
        transaction_id: uiFormData.transaction_id,
        commission_type: uiFormData.commission_type,
        commission_value: uiFormData.commission_value,
        brokerage_commission_value: uiFormData.brokerage_commission_value,
        brokerage_commission_type: uiFormData.brokerage_commission_type,
        revised_commission_percent: product.revised_commission_percent || [],
      }));

      // Only update if the data actually changed
      const hasChanged = selectedData.some((item, index) => {
        const original = formData[index];
        return (
          item.transaction_type !== original.transaction_type ||
          item.transaction_id !== original.transaction_id ||
          item.commission_type !== original.commission_type ||
          item.commission_value !== original.commission_value ||
          item.brokerage_commission_value !== original.brokerage_commission_value ||
          item.brokerage_commission_type !== original.brokerage_commission_type
        );
      });

      if (hasChanged) {
        setFormData(selectedData);
      }
    }
  }, [uiFormData.transaction_type, uiFormData.transaction_id, uiFormData.commission_type, uiFormData.commission_value, uiFormData.brokerage_commission_value, uiFormData.brokerage_commission_type]);

  const handleNextPage = (e: React.MouseEvent) => {
    e.preventDefault();
    clearError(form.commission_setup_crud.store);
    setError('');

    // Validate commission data
    const commissionErrors: { [key: string]: Array<{ error_type: string; tokens: { _attribute: string } }> } = {};

    // Validate commission_value based on commission_type
    if (uiFormData.commission_type === 'fixed' && !uiFormData.commission_value) {
      commissionErrors['commission_value'] = [
        {
          error_type: 'required',
          tokens: { _attribute: 'commission_value' },
        },
      ];
    }

    // Validate brokerage_commission_value based on brokerage_commission_type
    if (uiFormData.brokerage_commission_type === 'fixed' && !uiFormData.brokerage_commission_value) {
      commissionErrors['brokerage_commission_value'] = [
        {
          error_type: 'required',
          tokens: { _attribute: 'brokerage_commission_value' },
        },
      ];
    }

    // Validate transaction_type
    if (!uiFormData.transaction_type) {
      commissionErrors['transaction_type'] = [
        {
          error_type: 'required',
          tokens: { _attribute: 'transaction_type' },
        },
      ];
    }

    // Validate native product
    if (!defaultNativeProduct.id) {
      commissionErrors['product_name'] = [
        {
          error_type: 'required',
          tokens: { _attribute: 'product_name' },
        },
      ];
    }

    // If there are commission errors
    if (Object.keys(commissionErrors).length > 0) {
      printError(commissionErrors, form.commission_setup_crud.store, tBe);
      return;
    }
    console.log('selectedInsurerProductData', selectedInsurerProductData);

    // Validate insurer products
    if (selectedInsurerProductData.length === 0) {
      setError(t('select_at_least_one_insurer_product'));
      return;
    }

    // All validations passed - proceed to next tab
    setCurrentTab('third');
  };

  const onFormChange = (name: string, value: any) => {
    setUIFormData((prevFormData) => ({ ...prevFormData, [name]: value }));
  };

  const prepareApiData = (inputData: IFormData[]): CommissionSetupFormData[] => {
    return inputData.map((item) => ({
      product_id: item.id.toString(),
      insurer_id: item.vendor_id || '',
      native_product_id: defaultNativeProduct.id.toString(),
      transaction_type: item.transaction_id,
      sales_team_ids: salesTeamIds.length > 0 ? salesTeamIds.map((id) => id.toString()) : defaultTeamIds,
      brokerage_revenue_percent: [
        {
          value: parseFloat(item.brokerage_commission_value) || 0,
          type: item.brokerage_commission_type,
        },
      ],
      agent_commission_percent: [
        {
          value: parseFloat(item.commission_value) || 0,
          type: item.commission_type,
        },
      ],
      revised_commission_percent: item.revised_commission_percent.map((rc) => ({
        team_id: rc.team_id.toString(),
        user_id: rc.user_id.toString(),
        value: rc.value.toString() || '0',
        type: rc.type,
      })),
      commission_percent: [],
    }));
  };

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    clearError(form.commission_setup_crud.store);
    const apiData = prepareApiData(formData);
    setIsFormProcessing(true);
    try {
      const responseData = await createCommissionSetup(apiData);
      if (responseData.status_code === 417) {
        toaster.error(tBe(responseData.result.message));
        printError(responseData.result, form.commission_setup_crud.store, tBe);
      }

      if (responseData.is_success) {
        toaster.success(tBe(responseData.message));
        router.push('/finance/a/commission-setup');
      }
    } catch (error) {
      console.error('An error occurred:', error);
    } finally {
      setIsFormProcessing(false);
    }
  }

  return (
    <div>
      <form onSubmit={onSubmit} id={`${form.commission_setup_crud.store}`}>
        <div className="card p-4">
          {currenttab === 'second' && (
            <div className="row p-2">
              <div className="col-12 col-md-6 mb-3">
                <div className="custom-select">
                  <Label htmlFor="product_name" label={t('product_name')} isRequired />
                  <AsyncSelect
                    defaultValue={defaultNativeProduct}
                    onChange={(value, data) => {
                      onFormChange('product_name', value);
                      setinsurerTableKey((pre) => pre + 1);
                      setSelectedInsurerProductData([]);
                      setDefaultNativeProduct({ id: data.id, name: data.name });
                      const team_ids = data.teams?.map((team: { team_id: number }) => team.team_id);
                      setSalesTeamIds(team_ids || []);
                      setDefaultTeamIds(team_ids || []);
                    }}
                    className="form-control error-product_name"
                    loadOptions={fetchAllProductsData}
                  />
                </div>
              </div>
              <div className="col-12 col-md-6 mb-3">
                <div className="custom-select">
                  <Label htmlFor="transaction_type" label={t('transaction_type')} isRequired />
                  <AsyncSelect
                    defaultValue={uiFormData.transaction_type ? { id: uiFormData.transaction_id, name: uiFormData.transaction_type } : undefined}
                    onChange={(_, data) => {
                      onFormChange('transaction_type', data.name), onFormChange('transaction_id', data.id);
                    }}
                    className="form-control error-transaction_type"
                    loadOptions={fetchAllTransationTypeData}
                    option={{
                      value: 'id',
                      label: 'name',
                    }}
                  />
                </div>
              </div>
              {/* Brokerage Commission Section */}
              <div className="col-12 col-md-6 my-3">
                <div className="row">
                  <div className="col-12 col-md-6 mb-3">
                    <Label htmlFor="brokerage_commission_type" label={t('commission_type')} />
                    <div className="mb-3 d-flex flex-row gap-2 align-items-center">
                      <input
                        type="radio"
                        id="fixed"
                        name="percentage_method"
                        value="fixed"
                        className="mb-2"
                        onChange={(e) => onFormChange('brokerage_commission_type', e.target.value)}
                        defaultChecked={uiFormData.brokerage_commission_type === 'fixed'}
                      />
                      <Label htmlFor="fixed" label={t('fixed')} />
                      <input
                        type="radio"
                        id="percentage"
                        name="percentage_method"
                        value="percentage"
                        className="mb-2"
                        onChange={(e) => onFormChange('brokerage_commission_type', e.target.value)}
                        defaultChecked={uiFormData.brokerage_commission_type === 'percentage'}
                      />
                      <Label htmlFor="percentage" label={t('percentage')} />
                    </div>
                  </div>
                  <div className="col-12 col-md-6">
                    <Input
                      label={t('brokerage_revenue')}
                      value={uiFormData.brokerage_commission_value}
                      onChange={(e) => onFormChange('brokerage_commission_value', e.target.value)}
                      className="form-control error-brokerage_commission_value"
                      name="brokerage_commission_value"
                      type="number"
                      isRequired
                    />
                  </div>
                </div>
              </div>
              {/* Agent Commission Section */}
              <div className="col-12 col-md-6 my-3">
                <div className="row">
                  <div className="col-12 col-md-6 mb-3">
                    <Label htmlFor="commission_type" label={t('commission_type')} />
                    <div className="mb-3 d-flex flex-row gap-2 align-items-center">
                      <input
                        type="radio"
                        id="a_fixed"
                        name="a_percentage_method"
                        value="fixed"
                        className="mb-2"
                        onChange={(e) => onFormChange('commission_type', e.target.value)}
                        defaultChecked={uiFormData.commission_type === 'fixed'}
                      />
                      <Label htmlFor="a_fixed" label={t('fixed')} />
                      <input
                        type="radio"
                        id="a_percentage"
                        name="a_percentage_method"
                        value="percentage"
                        className="mb-2"
                        onChange={(e) => onFormChange('commission_type', e.target.value)}
                        defaultChecked={uiFormData.commission_type === 'percentage'}
                      />
                      <Label htmlFor="a_percentage" label={t('percentage')} />
                    </div>
                  </div>
                  <div className="col-12 col-md-6">
                    <Input
                      label={t('agent_commission')}
                      value={uiFormData.commission_value}
                      onChange={(e) => onFormChange('commission_value', e.target.value)}
                      className="form-control error-commission_value"
                      name="commission_value"
                      type="number"
                      isRequired
                    />
                  </div>
                </div>
              </div>
            </div>
          )}

          {defaultNativeProduct.id !== '' && currenttab === 'second' && (
            <>
              <div className="panel-title">{t('insurer_products')}</div>
              {error && <div className="err-msg">{error}</div>}
              <InsurerProductsList
                selectedInsurerProductData={selectedInsurerProductData}
                uiFormData={uiFormData}
                nativeProductId={defaultNativeProduct.id}
                tableVers={insurerTableKey}
                setSelectedInsurerProductData={setSelectedInsurerProductData}
                setFormData={setFormData}
                key={insurerTableKey}
              />
              {selectedInsurerProductData.length > 0 && (
                <>
                  <div className="panel-title">{t('teams')}</div>
                  <NativeTeamsList
                    nativeProductId={defaultNativeProduct.id}
                    tableVers={0}
                    setIsRCommissionEditVisible={setIsRCommissionEditVisible}
                    setCurrentTeamMemberId={setCurrentTeamMemberId}
                    setCurrentTeamId={setCurrentTeamId}
                    currentIProductId={selectedInsurerProductData[0]?.id || ''}
                    setCurrentIProductId={setCurrentIProductId}
                    formData={formData}
                    teamUserTableVers={teamUserTableVers}
                    salesTeamIds={salesTeamIds?.map((id) => ({ id })) || []}
                    setSalesTeamIds={setSalesTeamIds}
                  />
                </>
              )}
            </>
          )}

          {currenttab === 'third' && (
            <div className="" key={iProductTableVers}>
              <div className="panel-title mb-2">{defaultNativeProduct.name}</div>
              <InsurerProductWithTeamList
                formData={formData}
                // nativeProductId={defaultNativeProduct.id}
                selectedInsurerProductData={selectedInsurerProductData}
                // setCurrentTeamId={setCurrentTeamId}
                // setCurrentTeamMemberId={setCurrentTeamMemberId}
                // setIsRCommissionEditVisible={setIsRCommissionEditVisible}
                setIsAddCommissionVisible={setIsAddCommissionVisible}
                setCurrentIProductId={setCurrentIProductId}
                // teamUserTableVers={teamUserTableVers}
                // salesTeamIds={salesTeamIds}
                // setSalesTeamIds={setSalesTeamIds}
              />
            </div>
          )}

          <div className="d-flex gap-2 justify-content-end mt-4">
            {/* <Button
              text={t('close')}
              color="light"
              width="sm"
              onClick={() => {
                router.push('/finance/a/commission-setup');
                // if (currenttab === 'third') {
                //   setCurrentTab('second');
                // } else if (currenttab === 'second') {
                //   setcurrentPg('first');
                // }
              }}
            /> */}
            {currenttab === 'second' ? (
              <Button text={t('next')} type="button" width="sm" onClick={(e) => handleNextPage(e)} />
            ) : (
              <Button text={t('create')} type="submit" width="sm" isLoading={isFormProcessing} />
            )}
          </div>
        </div>
      </form>

      {isAddCommissionVisible && (
        <AddCommison
          isOpen={isAddCommissionVisible}
          onCancel={() => {
            setIsAddCommissionVisible(false);
          }}
          currentIProductId={currentIProductId}
          initialData={formData.find((item) => item.id === currentIProductId) as IFormData}
          setFormData={setFormData}
          afterEdit={() => {
            setIProductTableVers((pre) => pre + 1);
          }}
        />
      )}
      <RevisedCommission
        isOpen={isRCommissionEditVisible}
        onCancel={() => {
          setIsRCommissionEditVisible(false);
        }}
        uiFormData={formData.find((item) => item.id === currentIProductId) as IFormData}
        currentTeamMemberId={currentTeamMemberId}
        currentTeamId={currentTeamId}
        currentIProductId={currentIProductId}
        setFormData={setFormData}
        formData={formData}
        setTeamUserTableVers={setTeamUserTableVers}
      />
    </div>
  );
}
