import { IStorageOptions } from '@/interface/IStorageKey';
import { decrypt, encrypt, replacePlaceholders } from '../services/commonService';

type OptionProps = {
  replacements?: Record<string, string>;
  value?: any;
};

export function getLocalStorage(storageKey: IStorageOptions, options?: OptionProps) {
  if (typeof window !== 'undefined') {
    const { name, secretName, encrypted } = storageKey;
    let itemName = encrypted ? secretName || name : name;

    if (options?.replacements) {
      itemName = replacePlaceholders(encrypted ? secretName || name : name, options?.replacements);
    }

    let itemValue = '';
    const storedValues = localStorage.getItem(itemName);

    if (storedValues) {
      itemValue = JSON.parse(storedValues);
    }

    if (encrypted && itemValue) {
      try {
        const decryptedValue = decrypt(itemValue);
        return decryptedValue;
      } catch (error) {
        console.error('Error during decryption:', error);
        return null;
      }
    }

    return itemValue || null;
  }

  return null;
}

export function setLocalStorage(storageKey: IStorageOptions, options?: OptionProps) {
  const { name, secretName, encrypted } = storageKey;
  let itemName = encrypted ? secretName || name : name;

  if (options?.replacements) {
    itemName = replacePlaceholders(encrypted ? secretName || name : name, options?.replacements);
  }

  if (encrypted) {
    const encryptedValue = encrypt(options?.value);
    localStorage.setItem(itemName, JSON.stringify(encryptedValue));
  } else {
    localStorage.setItem(itemName, JSON.stringify(options?.value));
  }
}

export function clearAllLocalStorage() {
  localStorage.clear();
}

export const clearLocalStorage = (storageKey: IStorageOptions, options?: OptionProps) => {
  const { name, secretName, encrypted = false } = storageKey;
  let itemName = encrypted ? secretName || name : name;

  if (options?.replacements) {
    itemName = replacePlaceholders(encrypted ? secretName || name : name, options?.replacements);
  }

  localStorage.removeItem(itemName);
};
