import { useCurrency } from '@/contexts/CurrencyContext';

export function getCurrency() {
  const { currency } = useCurrency();
  return currency;
}
