'use client';

import React, { createContext, useContext, useState, ReactNode, useCallback } from 'react';

interface Currency {
  code: string;
  symbol: string;
  id: number;
}

interface CurrencyContextType {
  currency: Currency;
  setCurrency: (currency: Currency) => void;
}

const defaultCurrency: Currency = {
  code: 'LKR',
  symbol: '₨',
  id: 2,
};

const CurrencyContext = createContext<CurrencyContextType>({
  currency: defaultCurrency,
  setCurrency: () => {},
});

export const useCurrency = () => useContext(CurrencyContext);

export const CurrencyProvider = ({ children }: { children: ReactNode }) => {
  const [currency, setCurrencyState] = useState<Currency>(defaultCurrency);

  const setCurrency = useCallback((currency: Currency) => {
    setCurrencyState(currency);
  }, []);

  return <CurrencyContext.Provider value={{ currency, setCurrency }}>{children}</CurrencyContext.Provider>;
};
