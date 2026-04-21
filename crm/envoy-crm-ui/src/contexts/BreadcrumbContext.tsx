'use client';

import React, { createContext, useContext, useState, ReactNode, useCallback } from 'react';

interface CustomBreadcrumb {
  text: string;
  backurl: string;
}

interface BreadcrumbContextType {
  customBreadcrumb: CustomBreadcrumb | null;
  setCustomBreadcrumb: (breadcrumb: CustomBreadcrumb | null) => void;
}

const BreadcrumbContext = createContext<BreadcrumbContextType>({
  customBreadcrumb: null,
  setCustomBreadcrumb: () => {},
});

export const useBreadcrumb: any = () => useContext(BreadcrumbContext);

export const BreadcrumbProvider = ({ children }: { children: ReactNode }) => {
  const [customBreadcrumb, setCustomBreadcrumbState] = useState<CustomBreadcrumb | null>(null);

  const setCustomBreadcrumb = useCallback((breadcrumb: CustomBreadcrumb | null) => {
    setCustomBreadcrumbState(breadcrumb);
  }, []);

  return <BreadcrumbContext.Provider value={{ customBreadcrumb, setCustomBreadcrumb }}>{children}</BreadcrumbContext.Provider>;
};
