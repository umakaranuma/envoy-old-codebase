'use server';

import { cookie } from '@/constans/StorageKeys';
import { getCookies } from '../handlers/cookiesHandler';

export const getThemeMode = async () => {
  const storedThemeMode = await getCookies(cookie.theme_mode);

  return storedThemeMode || 'light';
};

export async function convertMenuStringToArray(menuString: string) {
  try {
    // First, replace template literals with regular strings
    const withoutTemplateLiterals = menuString.replace(/`([^`]+)`/g, '"$1"');

    // Then, replace property names with quoted versions, but be careful with arrays
    const formattedString = withoutTemplateLiterals
      .replace(/(\w+):/g, '"$1":') // Add quotes around property names
      .replace(/'/g, '"') // Replace single quotes with double quotes
      .replace(/\n/g, '') // Remove newlines
      .replace(/\s+/g, ' ') // Normalize whitespace
      .replace(/(\w+):\s*\[/g, '"$1": [') // Handle array properties
      .replace(/(\w+):\s*{/g, '"$1": {') // Handle object properties
      .replace(/(\w+):\s*"/g, '"$1": "') // Handle string properties
      .replace(/(\w+):\s*(\d+)/g, '"$1": $2') // Handle number properties
      .replace(/(\w+):\s*true/g, '"$1": true') // Handle boolean true
      .replace(/(\w+):\s*false/g, '"$1": false') // Handle boolean false
      .replace(/(\w+):\s*null/g, '"$1": null') // Handle null
      .trim();

    // Then parse the JSON string
    return JSON.parse(formattedString);
  } catch (error) {
    console.error('Error parsing menu string:', error);
    return [];
  }
}
