import { ApexOptions } from 'apexcharts';

interface MappedChart {
  type: 'line' | 'bar' | 'area' | 'donut' | 'scatter';
  options: ApexOptions;
  series: any;
}

export const mapChartType = (type: string, data: any): MappedChart => {
  let chartType: 'line' | 'bar' | 'area' | 'donut' | 'scatter' = 'line';
  let options: ApexOptions = {};
  let series: any;

  // Helper function to extract numeric value
  const getNumericValue = (value: any, idx: number) => {
    if (typeof value === 'number') return value;
    const num = Number(value);
    return isNaN(num) ? idx + 1 : num;
  };

  switch (type) {
    /** ---------------- BAR CHARTS ---------------- **/
    case 'single-bar':
      chartType = 'bar';
      options = {
        chart: { type: chartType, stacked: false },
        plotOptions: { bar: { horizontal: false } },
        xaxis: {
          categories: Array.isArray(data) ? data.map((item: any) => item.label || '') : [],
        },
      };
      series = [
        {
          name: 'Value',
          data: Array.isArray(data) ? data.map((item: any, idx: number) => getNumericValue(item.value, idx)) : [],
        },
      ];
      break;

    case 'stacked-bar':
      chartType = 'bar';
      options = {
        chart: { type: chartType, stacked: true },
        plotOptions: { bar: { horizontal: false } },
        xaxis: {
          categories: data?.labels || [],
        },
      };
      series = (data?.datasets || []).map((ds: any) => ({
        name: ds.label,
        data: ds.data.map((val: any, idx: number) => getNumericValue(val, idx)),
      }));
      break;

    case 'group-bar':
      chartType = 'bar';
      options = {
        chart: { type: chartType, stacked: false },
        plotOptions: { bar: { horizontal: false } },
        xaxis: {
          categories: data?.labels || [],
        },
      };
      series = (data?.datasets || []).map((ds: any) => ({
        name: ds.label,
        data: ds.data.map((val: any, idx: number) => getNumericValue(val, idx)),
      }));
      break;

    /** ---------------- LINE CHARTS ---------------- **/
    case 'single-line':
      chartType = 'line';
      options = {
        chart: { type: chartType },
        stroke: { curve: 'smooth' },
        xaxis: {
          categories: Array.isArray(data) ? data.map((item: any) => item.label || '') : [],
        },
      };
      series = [
        {
          name: 'Value',
          data: Array.isArray(data) ? data.map((item: any, idx: number) => getNumericValue(item.value, idx)) : [],
        },
      ];
      break;

    case 'multi-line':
      chartType = 'line';
      options = {
        chart: { type: chartType },
        stroke: { curve: 'smooth' },
        xaxis: {
          categories: data?.labels || [],
        },
      };
      series = (data?.datasets || []).map((ds: any) => ({
        name: ds.label,
        data: ds.data.map((val: any, idx: number) => getNumericValue(val, idx)),
      }));
      break;

    /** ---------------- AREA CHARTS ---------------- **/
    case 'single-area':
      chartType = 'area';
      options = {
        chart: { type: chartType },
        stroke: { curve: 'smooth' },
        xaxis: {
          categories: Array.isArray(data) ? data.map((item: any) => item.label || '') : [],
        },
      };
      series = [
        {
          name: 'Value',
          data: Array.isArray(data) ? data.map((item: any, idx: number) => getNumericValue(item.value, idx)) : [],
        },
      ];
      break;

    case 'multi-area':
      // Handle both array format and labels/datasets format
      if (Array.isArray(data)) {
        // For the multi-area chart in your API response that uses array format
        const xAxisKey = 'Due Date'; // or whichever field should be on x-axis
        const yAxisKeys = ['Invoice Amount', 'Outstanding Amount', 'Invoice Paid Amount'];

        options = {
          chart: { type: 'area' },
          stroke: { curve: 'smooth' },
          xaxis: {
            categories: data.map((item: any) => item[xAxisKey] || ''),
          },
        };

        series = yAxisKeys.map((key) => ({
          name: key,
          data: data.map((item: any) => getNumericValue(item[key], 0)),
        }));
      } else {
        // Standard labels/datasets format
        options = {
          chart: { type: 'area' },
          stroke: { curve: 'smooth' },
          xaxis: { categories: data?.labels || [] },
        };
        series = (data?.datasets || []).map((ds: any) => ({
          name: ds.label,
          data: ds.data.map((val: any, idx: number) => getNumericValue(val, idx)),
        }));
      }
      break;

    /** ---------------- PIE / DONUT ---------------- **/
    case 'donut-pie':
      chartType = 'donut';
      series = Array.isArray(data) ? data.map((item: any) => getNumericValue(item.value, 0)) : [];
      options = {
        chart: { type: chartType },
        legend: { position: 'bottom' },
        labels: Array.isArray(data) ? data.map((item: any) => item.label || '') : [],
        dataLabels: { enabled: true },
      };
      break;

    /** ---------------- SCATTER ---------------- **/
    case 'scatter-plot':
      chartType = 'scatter';
      if (data?.data && Array.isArray(data.data)) {
        series = [
          {
            name: 'Scatter',
            data: data.data.map((item: any, idx: number) => ({
              x: getNumericValue(item[data.labels?.x], idx), // Convert x to number
              y: getNumericValue(item[data.labels?.y], idx),
            })),
          },
        ];
      } else {
        series = [];
      }
      options = {
        chart: { type: chartType },
        markers: { size: 5 },
      };
      break;

    /** ---------------- DEFAULT (LINE) ---------------- **/
    default:
      chartType = 'line';
      options = {
        chart: { type: chartType },
        stroke: { curve: 'smooth' },
        xaxis: { categories: data?.labels || [] },
      };
      series = (data?.datasets || []).map((ds: any) => ({
        name: ds.label,
        data: ds.data.map((val: any, idx: number) => getNumericValue(val, idx)),
      }));
  }

  return { type: chartType, options, series };
};
