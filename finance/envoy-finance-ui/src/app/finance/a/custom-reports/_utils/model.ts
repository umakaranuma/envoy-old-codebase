export interface IChart {
  id: number;
  title: string;
  type: string;
  json: string;
  description: null;
  created_at: Date;
  updated_at: Date;
  report_id_id: number;
  query: string;
  report_title: string;
  chart_data: IChartData;
}

export interface IChartData {
  labels: (string | number)[];
  datasets: { label: string; data: number[] }[];
}

export type Filter = { code: string; type: string; default: string; title: string };
export type Field = { code: string; label: string; dataType: string };
export type SkipColumn = { code: string; title: string };

export interface SqlToJsonResult {
  filters: Filter[];
  fields: Field[];
  skip_columns?: SkipColumn[];
}

export const initExcelFormData = {
  json_data: [
    {
      title: '',
      data: [],
    },
  ],
  styles: {
    common: {
      header: {
        font: { bold: true, color: '0000FF' },
        alignment: { horizontal: 'center' },
      },
    },
  },
  type: 'excel',
  report_id: '',
};

export const initPDFFormData = {
  html_content: '',
  type: 'pdf',
  report_id: '',
};
