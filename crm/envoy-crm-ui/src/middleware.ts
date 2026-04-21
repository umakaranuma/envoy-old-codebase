import { NextRequest, NextResponse } from 'next/server';
import { getCookies } from './helpers/handlers/cookiesHandler';
import { cookie } from './constans/StorageKeys';

export async function middleware(request: NextRequest) {
  const pathname = request.nextUrl.pathname;

  if (pathname.startsWith('/_next/')) return NextResponse.next();

  const token = await getCookies(cookie.token);

  if (pathname === '/login' && token !== null && token !== undefined) {
    return NextResponse.redirect(new URL(`/a/dashboard`, request.url));
  }
  if (pathname.startsWith('/crm') && (token === null || token === undefined)) {
    return NextResponse.redirect(new URL(`/login`, request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: ['/:path*'],
};
