'use client';

import React, { createContext, useContext, useState, ReactNode, useCallback } from 'react';

export interface ICurrencyContext {
  code: string;
  symbol: string;
}

interface CurrencyContextType {
  currency: ICurrencyContext;
  setCurrency: (currency: ICurrencyContext) => void;
}

const CurrencyContext = createContext<CurrencyContextType>({
  currency: { code: 'LKR', symbol: '₨' },
  setCurrency: () => {},
});

export const useCurrency = () => useContext(CurrencyContext);

export const CurrencyProvider = ({ children }: { children: ReactNode }) => {
  const [currency, setCurrencyState] = useState<ICurrencyContext>({ code: 'LKR', symbol: '₨' });

  const setCurrency = useCallback((currency: ICurrencyContext) => {
    setCurrencyState(currency);
  }, []);

  return <CurrencyContext.Provider value={{ currency, setCurrency }}>{children}</CurrencyContext.Provider>;
};
