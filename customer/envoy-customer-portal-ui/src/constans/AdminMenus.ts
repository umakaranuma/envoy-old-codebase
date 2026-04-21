import { MenuCategory } from '@/interface/IAdminLayout';

export const adminMenus: MenuCategory[] = [
  {
    menus: [
      {
        name: 'my_requests',
        icon: 'dashboard',
        path: `/a/my-requests`,
        matcher: [`/{appId}/a/my-requests`, `/{appId}/a/my-requests/{requestId}`],
      },
      {
        name: 'my_quotations',
        icon: 'users',
        path: `/a/my-quotations`,
        matcher: [`/{appId}/a/my-quotations`, `/{appId}/a/my-quotations/create`, `/{appId}/a/my-quotations/{quotationId}/view`, `/{appId}/a/my-quotations/{quotationId}/temp-view`],
      },
      {
        name: 'my_policies',
        icon: 'service-providers',
        path: `/a/my-policies`,
        matcher: [`/{appId}/a/my-policies`, `/{appId}/a/my-policies/create`, `/{appId}/a/my-policies/{policyId}`],
      },
      {
        name: 'my_claims',
        icon: 'service-providers',
        path: `/a/my-claims`,
        matcher: [`/{appId}/a/my-claims`, `/{appId}/a/my-claims/create`, `/{appId}/a/my-claims/{claimId}`],
      },
      {
        name: 'profile',
        icon: 'service-providers',
        path: `/a/profile`,
        matcher: [`/{appId}/a/profile`],
      },
      {
        name: 'notifications',
        icon: 'service-providers',
        path: `/a/notifications`,
        matcher: [`/{appId}/a/notifications`],
      },
      // {
      //     name: "Package Management",
      //     icon: 'package',
      //     matcherStartWith: `/admin/package-management`,
      //     subMenus: [
      //         {
      //             name: "Care Request",
      //             path: `/admin/package-management/care-request`
      //         },
      //         {
      //             name: "Care Package",
      //             path: `/admin/package-management/care-packages`
      //         },
      //         {
      //             name: "Package Library",
      //             path: `/admin/package-management/package-libraries`,
      //             matcher: [`/admin/package-management`]
      //         },
      //         {
      //             name: "EPA Package Management",
      //             path: `/admin/package-management/epa-package-management`,
      //             matcher: [`/admin/package-management`]
      //         }
      //     ]
      // }
    ],
  },
];
