'use server';

import { cookie } from '@/constans/StorageKeys';
import { getCookies } from '../handlers/cookiesHandler';
import { adminMenus, bottomMenus } from '@/constans/AdminMenus';

export const getThemeMode = async () => {
  const storedThemeMode = await getCookies(cookie.theme_mode);

  return storedThemeMode || 'light';
};

export const getAppMenu = async () => {
  return adminMenus;
};

export const getBottomMenu = async () => {
  return bottomMenus;
};
