/** @type {import('next').NextConfig} */

const nextConfig = {
  poweredByHeader: false,
  generateEtags: false,
  reactStrictMode: true,
  trailingSlash: false,
  output: 'standalone',
  images: {
    deviceSizes: [640, 750, 828, 1080, 1200, 1920, 2048, 3840],
    remotePatterns: [
      {
        protocol: 'http',
        hostname: 'localhost',
      },
      ...(process.env.S3CDN_Domain
        ? [
            {
              protocol: 'https',
              hostname: process.env.S3CDN_Domain,
            },
          ]
        : []),
    ],
  },
  experimental: {
    serverActions: {
      bodySizeLimit: '500mb',
    },
  },
  env: {
    CORE_API_URL: process.env.CORE_API_URL,
    CRM_API_URL: process.env.CRM_API_URL,
    NOVA_API_URL: process.env.NOVA_API_URL,
    CRM_BASE_URL: process.env.CRM_BASE_URL,
    POLICY_BASE_URL: process.env.POLICY_BASE_URL,
    FINANCE_BASE_URL: process.env.FINANCE_BASE_URL,
    S3_REGION: process.env.S3_REGION,
    S3_BUCKET_NAME: process.env.S3_BUCKET_NAME,
    S3_SECRET_ACCESS_KEY: process.env.S3_SECRET_ACCESS_KEY,
    S3_ACCESS_KEY_ID: process.env.S3_ACCESS_KEY_ID,
    S3CDN: process.env.S3CDN,
    S3CDN_Domain: process.env.S3CDN_Domain,

    NOVA_PROXY_PREFIX: '/nova-api',
    CORE_PROXY_PREFIX: '/core-api',
    CRM_PROXY_PREFIX: '/crm-internal-api',
  },
  async rewrites() {
    return {
      beforeFiles: [
        {
          source: nextConfig.env.CORE_PROXY_PREFIX + '/:path(.*)',
          destination: (process.env.CORE_API_URL || 'http://localhost') + '/:path',
        },
        {
          source: nextConfig.env.CRM_PROXY_PREFIX + '/:path(.*)',
          destination: (process.env.CRM_API_URL || 'http://localhost') + '/:path',
        },
        {
          source: nextConfig.env.NOVA_PROXY_PREFIX + '/:path(.*)',
          destination: (process.env.NOVA_API_URL || 'http://localhost') + '/:path',
        },
        {
          source: '/crm/:path+',
          destination: `${process.env.CRM_BASE_URL || 'http://localhost'}/crm/:path+`,
        },
        {
          source: '/crm-static/_next/:path+',
          destination: `${process.env.CRM_BASE_URL || 'http://localhost'}/crm-static/_next/:path+`,
        },
        {
          source: '/crm-api/:path+',
          destination: `${process.env.CRM_BASE_URL || 'http://localhost'}/crm-api/:path+`,
        },
        {
          source: '/policy/:path+',
          destination: `${process.env.POLICY_BASE_URL || 'http://localhost'}/policy/:path+`,
        },
        {
          source: '/policy-static/_next/:path+',
          destination: `${process.env.POLICY_BASE_URL || 'http://localhost'}/policy-static/_next/:path+`,
        },
        {
          source: '/policy-api/:path+',
          destination: `${process.env.POLICY_BASE_URL || 'http://localhost'}/policy-api/:path+`,
        },
        {
          source: '/finance/:path+',
          destination: `${process.env.FINANCE_BASE_URL || 'http://localhost'}/finance/:path+`,
        },
        {
          source: '/finance-static/_next/:path+',
          destination: `${process.env.FINANCE_BASE_URL || 'http://localhost'}/finance-static/_next/:path+`,
        },
        {
          source: '/finance-api/:path+',
          destination: `${process.env.FINANCE_BASE_URL || 'http://localhost'}/finance-api/:path+`,
        },
        {
          source: '/utilities-api/:path+',
          destination: `${process.env.FINANCE_BASE_URL || 'http://localhost'}/utilities-api/:path+`,
        },
        {
          source: '/reports-api/:path+',
          destination: `${process.env.FINANCE_BASE_URL || 'http://localhost'}/reports-api/:path+`,
        },
      ],
      fallback: [
        {
          source: '/:path*',
          destination: '/a/:path*',
        },
      ],
    };
  },
  async redirects() {
    return [
      {
        source: '/',
        destination: '/login',
        permanent: false,
      },
      {
        source: '/a',
        destination: '/login',
        permanent: false,
      },
    ];
  },
};

export default nextConfig;
