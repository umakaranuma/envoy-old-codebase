import { useTrans } from '@/helpers/services/lang/langService';
import { getAllCustomers, getAllContacts } from './api-service';

export const customerTypes = () => {
  const t = useTrans('label.accounts');
  return [
    { label: t('corporate'), value: 'Corporate' },
    { label: t('personal'), value: 'Personal' },
  ];
};

export async function fetchContacts(searchValue: any, currentPage: any) {
  const response = await getAllContacts({ search: searchValue, page: currentPage }, false);

  return response.result.data || [];
}

export async function fetchAllCustomers(searchValue: any, currentPage: any, type: string) {
  console.log('type', type);

  const response = await getAllCustomers({ search: searchValue, page: currentPage, type }, false);

  return response.result.data || [];
}
