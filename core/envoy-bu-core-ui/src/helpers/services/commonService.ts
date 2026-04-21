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
//   if (value === '' || value === null || value === undefined || (Array.isArray(value) && value.length === 0)) {
//     setFilter({});
//     return;
//   }
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

export function hexToRgba(hex: string, opacity: number) {
  const bigint = parseInt(hex.replace('#', ''), 16);
  const r = (bigint >> 16) & 255;
  const g = (bigint >> 8) & 255;
  const b = bigint & 255;

  return `rgba(${r}, ${g}, ${b}, ${opacity})`;
}

export function thousandSeparator(number: number | string): string {
  if (number === undefined || number === null || number === '') {
    return '-';
  }

  const numStr = String(number);
  if (isNaN(Number(numStr))) {
    return '-';
  }

  const [integerPart, decimalPart] = numStr.split('.');

  // Add commas to the integer part
  const formattedInteger = integerPart.replace(/\B(?=(\d{3})+(?!\d))/g, ',');

  // Combine with decimal part if it exists
  return decimalPart ? `${formattedInteger}.${decimalPart}` : formattedInteger;
}

export const formatDate = (dateString: string, formatType: string = 'YYYY-MM-DD') => {
  if (!dateString) {
    return '-';
  }
  const date = moment(dateString);
  return date.isValid() ? date.format(formatType) : '-';
};

export const formatPhoneNumber = (number: string, code: string = '+94') => {
  // Check if number is null, undefined, or empty
  if (!number || typeof number !== 'string') {
    return '';
  }

  // Remove non-digits from number
  const cleanedNumber = number.replace(/\D/g, '');

  // Special case: Sri Lanka (+94 with 9 digits)
  if (code === '+94' && cleanedNumber.length === 9) {
    return `${code} ${cleanedNumber.slice(0, 2)} ${cleanedNumber.slice(2, 5)} ${cleanedNumber.slice(5)}`;
  }

  // Generic rule: split number into 2–3 digit chunks
  const groups: string[] = [];
  let i = 0;
  while (i < cleanedNumber.length) {
    if (cleanedNumber.length - i > 4) {
      groups.push(cleanedNumber.slice(i, i + 2));
      i += 2;
    } else {
      groups.push(cleanedNumber.slice(i));
      break;
    }
  }

  return `${code} ${groups.join(' ')}`;
};

export const capitalizeFirstLetter = (str: string): string => {
  if (!str) return '';

  return str
    .split('_') // split by underscore
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase()) // capitalize
    .join(' '); // join with space
};

export const removeCountryCode = (phoneNumber: string, countryCode: string) => {
  if (!phoneNumber || !countryCode) return phoneNumber;

  // If phoneNumber is exactly the country code (with or without '+'), return empty
  if (phoneNumber === countryCode || phoneNumber === `+${countryCode}`) {
    return '';
  }

  // If phoneNumber starts with the country code (with '+'), return empty
  if (phoneNumber.startsWith(`+${countryCode}`)) {
    return '';
  }

  // Otherwise, return the original phone number
  return phoneNumber;
};

export const handleFileUpload = async (resource: File | null, fileIdentifier: string = 'doc', folder: string = 'core') => {
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

export function generateFileName() {
  const timestamp = Date.now();
  // const randomString = Math.random().toString(36).substring(2, 5);
  return `${timestamp}`;
}

export function getNotificationTime(dateString: string): string {
  if (!dateString) return '';
  const now = moment();
  const date = moment(dateString);
  if (!date.isValid()) return '';

  const diffSeconds = now.diff(date, 'seconds');
  const diffMinutes = now.diff(date, 'minutes');
  const diffHours = now.diff(date, 'hours');

  if (diffSeconds < 60) {
    return 'just now';
  } else if (diffMinutes < 60) {
    return `${diffMinutes} minute${diffMinutes === 1 ? '' : 's'} ago`;
  } else if (diffHours < 24) {
    return `${diffHours} hour${diffHours === 1 ? '' : 's'} ago`;
  } else {
    return date.format('hh:mm A');
  }
}
