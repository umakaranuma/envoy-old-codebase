import CryptoJS from 'crypto-js';
import moment from 'moment';
import { fileUploader } from './storageService';

export function replacePlaceholders(template: string, replacements: any): string {
  return template.replace(/\${(\w+)}/g, (_, match) => {
    return replacements[match] !== undefined ? replacements[match] : '';
  });
}

export function encrypt(value: any): any {
  const secretKey = process.env.CRYPT_SECRET_KEY || '';
  const encryptedValue = CryptoJS.AES.encrypt(JSON.stringify(value), secretKey).toString();

  // Convert the encrypted value to Base64 to remove special characters
  const base64EncryptedValue = Buffer.from(encryptedValue).toString('base64');

  return base64EncryptedValue;
}

export function decrypt(encryptedValue: any): any {
  const secretKey = process.env.CRYPT_SECRET_KEY || '';

  try {
    // Decode Base64 before decrypting
    const base64DecodedValue = Buffer.from(encryptedValue, 'base64').toString('utf-8');

    const bytes = CryptoJS.AES.decrypt(base64DecodedValue, secretKey);
    const decryptedValue = JSON.parse(bytes.toString(CryptoJS.enc.Utf8));
    return decryptedValue;
  } catch (error) {
    console.error('Error decrypting value:', error);
    return '';
  }
}

export function generateFileName() {
  const timestamp = Date.now();
  // const randomString = Math.random().toString(36).substring(2, 5);
  return `${timestamp}`;
}

export const handleFileUpload = async (resource: File | null, fileIdentifier: string = 'doc', folder: string = 'envoy') => {
  if (!resource) {
    return null;
  }
  const formData = new FormData();
  formData.append('file', resource);
  const fileExtension = resource.name.split('.').pop();
  const fileName = `${fileIdentifier}_${generateFileName()}.${fileExtension}`;
  const key = await fileUploader(formData, folder);
  return { key: key, name: fileName, type: fileExtension };
};

export function getQueryParamValue(paramName: string): string {
  if (typeof window !== 'undefined') {
    const searchParams = new URLSearchParams(window.location.search);
    return searchParams.get(paramName) as string;
  }

  return '';
}

export const ucFirst = (str: string): string => str.charAt(0).toUpperCase() + str.slice(1).toLowerCase();

// export const handleFilterInputChange = ({
//   setFilter,
//   key,
//   value,
//   operation = '=',
//   valueType = 'T',
// }: {
//   setFilter: (prevFilterData: any) => any;
//   key: string;
//   value: any;
//   operation?: '=' | '>' | '<' | '<>' | 'LIKE';
//   valueType?: 'A' | 'T';
// }) => {
//   setFilter((prevFilterData: any) => ({
//     ...prevFilterData,
//     [key]: {
//       o: operation,
//       v: value,
//       t: valueType,
//     },
//   }));
// };

export const handleFilterInputChange = ({
  setFilter,
  key,
  value,
  operation = '=',
  valueType = 'T',
}: {
  setFilter: (prevFilterData: any) => any;
  key: string;
  value: any;
  operation?: '=' | '>' | '<' | '<>' | 'LIKE';
  valueType?: 'A' | 'T';
}) => {
  setFilter((prevFilterData: any) => {
    // Check if value is empty (null, empty string, or empty array)
    const isEmpty = value === null || value === '' || (Array.isArray(value) && value.length === 0);

    if (isEmpty) {
      // Remove the key from the filter object
      const { [key]: _, ...rest } = prevFilterData;
      return rest;
    }

    // Otherwise, update the filter
    return {
      ...prevFilterData,
      [key]: {
        o: operation,
        v: value,
        t: valueType,
      },
    };
  });
};

export const isEmptyObj = (obj: any) => Object.keys(obj).length === 0;

export const convertToString = (array: any[], key: string) => {
  // Extract the primary key from the tableData and filter out null values
  const serviceProviderIds = array.map((item: any) => item[key]).filter((id: any) => id !== null);

  // Remove duplicates using Set and convert back to an array
  const uniqueServiceProviderIds = Array.from(new Set(serviceProviderIds));

  // Join the IDs with a comma separator and return as a string
  return uniqueServiceProviderIds.join(',');
};

export const convertToMap = (array: any[], key: string) => {
  // Define result as an object with number keys and any values (to store the entire object)
  const result: { [key: number]: any } = {};

  array.forEach((item) => {
    const id = item[key];
    if (id && !result[id]) {
      // Group all data under the primary key key
      result[id] = { ...item };
    }
  });

  return result;
};

// Function to capitalize all letters in a string
export const capitalizeAllLetters = (str: string): string => {
  return str.toUpperCase();
};

export const formatDate = (dateString: string, formatType: string = 'YYYY-MM-DD') => {
  if (!dateString) {
    return '-';
  }
  const date = moment(dateString);
  return date.isValid() ? date.format(formatType) : '-';
};

export function hexToRgba(hex: string, opacity: number) {
  const bigint = parseInt(hex.replace('#', ''), 16);
  const r = (bigint >> 16) & 255;
  const g = (bigint >> 8) & 255;
  const b = bigint & 255;

  return `rgba(${r}, ${g}, ${b}, ${opacity})`;
}

export const getTimeFromTimestamps = (dateString: string) => {
  if (!dateString) {
    return '-';
  }

  const date = new Date(dateString);
  const hours = date.getHours().toString().padStart(2, '0');
  const minutes = date.getMinutes().toString().padStart(2, '0');
  return `${hours}:${minutes}`;
};

export function thousandSeparator(number: number | string): string {
  if (number === undefined || number === null || number === '') {
    return '0.00';
  }

  const numStr = String(number);
  if (isNaN(Number(numStr))) {
    return '0.00';
  }

  const [integerPart, decimalPart] = numStr.split('.');

  // Add commas to the integer part
  const formattedInteger = integerPart.replace(/\B(?=(\d{3})+(?!\d))/g, ',');

  // Combine with decimal part if it exists
  return decimalPart ? `${formattedInteger}.${decimalPart.slice(0, 2)}` : formattedInteger;
}

export function snakeToTitleCase(input: string): string {
  if (!input || input.trim() === '') {
    return '';
  }

  return input
    .split('_')
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
}

export const getCurrentDate = () => {
  const now = new Date();
  const year = now.getFullYear();
  const month = String(now.getMonth() + 1).padStart(2, '0');
  const day = String(now.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
};

export function generateHtml(data: any) {
  // Extract table headers from keys
  const headers = Object.keys(data[0]);

  // Build table header row
  const headerRow = headers.map((h) => `<th>${h}</th>`).join('');

  // Build table body rows
  const bodyRows = data.map((data: any) => '<tr>' + headers.map((h) => `<td>${data[h] !== null ? data[h] : ''}</td>`).join('') + '</tr>').join('');

  // Final HTML
  return `
    <html>
      <body>
        <h1>Policy Data</h1>
        <table border="1" cellspacing="0" cellpadding="5">
          <tr>${headerRow}</tr>
          ${bodyRows}
        </table>
      </body>
    </html>
  `;
}
