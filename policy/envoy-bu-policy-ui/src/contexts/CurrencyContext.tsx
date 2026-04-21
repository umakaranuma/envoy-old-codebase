'use client';

import React, { createContext, useContext, useState, ReactNode, useCallback } from 'react';

type Currency = {
  code: string;
  symbol: string;
};

interface CurrencyContextType {
  currency: Currency;
  setCurrency: (currency: Currency) => void;
}

const CurrencyContext = createContext<CurrencyContextType>({
  currency: { code: 'LKR', symbol: '₨' },
  setCurrency: () => {},
});

export const useCurrency = () => useContext(CurrencyContext);

export const CurrencyProvider = ({ children }: { children: ReactNode }) => {
  const [currency, setCurrencyState] = useState<Currency>({ code: 'LKR', symbol: '₨' });

  const setCurrency = useCallback((newCurrency: Currency) => {
    setCurrencyState(newCurrency);
  }, []);

  return <CurrencyContext.Provider value={{ currency, setCurrency }}>{children}</CurrencyContext.Provider>;
};
