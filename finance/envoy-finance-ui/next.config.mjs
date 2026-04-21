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
  assetPrefix: '/finance-static',
  env: {
    CORE_API_URL: process.env.CORE_API_URL,
    CRM_API_URL: process.env.CRM_API_URL,
    POLICY_API_URL: process.env.POLICY_API_URL,
    FINANCE_API_URL: process.env.FINANCE_API_URL,
    UTILITIES_API_URL: process.env.UTILITIES_API_URL,
    REPORTS_API_URL: process.env.REPORTS_API_URL,
    ENCRYPTION_MODE: process.env.ENCRYPTION_MODE,
    CRYPT_SECRET_KEY: process.env.CRYPT_SECRET_KEY,
    CORE_BASE_URL: process.env.CORE_BASE_URL,
    S3CDN: process.env.S3CDN,
    S3CDN_Domain: process.env.S3CDN_Domain,
    UTILITIES_PROXY_PREFIX: '/utilities-api',
    CORE_PROXY_PREFIX: '/core-api',
    CRM_PROXY_PREFIX: '/crm-api',
    POLICY_PROXY_PREFIX: '/policy-api',
    FINANCE_PROXY_PREFIX: '/finance-api',
    REPORTS_PROXY_PREFIX: '/reports-api',
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
          source: nextConfig.env.CORE_PROXY_PREFIX + '/:path(.*)',
          destination: process.env.CORE_API_URL + '/:path',
        },
        {
          source: nextConfig.env.POLICY_PROXY_PREFIX + '/:path(.*)',
          destination: process.env.POLICY_API_URL + '/:path',
        },
        {
          source: nextConfig.env.CRM_PROXY_PREFIX + '/:path(.*)',
          destination: process.env.CRM_API_URL + '/:path',
        },
        {
          source: nextConfig.env.FINANCE_PROXY_PREFIX + '/:path(.*)',
          destination: process.env.FINANCE_API_URL + '/:path',
        },
        {
          source: nextConfig.env.UTILITIES_PROXY_PREFIX + '/:path(.*)',
          destination: process.env.UTILITIES_API_URL + '/:path',
        },
        {
          source: nextConfig.env.REPORTS_PROXY_PREFIX + '/:path(.*)',
          destination: process.env.REPORTS_API_URL + '/:path',
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
        source: '/finance',
        destination: `/login`,
        permanent: false,
      },
    ];
  },
};

export default nextConfig;
