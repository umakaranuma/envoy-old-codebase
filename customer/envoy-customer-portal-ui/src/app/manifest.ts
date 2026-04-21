import { MetadataRoute } from 'next';

export default function manifest(): MetadataRoute.Manifest {
  return {
    name: 'Vanguard X',
    short_name: 'Vanguard X',
    description: 'Vanguard X',
    start_url: '/',
    display: 'standalone',
    background_color: '#ffffff',
    theme_color: '#000000',
    icons: [
      {
        src: '/images/brand/favicon.ico',
        sizes: '48x48',
        type: 'image/x-icon',
      },
      // {
      //     "src": "/images/brand/maskable_icon.png",
      //     "type": "image/png",
      //     "sizes": "512x512",
      //     "purpose": "maskable"
      // },
      {
        src: '/images/brand/192x192.png',
        type: 'image/png',
        sizes: '192x192',
      },
      {
        src: '/images/brand/512x512.png',
        type: 'image/png',
        sizes: '512x512',
      },
    ],
  };
}
