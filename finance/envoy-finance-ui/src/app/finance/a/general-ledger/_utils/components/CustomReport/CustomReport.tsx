import { useTrans } from '@/helpers/services/lang/langService';
import { AsyncSelect } from '@apptimus-ui/select';
import { Button, Input, Label } from '@apptimus-ui/ui-element';
import React, { useState } from 'react';
import { fetchAllSampleData } from '../../service';
import { useRouter } from 'next/navigation';
import { initInsurancePolicyFormData } from '../../model';

function CustomReport() {
  const router = useRouter();
  const [includeGraphs, setIncludeGraphs] = useState(true);
  const [selectedCharts, setSelectedCharts] = useState<string[]>(['Bar Chart']);
  const [exportFormat, setExportFormat] = useState<string[]>(['PDF']);
  const [formData, setFormData] = useState(initInsurancePolicyFormData);

  const t = useTrans('label.sales_report,otr.common');

  const onFormChange = (name: string, value: any) => {
    setFormData((prevFormData) => ({ ...prevFormData, [name]: value }));
  };

  // Financial metrics checkboxes
  const [financialMetrics, setFinancialMetrics] = useState({
    totalAmount: false,
    premiumAmount: false,
    commissionAmount: false,
    taxAmount: false,
  });

  // Transaction metrics checkboxes
  const [transactionMetrics, setTransactionMetrics] = useState({
    transactionDate: false,
    transactionAmount: false,
    transactionType: false,
  });

  // Product metrics checkbox
  const [productMetrics, setProductMetrics] = useState(false);

  const handleFinancialMetricChange = (metric: string) => {
    setFinancialMetrics({
      ...financialMetrics,
      [metric]: !financialMetrics[metric as keyof typeof financialMetrics],
    });
  };

  const handleTransactionMetricChange = (metric: string) => {
    setTransactionMetrics({
      ...transactionMetrics,
      [metric]: !transactionMetrics[metric as keyof typeof transactionMetrics],
    });
  };

  const handleChartSelection = (chart: string) => {
    if (selectedCharts.includes(chart)) {
      setSelectedCharts(selectedCharts.filter((c) => c !== chart));
    } else {
      setSelectedCharts([...selectedCharts, chart]);
    }
  };

  const handleExportFormatChange = (format: string) => {
    if (exportFormat.includes(format)) {
      setExportFormat(exportFormat.filter((f) => f !== format));
    } else {
      setExportFormat([...exportFormat, format]);
    }
  };

  return (
    <div className="mt-4">
      <div>
        <div className="row">
          {/* Left Card */}
          <div className="col-md-8">
            <div className="card">
              <div className="card-body">
                <div className="col-md-6 mb-4">
                  <Label htmlFor="report_name" label={t('report_name')} isRequired />
                  <Input type="text" className="form-control" value="Quaterly Sale Report" />
                </div>

                {/* Date Range Section */}
                <div className="row mb-4">
                  <div className="col-md-12">
                    <h6>{t('by_date_range')}</h6>
                    <div className="row">
                      <div className="col-md-6">
                        <Label htmlFor="start_date" label={t('start_date')} isRequired />
                        <Input type="date" className="form-control" value="01/01/2024" />
                      </div>
                      <div className="col-md-6">
                        <Label htmlFor="end_date" label={t('end_date')} isRequired />
                        <Input type="date" className="form-control" value="31/03/2024" />
                      </div>
                    </div>
                  </div>
                </div>

                {/* User Types Section */}
                <div className="row mb-4">
                  <div className="col-md-12">
                    <h6>{t('by_user_types')}</h6>
                    <div className="row">
                      <div className="col-md-4 custom-select">
                        <Label htmlFor="customer_name" label={t('customer_name')} isRequired />
                        <AsyncSelect
                          defaultValue={formData.customer_name}
                          onChange={(value) => onFormChange('customer_name', value)}
                          className="form-control error-customer_name"
                          loadOptions={fetchAllSampleData}
                          option={{
                            value: 'id',
                            label: 'sample_name',
                          }}
                        />
                      </div>
                      <div className="col-md-4 custom-select">
                        <Label htmlFor="insurer_name" label={t('insurer_name')} isRequired />
                        <AsyncSelect
                          defaultValue={formData.insurer_name}
                          onChange={(value) => onFormChange('insurer_name', value)}
                          className="form-control error-insurer_name"
                          loadOptions={fetchAllSampleData}
                          option={{
                            value: 'id',
                            label: 'sample_name',
                          }}
                        />
                      </div>
                      <div className="col-md-4 custom-select">
                        <Label htmlFor="agent_name" label={t('agent_name')} isRequired />
                        <AsyncSelect
                          defaultValue={formData.agent_name}
                          onChange={(value) => onFormChange('agent_name', value)}
                          className="form-control error-agent_name"
                          loadOptions={fetchAllSampleData}
                          option={{
                            value: 'id',
                            label: 'sample_name',
                          }}
                        />
                      </div>
                      <div className="mt-2 col-md-4 custom-select">
                        <Label htmlFor="customer_id" label={t('customer_id')} isRequired />
                        <AsyncSelect
                          defaultValue={formData.customer_id}
                          onChange={(value) => onFormChange('customer_id', value)}
                          className="form-control error-customer_id"
                          loadOptions={fetchAllSampleData}
                          option={{
                            value: 'id',
                            label: 'sample_name',
                          }}
                        />
                      </div>
                      <div className="mt-2 col-md-4 custom-select">
                        <Label htmlFor="insurer_id" label={t('insurer_id')} isRequired />
                        <AsyncSelect
                          defaultValue={formData.insurer_id}
                          onChange={(value) => onFormChange('insurer_id', value)}
                          className="form-control error-insurer_id"
                          loadOptions={fetchAllSampleData}
                          option={{
                            value: 'id',
                            label: 'sample_name',
                          }}
                        />
                      </div>
                      <div className="mt-2 col-md-4 custom-select">
                        <Label htmlFor="agent_id" label={t('agent_id')} isRequired />
                        <AsyncSelect
                          defaultValue={formData.agent_id}
                          onChange={(value) => onFormChange('agent_id', value)}
                          className="form-control error-agent_id"
                          loadOptions={fetchAllSampleData}
                          option={{
                            value: 'id',
                            label: 'sample_name',
                          }}
                        />
                      </div>
                    </div>
                  </div>
                </div>

                {/* Policy Details Section */}
                <div className="row mb-4">
                  <div className="col-md-12">
                    <h6>{t('by_policies_details')}</h6>
                    <div className="row">
                      <div className="col-md-4 custom-select">
                        <Label htmlFor="policy_name" label={t('policy_name')} isRequired />
                        <AsyncSelect
                          defaultValue={formData.policy_name}
                          onChange={(value) => onFormChange('policy_name', value)}
                          className="form-control error-policy_name"
                          loadOptions={fetchAllSampleData}
                          option={{
                            value: 'id',
                            label: 'sample_name',
                          }}
                        />
                      </div>
                      <div className="col-md-4 custom-select">
                        <Label htmlFor="policy_id" label={t('policy_id')} isRequired />
                        <AsyncSelect
                          defaultValue={formData.policy_id}
                          onChange={(value) => onFormChange('policy_id', value)}
                          className="form-control error-policy_id"
                          loadOptions={fetchAllSampleData}
                          option={{
                            value: 'id',
                            label: 'sample_name',
                          }}
                        />
                      </div>
                      <div className="col-md-4 custom-select">
                        <Label htmlFor="policy_type" label={t('policy_type')} isRequired />
                        <AsyncSelect
                          defaultValue={formData.policy_type}
                          onChange={(value) => onFormChange('policy_type', value)}
                          className="form-control error-policy_type"
                          loadOptions={fetchAllSampleData}
                          option={{
                            value: 'id',
                            label: 'sample_name',
                          }}
                        />
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Right Card */}
          <div className="col-md-4">
            <div className="card">
              <div className="card-body">
                {/* Financial Metrics Section */}
                <div className="mb-4">
                  <h6>{t('financial_metrics')}</h6>
                  <div className="form-check">
                    <Input className="form-check-input" type="checkbox" checked={financialMetrics.totalAmount} onChange={() => handleFinancialMetricChange('totalAmount')} />
                    <Label htmlFor="total_amount" label={t('total_amount')} isRequired />
                  </div>

                  <div className="form-check">
                    <Input className="form-check-input" type="checkbox" checked={financialMetrics.premiumAmount} onChange={() => handleFinancialMetricChange('premiumAmount')} />
                    <Label htmlFor="premium_amount" label={t('premium_amount')} isRequired />
                  </div>

                  <div className="form-check">
                    <Input className="form-check-input" type="checkbox" checked={financialMetrics.commissionAmount} onChange={() => handleFinancialMetricChange('commissionAmount')} />
                    <Label htmlFor="commission_amount" label={t('commission_amount')} isRequired />
                  </div>

                  <div className="form-check">
                    <Input className="form-check-input" type="checkbox" checked={financialMetrics.taxAmount} onChange={() => handleFinancialMetricChange('taxAmount')} />
                    <Label htmlFor="tax_amount" label={t('tax_amount')} isRequired />
                  </div>
                </div>

                {/* Transaction Metrics Section */}
                <div className="mb-4">
                  <h6>{t('transaction_metrics')}</h6>
                  <div className="form-check">
                    <Input className="form-check-input" type="checkbox" checked={transactionMetrics.transactionDate} onChange={() => handleTransactionMetricChange('transactionDate')} />
                    <Label htmlFor="transaction_date" label={t('transaction_date')} isRequired />
                  </div>

                  <div className="form-check">
                    <Input className="form-check-input" type="checkbox" checked={transactionMetrics.transactionAmount} onChange={() => handleTransactionMetricChange('transactionAmount')} />
                    <Label htmlFor="transaction_amount" label={t('transaction_amount')} isRequired />
                  </div>

                  <div className="form-check">
                    <Input className="form-check-input" type="checkbox" checked={transactionMetrics.transactionType} onChange={() => handleTransactionMetricChange('transactionType')} />
                    <Label htmlFor="transaction_type" label={t('transaction_type')} isRequired />
                  </div>
                </div>

                {/* Product Metrics Section */}
                <div className="mb-4">
                  <h6>{t('product_metrics')}</h6>

                  <div className="form-check">
                    <Input className="form-check-input" type="checkbox" checked={productMetrics} onChange={() => setProductMetrics(!productMetrics)} />
                    <Label htmlFor="product_types" label={t('product_types')} isRequired />
                  </div>
                </div>

                {/* Visualization Options */}
                <div className="mb-4">
                  <h6>{t('visualization_options')}</h6>

                  {['Bar Chart', 'Line Chart', 'Pie Chart', 'Table View'].map((chart) => (
                    <div className="form-check" key={chart}>
                      <Input className="form-check-input" type="checkbox" checked={selectedCharts.includes(chart)} onChange={() => handleChartSelection(chart)} id={`chart-${chart}`} />
                      <Label htmlFor={`chart-${chart}`} label={chart} isRequired />
                    </div>
                  ))}
                </div>

                {/* Export Options */}
                <div className="mb-4">
                  <h6>{t('export_options')}</h6>

                  {['PDF', 'Excel', 'CSV'].map((format) => (
                    <div className="form-check" key={format}>
                      <Input className="form-check-input" type="checkbox" checked={exportFormat.includes(format)} onChange={() => handleExportFormatChange(format)} id={`export-${format}`} />
                      <Label htmlFor={`export-${format}`} label={format} isRequired />
                    </div>
                  ))}
                </div>

                {/* Include Graphs Section */}
                <div className="mb-4">
                  <h6>{t('include_graphs')}</h6>
                  <div className="d-flex">
                    <div className="form-check me-4">
                      <Input
                        type="checkbox"
                        className="form-check-input"
                        id="graphYes"
                        checked={includeGraphs}
                        onChange={() => {
                          if (!includeGraphs) setIncludeGraphs(true);
                        }}
                      />
                      <Label htmlFor="graphYes" label={t('yes')} />
                    </div>
                    <div className="form-check">
                      <Input
                        type="checkbox"
                        className="form-check-input"
                        id="graphNo"
                        checked={!includeGraphs}
                        onChange={() => {
                          if (includeGraphs) setIncludeGraphs(false);
                        }}
                      />
                      <Label htmlFor="graphNo" label={t('no')} />
                    </div>
                  </div>
                </div>
                {/* Action Buttons */}
                <div className="row mt-3">
                  <div className="col-12 d-flex justify-content-start">
                    <Button
                      text={'Generate Report'}
                      color={'primary'}
                      onClick={() => {
                        window.scrollTo({ top: 0, behavior: 'instant' });
                        router.push('/finance/a/general-ledger/custom-report/create');
                      }}
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default CustomReport;
