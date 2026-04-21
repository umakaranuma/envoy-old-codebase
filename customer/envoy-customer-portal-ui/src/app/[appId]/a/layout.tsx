import type { Metadata } from 'next';
import '../../../../public/styles/theme.css';
import '@apptimus-ui/theme/dist/components/styles/ynex/app.css';
import '../../../../public/styles/custom.css';
import '../../../../public/styles/page-related/claim-table.css';
import '../../../../public/styles/page-related/claim-creation.css';
import { getThemeMode } from '@/helpers/services/serverSideServices';
import AdminLayout from '@/components/layout/AdminLayout';
import { getCookies } from '@/helpers/handlers/cookiesHandler';
import { cookie } from '@/constans/StorageKeys';
import favicon from '../../../../public/images/brand/favicon.ico';

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

  // const aupResponse = await getAllAuthUserPermissions('CRM');
  // const authUserPermissions = aupResponse.is_success ? aupResponse.result : [];
  const appKey = await getCookies(cookie.appKey);
  // const appMenuResponse = await getAppMenu();
  // const appMenu: MenuCategory[] = appMenuResponse?.responseData?.menu || [];

  return (
    <html lang={locale || 'en'}>
      <AdminLayout locale={locale || 'en'} themeMode={themeMode} authUserPermissions={[]} appKey={appKey}>
        {children}
      </AdminLayout>
    </html>
  );
}
