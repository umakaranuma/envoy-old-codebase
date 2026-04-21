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
import React from 'react';
import { useParams, usePathname, useRouter } from 'next/navigation';
import { buildUrlWithParams } from './Sidebar';
import { useTrans } from '@/helpers/services/lang/langService';
import { adminMenus } from '@/constans/AdminMenus';
import ContactAgent from '@/app/[appId]/a/profile/_utils/components/ContactAgent';
import { useNotification } from '@/hooks/NotificationProvider';

export const Header = ({
  handleMenuToggleClick,
  themeMode,
  sbClosed,
  reachedBreakpoint,
  appKey,
}: {
  handleMenuToggleClick: Function;
  themeMode: 'light' | 'dark';
  sbClosed: boolean;
  reachedBreakpoint: boolean;
  appKey: string;
}) => {
  return (
    <div className={`${!reachedBreakpoint ? 'px-5 customer-app-header' : ''} shadow-sm app-header`}>
      {/* Start::main-header-container */}
      <div className="main-header-container container-fluid d-flex align-items-center justify-content-between p-2">
        <HeaderContentLeft {...{ handleMenuToggleClick, sbClosed, reachedBreakpoint, themeMode, appKey }} />
        {!reachedBreakpoint && <HeaderMenu appKey={appKey} />}
        <div className="d-flex align-items-center">
          <HeaderContentRight themeMode={themeMode} reachedBreakpoint={reachedBreakpoint} appKey={appKey} />
        </div>
      </div>
      {/* End::main-header-container */}
    </div>
  );
};

export const HeaderContentLeft = ({
  handleMenuToggleClick,
  themeMode,
  sbClosed,
  reachedBreakpoint,
  appKey,
}: {
  handleMenuToggleClick: Function;
  sbClosed: boolean;
  themeMode: 'light' | 'dark';
  reachedBreakpoint: boolean;
  appKey: string;
}) => {
  // const pathName = usePathname();
  // const t = useTrans('otr.sidebar');
  // const params = useParams();

  // const findBreadcrumb = (menus: any, path: any) => {
  //   for (const menu of menus) {
  //     if (menu.matcher) {
  //       for (const matcher of menu.matcher) {
  //         if (buildUrlWithParams(matcher, params) === path) {
  //           return [menu];
  //         }
  //       }
  //     }
  //     if (menu.path && buildUrlWithParams(menu.path, params) === path) {
  //       return [menu];
  //     }
  //     if (menu.subMenus) {
  //       const subMenuPath: any = findBreadcrumb(menu.subMenus, path);
  //       if (subMenuPath.length) {
  //         return [menu, ...subMenuPath];
  //       }
  //     }
  //   }
  //   return [];
  // };

  // const breadcrumb = useMemo(() => {
  //   for (const category of appMenu) {
  //     const path = findBreadcrumb(category.menus, pathName);
  //     if (path.length) {
  //       return path;
  //     }
  //   }
  //   return [];
  // }, [pathName]);

  return (
    <div className="header-content-left">
      {/* Start::header-element */}
      {!reachedBreakpoint && (
        <div className="header-element">
          <div className="horizontal-logo">
            <Link href={`/${appKey}/a/home`} className="header-logo">
              <Image src={desktopLogo} width={140} alt="logo" className="desktop-logo" />
              <Image src={toggleLogo} alt="logo" width={40} className="toggle-logo" />
              <Image src={desktopDark} width={140} alt="logo" className="desktop-dark" />
              <Image src={toggleDark} alt="logo" width={40} className="toggle-dark" />
            </Link>
          </div>
        </div>
      )}
      {/* End::header-element */}

      {/* Start::header-element */}
      {reachedBreakpoint && (
        <div className="header-element">
          {/* Start::header-link */}
          <a onClick={(e) => (e.stopPropagation(), handleMenuToggleClick())} className="" role="button">
            <Flexicon icon={sbClosed ? 'menu-01' : 'menu-02'} variant="line" />
          </a>
          {/* End::header-link */}
        </div>
      )}
      {/* End::header-element */}

      {/* <div className="header-element ms-1 fs-14">
        <div className="d-flex align-items-center gap-2">
          <Link href={`/a/dashboard`} className="text-muted clickable-text-primary d-flex align-items-center">
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
      </div> */}
      {!reachedBreakpoint && (
        <div className="header-element ms-1 fs-14">
          <div className="">
            <Link href={`/${appKey}/a/home`} className="header-logo">
              <Image src={themeMode === 'dark' ? desktopDark : desktopLogo} width={140} alt="logo" className="desktop-logo" />
              {/* <Image src={themeMode === 'dark' ? toggleDark : toggleLogo} alt="logo" width={40} className="toggle-dark" /> */}
            </Link>
          </div>
        </div>
      )}
    </div>
  );
};

const HeaderContentRight = ({ themeMode, reachedBreakpoint, appKey }: { themeMode: 'light' | 'dark'; reachedBreakpoint: boolean; appKey: string }) => {
  // const userLocale = useContext(UserLocale);
  const router = useRouter();
  const { notifications } = useNotification();
  const changeThemeMode = async () => {
    // Set the expiration date far in the future (e.g., 10 years from now)
    const tenYearsFromNow = new Date();
    tenYearsFromNow.setFullYear(tenYearsFromNow.getFullYear() + 10);

    setCookies(cookie.theme_mode, {
      value: themeMode === 'light' ? 'dark' : 'light',
      expires: tenYearsFromNow,
    });
  };
  console.log('notifications', notifications);

  // const handleLangClick = async (lang: IAppLanguage, onClose: any) => {
  //   await setCookies(cookie.locale, { value: lang.code });
  //   onClose();
  //   window.location.reload();
  // };

  return (
    <div className="header-content-right">
      {!reachedBreakpoint && (
        <div className="header-element mx-2">
          <ContactAgent reachedBreakpoint={reachedBreakpoint} />
        </div>
      )}
      <div className="header-element mx-2">
        <div className="header-element mx-2">
          <div
            className="notification-icon position-relative d-flex align-items-center justify-content-center pointer p-2 rounded-3 border-0"
            onClick={() => router.push(`/${appKey}/a/notifications`)}
          >
            <Flexicon icon="bell-02" variant="line" />
            {notifications.length > 0 && (
              <div className={`notification-badge position-absolute d-flex align-items-center justify-content-center ${themeMode === 'dark' ? 'notification-badge-dark' : 'notification-badge-light'}`}>
                <div className="notification-badge-dot" />
              </div>
            )}
          </div>
        </div>
      </div>
      {/* <div className="header-element country-selector">
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
                  return null;
                }

                return <DropdownItem key={lang.code} option={lang.name} onClick={() => handleLangClick(lang, onClose)} />;
              })}
            </>
          )}
        </Dropdown>
      </div> */}

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

const HeaderMenu = ({ appKey }: { appKey: string }) => {
  const t = useTrans('otr.sidebar');
  const pathName = usePathname();
  const params = useParams();
  return (
    <div className="header-menu">
      {adminMenus.map((category, i) => (
        <div key={i}>
          {category.menus.slice(0, 4).map((menu, index) => {
            const isActive = menu.matcher ? menu.matcher.some((path: string) => pathName === buildUrlWithParams(path, params)) : pathName === menu.path;

            return (
              <Link key={index} href={`/${appKey}/${menu.path}`} className={`fw-medium header-menu-button ${isActive ? 'border border-primary text-primary' : 'header-menu-button-border'}`}>
                {t(menu.name)}
              </Link>
            );
          })}
        </div>
      ))}
    </div>
  );
};
