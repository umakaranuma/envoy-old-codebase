import React from 'react';
import ReactApexChart from 'react-apexcharts';
import type { ApexOptions } from 'apexcharts';

export type ChartType = 'pie' | 'bar' | 'line' | 'area' | 'donut' | 'radar' | 'radialBar';

interface CommonChartProps {
  type: ChartType;
  series: ApexAxisChartSeries | ApexNonAxisChartSeries;
  categories?: string[];
  colors?: string[];
  height?: number;
  width?: number | string;
  showLegend?: boolean;
  showToolbar?: boolean;
  className?: string;
  options?: Partial<ApexOptions>;
  onDataPointSelection?: (event: any, chartContext: any, config: any) => void;
}

function CustomChart({
  type,
  series,
  categories,
  colors = ['#008FFB', '#00E396', '#FEB019', '#FF4560', '#775DD0', '#3F51B5', '#546E7A', '#D4526E', '#8D5B4C', '#F86624'],
  height = 350,
  width = '100%',
  showLegend = true,
  showToolbar = true,
  className = '',
  options = {},
  onDataPointSelection,
}: CommonChartProps) {
  const baseOptions: ApexOptions = {
    chart: {
      type,
      toolbar: {
        show: showToolbar,
      },
      events: {
        dataPointSelection: onDataPointSelection,
      },
    },
    colors,
    legend: {
      position: ['pie', 'donut', 'radialBar'].includes(type) ? 'bottom' : 'top',
      horizontalAlign: 'center',
      show: showLegend,
    },
    ...options,
  };

  // Add xaxis categories if provided and needed
  if (categories && ['bar', 'line', 'area', 'radar'].includes(type)) {
    baseOptions.xaxis = {
      ...baseOptions.xaxis,
      categories,
    };
  }

  // Add labels for pie/donut/radialBar charts if categories are provided
  if (categories && ['pie', 'donut', 'radialBar'].includes(type)) {
    baseOptions.labels = categories;
  }

  return (
    <div className={`common-chart ${className}`} style={{ width }}>
      <ReactApexChart options={baseOptions} series={series} type={type} height={height} width={width} />
    </div>
  );
}

export default CustomChart;
