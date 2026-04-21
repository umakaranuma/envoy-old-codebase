'use server';

import { cookie } from '@/constans/StorageKeys';
import { getCookies } from '../handlers/cookiesHandler';

export const getThemeMode = async () => {
  const storedThemeMode = await getCookies(cookie.theme_mode);

  return storedThemeMode || 'light';
};
