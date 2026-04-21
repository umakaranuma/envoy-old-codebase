export interface INetLinkResponse {
  success: boolean;
  statusCode: number;
  message: string;
  responseData?: IApiResponseData;
  response?: any;
  exception?: any;
}

export interface IApiResponseData {
  is_success: boolean;
  message: string;
  status_code: number;
  result?: any;
  system_code?: string;
}

interface IValidationErrorDetail {
  error_type: string;
  tokens: any;
}

export interface IValidationErrors {
  [key: string]: IValidationErrorDetail[];
}

export interface ITablePropertyColumn {
  id?: string;
  header?: string;
  accessorKey?: string;
  sort?: boolean;
  customizable?: boolean;
  visibilityLock?: boolean;
  isHidden?: boolean;
  order?: number;
  entity?: string;
  accessorFn?: any;
}

export interface IAppLanguage {
  name: string;
  code: string;
}
