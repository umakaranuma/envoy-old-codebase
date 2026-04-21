import { IApiResponseData, INetLinkResponse } from '@/interface/ICommon';

export function responseHandling(response: INetLinkResponse): IApiResponseData {
  switch (response.statusCode) {
    case 404:
      console.log('Response Data (404: Not Found):', response.responseData?.message);
      break;
    case 403:
      console.log('Response Data (403: Forbidden):', response.responseData?.message);
      break;
    case 500:
      console.log('Response Data (500: Internal Server Error):', response.responseData?.message);
      break;
    case 417:
      console.log('Response Data (417: Validation Error):', response.responseData?.message);
      break;
    case 401:
      console.log('Response Data (401: Unauthorized):', response.responseData?.message);
      break;
    case 409:
      console.log('Response Data (409: Conflict):', response.responseData?.message);
      break;
    case 429:
      break;
    default:
      break;
  }

  const r: IApiResponseData = {
    is_success: response.responseData?.is_success || false,
    message: response.responseData?.message || '',
    status_code: response.statusCode,
    result: response.responseData?.result || {},
    system_code: response.responseData?.system_code || '',
  };

  return r;
}
