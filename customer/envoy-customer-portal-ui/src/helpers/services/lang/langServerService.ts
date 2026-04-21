'use server';

import { cookie } from '@/constans/StorageKeys';
import { getCookies } from '@/helpers/handlers/cookiesHandler';
import { replaceTokens } from './langService';

/**
 * A server-side function for handling translations.
 *
 * This function retrieves translations for the current user's locale and specified modules.
 * It merges translations from multiple modules (if provided) and returns a function
 * to access specific translation keys.
 *
 * @param {string} [modules] - A comma-separated string of module names to load translations from.
 *                             Example: "msg.user,msg.role"
 * @returns {Promise<(key: string) => string>} - A function that takes a translation key and returns the corresponding value.
 *                                               If the key is not found, it returns "UNKNOWN_KEY".
 *
 * @example
 * const trans = await useServerTrans('msg.user,msg.role');
 * console.log(trans('users')); // Output: "Users" (if the key exists) or "UNKNOWN_KEY" (if the key is missing)
 */
export async function useServerTrans(modules?: string) {
  // Split the modules string into an array of individual modules
  const modulesArray = modules ? modules.split(',') : [];

  // Retrieve the current locale from cookies (fallback to 'en' if none found)
  const locale = (await getCookies(cookie.locale)) || 'en';

  let translation: Record<string, string> = {};

  // Create an array of promises for module imports
  const importPromises = modulesArray.map(async (module) => {
    try {
      // Convert module name like "msg.user" to a file path "/msg/user.ts"
      const dictionary = await import(`../../../locale/${locale}/${module.replace(/\./g, '/')}.ts`);

      // Merge the dictionary into the translations object
      translation = { ...translation, ...dictionary.default };
    } catch (error) {
      console.warn(`Translation module not found for: ${module}`);
    }
  });

  // Wait for all imports to complete
  await Promise.all(importPromises);

  // Return a function that takes a translation key and returns the corresponding value with token replacements
  return (key: string, tokens?: any) => replaceTokens(translation[key], tokens) || 'UNKNOWN_KEY';
}
