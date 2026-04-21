import { IApiResponseData } from './ICommon';

export interface UploadResultDetails {
  new_values?: Record<string, any>;
  updated_fields?: Record<string, { old_value: any; new_value: any }>;
  error?: string;
  mapping_id?: number;
}

export interface UploadResultItem {
  invoice_number: string;
  insurer_invoice_id: number;
  status: string;
  details: UploadResultDetails;
}

export interface UploadCounts {
  add_count: number;
  update_count: number;
  ignore_count: number;
  total_count: number;
}

export interface UploadResult {
  message?: string;
  processed_rows?: number;
  mappings?: number;
  flex_fields?: number;
  mapping_ids?: number[];
  results?: UploadResultItem[];
  counts?: UploadCounts;
}

export interface UploadSummaryData extends IApiResponseData {
  result?: UploadResult;
}
