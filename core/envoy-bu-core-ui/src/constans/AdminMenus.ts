import { MenuCategory } from '../interface/IAdminLayout';
// const t = useTrans('otr.common');
export const adminMenus: MenuCategory[] = [
  {
    // Category for general menus: add if you don't separate menus as groups. Ignore this category if not needed.
    category: '', //general
    menus: [
      {
        name: 'dashboard',
        // Need to maintain this SVG in the <SVG /> component in @/components/others/SVG
        icon: 'dashboard',
        path: `/a/dashboard`,
      },
      {
        name: 'core',
        icon: 'core',
        matcherStartWith: `/a`,
        subMenus: [
          // {
          //   name: 'org_levels',
          //   path: `/a/org-levels`,
          // },
          // {
          //   name: 'org_nodes',
          //   path: `/a/nodes`,
          // },
          {
            name: 'roles',
            path: `/a/roles`,
          },
          {
            name: 'accounts',
            path: `/a/accounts`,
            matcher: [`/a/accounts`, `/a/accounts/{accountId}`, `/a/accounts/{accountId}/hierarchy`],
          },
          {
            name: 'users_staffs',
            path: `/a/users`,
          },
          {
            name: 'teams',
            path: `/a/teams`,
          },
          {
            name: 'contacts',
            path: `/a/contacts`,
            matcher: [`/a/contacts`, `/a/contacts/{id}`],
          },
          // {
          //   name: 'forms',
          //   path: `/a/forms`,
          // },
          {
            name: 'templates',
            path: `/a/templates`,
            matcher: [`/a/templates`, `/a/templates/{id}`],
          },
          // {
          //   name: 'job_titles',
          //   path: `/a/job-titles`,
          // },
          {
            name: 'flags',
            path: `/a/flags`,
          },
          {
            name: 'channels',
            path: `/a/channels`,
          },
          {
            name: 'reasons',
            path: `/a/reasons`,
          },
          {
            name: 'partners',
            path: `/a/partners`,
            matcher: [`/a/partners`, `/a/partners/{partnerId}`],
          },
          {
            name: 'products',
            path: `/a/products`,
            matcher: [`/a/products`, `/a/products/{id}`],
          },
          {
            name: 'product_categories',
            path: `/a/product-categories`,
            matcher: [`/a/product-categories`, `/a/product-categories/{categoryId}`],
          },
          {
            name: 'product_items',
            path: `/a/product-items`,
            matcher: [`/a/product-items`, `/a/product-items/{itemId}`],
          },
          {
            name: 'service_types',
            path: `/a/service-types`,
          },
          {
            name: 'approvals',
            path: `/a/approvals`,
            matcher: [`/a/approvals`, `/a/approvals/{approvalId}`],
          },
          {
            name: 'customer_requests',
            path: `/a/customer-requests`,
            matcher: [`/a/customer-requests`, `/a/customer-requests/{requestId}`],
          },
        ],
      },
      {
        name: 'crm',
        icon: 'crm',
        matcherStartWith: `/crm/a`,
        subMenus: [
          {
            name: 'tasks',
            path: `/crm/a/tasks`,
          },
          {
            name: 'sales_management',
            path: `/crm/a/sales-management`,
            matcher: [`/crm/a/sales-management`, `/crm/a/sales-management/{salesManagementId}`],
          },
          {
            name: 'task_types',
            path: `/crm/a/task-types`,
          },
          {
            name: 'quotations',
            path: `/crm/a/quotations`,
          },
          // {
          //   name: 'approvals',
          //   path: `/crm/a/approvals`,
          //   matcher: [`/crm/a/approvals`, `/crm/a/approvals/{approvalId}`],
          // },
        ],
      },
      {
        name: 'policy',
        icon: 'crm',
        matcherStartWith: `/policy/a`,
        subMenus: [
          {
            name: 'risk_register',
            path: `/policy/a/risk-register`,
            matcher: [`/policy/a/risk-register`, `/policy/a/risk-register/{riskId}`, `/policy/a/risk-register/create`],
          },
          {
            name: 'policy_requests',
            path: `/policy/a/policy-request`,
            matcher: [`/policy/a/policy-request`, `policy/a/policy-request/{policyRequestId}`, `/policy/a/policy-request/create`],
          },
          {
            name: 'policy_management',
            path: `/policy/a/issued-policies`,
            matcher: [`/policy/a/issued-policies`, `/policy/a/issued-policies/{policyId}`],
          },
          {
            name: 'draft_policies',
            path: `/policy/a/draft-policies`,
            matcher: [`/policy/a/draft-policies`],
          },
          {
            name: 'claims',
            path: `/policy/a/claim`,
            matcher: [`/policy/a/claim/create`, `/policy/a/claim`, `/policy/a/claim/{claimId}/edit`, `/policy/a/claim/{claimId}`],
          },
        ],
      },
      {
        name: 'finance',
        icon: 'crm',
        matcherStartWith: `/finance/a`,
        subMenus: [
          {
            name: 'dr_cr_note',
            path: `/finance/a/dr-cr-note`,
            matcher: [`/finance/a/dr-cr-note`, `/finance/a/dr-cr-note/{drCrNoteId}`],
          },
          {
            name: 'commissions',
            path: `/finance/a/commission`,
            matcher: [`/finance/a/commission`, `/finance/a/commission/{commissionsId}`],
          },
          {
            name: 'commission_setup',
            path: `/finance/a/commission-setup`,
            matcher: [`/finance/a/commission-setup`, `/finance/a/commission-setup/{commissionSetupId}`],
          },
          {
            name: 'payments',
            path: `/finance/a/payments`,
            matcher: [`/finance/a/payments`, `/finance/a/payments/{paymentsId}`],
          },
          {
            name: 'general_ledger',
            path: `/finance/a/general-ledger`,
            matcher: [`/finance/a/general-ledger`, `/finance/a/general-ledger/{generalLedgerId}`],
          },
          {
            name: 'service_rendered',
            path: `/finance/a/service-rendered`,
            matcher: [`/finance/a/service-rendered`, `/finance/a/service-rendered/{serviceRenderedId}`],
          },
          {
            name: 'sales_targets',
            path: `/finance/a/sales-target`,
            matcher: [`/finance/a/sales-target`, `/finance/a/sales-target/create`],
          },
          {
            name: 'incentives_setup',
            path: `/finance/a/incentive-setup`,
            matcher: [`/finance/a/incentive-setup`, `/finance/a/incentive-setup/create`],
          },
          {
            name: 'incentives',
            path: `/finance/a/incentive`,
            matcher: [`/finance/a/incentive`],
          },
          {
            name: 'custom_reports',
            path: `/finance/a/custom-reports`,
            matcher: [`/finance/a/custom-reports`],
          },
          {
            name: 'report_types',
            path: `/finance/a/report-types`,
            matcher: [`/finance/a/report-types`],
          },
        ],
      },
    ],
  },
];

// Bottom menus
export const bottomMenus: MenuCategory[] = [
  {
    category: '',
    menus: [
      {
        name: 'settings',
        icon: 'core',
        path: `/a/settings`,
      },
    ],
  },
];
