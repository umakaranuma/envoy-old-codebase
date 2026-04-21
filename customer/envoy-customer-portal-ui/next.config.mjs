/** @type {import('next').NextConfig} */

const nextConfig = {
  poweredByHeader: false,
  generateEtags: false,
  reactStrictMode: true,
  trailingSlash: false,
  output: 'standalone',
  experimental: {
    serverActions: {
      bodySizeLimit: '25mb',
    },
  },
  env: {
    CUSTOMER_API_URL: process.env.CUSTOMER_API_URL,

    ENCRYPTION_MODE: process.env.ENCRYPTION_MODE,
    CRYPT_SECRET_KEY: process.env.CRYPT_SECRET_KEY,
    S3CDN: process.env.S3CDN,
    S3CDN_Domain: process.env.S3CDN_Domain,

    CUSTOMER_PROXY_PREFIX: '/customer-api',
  },
  images: {
    deviceSizes: [640, 750, 828, 1080, 1200, 1920, 2048, 3840],
    remotePatterns: [
      {
        protocol: 'http',
        hostname: 'localhost',
      },
      {
        protocol: 'https',
        hostname: process.env.S3CDN_Domain,
      },
    ],
  },
  async rewrites() {
    return {
      beforeFiles: [
        {
          source: nextConfig.env.CUSTOMER_PROXY_PREFIX + '/:path(.*)',
          destination: process.env.CUSTOMER_API_URL + '/:path',
        },
      ],
    };
  },
  async redirects() {
    return [
      {
        source: '/',
        destination: `/login`,
        permanent: false,
      },
      {
        source: '/customer',
        destination: `/login`,
        permanent: false,
      },
    ];
  },
};

export default nextConfig;
