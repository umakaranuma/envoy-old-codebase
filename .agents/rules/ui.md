---
trigger: always_on
---

# UI Development Rules

When developing UI components or pages, follow these guidelines to ensure consistency and maintainability across the Envoy platform.

## Design Principles
- **Modern Design**: Maintain a modern, professional, and premium aesthetic throughout the application.
- **Consistency**: Adhere strictly to the design system documentation located at:
  - `{respective_module_ui_directory}/.docs/design-system`
  
  For example:
  - `envoy_core/envoy_core_ui/.docs/design-system`
  - `envoy_crm/envoy_crm_ui/.docs/design-system`
  - `envoy_policy/envoy_policy_ui/.docs/design-system`
  - `envoy_policy/envoy_finance_ui/.docs/design-system`
  - `envoy_customer/envoy_customer_ui/.docs/design-system`

  All colors, typography, spacing, and layout patterns **must** match the specifications defined in the design system files.

- **Design System as Source of Truth**: The design system folder contains reference files (screens, components, tokens, etc.) that define the visual language of the application. When building any element, widget, or component:
  - If a reference file exists in the design system for what you are building → replicate its look exactly.
  - If no reference file exists for what you need to build → create your own design, but it **must** feel native to the existing files. Study the established patterns across the design system files — colors, typography, spacing, borders, shadows, and interaction styles — and match them precisely. Do not introduce visual styles that are inconsistent with what is already defined in those files.

## Component Organization
- **Base Components**: Base components (atoms, fundamental UI elements) must be built in the following directory:
  - `{respective_module_ui_directory}/common/components/base-components`

  For example:
  - `envoy_core/envoy_core_ui/common/components/base-components`
  - `envoy_crm/envoy_crm_ui/common/components/base-components`
  - `envoy_policy/envoy_policy_ui/common/components/base-components`
  - `envoy_policy/envoy_finance_ui/common/components/base-components`
  - `envoy_customer/envoy_customer_ui/common/components/base-components`

## Component Guidelines
- **Button Usage**: Use the **primary** button for the primary action on a page. For all other secondary actions, use the **secondary** button.
- **Confirmation**: Always use the `PopConfirm` component whenever a user confirmation is needed (e.g., when clicking a delete button or any other critical actions).
  - **Path**: `{respective_module_ui_directory}/common/components/base-components/PopConfirm.tsx`
- **Page Layout & Padding**:
  - Do NOT apply local paddings to page content containers (e.g., `p-8`). Instead, ensure the main content wrapper inside the parent layout (e.g., `DashboardLayout`) handles the standardized padding uniformly across the application.
  - Page specific root containers should utilize `w-full` instead of constrained max-widths (`max-w-[...]`) to ensure uniform alignment with the layout's defined margins and paddings.
- **Table Loading State**:
  - Do NOT build ad-hoc skeleton loaders for tables. Always use the standardized `<TLoader />` component imported from `Table.tsx` to handle loading rows within a `<TBody>`.
- **Empty States / Record Not Found**:
  - Whenever a list or data view returns zero records, you MUST use the `EmptyState` component. Do NOT build ad-hoc "record not found" text or containers.
  - **Path**: `{respective_module_ui_directory}/common/components/base-components/EmptyState.tsx`
- **Code Splitting**: If a component file grows too long (e.g., exceeds ~300 lines), split it into smaller, focused sub-components where possible. Extract logical sections (e.g., modals, forms, table rows, toolbars) into their own files within the same directory, and import them back into the parent component. This improves readability, maintainability, and reusability.

## Responsiveness
- **Mobile First**: All UI components and pages must be fully mobile-responsive. Ensure that layouts adapt gracefully to different screen sizes, prioritizing a seamless experience on mobile devices.

## SEO
- **Customer Portal**: When working on the Customer Portal (`envoy_customer/envoy_customer_ui`), you must implement SEO best practices (meta tags, structured data, semantic HTML, Open Graph tags, etc.) alongside all UI work.

## Caching (Next.js)
- **Cache Components**: Since the project uses Next.js, you must cache components wherever possible using the available caching strategies. If you are unsure about the latest Next.js caching patterns, search the web for the latest documentation before proceeding.
- **Cache Lifetime**: When building a cached component, you must present the available cache lifetime/revalidation options (e.g., 30s, 1min, 5min, 1hr, 24hr, etc.) to the user and **ask for confirmation** on which value to set for the cache before applying it.
