import { NextRequest, NextResponse } from 'next/server';
import { getCookies } from './helpers/handlers/cookiesHandler';
import { cookie } from './constans/StorageKeys';

export async function middleware(request: NextRequest) {
  const pathname = request.nextUrl.pathname;
  const protocol = request.nextUrl.protocol;
  const baseUrl = request.headers.get('host');

  if (pathname.startsWith('/_next/')) return NextResponse.next();
  if (pathname.startsWith('/api/configs')) return NextResponse.next();

  const token = await getCookies(cookie.token);
  const appKey = await getCookies(cookie.appKey);
  if (pathname === '/welcome' && token !== null && token !== undefined) {
    return NextResponse.redirect(new URL(`/${appKey}/a/home`, request.url));
  }

  if (pathname.startsWith(`/${appKey}/a`) && (token === null || token === undefined)) {
    const newUrl = `/welcome?idp=${process.env.IDP_URL}&sp=${process.env.SP_ID}&redirect=${encodeURIComponent(`${protocol}//${baseUrl}`)}`;
    return NextResponse.redirect(new URL(newUrl, request.url));
  }

  if (pathname.startsWith('/login')) {
    console.log('request.url', new URL('/welcome', request.url));

    //  const newUrl = `${process.env.IDP_URL}/login?sp=${process.env.SP_ID}&redirect=${encodeURIComponent(`${protocol}//${baseUrl}/idp-callback`)}`;
    //const newUrl = `${process.env.IDP_URL}/welcome?sp=${process.env.SP_ID}&redirect=${encodeURIComponent(`${protocol}//${baseUrl}`)}`;
    //return NextResponse.redirect(newUrl);
    const newUrl = `/welcome?idp=${process.env.IDP_URL}&sp=${process.env.SP_ID}&redirect=${encodeURIComponent(`${protocol}//${baseUrl}`)}`;
    return NextResponse.redirect(new URL(newUrl, request.url));
  }

  if (pathname.startsWith('/invitation')) {
    const email = request.nextUrl.searchParams.get('email');
    const token = request.nextUrl.searchParams.get('token');
    const newUrl = `${process.env.IDP_URL}/register?sp=${process.env.SP_ID}&email=${email}&token=${token}&redirect=${encodeURIComponent(`${protocol}//${baseUrl}/idp-callback`)}`;

    return NextResponse.redirect(new URL(newUrl, request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: ['/:path*'],
};
