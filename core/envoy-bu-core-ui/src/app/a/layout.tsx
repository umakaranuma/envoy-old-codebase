import type { Metadata } from 'next';
import localFont from 'next/font/local';
import '../../../public/styles/theme.css';
import '@apptimus-ui/theme/dist/components/styles/ynex/app.css';
import '../../../public/styles/custom.css';
import { getAppMenu, getBottomMenu, getThemeMode } from '@/helpers/services/serverSideServices';
import AdminLayout from '@/components/layout/AdminLayout';
import { getCookies } from '@/helpers/handlers/cookiesHandler';
import { cookie } from '@/constans/StorageKeys';
import favicon from '../../../public/images/brand/favicon.ico';
import { MenuCategory } from '@/interface/IAdminLayout';

const inter = localFont({
  src: [
    { path: '../../../public/fonts/Inter/Inter_18pt-Thin.ttf', weight: '100', style: 'normal' },
    { path: '../../../public/fonts/Inter/Inter_18pt-Light.ttf', weight: '300', style: 'normal' },
    { path: '../../../public/fonts/Inter/Inter_18pt-Regular.ttf', weight: '400', style: 'normal' },
    { path: '../../../public/fonts/Inter/Inter_18pt-Medium.ttf', weight: '500', style: 'normal' },
    { path: '../../../public/fonts/Inter/Inter_18pt-SemiBold.ttf', weight: '600', style: 'normal' },
    { path: '../../../public/fonts/Inter/Inter_18pt-Bold.ttf', weight: '700', style: 'normal' },
    { path: '../../../public/fonts/Inter/Inter_18pt-ExtraBold.ttf', weight: '800', style: 'normal' },
    { path: '../../../public/fonts/Inter/Inter_18pt-Black.ttf', weight: '900', style: 'normal' },
  ],
  variable: '--font-inter',
  display: 'swap',
});

export const metadata: Metadata = {
  generator: 'Vanguard X',
  applicationName: 'Vanguard X',
  referrer: 'origin-when-cross-origin',
  title: {
    template: '%s | Vanguard X',
    default: 'Vanguard X',
  },
  description: 'Vanguard X',

  icons: {
    icon: favicon.src,
  },
};

export default async function AppLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  const themeMode = await getThemeMode();
  const locale = await getCookies(cookie.locale);
  const appMenu: MenuCategory[] = await getAppMenu();
  const bottomMenus: MenuCategory[] = await getBottomMenu();
  const token = await getCookies(cookie.token);

  return (
    <html lang={locale || 'en'} className={inter.variable}>
      <AdminLayout locale={locale || 'en'} themeMode={themeMode} appMenu={appMenu} bottomMenus={bottomMenus} token={token || ''}>
        {children}
      </AdminLayout>
    </html>
  );
}
