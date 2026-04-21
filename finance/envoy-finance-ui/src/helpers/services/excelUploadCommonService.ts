import sendRequest from 'apptimus-netlink';
import { responseHandling } from '../handlers/responseHandler';

export interface FlexField {
  name: string;
  dataType: string;
  dataValue: string;
}

export interface FieldMapping {
  systemField: string;
  excelField: string;
}

export interface MappingSubmitData {
  mappings: FieldMapping[];
  flexFields: FlexField[];
}

export interface ExcelMappingResponse {
  success: boolean;
  message: string;
  result: {
    headers: Array<{ key: number; value: string | number }>;
    rows: Array<Record<string, string>>;
  };
  system_code: number;
}

export const submitMapping = async (data: MappingSubmitData): Promise<any> => {
  try {
    const response = await sendRequest({
      url: `${process.env.FINANCE_PROXY_PREFIX}/api/mapping/attributes`,
      method: 'POST',
      data: data,
    });
    return responseHandling(response);
  } catch (error) {
    console.error('Error submitting mapping:', error);
    throw error;
  }
};

export const uploadExcelToJson = async (file: File): Promise<ExcelMappingResponse> => {
  const formData = new FormData();
  formData.append('file', file);

  try {
    const response = await fetch(`${process.env.UTILITIES_PROXY_PREFIX}/api/app/export/excel-to-json`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`Upload failed with status ${response.status}`);
    }

    const result = await response.json();

    if (result.success) {
      return result;
    } else {
      throw new Error(result.message || 'Failed to upload file');
    }
  } catch (error) {
    console.error('Error uploading Excel file:', error);
    throw error;
  }
};

export const getMappingPreview = async (mappingId: string): Promise<any> => {
  try {
    const response = await fetch(`${process.env.FINANCE_PROXY_PREFIX}/api/mapping/attributes/${mappingId}`, {
      method: 'GET',
    });

    if (!response.ok) {
      throw new Error(`Failed to get preview with status ${response.status}`);
    }

    const result = await response.json();
    return result;
  } catch (error) {
    console.error('Error getting mapping preview:', error);
    throw error;
  }
};
