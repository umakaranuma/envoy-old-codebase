---
name: nextjs-code-writing
description: Guides writing Next.js code following project folder and file structure, environment variable usage (NEXT_PUBLIC_ for client only), HTTP request handling (native fetch), cookies/localStorage handling, and Zod for form validation and sanitization. Use when creating routes, shared code, forms, API calls, or when using env vars, cookies, localStorage, or Zod.
---

# Next.js Code Writing

## Project folder and file structure

Follow this layout for all new routes and shared code.

### App structure (`app/`)

- **Root layout** – `layout.tsx` (server component). Should only contain the `html` tag; its child content can live in `common/components/`.
- **Route prefixes** – Use `{prefix}/` segments: e.g. `auth` for authentication, `a` for admin, and a group route like `(public)` for public pages.

Example:

- `app/`
  - `layout.tsx` (server component) — only the `html` tag; child can be in `common/components/`
  - `auth/`
    - `layout.tsx` (server component) — can live in `common/components/`; may contain other tags like `body` (not `html`)
    - `login/page.tsx` (server component)
    - `register/page.tsx` (server component)
    - `forgot-password/page.tsx` (server component)
    - `reset-password/page.tsx` (server component)
    - `verify-email/page.tsx` (server component)
  - `a/`
    - `dashboard/page.tsx` (server component)
    - `users/page.tsx` (server component)
    - `settings/page.tsx` (server component)
    - `profile/page.tsx` (server component)
  - `(public)/`
    - `home/page.tsx` (server component)

### Setup (`setup/`)

Keep env templates here (no secrets). Copy to project root when setting up:

- `.env.example`, `.env.local.example`, `.env.production.example`, `.env.development.example`, `.env.test.example`, `.env.staging.example`

### Route-scoped code (`app/{route}/_route/`)

Under each route segment, use a `_route` folder (underscore = private to Next.js routing, `route` = scoped to this route) for all route-private code. It contains:

- **components/** – Single `.tsx` or grouped folders
- **services/** – Single `.ts` or grouped folders
- **api-services/** – `{name}.client.ts` and `{name}.server.ts` (single or in grouped folders)
- **types/** – Type definitions
- **helpers/** – Pure utility functions, Zod schemas, formatters
- **hooks/** – Custom hooks
- **constants/** – Route-level constants
- **interfaces/** – Interfaces

Full example structure:

```
app/a/boards/
├── page.tsx
└── _route/
    ├── components/
    ├── services/
    ├── api-services/
    ├── hooks/
    ├── types/
    ├── interfaces/
    ├── constants/
    └── helpers/        ← pure utils, Zod schemas, formatters
```

Each route has its own `page.tsx` (server component). Nested routes repeat the same `_route` structure under their segment.

### Shared code (`common/`)

Reusable across the app (same subfolders as `_route/`, no `_route` wrapper):

- `components/`, `services/`, `api-services/`, `types/`, `helpers/`, `hooks/`, `constants/`, `interfaces/`

### Libraries (`lib/`)

Shared library wrappers and configs (e.g. `redis.ts`, `socket.io.ts`):

- Single file → `{name}.ts` in `lib/`
- Group → `{group}/` folder with individual `{name}.ts` files inside

### Rules

- **Route-specific** → `app/{route}/_route/{category}/`
- **Shared** → `common/{category}/`; **library wrappers** → `lib/`
- **Pages** → `page.tsx` at the route segment; keep as server components.
- Single files go directly in the category folder; related groups get a subfolder with individual files inside.
- **api-services** – Use `.client.ts` for client-side API calls and `.server.ts` for server-side (e.g. in server components or route handlers).

---

## Environment variables

**Sensitive environment variables** (any env var *not* prefixed with `NEXT_PUBLIC_`) must **only** be used in:

- Server components
- Server-side service files (e.g. `*.server.ts`, server-only code in `services/`)

They must **never** be accessed in client-side code (client components, `'use client'` files, client-only helpers, or any code that runs in the browser).

**Client-accessible variables** – Only variables prefixed with `NEXT_PUBLIC_` may be read in client-side code. Anything else is stripped from the client bundle and must not be relied on there.

---

## HTTP request handling

Do **not** use any third-party HTTP library (e.g. axios, ky). Use only the native JavaScript **`fetch`** API. All app HTTP calls go through a single shared handler under **`common/helpers/`**.

### Handler location and file

- **Path:** `common/helpers/httpClient.ts`
- **Role:** One place for all `fetch`-based requests; no extra dependencies.

### Interface

Define a single function used by both `.client.ts` and `.server.ts` api-services:

- **`sendRequest(options)`** – `options`: `url` (string), `method` (e.g. `'GET'`, `'POST'`, `'PUT'`, `'PATCH'`, `'DELETE'`), optional `data` (object, sent as JSON body), optional `headers` (record of strings), optional `signal` (`AbortSignal` for cancellation/timeout). Returns a Promise with the parsed response and status so callers can type the result as `IApiResponse`.

### Implementation requirements

- Use **only** the global **`fetch`** (no wrappers or packages).
- **Headers:** Default `Content-Type: application/json` when `data` is provided; merge with any `options.headers`.
- **Body:** When `method` is not `GET` and `data` is provided, send `JSON.stringify(data)` as body.
- **Response:** Parse with `response.json()` when the response has JSON content-type; otherwise return a safe fallback or throw so callers can handle errors.
- **Errors:** Catch network failures and non-OK responses; return a consistent shape (e.g. `{ responseData, status, ok }`) so api-services can always read `responseData` and optionally check `status` / `ok`.
- **Cancellation / timeout:** Support `signal` (e.g. from `AbortController`) so callers can implement timeouts or cancel in-flight requests.

### Return shape

Return an object that api-services can use without touching `fetch` directly:

- **`ok`** – boolean, same as `response.ok`
- **`status`** – number, HTTP status code
- **`responseData`** – parsed JSON (or fallback object on parse error), so callers can cast to `IApiResponse<T>`

### Usage in api-services

- **Client:** In `*.client.ts`, use `NEXT_PUBLIC_` env vars for base URL (e.g. `NEXT_PUBLIC_API_URL`). Call `sendRequest({ url, method, data })` and use `response.responseData as IApiResponse`.
- **Server:** In `*.server.ts`, you may use non-public env vars for URLs; same `sendRequest` signature. For timeout, create an `AbortController`, pass its `signal` to `sendRequest`, and `abort()` after a delay if needed.

Example (client):

```ts
// app/a/boards/_route/api-services/board.client.ts
import { sendRequest } from "@/common/helpers/httpClient"
import { IApiResponse } from "@/common/interfaces/ICommon"

export async function createBoard(data: BoardFormData): Promise<IApiResponse> {
  const { responseData } = await sendRequest({
    url: `${process.env.NEXT_PUBLIC_API_URL}/api/recruiters/crm-boards`,
    method: "POST",
    data,
  })
  return responseData as IApiResponse
}
```

Optional timeout (e.g. in server or client):

```ts
const controller = new AbortController()
const timeoutId = setTimeout(() => controller.abort(), 10_000)
const { responseData } = await sendRequest({
  url: "...",
  method: "GET",
  signal: controller.signal,
})
clearTimeout(timeoutId)
```

---

## Cookies and localStorage handling

Anywhere code gets, stores, deletes, or updates values in cookies or localStorage, use the following pattern. Place these files in **`common/constants/`** (for `storageKeys.ts`) and **`common/helpers/`** (for handlers and commonService).

### 1. `storageKeys.ts`

Holds all storage keys for cookies and localStorage. Use a single source of truth; no raw string keys elsewhere.

- **`isEncrypted`** – `true` when `NODE_ENV === 'production'` and `ENVIRONMENT` is `production` / `prod` / `demo`; use so dev can read keys in the browser.
- **Cookies** – export object `cookie` with one entry per key. Each entry: `name`, `secretName` (unique), `encrypted` (boolean).
- **Local storage** – export object `local_storage` with same shape.
- **Dynamic keys** – use placeholders in `name` (e.g. `selected_org_${user_id}_${org_id}`); pass `replacements` when calling get/set/clear.

Example:

```ts
const isEncrypted = process.env.NODE_ENV === 'production' &&
  (process.env.ENVIRONMENT === 'production' || process.env.ENVIRONMENT === 'prod' || process.env.ENVIRONMENT === 'demo');

export const cookie = {
  access_token: { name: 'access_token', secretName: 'RTASKXFGLSIZXZBXEEFK', encrypted: isEncrypted },
  theme_mode: { name: 'theme_mode', secretName: 'OKHGKXFGDFGSXZBXVCXS', encrypted: false },
  selected_org: { name: 'selected_org_${user_id}_${org_id}', secretName: 'OKHGKXFGDFASSDBXVCXS', encrypted: false },
};

export const local_storage = {
  auth_user_info: { name: 'auth_user_info', secretName: 'FSDVKXFGLESDRZBXITGH', encrypted: isEncrypted },
  selected_sub_module: { name: 'selected_sub_module_${user_id}_${module_id}', secretName: 'OKHGKXFGDFWESDBXVCXS', encrypted: false },
};
```

Define **`IStorageOptions`** (e.g. in `common/interfaces/`) as `{ name: string; secretName: string; encrypted: boolean }`.

### 2. `cookiesHandler.ts`

Server-only: use `'use server'` and `cookies()` from `next/headers`. Implement:

- **getCookies(storageKey, options?)** – resolve key name (use `secretName` when `encrypted`), apply `replacePlaceholders` if `options.replacements`, get from cookie store; if `encrypted`, decrypt and return.
- **setCookies(storageKey, options?)** – same key resolution; if `encrypted`, encrypt `options.value` then set. Support `expires`, `maxAge`, `domain`, `path`, `secure`, `httpOnly`, `sameSite`.
- **clearCookie(storageKey, options?)** – resolve key (with replacements) and delete that cookie.
- **clearAllCookies()** – delete all cookies (e.g. loop over `cookieStore.getAll()` and delete each by name).

Import `decrypt`, `encrypt`, `replacePlaceholders` from the common service and `IStorageOptions` from interfaces.

### 3. `localStorageHandler.ts`

Client-only: guard with `typeof window !== 'undefined'`. Implement:

- **getLocalStorage(storageKey, options?)** – resolve key (secretName when encrypted, apply replacements); `localStorage.getItem`; if encrypted, decrypt (with try/catch, return null on error); otherwise parse JSON and return.
- **setLocalStorage(storageKey, options?)** – resolve key; if encrypted, encrypt `options.value`; store with `localStorage.setItem(itemName, JSON.stringify(value))`.
- **clearLocalStorage(storageKey, options?)** – resolve key and `localStorage.removeItem(itemName)`.
- **clearAllLocalStorage()** – `localStorage.clear()`.

Import `IStorageOptions`, `decrypt`, `encrypt`, `replacePlaceholders` from the same common service and interfaces.

### 4. `commonService.ts`

- **replacePlaceholders(template, replacements)** – replace `${key}` in template with `replacements[key]` (regex e.g. `/\${(\w+)}/g`).
- **encrypt(value)** – use `process.env.CRYPT_SECRET_KEY`; implement with chosen encryption library; return encrypted value.
- **decrypt(encryptedValue)** – same secret; decrypt and return. Ensure this and the secret are not exposed to the client.

### Usage

- **Cookies (server):** `getCookies(cookie.access_token)`, `setCookies(cookie.access_token, { value })`, `clearCookie(cookie.access_token)`, `clearAllCookies()`.
- **LocalStorage (client):** `getLocalStorage(local_storage.auth_user_info)`, `setLocalStorage(local_storage.auth_user_info, { value })`, `clearLocalStorage(local_storage.auth_user_info)`, `clearAllLocalStorage()`.
- **Dynamic keys:** always pass `replacements`, e.g. `getCookies(cookie.selected_org, { replacements: { user_id: '1', org_id: '1' } })`, and same for set/clear. Same pattern for `local_storage` keys with placeholders.

---

## Form Validation & Submission

Use **react-hook-form + Zod** as the standard for all forms. This gives you type safety, client-side validation, sanitization, and a clean way to surface backend errors — all in one consistent pattern.

### Install

```bash
npm install zod react-hook-form @hookform/resolvers sanitize-html
npm install -D @types/sanitize-html
```

### API Response Shape

Every API response follows this structure:

```ts
// common/interfaces/ICommon.ts
export interface IApiResponse<T = null> {
  is_success: boolean
  message: string
  result: T | null               // GET: returned data. POST success: stored value or null.
                                 // POST fail (417): field validation errors { field: string[] }
  system_code: string            // empty string normally; special codes for middleware-level events
                                 // e.g. "user_inactive", "subscription_expired"
}
```

**`result` behaviour by context:**

| Scenario | `result` value |
|---|---|
| GET success | The returned data |
| POST / PUT success | Stored/created value, or `null` |
| POST / PUT validation fail (417) | `{ fieldName: ["error msg"] }` |
| Other errors | `null` |

**`system_code` examples** — set by backend middleware before the main handler runs:

| Code | Meaning |
|---|---|
| `""` (empty) | Normal response, no special handling needed |
| `"user_inactive"` | User account is inactive |
| `"subscription_expired"` | Subscription has lapsed |
| Any non-empty value | Handle explicitly in the form or a shared response handler |

---

### Flow

```
User submits
     ↓
react-hook-form runs Zod resolver
     ↓ fail → errors shown inline per field, no API call
     ↓ pass (data is validated + sanitized by Zod)
API call with clean data
     ↓
Check system_code first — handle middleware-level events (redirect, notify, etc.)
     ↓ no system_code
Check is_success
     ↓ false + 417 → result has field errors → setError() per field
     ↓ false + other → message is global error → setError("root")
     ↓ true → proceed (use result if needed)
```

---

### Step 1 — Define the Zod Schema

Place in `_route/helpers/` (route-specific) or `common/helpers/` (shared). Validate and sanitize in the same schema using `.transform()`.

```ts
// app/a/boards/_route/helpers/boardSchema.ts
import { z } from "zod"
import sanitizeHtml from "sanitize-html"

const clean = (val: string) =>
  sanitizeHtml(val.trim(), { allowedTags: [], allowedAttributes: {} })

export const boardSchema = z.object({
  title: z.string()
    .min(1, "Title is required")
    .max(100, "Title too long")
    .transform(clean),

  status: z.enum(["active", "closed"], {
    required_error: "Status is required",
  }),

  description: z.string()
    .max(1000)
    .optional()
    .transform(val => val ? clean(val) : ""),

  email: z.string()
    .email("Invalid email")
    .transform(val => val.trim().toLowerCase()),

  // Numbers from inputs come in as strings — use coerce
  age: z.coerce.number().int().min(18, "Must be 18+").optional(),
})

export type BoardFormData = z.infer<typeof boardSchema>
```

**Common validators:**

| Use case | Zod syntax |
|---|---|
| Required string | `z.string().min(1, "Required")` |
| Email | `z.string().email("Invalid email")` |
| Number from input | `z.coerce.number().min(0)` |
| Optional | `z.string().optional()` |
| Enum / select | `z.enum(["a", "b"])` |
| Strip HTML | `.transform(val => sanitizeHtml(val.trim(), { allowedTags: [] }))` |

**Password confirmation:**
```ts
const schema = z.object({
  password: z.string().min(8),
  confirmPassword: z.string(),
}).refine(d => d.password === d.confirmPassword, {
  message: "Passwords don't match",
  path: ["confirmPassword"],
})
```

---

### Step 2 — API Service Function

Returns `IApiResponse` directly — no error interpretation inside the service. All response handling stays in the form.

```ts
// app/a/boards/_route/api-services/board.client.ts
import { BoardFormData } from "../helpers/boardSchema"
import { IApiResponse } from "@/common/interfaces/ICommon"

export async function createBoard(data: BoardFormData): Promise<IApiResponse> {
  const response = await sendRequest({
    url: `${process.env.NEXT_PUBLIC_API_URL}/api/recruiters/crm-boards`,
    method: "POST",
    data,
  })

  return response.responseData as IApiResponse
}
```

> `NEXT_PUBLIC_` prefix is required for env vars used in client-side code.

---

### Step 3 — The Form Component

```tsx
// app/a/boards/_route/components/BoardForm.tsx
"use client"

import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { boardSchema, type BoardFormData } from "../helpers/boardSchema"
import { createBoard } from "../api-services/board.client"

export default function BoardForm({ onSuccess }: { onSuccess: () => void }) {
  const {
    register,
    handleSubmit,
    setValue,
    setError,
    formState: { errors, isSubmitting },
    reset,
  } = useForm<BoardFormData>({
    resolver: zodResolver(boardSchema),
  })

  const onSubmit = async (data: BoardFormData) => {
    // data is already validated + sanitized by Zod at this point
    const response = await createBoard(data)

    // 1. Handle system_code first (if needed for this call) — middleware-level events
    if (response.system_code) {
      switch (response.system_code) {
        case "user_inactive":
          setError("root", { message: "Your account is inactive. Please contact support." })
          return
        case "subscription_expired":
          window.location.href = "/pricing"
          return
        default:
          setError("root", { message: response.message })
          return
      }
    }

    // 2. Field-level validation errors from backend (417)
    //    result is { fieldName: ["error message"] }
    if (!response.is_success && response.result && typeof response.result === "object") {
      Object.entries(response.result as Record<string, string[]>).forEach(([field, messages]) => {
        setError(field as keyof BoardFormData, {
          type: "server",
          message: messages[0],
        })
      })
      return
    }

    // 3. Global error — message describes what went wrong
    if (!response.is_success) {
      setError("root", { type: "server", message: response.message })
      return
    }

    // 4. Success
    reset()
    onSuccess()
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)}>

      {/* Global / root error banner */}
      {errors.root && (
        <div role="alert">{errors.root.message}</div>
      )}

      <div>
        <label>Title</label>
        <input {...register("title")} placeholder="Title" />
        {errors.title && <span role="alert">{errors.title.message}</span>}
      </div>

      <div>
        <label>Description</label>
        <input
          type="textarea"
          rows={4}
          placeholder="Description"
          {...register("description")}
        />
        {errors.description && <span role="alert">{errors.description.message}</span>}
      </div>

      <div>
        <button type="button" onClick={() => reset()}>Cancel</button>
        <button type="submit" disabled={isSubmitting}>
          {isSubmitting ? "Processing..." : "Proceed"}
        </button>
      </div>

    </form>
  )
}
```

> Use `setValue` in the `onChange` handler instead of `{...register(...)}`.

---

### Sanitization Reference

| Threat | Fix |
|---|---|
| XSS / HTML injection | `sanitizeHtml(val, { allowedTags: [] })` in `.transform()` |
| Whitespace | `.trim()` inside `.transform()` |
| Email casing | `.toLowerCase()` inside `.transform()` |
| SQL injection | Use parameterized queries (Prisma handles automatically) |

> **Golden rule:** Never trust client-side validation alone. Always validate on the server too — Zod on the client only saves a round-trip.

---