import { UserLocale } from '@/components/layout/AdminLayout';
import dictionary from '@/locale/dictionary';
import { useContext } from 'react';

/**
 * A custom React hook for handling translations.
 *
 * This hook retrieves translations for the current user's locale and specified modules.
 * It merges translations from multiple modules (if provided) and returns a function
 * to access specific translation keys.
 *
 * @param {string} [modules] - A comma-separated string of module names to load translations from.
 *                             Example: "msg.user,msg.role"
 * @returns {(key: string) => string} - A function that takes a translation key and returns the corresponding value.
 *                                      If the key is not found, it returns "UNKNOWN_KEY".
 *
 * @example
 * const trans = useTrans('msg.user,msg.role');
 * console.log(trans('users')); // Output: "Users" (if the key exists) or "UNKNOWN_KEY" (if the key is missing)
 */
export function useTrans(modules?: string) {
  // Retrieve the current user's locale from the context
  const userLocale = useContext(UserLocale);

  // Split the modules string into an array of individual modules
  const modulesArray = modules ? modules.split(',') : [];

  // Initialize an empty object to store merged translations
  let translation: any = {};

  // Iterate over each module and merge its translations into the `translation` object
  modulesArray.forEach((module) => {
    // Construct the key in the format `${locale}.${module}`
    const key: any = `${userLocale}.${module}`;

    // Merge the translations from the current module into the `translation` object
    translation = { ...translation, ...dictionary[key] };
  });

  // Return a function that takes a translation key and returns the corresponding value with token replacements
  return (key: string, tokens?: any) => replaceTokens(translation[key], tokens) || 'UNKNOWN_KEY';
}

// Function to replace placeholders in the format {{}} with corresponding values from the tokens object
export function replaceTokens(template: string, tokens: any): string {
  try {
    return template.replace(/{{(\w+)}}/g, (_, match) => {
      return tokens[match] !== undefined ? tokens[match] : '';
    });
  } catch (error) {
    return template;
  }
}
