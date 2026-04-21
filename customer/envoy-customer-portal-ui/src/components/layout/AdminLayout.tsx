'use client';

import React, { createContext, useEffect, useState } from 'react';
import { getLocalStorage, setLocalStorage } from '@/helpers/handlers/localStorageHandler';
import { local_storage } from '@/constans/StorageKeys';
import { Header } from './admin-layout-properties/Header';
import { Sidebar, SidebarMenu } from './admin-layout-properties/Sidebar';
import { Toaster } from 'react-hot-toast';
import { adminMenus } from '@/constans/AdminMenus';
import BreadCrumb from './admin-layout-properties/BreadCrumb';
import LoadingIcon from '../others/page-related/LoadingIcon';
import NotificationProvider from '@/hooks/NotificationProvider';

export const UserLocale = createContext('');
export const UserPermissions = createContext([] as any);

function AdminLayout({
  children,
  themeMode,
  locale,
  authUserPermissions,
  appKey,
}: {
  children: React.ReactNode;
  themeMode: 'light' | 'dark';
  locale: string;
  authUserPermissions: any[];
  appKey: string;
}) {
  const [reachedBreakpoint, setReachedBreakpoint] = useState(false); // State to keep track if the screen width is less than 992px
  const [sbClosed, setSbClosed] = useState(false); // State to keep track if the sidebar is closed on desktop
  const [mobileSbClosed, setMobileSbClosed] = useState(true); // State to keep track if the sidebar is closed on mobile
  const [iconOverlay, setIconOverlay] = useState(false); // State to manage the overlay effect on sidebar icons
  const [mounted, setMounted] = useState(false);
  // Determine the toggle state based on the current screen width and sidebar states
  const getDataToggle = reachedBreakpoint ? (mobileSbClosed ? 'close' : 'open') : sbClosed ? 'icon-overlay-close' : '';

  // Handler to toggle the sidebar menu on click
  const handleMenuToggleClick = () => {
    if (reachedBreakpoint) {
      // Retrieve the mobile sidebar toggle status from local storage
      const sidemenuToggleStatusSm = getLocalStorage(local_storage.sm_sidebar_close) || '0';

      if (sidemenuToggleStatusSm === '0') {
        // If the sidebar is currently open, set it to close
        setLocalStorage(local_storage.sm_sidebar_close, { value: '1' });
        setMobileSbClosed(true);
      } else {
        // If the sidebar is currently closed, set it to open
        setLocalStorage(local_storage.sm_sidebar_close, { value: '0' });
        setMobileSbClosed(false);
      }
    } else {
      // Retrieve the desktop sidebar toggle status from local storage
      const sidemenuToggleStatus = getLocalStorage(local_storage.sidebar_close) || '0';

      if (sidemenuToggleStatus === '0') {
        // If the sidebar is currently open, set it to close
        setLocalStorage(local_storage.sidebar_close, { value: '1' });
        setSbClosed(true);
      } else {
        // If the sidebar is currently closed, set it to open
        setLocalStorage(local_storage.sidebar_close, { value: '0' });
        setSbClosed(false);
      }
    }
  };

  // Handler to manage the sidebar overlay effect on hover
  const handleSidebarOverlay = (onHover: boolean) => {
    if (!reachedBreakpoint && sbClosed && onHover) {
      setIconOverlay(true);
    } else {
      setIconOverlay(false);
    }
  };

  // Effect to synchronize sidebar state with local storage on component mount
  useEffect(() => {
    const _sbClosed = (getLocalStorage(local_storage.sidebar_close) || '0') === '0' ? false : true;
    if (sbClosed !== _sbClosed) {
      setSbClosed(_sbClosed);
    }
    setMounted(true);
  }, []);

  // Effect to handle window resize events and update the breakpoint status
  useEffect(() => {
    const handleResize = () => {
      if (window.innerWidth < 992) {
        // If the window width is less than 992px, set reachedBreakpoint to true
        setReachedBreakpoint(true);

        // Ensure the mobile sidebar is closed and update local storage
        setLocalStorage(local_storage.sm_sidebar_close, { value: '1' });
        setMobileSbClosed(true);
      } else {
        // If the window width is 992px or greater, set reachedBreakpoint to false
        setReachedBreakpoint(false);

        // Ensure the mobile sidebar is closed and update local storage
        setLocalStorage(local_storage.sm_sidebar_close, { value: '1' });
        setMobileSbClosed(true);
      }
    };

    // Add event listener for window resize
    window.addEventListener('resize', handleResize);
    handleResize();

    // Clean up event listener on component unmount
    return () => {
      window.removeEventListener('resize', handleResize);
    };
  }, []);

  return (
    <UserLocale value={locale}>
      <UserPermissions value={authUserPermissions}>
        <NotificationProvider>
          <body
            style={{ '--bs-body-font-family': 'Poppins' } as React.CSSProperties}
            data-layout-style="style-2"
            data-nav-layout="vertical"
            data-theme-mode={themeMode}
            data-menu-styles={themeMode}
            data-header-styles={themeMode}
            data-vertical-style="overlay"
            // data-bg-img="bgimg1"
            {...(iconOverlay && { 'data-icon-overlay': 'open' })}
            {...(getDataToggle && { 'data-toggled': getDataToggle })}
          >
            {mounted ? (
              <div className="page">
                <Header {...{ handleMenuToggleClick, themeMode, sbClosed, reachedBreakpoint, mounted, appKey }} />
                {reachedBreakpoint && (
                  <Sidebar handleSidebarOverlay={handleSidebarOverlay} appKey={appKey}>
                    <SidebarMenu handleMenuToggleClick={() => reachedBreakpoint && handleMenuToggleClick()} reachedBreakpoint={reachedBreakpoint} appKey={appKey} />
                  </Sidebar>
                )}
                <div className={`${reachedBreakpoint ? 'main-content app-content' : 'customer-app-content'}`}>
                  <div className={`py-4 ${reachedBreakpoint ? 'mx-1' : 'px-5'}`}>
                    <BreadCrumb appMenu={adminMenus} appKey={appKey} />
                    {/* {isOnline ? children : 'Something went wrong...'} */}
                    {children}
                  </div>
                </div>
              </div>
            ) : (
              <div className="vh-100 d-flex justify-content-center align-items-center">
                <LoadingIcon />
              </div>
            )}
            {/* <footer className="footer mt-auto py-3 bg-white text-center d-sm-none d-md-block">
                    <div className="container">
                        <span className="text-muted d-flex justify-content-center gap-4"> <span>Copyright © {new Date().getFullYear()}</span> <span className="fw-semibold text-primary text-decoration-underline">VANGUARD X</span><span className='ms-1'>All rights reserved</span></span>
                    </div>
                </footer> */}
            <div id="responsive-overlay" {...(!mobileSbClosed && { className: 'active' })} onClick={() => handleMenuToggleClick()}></div>
            <Toaster
              toastOptions={{
                style: {
                  background: 'var(--default-body-bg-color)',
                  color: 'var(--default-text-color)',
                },
              }}
            />
          </body>
        </NotificationProvider>
      </UserPermissions>
    </UserLocale>
  );
}

export default AdminLayout;
