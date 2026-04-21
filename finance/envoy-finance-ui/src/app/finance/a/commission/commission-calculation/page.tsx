'use client';

import Table from '@/components/table-properties/Table';
import { ITablePropertyColumn } from '@/interface/ICommon';
import { useAsyncTable } from '@apptimus-ui/table';
import { useEffect, useMemo, useState } from 'react';
import PageHeading from '@/components/others/PageHeading';
import { useTrans } from '@/helpers/services/lang/langService';
import { Button, Input, Label } from '@apptimus-ui/ui-element';
import { AsyncSelect } from '@apptimus-ui/select';
import { fetchAllUsersData, fetchMultiAgentRevenuesTableData, fetchMultiBrokerageRevenuesTableData } from '../_utils/services';
import { getAgentCommissionSummaryTotals, getInsurerCommissionSummaryTotals, getMultiAgentRevenuesPayments, makeAgentCommission } from '../_utils/api-service';
import { fetchAllInsurerData } from '../../commission-setup/_utils/services';
import { useRouter, useSearchParams } from 'next/navigation';
import { Flexicon } from '@apptimus-ui/flexicon';
import { toaster } from '@/helpers/services/toaster';
import GoBack from '@/components/others/page-related/GoBack';
import ProfileInfo from '@/components/others/page-related/ProfileInfo';
import { getCurrency } from '@/helpers/services/currencyService';
import { hexToRgba, thousandSeparator } from '@/helpers/services/commonService';

function CommissionCalculationList() {
  const t = useTrans('label.commission,otr.common');
  const tBe = useTrans('be.msg,be.error,be.attri');
  const currency = getCurrency();
  const searchParams = useSearchParams();
  const router = useRouter();
  const [isFormProcessing, setIsFormProcessing] = useState(false);
  const [commissionType, setCommissionType] = useState('brokerage');
  const [agentTablevar, setAgentTablevar] = useState(0);
  const [paymentAgentId, setPaymentAgentId] = useState([]);
  const [brokerageTotals, setBrokerageTotals] = useState({
    total_commission: '0',
    total_revenue_realized: '0',
    total_overriding_commission: '0',
    total_agent_commission: '0',
  });
  const [agentTotals, setAgentTotals] = useState({
    total_commission_earned: '0',
    total_commission_received: '0',
    total_commission_pending: '0',
  });
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [selectedAgent, setSelectedAgent] = useState([]);
  const [selectedInsurer, setSelectedInsurer] = useState([]);
  const [tab, setTab] = useState('pending');

  useEffect(() => {
    const urlTab = searchParams?.get('tab') || 'brokerage_revenue';
    setCommissionType(urlTab === 'agent_commission' ? 'agent' : 'brokerage');
  }, [searchParams]);

  useEffect(() => {
    const fetchCommisionTotal = async () => {
      try {
        const queryParams: any = {
          start_date: startDate,
          end_date: endDate,
        };
        if (commissionType === 'brokerage') {
          const formdata = {
            insurer_ids: selectedInsurer,
          };
          const response = await getInsurerCommissionSummaryTotals(queryParams, true, formdata);
          if (response?.result) {
            setBrokerageTotals(response.result);
          }
          tablebrokerage.reload();
        } else {
          const formdata = {
            agent_ids: selectedAgent,
          };
          const response = await getAgentCommissionSummaryTotals(queryParams, true, formdata);
          if (response?.result) {
            setAgentTotals(response.result);
          }
          tableAgent.reload();
        }
      } catch (error) {
        console.error('Error fetching totals:', error);
      }
    };
    fetchCommisionTotal();
  }, [startDate, endDate, selectedAgent, selectedInsurer]);

  useEffect(() => {
    tableAgent.reload();
    tableAgent.reset({ type: 'row-selection' });
  }, [agentTablevar, tab]);

  async function onSubmitCommission() {
    setIsFormProcessing(true);

    try {
      const formData = {
        commission_ids: paymentAgentId,
      };
      const responseData = await makeAgentCommission(formData);
      setIsFormProcessing(false);

      if (responseData.is_success) {
        toaster.success(tBe(responseData.message));
        setAgentTablevar((pre) => pre + 1);
        setPaymentAgentId([]);
      }
    } catch (error) {
      console.error('An error occurred:', error);
    }
  }

  async function handleDownloadDocument() {
    setIsFormProcessing(true);

    try {
      const responseData = await getMultiAgentRevenuesPayments({ download: 'true', status: 'agent_comm_full_paid' });
      setIsFormProcessing(false);

      if (responseData.is_success) {
        const pdfUrl = responseData.result?.pdf_document?.download_link;
        window.open(pdfUrl, '_blank');
        toaster.success(tBe(responseData.message));
      }
    } catch (error) {
      console.error('An error occurred:', error);
    }
  }

  const Brokerage = useMemo<ITablePropertyColumn[]>(
    () => [
      {
        id: 'insurer_name',
        header: t('insurer_name'),
        accessorKey: 'insurer_name',
        sort: true,
      },
      {
        id: 'brokerage_policy_id',
        header: t('total_policies'),
        accessorKey: 'brokerage_policy_id',
        sort: true,
      },
      {
        id: 'insurer_name',
        header: t('insured_details'),
        accessorKey: 'insurer_name',
        sort: true,
      },
      {
        id: 'total_revenue_realized',
        header: t('total_revenue_realized'),
        accessorKey: 'total_revenue_realized',
        sort: true,
      },
    ],
    [],
  );

  const Agent = useMemo<ITablePropertyColumn[]>(
    () => [
      {
        id: 'user_name',
        header: t('agent_details'),
        accessorKey: 'user_name',
        sort: true,
        visibilityLock: false,
        cell: ({ cell }: { cell: any }) => {
          return <ProfileInfo title={cell.agent_name} subtitle={cell.agent_email} imageKey={cell.agent_picture} />;
        },
      },
      {
        id: 'invoice_number',
        header: t('dr_cr_note_number'),
        accessorKey: 'invoice_number',
        sort: true,
        visibilityLock: false,
        cell: ({ cell }: { cell: any }) => cell.getValue() || '-',
      },
      {
        id: 'invoice_amount',
        header: `${t('amount')} (${currency.code})`,
        accessorKey: 'invoice_amount',
        sort: true,
        cell: ({ cell }: { cell: any }) => <div className="amount-container">{thousandSeparator(cell.getValue()) || '-'}</div>,
      },
      {
        id: 'total_agent_commission',
        header: t('agent_commission_persentage'),
        accessorKey: 'total_agent_commission',
        sort: true,
        cell: ({ cell }: { cell: any }) => {
          if (cell.agent_commission_type === 'percentage') {
            return <div>{cell.getValue()} %</div>;
          } else {
            return <div>{cell.getValue()}</div>;
          }
        },
      },
      {
        id: 'revenue_recognized',
        header: t('recognized_amount'),
        accessorKey: 'revenue_recognized',
        sort: true,
        cell: ({ cell }: { cell: any }) => <div className="amount-container">{thousandSeparator(cell.getValue()) || '-'}</div>,
      },
      {
        id: 'revenue_realized',
        header: t('revenue_realized_amount'),
        accessorKey: 'revenue_realized',
        sort: true,
        cell: ({ cell }: { cell: any }) => <div className="amount-container">{thousandSeparator(cell.getValue()) || '-'}</div>,
      },
      {
        id: 'revised_amount_percent',
        header: t('revised_amount'),
        accessorKey: 'revised_amount_percent',
        sort: true,
        cell: ({ cell }: { cell: any }) => <div className="amount-container">{thousandSeparator(cell.getValue()) || '-'}</div>,
      },
      {
        id: 'commission_deductible ',
        header: t('deductible'),
        accessorKey: 'commission_deductible',
        sort: true,
        cell: ({ cell }: { cell: any }) => <div className="amount-container">{thousandSeparator(cell.getValue()) || '-'}</div>,
      },
      {
        id: 'paid_amount',
        header: t('paid_amount'),
        accessorKey: 'paid_amount',
        sort: true,
        cell: ({ cell }: { cell: any }) => <div className="amount-container">{thousandSeparator(cell.getValue()) || '-'}</div>,
      },
      {
        id: 'outstanding',
        header: t('outstanding_amount'),
        accessorKey: 'outstanding',
        sort: true,
        cell: ({ cell }: { cell: any }) => <div className="amount-container">{thousandSeparator(cell.getValue()) || '-'}</div>,
      },
      {
        id: 'status',
        header: t('status'),
        accessorKey: 'status',
        sort: true,
        cell: ({ cell, onClick }: any) => (
          <div
            className="rounded-5 fw-semibold badge"
            style={{ background: hexToRgba(cell?.status_color || '', 0.1), border: `1px solid ${cell?.status_color}`, color: cell?.status_color }}
            onClick={onClick}
          >
            {cell?.status}
          </div>
        ),
      },
    ],
    [],
  );

  const tablebrokerage = useAsyncTable({
    columns: Brokerage,
    loadData: (params) =>
      fetchMultiBrokerageRevenuesTableData({
        ...params,
        insurer_id: selectedInsurer,
        start_date: startDate,
        end_date: endDate,
        data: {
          insurer_ids: selectedInsurer,
        },
      }),
    paginate: true,
  });

  const tableAgent = useAsyncTable({
    columns: Agent,
    loadData: (params) =>
      fetchMultiAgentRevenuesTableData({
        ...params,
        itemsPerPage: 5,
        start_date: startDate,
        end_date: endDate,
        data: {
          agent_ids: selectedAgent,
        },
        status: tab === 'pending' ? 'agent_comm_pending' : 'agent_comm_full_paid',
      }),
    paginate: true,
    rowSelection: true,
    rowSelectionProp: {
      key: 'id',
      mode: 'multiple',
      actionColumn: tab === 'pending',
      enableSelectAll: tab === 'pending',
      action: (value: any) => {
        setPaymentAgentId(value);
      },
      disableRowFn: (row: any) => row.outstanding <= 0,
    },
  });

  return (
    <>
      <GoBack goTo={() => router.back()} title={t('commission_calculation')} />
      <div>
        <div className="row g-3">
          <div className="col-12 col-lg-8">
            <div className="bg-white p-3 p-md-5 rounded-3">
              <div className="row gy-3">
                <div className="col-12">
                  <div className="row g-3">
                    <div className="col-12 col-sm-6">
                      <Label htmlFor="start-date" label="Start Date" isRequired />
                      <Input type="date" id="start-date" value={startDate} onChange={(e) => setStartDate(e.target.value)} />
                    </div>
                    <div className="col-12 col-sm-6">
                      <Label htmlFor="end-date" label="End Date" isRequired />
                      <Input type="date" id="end-date" value={endDate} onChange={(e) => setEndDate(e.target.value)} />
                    </div>
                  </div>
                </div>
                <div className="col-12">
                  <div className="row g-3">
                    <div className="col-12">
                      <div className="custom-select">
                        <Label htmlFor={commissionType === 'brokerage' ? 'insurer_name' : 'agent_name'} label={commissionType === 'brokerage' ? 'Insurer Selection' : 'Agent Selection'} isRequired />
                        {commissionType === 'brokerage' ? (
                          <AsyncSelect
                            multiple
                            onChange={(value) => {
                              setSelectedInsurer(value);
                            }}
                            loadOptions={fetchAllInsurerData}
                            option={{
                              value: 'id',
                              label: 'name',
                            }}
                          />
                        ) : (
                          <AsyncSelect
                            multiple
                            onChange={(value) => {
                              setSelectedAgent(value);
                            }}
                            loadOptions={fetchAllUsersData}
                            option={{
                              value: 'id',
                              label: 'display_name',
                            }}
                          />
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div className="col-12 col-lg-4">
            <div className="bg-primary text-white p-3 p-md-4 rounded-3 h-100">
              <h2 className="mb-3 fs-14 text-center">{t('total_revenue_amount')}</h2>
              <div className="d-flex flex-column gap-3">
                {commissionType === 'brokerage' ? (
                  <>
                    <div className="text-center">
                      <h4 className="fs-14 mb-1">{t('total_commission')}</h4>
                      <h5 className="fw-bold fs-14 mb-0">LKR {Number(brokerageTotals.total_commission).toLocaleString()}</h5>
                    </div>
                    <div className="text-center">
                      <h4 className="fs-14 mb-1">{t('revenue_realized')}</h4>
                      <h5 className="fw-bold fs-14 mb-0">LKR {Number(brokerageTotals.total_revenue_realized).toLocaleString()}</h5>
                    </div>
                    <div className="text-center">
                      <h4 className="fs-14 mb-1">{t('overriding_commission')}</h4>
                      <h5 className="fw-bold fs-14 mb-0">LKR {Number(brokerageTotals.total_overriding_commission).toLocaleString()}</h5>
                    </div>
                    <div className="text-center">
                      <h4 className="fs-14 mb-1">{t('agent_commission')}</h4>
                      <h5 className="fw-bold fs-14 mb-0">LKR {Number(brokerageTotals.total_agent_commission).toLocaleString()}</h5>
                    </div>
                  </>
                ) : (
                  <>
                    <div className="text-center">
                      <h4 className="fs-14 mb-1">{t('commission_earned')}</h4>
                      <h5 className="fw-bold fs-14 mb-0">LKR {Number(agentTotals.total_commission_earned).toLocaleString()}</h5>
                    </div>
                    <div className="text-center">
                      <h4 className="fs-14 mb-1">{t('commission_received')}</h4>
                      <h5 className="fw-bold fs-14 mb-0">LKR {Number(agentTotals.total_commission_received).toLocaleString()}</h5>
                    </div>
                    <div className="text-center">
                      <h4 className="fs-14 mb-1">{t('commission_pending')}</h4>
                      <h5 className="fw-bold fs-14 mb-0">LKR {Number(agentTotals.total_commission_pending).toLocaleString()}</h5>
                    </div>
                  </>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
      <div className="d-flex justify-content-between align-items-center w-100 bg-white rounded-3 p-2 mt-3">
        <div className="fw-bold py-2">{t('commission_calculated')}</div>
        {commissionType === 'agent' && paymentAgentId?.length !== 0 && (
          <Button className="d-flex align-items-center gap-1" isLoading={isFormProcessing} onClick={onSubmitCommission}>
            <Flexicon icon="arrow-circle-broken-up" variant="line" size={18} />
            <span className="d-none d-sm-inline">{t('settle_commission')}</span>
          </Button>
        )}
      </div>
      {/* {commissionType === 'brokerage' && (
        <>
          <div className={`data-table-container card custom-card ${isFullscreen ? 'dtc-fullscreen card-fullscreen' : ''}`}>
            <Table tableProperties={tablebrokerage} heading={<PageHeading title={t('roles')} icon="sun-light" />} {...{ isFullscreen, setIsFullscreen }} />
          </div>
        </>
      )} */}
      {commissionType === 'agent' && (
        <div>
          <div className="d-flex justify-content-between bg-white px-2">
            <div className="il-box-tab">
              <div className={`il-box-tab-item ${tab === 'pending' ? 'active' : ''}`} onClick={() => setTab('pending')}>
                {t('pending')}
              </div>
              <div className={`il-box-tab-item ${tab === 'paid' ? 'active' : ''}`} onClick={() => setTab('paid')}>
                {t('paid')}
              </div>
            </div>
            {tab === 'paid' && (
              <div className="d-flex justify-content-end">
                <Button className="d-flex align-items-center gap-1" isLoading={isFormProcessing} onClick={handleDownloadDocument}>
                  <Flexicon icon="download-01" variant="line" size={16} />
                  <span className="d-none d-sm-inline">{t('download')}</span>
                </Button>
              </div>
            )}
          </div>
          <div className="px-2 py-1 bg-white">
            <Table tableProperties={{ ...tableAgent, itemsPerPage: 5 }} searchOption={false} heading={<PageHeading title={t('roles')} icon="sun-light" />} />
          </div>
        </div>
      )}
    </>
  );
}

export default CommissionCalculationList;
