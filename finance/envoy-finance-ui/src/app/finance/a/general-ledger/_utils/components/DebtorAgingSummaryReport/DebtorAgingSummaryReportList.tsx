import React, { useEffect, useMemo, useState } from 'react';
import { CustomizeColumn, useCustomizeColumn } from '@/components/others/CustomizeColumn';
import PageHeading from '@/components/others/PageHeading';
import { useTrans } from '@/helpers/services/lang/langService';
import { ITablePropertyColumn } from '@/interface/ICommon';
import { useAsyncTable } from '@apptimus-ui/table';
import Table from '@/components/table-properties/Table';
import { filterReducer } from '@/helpers/services/dataReducer';
import { fetchDebtorAgingSummaryReportTableData } from '../../service';
import { Modal } from '@apptimus-ui/modal';
import CustomChart from '../CustomChart';
import ReportHeadingSection from '../ReportHeadingSection';
import { getCurrency } from '@/helpers/services/currencyService';
import { thousandSeparator } from '@/helpers/services/commonService';

function DebtorAgingSummaryReportList({ tableVers }: { tableVers: number; onView: Function; onEdit: Function; handleOnDelete: Function }) {
  const t = useTrans('label.general_ledger,otr.common');
  const tableName = 'debtor_aging_summary';
  const currency = getCurrency();
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [isCustColumnVisible, setIsCustColumnVisible] = useState(false);
  const [tableColumnVers, setTableColumnVers] = useState(0);
  const [_filterComKey, setFilterComKey] = useState(0);
  const [_isFilterVisible, setIsFilterVisible] = useState(false);
  const [chartFullScreen, setChartFullScreen] = useState(false);
  const [chartComKey, setChartComKey] = useState(0);
  const [chartType, setChartType] = useState<'pie' | 'bar' | 'line' | 'area'>('pie');
  const [chartDefaultValue, setChartDefaultValue] = useState({ id: 'pie', label: 'Pie Chart' });
  const [chartData, setChartData] = useState({
    current: 0,
    days_1_30: 0,
    days_31_60: 0,
    days_61_90: 0,
    over_90_days: 0,
    total_outstanding: 0,
  });

  const columns = useMemo<ITablePropertyColumn[]>(
    () => [
      {
        id: 'insurer_name',
        header: t('debtor_name'),
        accessorKey: 'insurer_name',
        sort: true,
        cell: ({ cell }: { cell: any }) => cell.getValue() || '-',
      },
      {
        id: 'total_outstanding',
        header: `${t('total_outstanding')} (${currency.code})`,
        accessorKey: 'total_outstanding',
        sort: true,
        align: 'right',
        cell: ({ cell }: { cell: any }) => <div className="amount-container">{thousandSeparator(cell.getValue()) || '-'}</div>,
      },
      {
        id: 'current',
        header: `${t('current')} (${currency.code})`,
        accessorKey: 'current',
        sort: true,
        align: 'right',
        cell: ({ cell }: { cell: any }) => <div className="amount-container">{thousandSeparator(cell.getValue()) || '-'}</div>,
      },
      {
        id: 'days_1_30',
        header: `${t('days_1_30')} (${currency.code})`,
        accessorKey: 'days_1_30',
        sort: true,
        align: 'right',
        cell: ({ cell }: { cell: any }) => <div className="amount-container">{thousandSeparator(cell.getValue()) || '-'}</div>,
      },
      {
        id: 'days_31_60',
        header: `${t('days_31_60')} (${currency.code})`,
        accessorKey: 'days_31_60',
        sort: true,
        align: 'right',
        cell: ({ cell }: { cell: any }) => <div className="amount-container">{thousandSeparator(cell.getValue()) || '-'}</div>,
      },
      {
        id: 'days_61_90',
        header: `${t('days_61_90')} (${currency.code})`,
        accessorKey: 'days_61_90',
        sort: true,
        align: 'right',
        cell: ({ cell }: { cell: any }) => <div className="amount-container">{thousandSeparator(cell.getValue()) || '-'}</div>,
      },
      {
        id: 'over_90_days',
        header: `${t('over_90_days')} (${currency.code})`,
        accessorKey: 'over_90_days',
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
      const response = await fetchDebtorAgingSummaryReportTableData(params);
      if (response?.data) {
        const totals = response.data.reduce(
          (acc: any, curr: any) => ({
            current: acc.current + parseFloat(curr.current),
            days_1_30: acc.days_1_30 + parseFloat(curr.days_1_30),
            days_31_60: acc.days_31_60 + parseFloat(curr.days_31_60),
            days_61_90: acc.days_61_90 + parseFloat(curr.days_61_90),
            over_90_days: acc.over_90_days + parseFloat(curr.over_90_days),
            total_outstanding: acc.total_outstanding + parseFloat(curr.total_outstanding),
          }),
          {
            current: 0,
            days_1_30: 0,
            days_31_60: 0,
            days_61_90: 0,
            over_90_days: 0,
            total_outstanding: 0,
          },
        );
        setChartData(totals);
        setChartComKey((pre) => pre + 1);
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
        title={t('debtor_aging_summary')}
      />
      <div key={chartComKey}>
        <CustomChart
          type={chartType}
          series={
            chartType === 'pie'
              ? [chartData.current, chartData.days_1_30, chartData.days_31_60, chartData.days_61_90, chartData.over_90_days]
              : [
                  {
                    name: 'Outstanding Amount',
                    data: [chartData.current, chartData.days_1_30, chartData.days_31_60, chartData.days_61_90, chartData.over_90_days],
                  },
                ]
          }
          categories={['Current', '1-30 Days', '31-60 Days', '61-90 Days', 'Over 90 Days']}
          colors={['#088ab2', '#ffc107', '#fd7e14', '#dc3545', '#6c757d']}
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
          }}
        />
      </div>
    </div>
  );

  return (
    <div className="container-fluid mt-4">
      <div className="row">
        {/* Right Side - Table */}
        <div className="col-12 col-md-8">
          <div className={`data-table-container card custom-card ${isFullscreen ? 'dtc-fullscreen card-fullscreen' : ''}`}>
            <Table heading={<PageHeading title={t('debtor_aging_summary')} icon="sun-light" />} {...{ tableProperties, isFullscreen, setIsFullscreen, setIsCustColumnVisible, setIsFilterVisible }} />
          </div>
        </div>

        {/* Left Side - Card UI with Chart */}
        <div className="col-12 col-md-4 mb-4">{renderChart()}</div>
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

export default DebtorAgingSummaryReportList;
