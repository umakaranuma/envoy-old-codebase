export interface IFlexField {
  name: string;
  dataType: string;
  dataValue: string;
}

export interface IFieldMapping {
  systemField: string;
  excelField: string;
}

export interface IMappingSubmitData {
  mappings: IFieldMapping[];
  flexFields: IFlexField[];
}

export interface IExcelMappingResponse {
  success: boolean;
  message: string;
  result: {
    headers: Array<{ key: number; value: string | number }>;
    rows: Array<Record<string, string>>;
  };
  system_code: number;
}
