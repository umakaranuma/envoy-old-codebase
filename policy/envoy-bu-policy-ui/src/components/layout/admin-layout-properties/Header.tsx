import Image from 'next/image';
import Link from 'next/link';
import desktopDark from '../../../../public/logo/desktop-dark.png';
import desktopLogo from '../../../../public/logo/desktop-logo.png';
import toggleDark from '../../../../public/logo/toggle-dark.png';
import toggleLogo from '../../../../public/logo/toggle-logo.png';
import { setCookies } from '@/helpers/handlers/cookiesHandler';
import { cookie } from '@/constans/StorageKeys';
import { SVG } from '../../others/SVG';
import Profile from '../../others/page-related/Profile';
import { Flexicon } from '@apptimus-ui/flexicon';
import { Dropdown, DropdownItem } from '@apptimus-ui/dropdown';
import { appLanguages } from '@/constans/Common';
import { IAppLanguage } from '@/interface/ICommon';
import React, { useContext, useMemo } from 'react';
import { UserLocale } from '../AdminLayout';
import { capitalizeAllLetters } from '@/helpers/services/commonService';
import { useParams, usePathname, useRouter } from 'next/navigation';
import { buildUrlWithParams } from './Sidebar';
import { useTrans } from '@/helpers/services/lang/langService';
import { MenuCategory } from '@/interface/IAdminLayout';
import { useBreadcrumb } from '@/contexts/BreadcrumbContext';

export const Header = ({
  handleMenuToggleClick,
  themeMode,
  sbClosed,
  appMenu,
  hasNotifications,
}: {
  handleMenuToggleClick: Function;
  themeMode: 'light' | 'dark';
  sbClosed: boolean;
  appMenu: MenuCategory[];
  hasNotifications: boolean;
}) => {
  return (
    <div className="app-header">
      {/* Start::main-header-container */}
      <div className="main-header-container container-fluid d-flex align-items-center justify-content-between">
        <HeaderContentLeft {...{ handleMenuToggleClick, sbClosed, appMenu }} />
        <div className=" d-flex align-items-center">
          <HeaderContentRight themeMode={themeMode} hasNotifications={hasNotifications} />
        </div>
      </div>
      {/* End::main-header-container */}
    </div>
  );
};

const HeaderContentLeft = ({ handleMenuToggleClick, sbClosed, appMenu }: { handleMenuToggleClick: Function; sbClosed: boolean; appMenu: MenuCategory[] }) => {
  const pathName = usePathname();
  const t = useTrans('otr.sidebar');
  const params = useParams();
  const { customBreadcrumb } = useBreadcrumb();

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

  const findMenuItemByPath = (menus: any, targetPath: string): any => {
    for (const menu of menus) {
      // Check if menu path matches
      if (menu.path && buildUrlWithParams(menu.path, params) === targetPath) {
        return menu;
      }

      // Check matcher array
      if (menu.matcher) {
        for (const matcher of menu.matcher) {
          if (buildUrlWithParams(matcher, params) === targetPath) {
            return menu;
          }
        }
      }

      // Check matcherStartWith for partial matches
      if (menu.matcherStartWith && targetPath.startsWith(buildUrlWithParams(menu.matcherStartWith, params))) {
        return menu;
      }

      // Recursively search submenus
      if (menu.subMenus) {
        const found: any = findMenuItemByPath(menu.subMenus, targetPath);
        if (found) {
          return found;
        }
      }
    }
    return null;
  };

  const breadcrumb = useMemo(() => {
    for (const category of appMenu) {
      const path = findBreadcrumb(category.menus, pathName);

      if (path.length) {
        return path.map((item) => ({
          ...item,
          path: customBreadcrumb?.backurl || '/',
        }));
      }
    }

    // Generic fallback for other paths
    if (pathName && pathName !== '/a/dashboard') {
      const cleanPath = pathName.startsWith('/') ? pathName.slice(1) : pathName;
      const pathSegments = cleanPath.split('/').filter((segment) => segment && segment !== 'a');

      if (pathSegments.length > 0) {
        const breadcrumbItems: any[] = [];
        let currentPath = '';
        const usedMenuItems = new Set();

        for (let i = 0; i < pathSegments.length; i++) {
          const segment = pathSegments[i];
          currentPath += (currentPath ? '/' : '') + segment;
          const fullPath = '/' + currentPath;
          let foundMenuItem = null;

          for (const category of appMenu) {
            foundMenuItem = findMenuItemByPath(category.menus, fullPath);
            if (foundMenuItem && !usedMenuItems.has(foundMenuItem.name)) {
              usedMenuItems.add(foundMenuItem.name);
              break;
            }
          }

          breadcrumbItems.push({
            name: foundMenuItem?.name || segment.replace(/-/g, '_'),
            path: customBreadcrumb?.backurl || '/',
          });
        }

        return breadcrumbItems.slice(0, 2);
      }
    }

    return [];
  }, [pathName, appMenu, customBreadcrumb]);

  // Combine base breadcrumb with custom breadcrumb
  const finalBreadcrumb = useMemo(() => {
    if (customBreadcrumb) {
      return [
        ...breadcrumb,
        {
          name: customBreadcrumb.text,
          isCustom: true,
          backurl: customBreadcrumb.backurl || undefined,
        },
      ];
    }
    return breadcrumb;
  }, [breadcrumb, customBreadcrumb]);

  return (
    <div className="header-content-left">
      {/* Start::header-element */}
      <div className="header-element">
        <div className="horizontal-logo">
          <Link href={`/a/dashboard`} className="header-logo">
            <Image src={desktopLogo} width={140} alt="logo" className="desktop-logo" />
            <Image src={toggleLogo} alt="logo" width={40} className="toggle-logo" />
            <Image src={desktopDark} width={140} alt="logo" className="desktop-dark" />
            <Image src={toggleDark} alt="logo" width={40} className="toggle-dark" />
          </Link>
        </div>
      </div>
      {/* End::header-element */}

      {/* Start::header-element */}
      <div className="header-element">
        {/* Start::header-link */}
        <a onClick={(e) => (e.stopPropagation(), handleMenuToggleClick())} className="" role="button">
          <Flexicon icon={sbClosed ? 'menu-01' : 'menu-02'} variant="line" />
        </a>
        {/* End::header-link */}
      </div>
      {/* End::header-element */}

      <div className="header-element ms-4 fs-14 breadcrumb-mobile-hidden">
        <div className="d-flex align-items-center gap-2">
          <Link href={`/a/dashboard`} className="text-muted clickable-text-primary d-flex align-items-center">
            <Flexicon icon="home-line" variant="line" size={18} />
          </Link>
          <Flexicon icon="chevron-right" variant="line" size={14} className="text-muted" />
          {finalBreadcrumb.map((item, index) => {
            const isLastItem = index === finalBreadcrumb.length - 1;
            const isCustomItem = item.isCustom;
            console.log('item', item);

            return (
              <React.Fragment key={index}>
                {index > 0 && <Flexicon icon="chevron-right" variant="line" size={14} className="text-muted" />}
                {isCustomItem ? (
                  <div className="text-primary fw-semibold">{item.name}</div>
                ) : isLastItem ? (
                  <div className="text-primary fw-semibold">{item.name !== 'policy_requests' && t(item.name)}</div>
                ) : index === 0 ? (
                  <div className="fw-semibold text-muted">{t(item.name)}</div>
                ) : (
                  <Link
                    href={item.path}
                    className="text-muted clickable-breadcrumb-text"
                    onClick={() => {
                      console.log(item.path);
                    }}
                  >
                    {t(item.name)}
                  </Link>
                )}
              </React.Fragment>
            );
          })}
        </div>
      </div>
    </div>
  );
};

const HeaderContentRight = ({ themeMode, hasNotifications }: { themeMode: 'light' | 'dark'; hasNotifications: boolean }) => {
  const userLocale = useContext(UserLocale);
  const router = useRouter();
  const changeThemeMode = async () => {
    // Set the expiration date far in the future (e.g., 10 years from now)
    const tenYearsFromNow = new Date();
    tenYearsFromNow.setFullYear(tenYearsFromNow.getFullYear() + 10);

    setCookies(cookie.theme_mode, {
      value: themeMode === 'light' ? 'dark' : 'light',
      expires: tenYearsFromNow,
    });
  };

  const handleLangClick = async (lang: IAppLanguage, onClose: any) => {
    await setCookies(cookie.locale, { value: lang.code });
    onClose();
    window.location.reload();
  };

  return (
    <div className="header-content-right">
      <div className="header-element mx-2">
        <div className="notification-icon position-relative d-flex align-items-center justify-content-center pointer p-2 rounded-3 border-0" onClick={() => router.push(`/a/notifications`)}>
          <Flexicon icon="bell-02" variant="line" />
          {hasNotifications && (
            <div className={`notification-badge position-absolute d-flex align-items-center justify-content-center ${themeMode === 'dark' ? 'notification-badge-dark' : 'notification-badge-light'}`}>
              <div className="notification-badge-dot" />
            </div>
          )}
        </div>
      </div>
      <div className="header-element country-selector">
        <Dropdown
          trigger={
            <span className="header-link pointer px-2 py-1">
              <Flexicon icon="globe-02" variant="solid" size={22} />
              <span className="mb-0 fs-13 ms-1">{capitalizeAllLetters(userLocale)}</span>
            </span>
          }
        >
          {(onClose: any) => (
            <>
              {appLanguages.map((lang: IAppLanguage) => {
                if (userLocale === lang.code) {
                  return <DropdownItem key={lang.code} option={lang.name} onClick={() => onClose()} className="bg-primary text-white" />;
                }

                return (
                  <DropdownItem
                    key={lang.code}
                    option={lang.name}
                    onClick={() => {
                      userLocale === lang.code ? onClose() : handleLangClick(lang, onClose);
                    }}
                  />
                );
              })}
            </>
          )}
        </Dropdown>
      </div>

      {/* Start::header-theme-mode-element */}
      <div className="header-element header-theme-mode me-2">
        <div onClick={changeThemeMode} className="header-link layout-setting pointer">
          <span className="light-layout">
            <SVG icon="half-moon" width={22} height={22} />
          </span>
          <span className="dark-layout">
            <SVG icon="sun-light" width={22} height={22} />
          </span>
        </div>
      </div>
      {/* End::header-theme-mode-element */}

      {/* Start::header-profile-element */}
      <Profile />
      {/* End::header-profile-element */}
    </div>
  );
};
