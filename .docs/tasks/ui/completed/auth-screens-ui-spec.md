# Authentication Screens — UI Specification

**Application:** Vanguard X
**Screens:** Register (Create Account) · Login (Sign In)
**Version:** 1.0
**Status:** Draft
**Design System:** Vanguard X Auth

---

## Table of Contents

1. [Screen Overview](#1-screen-overview)
2. [Design Tokens](#2-design-tokens)
3. [Page Layout — Split Panel](#3-page-layout--split-panel)
4. [Left Panel — Form Area](#4-left-panel--form-area)
5. [Right Panel — Decorative Area](#5-right-panel--decorative-area)
6. [Brand Header](#6-brand-header)
7. [Register Screen — Create Account](#7-register-screen--create-account)
8. [Login Screen — Sign In](#8-login-screen--sign-in)
9. [Shared Form Components](#9-shared-form-components)
10. [Password Rules Checklist](#10-password-rules-checklist)
11. [Terms & Privacy Checkboxes](#11-terms--privacy-checkboxes)
12. [Submit Button](#12-submit-button)
13. [Footer Navigation Links](#13-footer-navigation-links)
14. [Form Validation & Error States](#14-form-validation--error-states)
15. [API Connections](#15-api-connections)
16. [Component States Summary](#16-component-states-summary)
17. [Responsive Behaviour](#17-responsive-behaviour)

---

## 1. Screen Overview

There are two authentication screens in the Vanguard X auth flow:

| Screen | Route | Purpose |
|---|---|---|
| **Register — Create Account** | `/auth/register` | New user completes account setup after clicking invitation link |
| **Login — Sign In** | `/auth/login` | Existing user signs in with email and password |

Both screens share the same **split-panel layout** — a white form panel on the left and a decorative dot-pattern panel on the right.

The Register screen is accessed via the invitation link sent by an admin. It is **not** a public self-registration page — the user arrives with a valid invitation token. The Name field is pre-filled from the invitation data.

---

## 2. Design Tokens

### 2.1 Colours

| Token | Hex | Usage |
|---|---|---|
| `--brand-blue` | `#3B5BDB` | Logo mark star icon |
| `--brand-blue-dark` | `#1E3A8A` | Logo text "VANGUARD X" |
| `--teal-500` | `#0D9488` | Links — "Terms and Condition", "Privacy Policy", "Sign In", "Sign Up" |
| `--teal-600` | `#0F766E` | Link hover state |
| `--red-500` | `#EF4444` | Required field asterisk `*`; inline error text |
| `--red-100` | `#FEE2E2` | Error input border background tint |
| `--gray-900` | `#111827` | Page title "Create Account" / "Sign In" — `font-weight: 700` |
| `--gray-600` | `#4B5563` | Page sub-title / description text |
| `--gray-500` | `#6B7280` | Field labels; placeholder text; helper text |
| `--gray-400` | `#9CA3AF` | Placeholder icons inside inputs; muted rule text (satisfied) |
| `--gray-300` | `#D1D5DB` | Input border default; checkbox border default |
| `--gray-200` | `#E5E7EB` | Submit button background (default / inactive state) |
| `--gray-100` | `#F3F4F6` | Right panel dot background base; input background on focus |
| `--white` | `#FFFFFF` | Left panel background; input background |
| `--dot-teal-light` | `#B2D8D8` | Right panel dot colour (large dots, bottom-left cluster) |
| `--dot-teal-mid` | `#9ECECE` | Right panel dot colour (mid-region) |
| `--dot-teal-faint` | `#D6EBEB` | Right panel dot colour (top-right faint region) |
| `--panel-bg` | `#EEF6F6` | Right panel background — very light teal-grey |
| `--rule-met` | `#9CA3AF` | Password rule row when condition is met (grey check) |
| `--rule-unmet` | `#D1D5DB` | Password rule row when condition not yet met |
| `--check-met-bg` | `#E5E7EB` | Circular check icon background when rule is met |

### 2.2 Typography

| Token | Value | Usage |
|---|---|---|
| `--font-family` | `'DM Sans', 'Segoe UI', sans-serif` | All text on auth screens |
| `--logo-font` | `700, 22px` | "VANGUARD X" brand text |
| `--title-font` | `700, 24px` | "Create Account" / "Sign In" heading |
| `--subtitle-font` | `400, 14px` | Description line below title |
| `--label-font` | `500, 13.5px` | Field labels |
| `--input-font` | `400, 13.5px` | Input text and placeholder text |
| `--helper-font` | `400, 12.5px` | Password rule lines |
| `--link-font` | `600, 13.5px` | "Terms and Condition", "Privacy Policy", "Sign In", "Sign Up" |
| `--footer-font` | `500, 13.5px` | "Already have an account?" / "Don't have an account?" |
| `--btn-font` | `600, 14px` | Submit button label |

### 2.3 Spacing

| Token | Value | Usage |
|---|---|---|
| `--form-gap` | `20px` | Vertical gap between form field groups |
| `--label-mb` | `6px` | Margin below label, above input |
| `--input-px` | `12px` | Input horizontal padding |
| `--input-py` | `11px` | Input vertical padding |
| `--section-mb` | `28px` | Margin below last form field before checkboxes |
| `--panel-px` | `60px` | Left panel horizontal padding (desktop) |
| `--panel-py` | `48px` | Left panel vertical padding (desktop) |

### 2.4 Borders & Radius

| Token | Value | Usage |
|---|---|---|
| `--input-radius` | `8px` | All text / email / password inputs |
| `--btn-radius` | `8px` | Submit button |
| `--checkbox-radius` | `4px` | Checkboxes |
| `--rule-icon-radius` | `50%` | Password rule check icon circle |
| `--input-border` | `1px solid #D1D5DB` | Default input border |
| `--input-border-focus` | `1.5px solid #0D9488` | Input border on focus |
| `--input-border-error` | `1.5px solid #EF4444` | Input border on validation error |

### 2.5 Shadows

| Token | Value | Usage |
|---|---|---|
| `--shadow-none` | `none` | Default inputs |
| `--shadow-focus` | `0 0 0 3px rgba(13,148,136,0.12)` | Input focus ring (teal glow) |
| `--shadow-btn` | `0 2px 8px rgba(0,0,0,0.10)` | Submit button hover |

---

## 3. Page Layout — Split Panel

Both screens use a **two-column full-viewport layout**:

```
┌─────────────────────────────┬──────────────────────────────────┐
│                             │                                  │
│      LEFT PANEL             │        RIGHT PANEL               │
│      (Form Area)            │        (Decorative)              │
│      width: ~52%            │        width: ~48%               │
│      background: #FFFFFF    │        background: #EEF6F6       │
│      overflow-y: auto       │        dot-pattern overlay       │
│                             │                                  │
│  ┌─────────────────────┐    │                                  │
│  │  Brand Header       │    │   ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○   │
│  │  Form Content       │    │  ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○    │
│  │  Footer Link        │    │ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○     │
│  └─────────────────────┘    │                                  │
│                             │                                  │
└─────────────────────────────┴──────────────────────────────────┘
```

| Property | Value |
|---|---|
| Outer container | `display: flex`, `min-height: 100vh`, `width: 100%` |
| Left panel | `flex: 0 0 52%`, `background: #FFFFFF`, `overflow-y: auto` |
| Right panel | `flex: 0 0 48%`, `background: #EEF6F6`, dot pattern, `position: relative` |
| Left panel inner | `max-width: 480px`, `margin: 0 auto`, `padding: 48px 60px` |

---

## 4. Left Panel — Form Area

**Background:** `#FFFFFF`
**Display:** Flex column
**Justify content:** `flex-start`
**Padding:** `48px 60px` (desktop)
**Max width of inner form:** `480px`, horizontally centred within panel

**Vertical stacking order:**
1. Brand Header (logo + name)
2. Screen title + description
3. Form fields
4. Password rules (Register only)
5. Agreement checkboxes (Register only)
6. Submit button
7. Footer navigation link

---

## 5. Right Panel — Decorative Area

**Background colour:** `#EEF6F6` (very light teal-grey)
**Content:** Repeating dot / oval pattern

### 5.1 Dot Pattern Specification

The right panel shows a grid of small oval / circular dots that fade from dense and saturated (bottom-left) to sparse and faint (top-right), creating a diagonal gradient effect.

| Property | Value |
|---|---|
| Dot shape | Slightly oval — `width: 8px, height: 10px, border-radius: 50%` |
| Dot grid | Repeating rows and columns, `gap: 10px horizontal, 8px vertical` |
| Dot colour — dense zone (bottom-left) | `#B2D8D8` at `opacity: 1.0` |
| Dot colour — mid zone | `#9ECECE` at `opacity: 0.7` |
| Dot colour — faint zone (top-right) | `#D6EBEB` at `opacity: 0.3` |
| Pattern direction | Diagonal fade: saturated bottom-left → faint top-right |
| Implementation | CSS `background-image: radial-gradient` repeating pattern OR SVG dot grid |

**CSS background-image approach (recommended):**
```css
.right-panel {
  background-color: #EEF6F6;
  background-image: radial-gradient(circle, #9ECECE 1px, transparent 1px);
  background-size: 18px 18px;
}
```

For the diagonal fade, layer a `linear-gradient` overlay:
```css
.right-panel::after {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(
    135deg,
    rgba(238,246,246,0.1) 0%,
    rgba(238,246,246,0.6) 60%,
    rgba(238,246,246,0.95) 100%
  );
  pointer-events: none;
}
```

---

## 6. Brand Header

Displayed at the top of the left panel, above the form title. Centred horizontally.

### 6.1 Elements

| Element | Spec |
|---|---|
| **Logo mark** | Snowflake / asterisk star SVG icon. Colour: `#3B5BDB` (blue-indigo). Width × height: `40×40px`. |
| **Brand name** | "VANGUARD X" — `font: 700 22px 'DM Sans'`, `color: #1E3A8A`, `letter-spacing: 0.5px` |
| **Layout** | Flex row, `align-items: center`, `gap: 8px`, `justify-content: flex-start` |
| **Margin bottom** | `32px` (space between header and form title) |

### 6.2 Logo SVG Description

The Vanguard X logo mark is a multi-pointed star / snowflake shape — 8 pointed arms radiating from a central ring, resembling a compass rose or asterisk. Each arm ends in a small circular tip.

**Approximate SVG structure:**
```
- 8 arms at 45° intervals
- Each arm: thin rectangle, rounded ends
- Small circle at tip of each arm
- Central open circle
- Fill: #3B5BDB
- viewBox: 0 0 40 40
```

---

## 7. Register Screen — Create Account

**Route:** `/auth/register?invitation={uid}&name={name}&email={email}&role_id={id}&role_name={name}`
**Title:** "Create Account"
**Sub-title:** "Join us today! Please fill in your details to create your account."

### 7.1 Screen Title Block

| Element | Spec |
|---|---|
| **Title** | "Create Account" — `font: 700 24px #111827` |
| **Description** | "Join us today! Please fill in your details to create your account." — `font: 400 14px #4B5563`, `margin-top: 6px` |
| **Margin bottom** | `24px` before first field |

### 7.2 Form Fields — Register

| # | Field | Label | Placeholder | Left icon | Right icon | Pre-filled | Required |
|---|---|---|---|---|---|---|---|
| 1 | Name | `Name *` | — | Person icon | — | Yes — from `name` query param | Yes |
| 2 | Email | `Email *` | "Enter your email" | Envelope icon | — | Yes — from `email` query param (read-only) | Yes |
| 3 | Password | `Password *` | "Your password" | Lock icon | Eye-slash toggle | No | Yes |
| 4 | Confirm password | `Confirm password *` | "Type again password" | Lock icon | Eye-slash toggle | No | Yes |

**Name field note:** Pre-filled from the invitation link query param `name`. The user can edit it if needed. It is not locked to read-only.

**Email field note:** Pre-filled from invitation query param `email` and rendered as **read-only** — the user cannot change the email at registration. Apply `background: #F9FAFB`, `cursor: not-allowed`, `color: #6B7280` to visually indicate it is locked.

### 7.3 Field Order (visual top to bottom)

```
Name field
Email field (read-only)
Password field
Confirm password field
─────────────────────────
Password rules checklist
─────────────────────────
☐ Terms and Condition checkbox
☐ Privacy Policy checkbox
─────────────────────────
[ Create Account ] button
─────────────────────────
Already have an account? Sign In
```

### 7.4 Submit Button — Register

| Property | Value |
|---|---|
| Label | "Create Account" |
| Width | `100%` |
| Background (inactive) | `#E5E7EB` (grey — disabled until form is valid) |
| Background (active / all valid) | `linear-gradient(135deg, #0F766E, #0D9488)` (teal gradient) |
| Text colour | `#374151` (inactive) → `#FFFFFF` (active) |
| Font | `600 14px` |
| Height | `44px` |
| Border radius | `8px` |
| Border | None |
| Cursor | `not-allowed` (inactive) → `pointer` (active) |
| Transition | `background 0.2s, color 0.2s` |

**Active state conditions (all must be true):**
- Name field is not empty
- Email field has valid format
- Password meets all rules (min 8 chars + special character)
- Confirm password matches Password
- Terms and Condition checkbox is checked
- Privacy Policy checkbox is checked

### 7.5 Footer Link — Register

```
Already have an account?  Sign In
```

| Element | Spec |
|---|---|
| Static text | "Already have an account?" — `font: 500 13.5px #374151` |
| Link | "Sign In" — `font: 600 13.5px #0D9488`, underline none, hover colour `#0F766E` |
| Layout | Flex row, centred, `gap: 4px` |
| Margin top | `20px` |
| Action | Navigate to `/auth/login` |

---

## 8. Login Screen — Sign In

**Route:** `/auth/login`
**Title:** "Sign In"
**Sub-title:** "Welcome back! Please enter your email and password to sign in."

### 8.1 Screen Title Block

| Element | Spec |
|---|---|
| **Title** | "Sign In" — `font: 700 24px #111827` |
| **Description** | "Welcome back! Please enter your email and password to sign in." — `font: 400 14px #4B5563`, `margin-top: 6px` |
| **Margin bottom** | `24px` before first field |

### 8.2 Form Fields — Login

| # | Field | Label | Placeholder | Left icon | Right icon | Required |
|---|---|---|---|---|---|---|
| 1 | Email | `Email *` | "Enter your email" | Envelope icon | — | Yes |
| 2 | Password | `Password *` | "Your password" | Lock icon | Eye-slash toggle | Yes |

### 8.3 Field Order (visual top to bottom)

```
Email field
Password field
─────────────────────────────────────
[ Sign In ] button
─────────────────────────────────────
Don't have an account? Sign Up
```

> **Note:** No "Forgot password?" link is shown in the current design. Add only if the feature is built — do not add as placeholder.

### 8.4 Submit Button — Login

| Property | Value |
|---|---|
| Label | "Sign In" |
| Width | `100%` |
| Background (inactive) | `#E5E7EB` |
| Background (active) | `linear-gradient(135deg, #0F766E, #0D9488)` |
| Text colour | `#374151` (inactive) → `#FFFFFF` (active) |
| Font | `600 14px` |
| Height | `44px` |
| Border radius | `8px` |
| Transition | `background 0.2s, color 0.2s` |

**Active state conditions:**
- Email field has valid email format
- Password field is not empty

### 8.5 Footer Link — Login

```
Don't have an account?  Sign Up
```

| Element | Spec |
|---|---|
| Static text | "Don't have an account?" — `font: 500 13.5px #374151` |
| Link | "Sign Up" — `font: 600 13.5px #0D9488`, hover `#0F766E` |
| Action | Navigate to `/auth/register` (or show message that registration requires an invitation) |

---

## 9. Shared Form Components

### 9.1 Form Field Group

Each field is wrapped in a `<div>` with this structure:

```
┌──────────────────────────────────────┐
│  Label text  *                       │  ← 13.5px weight 500 #6B7280
│                                      │    margin-bottom: 6px
│  ┌──────────────────────────────┐    │
│  │ 🔒  Placeholder text     👁  │    │  ← Input
│  └──────────────────────────────┘    │
│  Error message (if any)              │  ← 12px #EF4444, margin-top: 4px
└──────────────────────────────────────┘
```

**Vertical gap between field groups:** `20px`

### 9.2 Label

| Property | Value |
|---|---|
| Font | `500 13.5px #6B7280` |
| Margin bottom | `6px` |
| Required asterisk | `*` inline after label text, colour `#EF4444`, margin-left `2px` |
| Display | `block` |

Example: `Name *` where `*` is in red.

### 9.3 Input Field

| Property | Default | Focus | Error | Read-only |
|---|---|---|---|---|
| Background | `#FFFFFF` | `#FFFFFF` | `#FFFFFF` | `#F9FAFB` |
| Border | `1px solid #D1D5DB` | `1.5px solid #0D9488` | `1.5px solid #EF4444` | `1px solid #E5E7EB` |
| Border radius | `8px` | `8px` | `8px` | `8px` |
| Padding | `11px 12px 11px 38px` (with left icon) | Same | Same | Same |
| Font | `400 13.5px #111827` | Same | Same | `400 13.5px #6B7280` |
| Placeholder colour | `#9CA3AF` | `#9CA3AF` | `#9CA3AF` | — |
| Box shadow | None | `0 0 0 3px rgba(13,148,136,0.12)` | `0 0 0 3px rgba(239,68,68,0.10)` | None |
| Cursor | `text` | `text` | `text` | `not-allowed` |
| Width | `100%` | — | — | — |
| Box sizing | `border-box` | — | — | — |
| Transition | `border-color 0.15s, box-shadow 0.15s` | — | — | — |

### 9.4 Left Icon inside Input

Positioned absolutely inside the input wrapper.

| Property | Value |
|---|---|
| Position | `absolute`, `left: 12px`, `top: 50%`, `transform: translateY(-50%)` |
| Size | `16×16px` SVG |
| Colour | `#9CA3AF` |
| Pointer events | `none` |

**Icon map:**

| Field | Icon |
|---|---|
| Name | Person / user silhouette outline |
| Email | Envelope outline |
| Password | Padlock closed outline |
| Confirm password | Padlock closed outline |

### 9.5 Right Icon inside Input — Password Toggle

Shown on Password and Confirm Password fields only.

| Property | Value |
|---|---|
| Position | `absolute`, `right: 12px`, `top: 50%`, `transform: translateY(-50%)` |
| Size | `18×18px` SVG |
| Colour | `#9CA3AF` |
| Cursor | `pointer` |
| Icon — hidden state | Eye with slash through it (password hidden — dots shown) |
| Icon — visible state | Open eye (password text visible) |
| Toggle action | Click toggles `input type` between `"password"` and `"text"` |

---

## 10. Password Rules Checklist

Shown **only on the Register screen**, below the Confirm Password field and above the checkboxes. Updates in real-time as the user types in the Password field.

### 10.1 Layout

Flex column, `gap: 8px`, `margin-top: 12px`, `margin-bottom: 20px`

### 10.2 Rules

| # | Rule text | Condition |
|---|---|---|
| 1 | "Must be at least 8 characters" | `password.length >= 8` |
| 2 | "Must contain one special character" | `/[!@#$%^&*(),.?":{}|<>]/.test(password)` |

> Additional rules can be added as requirements grow. Each new rule follows the same component pattern below.

### 10.3 Rule Row Component

Each rule is a flex row: `align-items: center`, `gap: 10px`

```
[●]  Must be at least 8 characters
```

| Sub-element | Unmet state | Met state |
|---|---|---|
| **Check icon circle** | `18×18px`, `border-radius: 50%`, `background: #F3F4F6`, grey outline circle icon inside | `18×18px`, `border-radius: 50%`, `background: #E5E7EB`, filled grey checkmark icon inside |
| **Rule text** | `font: 400 12.5px #D1D5DB` (very light — not yet met) | `font: 400 12.5px #9CA3AF` (medium grey — satisfied) |

**Note from screenshot:** Both rules shown in the screenshot are in the "met" state (grey filled check circles, medium grey text). This is consistent with the password "Super" being in the Name field and the password fields being filled in the demo. Implement real-time reactive updates.

---

## 11. Terms & Privacy Checkboxes

Shown **only on the Register screen**, below the password rules checklist.

**Layout:** Flex column, `gap: 12px`, `margin-bottom: 24px`

### 11.1 Checkbox Row Component

Each row is a flex row: `align-items: flex-start`, `gap: 10px`

```
[ ]  I have read and agree to the  Terms and Condition
[ ]  I accept the use of cookies in accordance with the  Privacy Policy
```

| Sub-element | Spec |
|---|---|
| **Checkbox input** | `16×16px`, `border-radius: 4px`, `border: 1.5px solid #D1D5DB`, `accent-color: #0D9488` |
| **Checkbox — checked** | Background `#0D9488`, white tick mark, `border-color: #0D9488` |
| **Checkbox — unchecked** | Background `#FFFFFF`, border `#D1D5DB` |
| **Static text** | `font: 400 13.5px #374151` |
| **Link text** | `font: 600 13.5px #0D9488`, no underline by default, underline on hover |
| **Link hover colour** | `#0F766E` |

### 11.2 Checkbox Rows

| # | Full text | Link text | Link target |
|---|---|---|---|
| 1 | "I have read and agree to the **Terms and Condition**" | "Terms and Condition" | `/terms` or modal |
| 2 | "I accept the use of cookies in accordance with the **Privacy Policy**" | "Privacy Policy" | `/privacy` or modal |

**Validation rule:** Both checkboxes must be checked before the Create Account button becomes active (transitions from grey to teal gradient).

---

## 12. Submit Button

Full specification in Sections 7.4 (Register) and 8.4 (Login). Common behaviour summarised here.

### 12.1 States

| State | Background | Text colour | Cursor | Box shadow |
|---|---|---|---|---|
| **Disabled / inactive** | `#E5E7EB` | `#374151` | `not-allowed` | None |
| **Active / enabled** | `linear-gradient(135deg, #0F766E, #0D9488)` | `#FFFFFF` | `pointer` | None |
| **Hover (active only)** | Same gradient | `#FFFFFF` | `pointer` | `0 2px 8px rgba(0,0,0,0.10)` |
| **Loading / submitting** | Gradient (dimmed, `opacity: 0.8`) | `#FFFFFF` | `not-allowed` | None |

### 12.2 Loading State

While the API call is in-flight after button click:
- Show a spinning circle icon (white, `16×16px`) replacing or preceding the button label
- Label changes to "Creating account…" (Register) or "Signing in…" (Login)
- Button is disabled to prevent double-submit

---

## 13. Footer Navigation Links

### 13.1 Register Screen Footer

```
Already have an account?  Sign In
```

- Centred horizontally
- `margin-top: 20px`
- "Already have an account?" — `500 13.5px #374151`
- "Sign In" — `600 13.5px #0D9488`, navigates to `/auth/login`

### 13.2 Login Screen Footer

```
Don't have an account?  Sign Up
```

- Centred horizontally
- `margin-top: 20px`
- "Don't have an account?" — `500 13.5px #374151`
- "Sign Up" — `600 13.5px #0D9488`, navigates to `/auth/register` or shows invitation-required message

---

## 14. Form Validation & Error States

### 14.1 Inline Field Errors

Shown directly below the affected input field.

| Property | Value |
|---|---|
| Font | `400 12px #EF4444` |
| Margin top | `4px` |
| Display | Block, below input |

### 14.2 Register Screen Errors

| Field | Trigger | Error message |
|---|---|---|
| Name | Empty on submit | "Name is required." |
| Name | Exceeds 150 chars | "Name cannot exceed 150 characters." |
| Email | Empty on submit | "Email is required." |
| Email | Invalid format | "Please enter a valid email address." |
| Password | Empty on submit | "Password is required." |
| Password | Fewer than 8 chars | "Password must be at least 8 characters." |
| Password | No special character | "Password must contain at least one special character." |
| Confirm password | Empty on submit | "Please confirm your password." |
| Confirm password | Does not match password | "Passwords do not match." |
| Terms checkbox | Unchecked on submit | "You must agree to the Terms and Conditions." |
| Privacy checkbox | Unchecked on submit | "You must accept the Privacy Policy." |

### 14.3 Login Screen Errors

| Field | Trigger | Error message |
|---|---|---|
| Email | Empty on submit | "Email is required." |
| Email | Invalid format | "Please enter a valid email address." |
| Password | Empty on submit | "Password is required." |

### 14.4 API-level Errors (Toast Notifications)

Shown as a toast in top-right corner. Style: `background: #FEF2F2`, `border: 1px solid #FCA5A5`, `color: #991B1B`, `border-radius: 10px`, `padding: 12px 16px`, `font: 13px`, auto-dismiss after 5 seconds.

| Trigger | Toast message |
|---|---|
| `POST /api/auth/register` → `TOKEN_NOT_FOUND` | "This invitation link is invalid or has already been used." |
| `POST /api/auth/register` → `TOKEN_EXPIRED` | "This invitation has expired. Please contact your administrator." |
| `POST /api/auth/register` → `WEAK_PASSWORD` | "Password does not meet the strength requirements." |
| `POST /api/auth/register` → `PASSWORD_MISMATCH` | "Passwords do not match." |
| `POST /api/auth/login` → `INVALID_CREDENTIALS` | "Incorrect email or password. Please try again." |
| `POST /api/auth/login` → `ACCOUNT_INACTIVE` | "Your account has been deactivated. Please contact your administrator." |
| Network error | "Something went wrong. Please check your connection and try again." |

### 14.5 Validation Timing

| Field | When validation triggers |
|---|---|
| Required fields | On blur (leaving the field) AND on submit attempt |
| Email format | On blur |
| Password rules checklist | Real-time as user types (live update, no error text — just rule row states) |
| Confirm password match | On blur of confirm field AND on any change to password field after confirm has been touched |
| Checkboxes | On submit attempt only |

---

## 15. API Connections

### 15.1 Register Screen

| Action | Method | Endpoint | Trigger |
|---|---|---|---|
| Page load — validate invitation token | `GET` | `/api/auth/register/validate?token={token}` | On mount, before showing form |
| Pre-fill name and email | — | From URL query params `name`, `email` | Immediately on mount |
| Submit registration | `POST` | `/api/verify-invitation` | On "Create Account" button click (form valid) |

**On successful registration:**
1. Store `access_token` from response in auth state (localStorage / cookie / context)
2. Redirect to application dashboard `/dashboard`

**On `TOKEN_NOT_FOUND` or `TOKEN_EXPIRED` during page load:**
- Do not render the form
- Show a full-page error state with the message and a "Contact your administrator" note

### 15.2 Login Screen

| Action | Method | Endpoint | Trigger |
|---|---|---|---|
| Submit login | `POST` | `/api/auth/login` | On "Sign In" button click (form valid) |

**Login request body:**
```json
{
  "email": "jane.smith@example.com",
  "password": "SecureP@ss1"
}
```

**On successful login:**
1. Store `access_token` from response
2. Redirect to `/dashboard`

---

## 16. Component States Summary

### 16.1 Register Screen — State Machine

```
URL loads with ?invitation=...
         │
         ▼
  Validate token (GET /api/auth/register/validate)
         │
    ┌────┴────────────────────┐
    │                         │
  Valid                   Invalid / Expired
    │                         │
    ▼                         ▼
Show form              Show error page
(name + email           "Link invalid or
 pre-filled)             expired"
    │
    ▼
User fills password
+ confirm password
(real-time rule checks)
    │
    ▼
User checks both
checkboxes
    │
    ▼
Button becomes
teal (active)
    │
    ▼
User clicks
"Create Account"
    │
    ├── API call in-flight → button shows spinner, label = "Creating account…"
    │
    ├── 200 OK → store token → redirect to /dashboard
    │
    └── Error → show toast → re-enable button
```

### 16.2 Login Screen — State Machine

```
User lands on /auth/login
         │
         ▼
  Enter email + password
  (button activates when both filled)
         │
         ▼
  Click "Sign In"
         │
         ├── API call in-flight → spinner + "Signing in…"
         │
         ├── 200 OK → store token → redirect to /dashboard
         │
         └── Error → show toast → re-enable button
```

---

## 17. Responsive Behaviour

| Breakpoint | Left panel | Right panel |
|---|---|---|
| `≥ 1024px` (desktop) | `flex: 0 0 52%`, `padding: 48px 60px` | `flex: 0 0 48%`, visible |
| `768px – 1023px` (tablet) | `flex: 0 0 60%`, `padding: 40px 48px` | `flex: 0 0 40%`, visible (dot pattern scaled down) |
| `< 768px` (mobile) | `flex: 0 0 100%`, `padding: 32px 24px` | Hidden (`display: none`) |

**Mobile behaviour:**
- Right panel hidden completely
- Left panel takes full width
- Form inner width: `100%`
- Brand header centred on mobile
- All padding reduced to `32px 24px`
- Input height reduced slightly: `padding: 10px 12px 10px 36px`

---
## Task Status
| Task Type | Status | Assignee | Notes |
|---|---|---|---|
| Development | Completed | Agent | Implemented Login and Register screens with split-panel UI and profile icon navigation. |
| Testing | Pending |  | |
