'use client';
import React, { useEffect, useState } from 'react';
import { useTrans } from '@/helpers/services/lang/langService';
import { Button, Input, Label, Skeleton } from '@apptimus-ui/ui-element';
import { AsyncSelect } from '@apptimus-ui/select';
import { fetchAllInsurerData } from '@/app/finance/a/commission-setup/_utils/services';
import { getInsurerCommissionSummaryTotals, settleBrokerageCommission } from '../../api-service';
import GoBack from '@/components/others/page-related/GoBack';
import { useRouter } from 'next/navigation';
import DeductibleTable from './DeductibleTable';
import CommissionCalculatedTable from './CommissionCalculatedTable';
import { toaster } from '@/helpers/services/toaster';
import ConfirmationPop from '@/components/others/page-related/ConfirmationPop';
import { getCurrency } from '@/helpers/services/currencyService';

function BrokerageCommissionCalculation() {
  const t = useTrans('label.commission,otr.common');
  const [formData, setFormData] = useState({
    insurerIds: '',
    startDate: '',
    endDate: '',
    selectedDeductibles: [],
  });
  const [brokerageTotals, setBrokerageTotals] = useState({
    total_commission: 0,
    total_revenue_realized: 0,
    total_overriding_commission: 0,
    total_agent_commission: 0,
  });
  const [tableVers, setTableVers] = useState(0);
  const [deductibleTableVers, setDeductibleTableVers] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const router = useRouter();
  const currency = getCurrency();

  useEffect(() => {
    fetchCommissionTotal();
  }, []);

  useEffect(() => {
    setTableVers((prev) => prev + 1);
  }, [formData.insurerIds, formData.startDate, formData.endDate]);

  const fetchCommissionTotal = async () => {
    try {
      const queryParams: any = {
        start_date: formData.startDate,
        end_date: formData.endDate,
      };
      const formdata = {
        insurer_ids: formData.insurerIds ? [formData.insurerIds] : [],
        commission_ids: formData.selectedDeductibles,
      };
      const response = await getInsurerCommissionSummaryTotals(queryParams, true, formdata);
      if (response?.result) {
        setBrokerageTotals({
          total_commission: response.result.total_commission || 0,
          total_revenue_realized: response.result.total_revenue_realized || 0,
          total_overriding_commission: response.result.total_overriding_commission || 0,
          total_agent_commission: response.result.total_agent_commission || 0,
        });
      }
      setIsLoading(false);
    } catch (error) {
      console.error('Error fetching totals:', error);
      setIsLoading(false);
    }
  };

  const settleCommission = async (_entityId: any, _callback: Function, setLoader: Function, onClose: Function) => {
    try {
      setLoader(true);
      const response = await settleBrokerageCommission({ commission_ids: formData.selectedDeductibles });
      if (response?.is_success) {
        toaster.success(response?.message);
        setDeductibleTableVers((prev) => prev + 1);
        setTableVers((prev) => prev + 1);
      } else {
        toaster.error(response?.message);
      }
      setLoader(false);
      onClose();
    } catch (error) {
      console.error('Error fetching totals:', error);
    }
  };
  const onFormChange = (name: string, value: any) => {
    setFormData((prevFormData) => ({ ...prevFormData, [name]: value }));
  };

  return (
    <>
      <GoBack goTo={() => router.back()} title={t('commission_calculation')} />
      <div className="row g-3 mb-3">
        <div className="col-12 col-lg-8">
          <div className="bg-white p-3 p-md-5 rounded-3">
            <div className="row gy-3">
              <div className="col-12">
                <div className="row g-3">
                  <div className="col-12 col-sm-6">
                    <Label htmlFor="start-date" label="Start Date" isRequired />
                    <Input type="date" id="start-date" value={formData.startDate} onChange={(e) => onFormChange('startDate', e.target.value)} />
                  </div>
                  <div className="col-12 col-sm-6">
                    <Label htmlFor="end-date" label="End Date" isRequired />
                    <Input type="date" id="end-date" value={formData.endDate} onChange={(e) => onFormChange('endDate', e.target.value)} />
                  </div>
                </div>
              </div>
              <div className="col-12">
                <div className="row g-3">
                  <div className="col-12 col-md-6">
                    <div className="custom-select">
                      <Label label="Insurer Selection" isRequired />
                      <AsyncSelect
                        onChange={(value) => {
                          onFormChange('insurerIds', value);
                        }}
                        loadOptions={fetchAllInsurerData}
                        option={{
                          value: 'id',
                          label: 'name',
                        }}
                      />
                    </div>
                  </div>
                  <div className="d-flex flex-row gap-3">
                    <Button text={t('calculate')} onClick={fetchCommissionTotal} />
                    {formData.selectedDeductibles.length > 0 && (
                      <ConfirmationPop trigger={<Button text={t('process')} color="light" />} entityId={undefined} title="settle_confirmation" handleOnSubmit={settleCommission} />
                    )}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div className="col-12 col-lg-4">
          <div className="bg-primary text-white p-3 p-md-4 rounded-3 h-100">
            <h2 className="mb-3 fs-14 text-center">{t('total_revenue_amount')}</h2>
            {isLoading ? (
              <Skeleton height="200px" width="340px" />
            ) : (
              <div className="d-flex flex-column gap-3">
                <div className="text-center">
                  <h4 className="fs-14 mb-1">{t('total_commission')}</h4>
                  <h5 className="fw-bold fs-14 mb-0">
                    {currency.code} {(Number(brokerageTotals.total_commission) || 0).toLocaleString()}
                  </h5>
                </div>
                <div className="text-center">
                  <h4 className="fs-14 mb-1">{t('revenue_realized')}</h4>
                  <h5 className="fw-bold fs-14 mb-0">
                    {currency.code} {(Number(brokerageTotals.total_revenue_realized) || 0).toLocaleString()}
                  </h5>
                </div>
                <div className="text-center">
                  <h4 className="fs-14 mb-1">{t('overriding_commission')}</h4>
                  <h5 className="fw-bold fs-14 mb-0">
                    {currency.code} {(Number(brokerageTotals.total_overriding_commission) || 0).toLocaleString()}
                  </h5>
                </div>
                <div className="text-center">
                  <h4 className="fs-14 mb-1">{t('agent_commission')}</h4>
                  <h5 className="fw-bold fs-14 mb-0">
                    {currency.code} {(Number(brokerageTotals.total_agent_commission) || 0).toLocaleString()}
                  </h5>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
      <CommissionCalculatedTable formData={formData} tableVers={tableVers} />
      <DeductibleTable formData={formData} tableVers={deductibleTableVers} onSelectDeductible={(ids) => onFormChange('selectedDeductibles', ids)} />
    </>
  );
}

export default BrokerageCommissionCalculation;
