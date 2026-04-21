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
  assetPrefix: '/crm-static',

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
  env: {
    CORE_API_URL: process.env.CORE_API_URL,
    CRM_API_URL: process.env.CRM_API_URL,
    POLICY_API_URL: process.env.POLICY_API_URL,
    CORE_BASE_URL: process.env.CORE_BASE_URL,
    S3CDN: process.env.S3CDN,
    UTILITIES_API_URL: process.env.UTILITIES_API_URL,
    S3CDN_Domain: process.env.S3CDN_Domain,
    NOVA_PROXY_PREFIX: '/nova-api',
    CRM_PROXY_PREFIX: '/crm-api',
    POLICY_PROXY_PREFIX: '/policy-api',
    CORE_PROXY_PREFIX: '/core-api',
    UTILITIES_PROXY_PREFIX: '/utilities-api',
  },
  async rewrites() {
    return {
      beforeFiles: [
        {
          source: nextConfig.env.CORE_PROXY_PREFIX + '/:path(.*)',
          destination: process.env.CORE_API_URL + '/:path',
        },
        {
          source: nextConfig.env.CRM_PROXY_PREFIX + '/:path(.*)',
          destination: process.env.CRM_API_URL + '/:path',
        },
        {
          source: nextConfig.env.POLICY_PROXY_PREFIX + '/:path(.*)',
          destination: process.env.POLICY_API_URL + '/:path',
        },
        {
          source: nextConfig.env.NOVA_PROXY_PREFIX + '/:path(.*)',
          destination: process.env.NOVA_API_URL + '/:path',
        },
        {
          source: nextConfig.env.UTILITIES_PROXY_PREFIX + '/:path(.*)',
          destination: process.env.UTILITIES_API_URL + '/:path',
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
        source: '/crm',
        destination: `/login`,
        permanent: false,
      },
    ];
  },
};

export default nextConfig;
