'use client';

import React, { useContext } from 'react';
import Image from 'next/image';
import { UserPermissions } from '../layout/AdminLayout';

export const withUserPermission = (Component: any, entity: string, action: string) => {
  const WrappedComponent = (props: any) => {
    if (!hasPermission(entity, [action])) {
      return <Image src={'/images/errors/403.png'} alt="403" width={1920} height={1080} className="w-100 h-100" />;
    }

    return <Component {...props} />;
  };

  WrappedComponent.displayName = `withUserPermission(${Component.displayName || Component.name || 'Component'})`;

  return WrappedComponent;
};

export function hasPermission(entity: string, actions: string[]): boolean {
  const perm = useContext(UserPermissions);

  return actions.some((action) => perm.includes(entity + '_' + action));
}

export const Permission = ({ children, entity, action }: { children: React.ReactNode; entity: string; action: string }) => {
  const hasPerm = hasPermission(entity, [action]);

  if (hasPerm) {
    return children;
  } else {
    return null;
  }
};
