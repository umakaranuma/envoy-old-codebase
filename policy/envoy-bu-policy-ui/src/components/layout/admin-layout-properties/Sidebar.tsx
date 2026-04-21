import Link from 'next/link';
import Image from 'next/image';
import desktopLogo from '../../../../public/logo/desktop-logo.png';
import desktopDark from '../../../../public/logo/desktop-dark.png';
import toggleLogo from '../../../../public/logo/toggle-logo.png';
import toggleDark from '../../../../public/logo/toggle-dark.png';
import React, { useState } from 'react';
import { useParams, usePathname } from 'next/navigation';
import { IMenu, MenuCategory } from '@/interface/IAdminLayout';
import { SVG } from '../../others/SVG';
import { useTrans } from '@/helpers/services/lang/langService';

export const Sidebar = ({ children, handleSidebarOverlay }: { children: React.ReactNode; handleSidebarOverlay: Function }) => {
  return (
    <aside className="app-sidebar sticky" id="sidebar" onMouseEnter={() => handleSidebarOverlay(true)} onMouseLeave={() => handleSidebarOverlay(false)}>
      {/* Start::main-sidebar-header */}
      <div className="main-sidebar-header">
        <Link href="/a/dashboard" className="header-logo">
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

export const SidebarMenu = ({ handleMenuToggleClick, appMenu }: { handleMenuToggleClick: Function; appMenu: MenuCategory[] }) => {
  const t = useTrans('otr.sidebar');
  const pathName = usePathname();
  const params = useParams();

  // Find which menu should be open initially based on current path
  const getInitialOpenMenu = () => {
    for (const category of appMenu) {
      for (let i = 0; i < category.menus.length; i++) {
        const menu = category.menus[i];
        if (menu.subMenus && menu.matcherStartWith) {
          const matcherPath = buildUrlWithParams(menu.matcherStartWith, params);
          if (pathName.startsWith(matcherPath)) {
            return i;
          }
        }
      }
    }
    return null;
  };

  const [openMenu, setOpenMenu] = useState(getInitialOpenMenu);

  const handleMainMenuClick = (index: any) => {
    setOpenMenu((prevOpenMenu) => (prevOpenMenu === index ? null : index));
  };

  return (
    <>
      {appMenu.map((category, index) => (
        <React.Fragment key={index}>
          {category.category && (
            <li className="slide__category">
              <span className="category-name">{t(category.category)}</span>
            </li>
          )}
          {category?.menus.map((menu: any, i: any) => {
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
                  <SidebarSubMenu {...{ t, handleMenuToggleClick }} menus={menu} childOrder={1} isOpen={openMenu === i} />
                </li>
              );
            } else {
              const _isActive = menu.matcher ? menu.matcher.some((path: string) => pathName === buildUrlWithParams(path, params)) : pathName === menu.path;

              return (
                <li key={i} className={`slide pointer ${_isActive ? 'active' : ''}`}>
                  <Link href={menu.path || ''} className={`side-menu__item parent-menu my-1 ${_isActive ? 'active' : ''}`} onClick={() => (setOpenMenu(null), handleMenuToggleClick())}>
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
        </React.Fragment>
      ))}
    </>
  );
};

export const SidebarSubMenu = ({ t, menus, childOrder, isOpen, handleMenuToggleClick }: { t: any; menus: IMenu; childOrder: number; isOpen: boolean; handleMenuToggleClick: Function }) => {
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
                  <SidebarSubMenu {...{ t, handleMenuToggleClick }} menus={menu} childOrder={_childOrder} isOpen={openMenus.includes(i)} />
                </li>
              );
            } else {
              const _isActive = menu.matcher ? menu.matcher.some((path: string) => pathName === buildUrlWithParams(path, params)) : pathName === menu.path;

              return (
                <li key={i} className={`slide pointer ${_isActive ? 'active' : ''}`}>
                  <Link href={menu.path || ''} className={`side-menu__item my-1 ${_isActive ? 'active' : ''}`} onClick={() => handleMenuToggleClick()}>
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
