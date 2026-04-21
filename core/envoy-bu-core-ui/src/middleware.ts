import { NextRequest, NextResponse } from 'next/server';
import { getCookies } from './helpers/handlers/cookiesHandler';
import { cookie } from './constans/StorageKeys';

export async function middleware(request: NextRequest) {
  const pathname = request.nextUrl.pathname;

  if (pathname.startsWith('/_next/')) return NextResponse.next();
  if (pathname.startsWith('/api/configs')) return NextResponse.next();

  const token = await getCookies(cookie.token);

  if (pathname === '/login' && token !== null && token !== undefined) {
    return NextResponse.redirect(new URL('/a/dashboard', request.url));
  }
  if (pathname.startsWith('/a') && (token === null || token === undefined)) {
    return NextResponse.redirect(new URL('/login', request.url));
  }

  const protocol = request.nextUrl.protocol;
  const baseUrl = request.headers.get('host');

  if (pathname.startsWith('/login')) {
    const idpUrl = process.env.IDP_URL || 'http://localhost';
    const spId = process.env.SP_ID || '';
    const newUrl = `${idpUrl}/login?sp=${spId}&redirect=${encodeURIComponent(`${protocol}//${baseUrl}/idp-callback`)}`;
    return NextResponse.redirect(newUrl);
  }

  if (pathname.startsWith('/user-invitation')) {
    const idpUrl = process.env.IDP_URL || 'http://localhost';
    const spId = process.env.SP_ID || '';
    const invitation = request.nextUrl.searchParams.get('invitation');
    const newUrl = `${idpUrl}/register?sp=${spId}&redirect=${encodeURIComponent(`${protocol}//${baseUrl}/idp-callback?invitation=${invitation}`)}`;

    return NextResponse.redirect(newUrl);
  }

  return NextResponse.next();
}

export const config = {
  matcher: ['/:path*'],
};
