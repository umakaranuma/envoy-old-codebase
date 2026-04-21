import React, { useEffect, useMemo, useState } from 'react';
import { CustomizeColumn, useCustomizeColumn } from '@/components/others/CustomizeColumn';
import PageHeading from '@/components/others/PageHeading';
import { useTrans } from '@/helpers/services/lang/langService';
import { ITablePropertyColumn } from '@/interface/ICommon';
import { useAsyncTable } from '@apptimus-ui/table';
import Table from '@/components/table-properties/Table';
import { filterReducer } from '@/helpers/services/dataReducer';
import { fetchCashFlowStatementsTableData } from '../../service';
import { formatDate, thousandSeparator } from '@/helpers/services/commonService';
import { Modal } from '@apptimus-ui/modal';
import { ChartType } from '../../model';
import CustomChart from '../CustomChart';
import ReportHeadingSection from '../ReportHeadingSection';
import { getCurrency } from '@/helpers/services/currencyService';

function CashFlowStatementsList({ tableVers }: { tableVers: number; onView: Function; onEdit: Function; handleOnDelete: Function }) {
  const t = useTrans('label.general_ledger,otr.common');
  const tableName = 'cash flow statements';
  const currency = getCurrency();
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [isCustColumnVisible, setIsCustColumnVisible] = useState(false);
  const [tableColumnVers, setTableColumnVers] = useState(0);
  const [_filterComKey, setFilterComKey] = useState(0);
  const [_isFilterVisible, setIsFilterVisible] = useState(false);
  const [chartFullScreen, setChartFullScreen] = useState(false);
  const [chartComKey, setChartComKey] = useState(0);
  const [chartType, setChartType] = useState<ChartType>('line');
  const [chartDefaultValue, setChartDefaultValue] = useState({ id: 'line', label: 'Line Chart' });
  const [chartData, setChartData] = useState({
    dates: [] as string[],
    inflows: [] as number[],
    outflows: [] as number[],
    netCashflow: [] as number[],
  });

  // Prepare chart series data based on chart type
  const getChartSeries = (type: ChartType) => {
    if (type === 'pie') {
      const totalInflows = chartData.inflows.reduce((sum, val) => sum + val, 0);
      const totalOutflows = chartData.outflows.reduce((sum, val) => sum + val, 0);
      const totalNet = chartData.netCashflow.reduce((sum, val) => sum + val, 0);
      return [totalInflows, totalOutflows, totalNet];
    }

    return [
      {
        name: 'Cash Inflows',
        data: chartData.inflows,
      },
      {
        name: 'Cash Outflows',
        data: chartData.outflows,
      },
      {
        name: 'Net Cashflow',
        data: chartData.netCashflow,
      },
    ];
  };

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
        id: 'cash_inflows',
        header: `${t('cash_inflows')} (${currency.code})`,
        accessorKey: 'cash_inflows',
        sort: true,
        align: 'right',
        cell: ({ cell }: { cell: any }) => <div className="amount-container">{thousandSeparator(cell.getValue()) || '-'}</div>,
      },
      {
        id: 'cash_outflows',
        header: `${t('cash_outflows')} (${currency.code})`,
        accessorKey: 'cash_outflows',
        sort: true,
        align: 'right',
        cell: ({ cell }: { cell: any }) => <div className="amount-container">{thousandSeparator(cell.getValue()) || '-'}</div>,
      },
      {
        id: 'net_cash_flow',
        header: `${t('net_cashflow')} (${currency.code})`,
        accessorKey: 'net_cash_flow',
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
      const response = await fetchCashFlowStatementsTableData(params);
      if (response?.data) {
        const data = response.data;
        const inflows = data.map((item: any) => parseFloat(item.cash_inflows));
        const outflows = data.map((item: any) => parseFloat(item.cash_outflows));
        const netCashflow = data.map((item: any) => parseFloat(item.net_cash_flow));

        setChartData({
          dates: data.map((item: any) => item.date),
          inflows,
          outflows,
          netCashflow,
        });
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
        title={t('cash_flow_analysis')}
      />
      <div key={chartComKey}>
        <CustomChart
          type={chartType}
          series={getChartSeries(chartType)}
          categories={chartType === 'pie' ? ['Total Inflows', 'Total Outflows', 'Net Cashflow'] : chartData.dates}
          options={{
            chart: {
              toolbar: { show: true },
            },
            stroke: {
              curve: 'smooth',
            },
            legend: {
              position: 'top',
              horizontalAlign: 'right',
            },
            tooltip: {
              shared: true,
              intersect: false,
              y: {
                formatter: (val: number) => `${currency.code} ${val.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`,
              },
            },
            ...(chartType !== 'pie' && {
              xaxis: {
                categories: chartData.dates,
              },
              yaxis: {
                labels: {
                  formatter: (val) => `${currency.code} ${val.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`,
                },
              },
            }),
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
          height={chartFullScreen ? 350 : 300}
        />
      </div>
    </div>
  );

  return (
    <div className="container-fluid mt-4">
      <div className="row">
        {/* Left Side - Table */}
        <div className="col-12 col-md-8">
          <div className={`data-table-container card custom-card ${isFullscreen ? 'dtc-fullscreen card-fullscreen' : ''}`}>
            <Table heading={<PageHeading title={t('reason')} icon="sun-light" />} {...{ tableProperties, isFullscreen, setIsFullscreen, setIsCustColumnVisible, setIsFilterVisible }} />
          </div>
        </div>

        {/* Right Side - Card UI with CommonChart */}
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

export default CashFlowStatementsList;
