'use server';

import { IStorageOptions } from '@/interface/IStorageKey';
import { cookies } from 'next/headers';
import { decrypt, encrypt, replacePlaceholders } from '../services/commonService';

type OptionProps = {
  replacements?: Record<string, string>;
  value?: any;
  expires?: Date;
  maxAge?: number;
};

export async function getCookies(storageKey: IStorageOptions, options?: OptionProps) {
  const { name, secretName, encrypted } = storageKey;
  let cookieName = encrypted ? secretName || name : name;

  if (options?.replacements) {
    cookieName = replacePlaceholders(encrypted ? secretName || name : name, options?.replacements);
  }

  const cookieStore = await cookies();
  const cookieValue = cookieStore.get(cookieName)?.value;

  if (encrypted && cookieValue) {
    const decryptedValue = decrypt(cookieValue);
    return decryptedValue;
  }

  return cookieValue || null;
}

export async function setCookies(storageKey: IStorageOptions, options?: OptionProps) {
  const { name, secretName, encrypted } = storageKey;
  let cookieName = encrypted ? secretName || name : name;

  if (options?.replacements) {
    cookieName = replacePlaceholders(encrypted ? secretName || name : name, options?.replacements);
  }

  const cookieStore = await cookies();

  if (encrypted) {
    const encryptedValue = encrypt(options?.value);
    cookieStore.set(cookieName, encryptedValue, { expires: options?.expires, maxAge: options?.maxAge });
  } else {
    cookieStore.set(cookieName, options?.value, { expires: options?.expires, maxAge: options?.maxAge });
  }
}

export async function clearAllCookies() {
  const cookieStore = await cookies();
  cookieStore.getAll().map(async (cookie) => (await cookies()).delete(cookie.name));
}

export async function clearCookie(storageKey: IStorageOptions, options?: OptionProps) {
  const { name, secretName, encrypted } = storageKey;
  let cookieName = encrypted ? secretName || name : name;

  if (options?.replacements) {
    cookieName = replacePlaceholders(encrypted ? secretName || name : name, options?.replacements);
  }

  (await cookies()).delete(cookieName);
}
