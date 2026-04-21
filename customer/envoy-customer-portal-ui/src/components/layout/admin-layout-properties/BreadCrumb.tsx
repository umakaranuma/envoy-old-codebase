import { useTrans } from '@/helpers/services/lang/langService';
import { useParams, usePathname } from 'next/navigation';
import React, { useMemo } from 'react';
import { buildUrlWithParams } from './Sidebar';
import Link from 'next/link';
import { Flexicon } from '@apptimus-ui/flexicon';
import { MenuCategory } from '@/interface/IAdminLayout';

function BreadCrumb({ appMenu, appKey }: { appMenu: MenuCategory[]; appKey: string }) {
  const pathName = usePathname();
  const t = useTrans('otr.sidebar');
  const params = useParams();

  const findBreadcrumb = (menus: any, path: any) => {
    for (const menu of menus) {
      if (menu.matcher) {
        for (const matcher of menu.matcher) {
          if (buildUrlWithParams(matcher, params) === path) {
            return [menu];
          }
        }
      }
      if (menu.path && buildUrlWithParams(menu.path, params) === path) {
        return [menu];
      }
      if (menu.subMenus) {
        const subMenuPath: any = findBreadcrumb(menu.subMenus, path);
        if (subMenuPath.length) {
          return [menu, ...subMenuPath];
        }
      }
    }
    return [];
  };

  const breadcrumb = useMemo(() => {
    for (const category of appMenu) {
      const path = findBreadcrumb(category.menus, pathName);
      if (path.length) {
        return path;
      }
    }
    return [];
  }, [pathName]);

  return (
    <>
      {breadcrumb.length > 0 ? (
        <div className="header-element ms-1 fs-14 mb-4">
          <div className="d-flex align-items-center gap-2">
            <Link href={`/${appKey}/a/home`} className="text-muted clickable-text-primary d-flex align-items-center">
              <Flexicon icon="home-line" variant="line" size={18} />
            </Link>
            <Flexicon icon="chevron-right" variant="line" size={14} className="text-muted" />
            {breadcrumb.map((item, index) => (
              <React.Fragment key={index}>
                {index > 0 && <Flexicon icon="chevron-right" variant="line" size={14} className="text-muted" />}
                <div className={`text-muted ${index === breadcrumb.length - 1 ? 'text-primary fw-semibold' : ''}`}>{t(item.name)}</div>
              </React.Fragment>
            ))}
          </div>
        </div>
      ) : (
        <></>
      )}
    </>
  );
}

export default BreadCrumb;
