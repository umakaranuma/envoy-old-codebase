import Link from 'next/link';
import Image from 'next/image';
import desktopLogo from '../../../../public/logo/desktop-logo.png';
import desktopDark from '../../../../public/logo/desktop-dark.png';
import toggleLogo from '../../../../public/logo/toggle-logo.png';
import toggleDark from '../../../../public/logo/toggle-dark.png';
import React, { useState } from 'react';
import { useParams, usePathname } from 'next/navigation';
import { IMenu } from '@/interface/IAdminLayout';
import { SVG } from '../../others/SVG';
import { useTrans } from '@/helpers/services/lang/langService';
import { adminMenus } from '@/constans/AdminMenus';
import { Button } from '@apptimus-ui/ui-element';
import S3Avatar from '@/components/others/page-related/S3Avatar';
import { Flexicon } from '@apptimus-ui/flexicon';

export const Sidebar = ({ children, handleSidebarOverlay, appKey }: { children: React.ReactNode; handleSidebarOverlay: Function; appKey: string }) => {
  return (
    <aside className="app-sidebar sticky" id="sidebar" onMouseEnter={() => handleSidebarOverlay(true)} onMouseLeave={() => handleSidebarOverlay(false)}>
      {/* Start::main-sidebar-header */}
      <div className="main-sidebar-header">
        <Link href={`/${appKey}/a/home`} className="header-logo">
          <Image src={desktopLogo} width={140} alt="logo" className="desktop-logo" />
          <Image src={toggleLogo} alt="logo" width={40} className="toggle-logo" />
          <Image src={desktopDark} width={140} alt="logo" className="desktop-dark" />
          <Image src={toggleDark} alt="logo" width={40} className="toggle-dark" />
        </Link>
      </div>
      {/* End::main-sidebar-header */}

      {/* Start::main-sidebar */}
      <div className="main-sidebar" id="sidebar-scroll">
        {/* Start::nav */}
        <nav className="main-menu-container nav nav-pills flex-column sub-open">
          <ul className="main-menu">{children}</ul>
        </nav>
        {/* End::nav */}
      </div>
      {/* End::main-sidebar */}
    </aside>
  );
};

export const SidebarMenu = ({ handleMenuToggleClick, reachedBreakpoint, appKey }: { handleMenuToggleClick: Function; reachedBreakpoint: boolean; appKey: string }) => {
  const t = useTrans('otr.sidebar');
  const pathName = usePathname();
  const [openMenu, setOpenMenu] = useState(null);
  const params = useParams();

  const handleMainMenuClick = (index: any) => {
    setOpenMenu((prevOpenMenu) => (prevOpenMenu === index ? null : index));
  };

  return (
    <>
      {adminMenus.map((category, index) => (
        <React.Fragment key={index}>
          {category.category && (
            <li className="slide__category">
              <span className="category-name">{t(category.category)}</span>
            </li>
          )}
          {reachedBreakpoint && (
            <div className="header-element">
              <div className="horizontal-logo">
                <Link href={`/${appKey}/a/home`} className="header-logo">
                  <Image src={desktopLogo} width={140} alt="logo" className="desktop-logo" />
                  {/* <Image src={toggleLogo} alt="logo" width={40} className="toggle-logo" /> */}
                  <Image src={desktopDark} width={140} alt="logo" className="desktop-dark" />
                  {/* <Image src={toggleDark} alt="logo" width={40} className="toggle-dark" /> */}
                </Link>
              </div>
            </div>
          )}
          {category?.menus.slice(0, 4).map((menu: any, i: any) => {
            if (menu.subMenus) {
              const _isActive = pathName.startsWith(buildUrlWithParams(menu.matcherStartWith || '', params));

              return (
                <li key={i} className={`slide has-sub ${_isActive ? 'active' : ''} ${openMenu === i ? 'open' : ''}`}>
                  <a onClick={() => handleMainMenuClick(i)} className={`side-menu__item parent-menu my-1 pointer ${_isActive ? 'active' : ''}`}>
                    <span className="side-menu__icon">
                      <SVG icon={menu.icon} width={20} height={20} />
                    </span>
                    <span className="side-menu__label">
                      {t(menu.name)}
                      {/* notification badge here */}
                    </span>
                    <SVG icon="angle-down" width={15} height={15} className="side-menu__angle" />
                  </a>
                  <SidebarSubMenu {...{ t, handleMenuToggleClick }} menus={menu} childOrder={1} isOpen={openMenu === i} appKey={appKey} />
                </li>
              );
            } else {
              const _isActive = menu.matcher ? menu.matcher.some((path: string) => pathName === buildUrlWithParams(path, params)) : pathName === menu.path;

              return (
                <li key={i} className={`slide pointer ${_isActive ? 'active' : ''}`}>
                  <Link href={`/${appKey}/${menu.path}`} className={`side-menu__item parent-menu my-1 ${_isActive ? 'active' : ''}`} onClick={() => (setOpenMenu(null), handleMenuToggleClick())}>
                    <span className="side-menu__icon">
                      <SVG icon={menu.icon} width={20} height={20} />
                    </span>
                    <span className="side-menu__label">
                      {t(menu.name)}
                      {/* notification badge here */}
                    </span>
                  </Link>
                </li>
              );
            }
          })}
          {reachedBreakpoint && (
            <div className="mt-5 px-3">
              <div className="fw-medium">{t('contact_agent')}</div>
              <div className="d-flex align-items-center">
                <div className="p-3 px-2 mb-1">
                  <div className="d-flex flex-column gap-2">
                    <div>
                      <S3Avatar width={50} height={50} imageKey={''} />
                    </div>
                    <div className="align-self-center">
                      <div className="fs-16 fw-medium">Darlene Robertson</div>
                      <div className="fs-14 text-muted">d.robertson@example.com</div>
                    </div>
                    <div className="d-flex flex-row align-items-center gap-3 my-2">
                      <Button color="primary" className="d-flex align-items-center gap-1" variant="outline">
                        <Flexicon icon="mail-01" variant="line" size={18} />
                        {/* <span className="d-none d-sm-inline">{t('message')}</span> */}
                      </Button>
                      <Button color="primary" className="d-flex align-items-center gap-1">
                        <Flexicon icon="phone-call-01" variant="line" size={18} />
                        {/* <span className="d-none d-sm-inline">{t('call')}</span> */}
                      </Button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </React.Fragment>
      ))}
    </>
  );
};

export const SidebarSubMenu = ({
  t,
  menus,
  childOrder,
  isOpen,
  handleMenuToggleClick,
  appKey,
}: {
  t: any;
  menus: IMenu;
  childOrder: number;
  isOpen: boolean;
  handleMenuToggleClick: Function;
  appKey: string;
}) => {
  const pathName = usePathname();
  const params = useParams();
  const [openMenus, setOpenMenus] = useState([] as number[]);
  let _childOrder = childOrder;

  const handleMainMenuClick = (index: any) => {
    setOpenMenus((prevOpenMenus) => {
      const newOpenMenus = [...prevOpenMenus];
      if (newOpenMenus.includes(index)) {
        newOpenMenus.splice(newOpenMenus.indexOf(index), 1);
      } else {
        newOpenMenus.push(index);
      }
      return newOpenMenus;
    });
  };

  return (
    <div className={`wrapper ${isOpen ? 'open' : ''}`}>
      <ul className={`slide-menu inner child${childOrder}`}>
        <li className="slide side-menu__label1">
          <a onClick={(e) => e.stopPropagation()} className="pointer">
            {menus.name}
          </a>
        </li>
        {menus?.subMenus &&
          menus?.subMenus.map((menu, i) => {
            if (menu.subMenus) {
              _childOrder++;
            }

            if (menu.subMenus) {
              const _isActive = pathName.startsWith(buildUrlWithParams(menu.matcherStartWith || '', params));

              return (
                <li key={i} className={`slide has-sub ${openMenus.includes(i) ? 'open' : ''} ${_isActive ? 'active' : ''}`}>
                  <a onClick={() => handleMainMenuClick(i)} className={`side-menu__item my-1 pointer ${_isActive ? 'active' : ''}`}>
                    {t(menu.name)}
                    <SVG icon="angle-down" width={15} height={15} className="side-menu__angle" />
                  </a>
                  <SidebarSubMenu {...{ t, handleMenuToggleClick }} menus={menu} childOrder={_childOrder} isOpen={openMenus.includes(i)} appKey={appKey} />
                </li>
              );
            } else {
              const _isActive = menu.matcher ? menu.matcher.some((path: string) => pathName === buildUrlWithParams(path, params)) : pathName === menu.path;

              return (
                <li key={i} className={`slide pointer ${_isActive ? 'active' : ''}`}>
                  <Link href={`/${appKey}/${menu.path}`} className={`side-menu__item my-1 ${_isActive ? 'active' : ''}`} onClick={() => handleMenuToggleClick()}>
                    {t(menu.name)}
                  </Link>
                </li>
              );
            }
          })}
      </ul>
    </div>
  );
};

export const buildUrlWithParams = (path: string, params: any): string => {
  // Replace placeholders in the path with actual values from params
  const actualUrl = path.replace(/{(\w+)}/g, (_, key) => {
    const value = params[key];
    if (Array.isArray(value)) {
      // If the value is an array, join it with commas or handle appropriately
      return value.join(',');
    }
    return value || `{${key}}`; // Use the value or keep the placeholder if not found
  });

  return actualUrl;
};
