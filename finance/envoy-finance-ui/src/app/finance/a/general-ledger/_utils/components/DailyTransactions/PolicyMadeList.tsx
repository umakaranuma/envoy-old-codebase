import React, { useEffect, useMemo, useState } from 'react';
import { CustomizeColumn, useCustomizeColumn } from '@/components/others/CustomizeColumn';
import PageHeading from '@/components/others/PageHeading';
import { useTrans } from '@/helpers/services/lang/langService';
import { ITablePropertyColumn } from '@/interface/ICommon';
import { useAsyncTable } from '@apptimus-ui/table';
import Table from '@/components/table-properties/Table';
import { filterReducer } from '@/helpers/services/dataReducer';
import { fetchPolicyMadeTableData } from '../../service';
import { formatDate, thousandSeparator } from '@/helpers/services/commonService';
import { Modal } from '@apptimus-ui/modal';
import { ChartType } from '../../model';
import CustomChart from '../CustomChart';
import ReportHeadingSection from '../ReportHeadingSection';
import { getCurrency } from '@/helpers/services/currencyService';

function PolicyMadeList({ tableVers }: { tableVers: number; onView: Function; onEdit: Function; handleOnDelete: Function }) {
  const t = useTrans('label.general_ledger,otr.common');
  const tableName = 'policy_made_summary';
  const currency = getCurrency();
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [isCustColumnVisible, setIsCustColumnVisible] = useState(false);
  const [tableColumnVers, setTableColumnVers] = useState(0);
  const [_filterComKey, setFilterComKey] = useState(0);
  const [_isFilterVisible, setIsFilterVisible] = useState(false);
  const [chartFullScreen, setChartFullScreen] = useState(false);
  const [chartComKey, setChartComKey] = useState(0);
  const [chartType, setChartType] = useState<ChartType>('pie');
  const [chartDefaultValue, setChartDefaultValue] = useState({ id: 'pie', label: 'Pie Chart' });
  const [chartData, setChartData] = useState<{
    labels: string[];
    series: number[];
    totalPremium: number;
  }>({
    labels: [],
    series: [],
    totalPremium: 0,
  });

  const columns = useMemo<ITablePropertyColumn[]>(
    () => [
      {
        id: 'date',
        header: t('date'),
        accessorKey: 'date',
        sort: true,
        cell: ({ cell }: { cell: any }) => <>{formatDate(cell.date) || cell.getValue() || '-'}</>,
      },
      {
        id: 'customer_name',
        header: t('customer_name'),
        accessorKey: 'customer_name',
        sort: true,
        cell: ({ cell }: { cell: any }) => cell.getValue() || '-',
      },
      {
        id: 'policy_number',
        header: t('policy_no'),
        accessorKey: 'policy_number',
        sort: true,
        cell: ({ cell }: { cell: any }) => cell.getValue() || '-',
      },
      {
        id: 'premium_amount',
        header: `${t('premium_amount')} (${currency.code})`,
        accessorKey: 'premium_amount',
        sort: true,
        align: 'right',
        cell: ({ cell }: { cell: any }) => <div className="amount-container">{thousandSeparator(cell.getValue()) || '-'}</div>,
      },
    ],
    [],
  );

  const tableColumns = useCustomizeColumn({ ...{ tableName, columns, tableColumnVers } });

  const tableProperties = useAsyncTable({
    columns: tableColumns,
    loadData: async (params) => {
      const response = await fetchPolicyMadeTableData(params);
      if (response?.data) {
        // Aggregate premium_amount by policy_number
        const policyTotals: Record<string, number> = {};
        let totalPremium = 0;
        response.data.forEach((item: any) => {
          const policy = item.policy_number || 'Unknown';
          const premium = parseFloat(item.premium_amount) || 0;
          policyTotals[policy] = (policyTotals[policy] || 0) + premium;
          totalPremium += premium;
        });

        setChartData({
          labels: Object.keys(policyTotals),
          series: Object.values(policyTotals),
          totalPremium,
        });
        setChartComKey((prev) => prev + 1);
      }
      return response;
    },
    paginate: true,
    rowSelection: false,
    customState: {
      initState: {
        filters: {},
      },
      reducer: (_: any, action: any) => filterReducer({ action, setFilterComKey }),
    },
  });

  useEffect(() => {
    tableProperties.reload();
  }, [tableColumnVers, tableVers]);

  const renderChart = () => (
    <div className={`card h-100 ${!chartFullScreen && 'p-3'}`}>
      <ReportHeadingSection
        chartDefaultValue={chartDefaultValue}
        chartFullScreen={chartFullScreen}
        setChartComKey={setChartComKey}
        setChartDefaultValue={setChartDefaultValue}
        setChartFullScreen={setChartFullScreen}
        setChartType={setChartType}
        title={t('premium_by_policy')}
      />
      <div key={chartComKey}>
        <CustomChart
          type={chartType}
          series={
            chartType === 'pie'
              ? chartData.series
              : [
                  {
                    name: 'Premium Amount',
                    data: chartData.series,
                  },
                ]
          }
          categories={chartType === 'pie' ? chartData.labels : undefined}
          colors={['#008FFB', '#00E396', '#FEB019', '#FF4560', '#775DD0']}
          options={{
            tooltip: {
              y: {
                formatter: (val: number) => `${currency.code} ${val.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`,
              },
            },
            yaxis: {
              labels: {
                formatter: (val) => `${currency.code} ${val.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`,
              },
            },
            ...(chartType === 'area' && {
              fill: {
                type: 'gradient',
                gradient: {
                  shadeIntensity: 1,
                  opacityFrom: 0.7,
                  opacityTo: 0.3,
                },
              },
            }),
            ...(chartType === 'bar' && {
              plotOptions: {
                bar: {
                  horizontal: false,
                  columnWidth: '70%',
                },
              },
              dataLabels: {
                enabled: false,
              },
            }),
          }}
        />
      </div>
    </div>
  );

  return (
    <div className="container-fluid mt-4">
      <div className="row">
        {/* Left Side - Table */}
        <div className="col-md-8">
          <div className={`data-table-container card custom-card ${isFullscreen ? 'dtc-fullscreen card-fullscreen' : ''}`}>
            <Table heading={<PageHeading title={t('policy_made')} icon="sun-light" />} {...{ tableProperties, isFullscreen, setIsFullscreen, setIsCustColumnVisible, setIsFilterVisible }} />
          </div>
        </div>

        {/* Right Side - Card UI with Chart */}
        <div className="col-md-4 mb-4">{renderChart()}</div>
      </div>

      {/* Fullscreen Chart Modal */}
      <Modal size="fullscreen" isOpen={chartFullScreen}>
        <div className="">{renderChart()}</div>
      </Modal>

      <CustomizeColumn
        key={tableColumnVers}
        isOpen={isCustColumnVisible}
        tableName={tableName}
        columns={tableColumns}
        onClose={() => setIsCustColumnVisible(false)}
        afterUpdate={() => setTableColumnVers((prevTableColumnVers) => prevTableColumnVers + 1)}
      />
    </div>
  );
}

export default PolicyMadeList;
