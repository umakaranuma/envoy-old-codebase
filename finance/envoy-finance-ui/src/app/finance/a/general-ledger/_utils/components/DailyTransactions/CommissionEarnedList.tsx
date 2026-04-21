import React, { useEffect, useMemo, useState } from 'react';
import { CustomizeColumn, useCustomizeColumn } from '@/components/others/CustomizeColumn';
import PageHeading from '@/components/others/PageHeading';
import { useTrans } from '@/helpers/services/lang/langService';
import { ITablePropertyColumn } from '@/interface/ICommon';
import { useAsyncTable } from '@apptimus-ui/table';
import Table from '@/components/table-properties/Table';
import { filterReducer } from '@/helpers/services/dataReducer';
import { fetchCommissionEarnedTableData } from '../../service';
import { formatDate, thousandSeparator } from '@/helpers/services/commonService';
import { Modal } from '@apptimus-ui/modal';
import CustomChart from '../CustomChart';
import ReportHeadingSection from '../ReportHeadingSection';
import { getCurrency } from '@/helpers/services/currencyService';
type ChartType = 'pie' | 'bar' | 'line' | 'area';

function CommissionEarnedList({ tableVers }: { tableVers: number; onView: Function; onEdit: Function; handleOnDelete: Function }) {
  const t = useTrans('label.general_ledger,otr.common');
  const tableName = 'commission_earned_summary';
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
    totalCommission: number;
  }>({
    labels: [],
    series: [],
    totalCommission: 0,
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
        id: 'recipient_name',
        header: t('recipient_name'),
        accessorKey: 'recipient_name',
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
        id: 'commission_amount',
        header: `${t('commission_amount')} (${currency.code})`,
        accessorKey: 'commission_amount',
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
      const response = await fetchCommissionEarnedTableData(params);
      if (response?.data) {
        // Aggregate commission_amount by recipient_name
        const commissionTotals: Record<string, number> = {};
        let totalCommission = 0;
        response.data.forEach((item: any) => {
          const recipient = item.recipient_name || 'Unknown';
          const commission = parseFloat(item.commission_amount) || 0;
          commissionTotals[recipient] = (commissionTotals[recipient] || 0) + commission;
          totalCommission += commission;
        });

        setChartData({
          labels: Object.keys(commissionTotals),
          series: Object.values(commissionTotals),
          totalCommission,
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
        title={t('commission_by_recipient')}
      />
      <div key={chartComKey}>
        <CustomChart
          type={chartType}
          series={
            chartType === 'pie'
              ? chartData.series
              : [
                  {
                    name: 'Commission Amount',
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
            <Table heading={<PageHeading title={t('commission_earned')} icon="sun-light" />} {...{ tableProperties, isFullscreen, setIsFullscreen, setIsCustColumnVisible, setIsFilterVisible }} />
          </div>
        </div>

        {/* Right Side - Card UI with Chart */}
        <div className="col-md-4 mb-4">{renderChart()}</div>
      </div>

      {/* Fullscreen Chart Modal */}
      <Modal size="fullscreen" isOpen={chartFullScreen}>
        {renderChart()}
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

export default CommissionEarnedList;
