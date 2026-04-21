# Vanguard X — Design System

> **Version:** 1.0.0 · **Platform:** Web (Desktop-first) · **©2024 Envoy**

---

## Table of Contents

1. [Brand & Identity](#1-brand--identity)
2. [Color Palette](#2-color-palette)
3. [Typography](#3-typography)
4. [Spacing & Layout](#4-spacing--layout)
5. [Border Radius](#5-border-radius)
6. [Shadows & Elevation](#6-shadows--elevation)
7. [CSS Variables (Tokens)](#7-css-variables-tokens)
8. [Components](#8-components)
   - [Sidebar Navigation](#81-sidebar-navigation)
   - [Top Bar](#82-top-bar)
   - [Buttons](#83-buttons)
   - [Form Inputs](#84-form-inputs)
   - [Search Box](#85-search-box)
   - [Tabs](#86-tabs)
   - [Table](#87-table)
   - [Pagination](#88-pagination)
   - [Status Badges](#89-status-badges)
   - [Checkboxes](#810-checkboxes)
   - [Module Accordion (Privileges)](#811-module-accordion-privileges)
   - [Hierarchy / Org Chart Node](#812-hierarchy--org-chart-node)
   - [Cards](#813-cards)
   - [Breadcrumb](#814-breadcrumb)
   - [Row Actions](#815-row-actions)
9. [Page Templates](#9-page-templates)
   - [List Page](#91-list-page)
   - [Add / Edit Form Page](#92-add--edit-form-page)
   - [Single / Detail View Page](#93-single--detail-view-page)
   - [Hierarchy View Page](#94-hierarchy-view-page)
10. [Motion & Animation](#10-motion--animation)
11. [Iconography](#11-iconography)
12. [Accessibility](#12-accessibility)
13. [Do / Don't](#13-do--dont)

---

## 1. Brand & Identity

| Item | Value |
|------|-------|
| **Product Name** | Vanguard X |
| **Tagline** | Insurance management platform |
| **Logo Mark** | Layered chevron / stack icon, `#6C63FF` fill, 28×28 px, `border-radius: 7px` |
| **Wordmark** | `VANGUARD X` in **Syne 800**, `letter-spacing: 0.04em`, `#12122A` |
| **Favicon** | Logo mark at 16×16 and 32×32 |

### Logo Usage

```
┌─────────┐  VANGUARD X
│  ✦ icon │  (Syne Extra-Bold, #12122A)
└─────────┘
  28×28px    font-size: 13.5px
```

- Minimum clear space: 8 px on all sides
- Never recolor the wordmark
- Never stretch or skew the logo mark

---

## 2. Color Palette

### Primary

| Token | Hex | Usage |
|-------|-----|-------|
| `--accent` | `#6C63FF` | Primary interactive, active states, focus rings |
| `--accent-soft` | `#EDEEFF` | Active nav backgrounds, badge fills, chip fills |
| `--accent-hover` | `#5449E0` | Hover state on `--accent` surfaces |

### Secondary / CTA

| Token | Hex | Usage |
|-------|-----|-------|
| `--teal` | `#00A8A2` | Primary CTA buttons (Invite, Create, Add New) |
| `--teal-hover` | `#007F7A` | Hover on teal buttons |
| `--teal-soft` | `#E0FAF8` | Edit icon hover background |

### Neutrals

| Token | Hex | Usage |
|-------|-----|-------|
| `--bg` | `#F7F8FC` | Page background |
| `--surface` | `#FFFFFF` | Cards, sidebar, topbar, inputs |
| `--surface-2` | `#F0F2FA` | Table header, hover rows, secondary surfaces |
| `--border` | `#E3E6F0` | All dividers, input borders, card borders |

### Text

| Token | Hex | Usage |
|-------|-----|-------|
| `--text-primary` | `#12122A` | Headings, table cell names, labels |
| `--text-secondary` | `#5B5E7A` | Descriptions, secondary labels, nav items |
| `--text-muted` | `#9295B0` | Placeholder, meta info, column headers |

### Semantic

| Token | Hex | Usage |
|-------|-----|-------|
| `--success` / Active | `#22C55E` bg `#DCFCE7` | Active status badge |
| `--warning` / Pending | `#F59E0B` bg `#FEF3C7` | Pending status badge |
| `--danger` | `#FF5A5F` | Delete hover, Cancelled badge, notification dot |
| `--danger-soft` | `#FFF0F0` | Delete hover background |

---

## 3. Typography

### Font Stack

```css
--font-head: 'Syne', sans-serif;   /* Headings, logo, card titles, page titles */
--font-body: 'DM Sans', sans-serif; /* All body text, labels, inputs, nav */
```

Import via Google Fonts:
```html
<link href="https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet">
```

### Type Scale

| Role | Font | Size | Weight | Line Height | Usage |
|------|------|------|--------|-------------|-------|
| Page Title | Syne | 24–26px | 800 | 1.2 | `<h1>` on every list/form page |
| Card Title | Syne | 15–16px | 700 | 1.3 | Section headers inside cards |
| Form Page Title | Syne | 22px | 800 | 1.2 | Add New / Edit form headings |
| Nav Section Label | DM Sans | 9.5–10px | 700 | 1 | Sidebar group labels (uppercase) |
| Nav Item | DM Sans | 12.5–13px | 400/500 | 1.4 | Sidebar links |
| Table Column Header | DM Sans | 10–10.5px | 600 | 1 | `<th>` (uppercase, tracked) |
| Table Cell — Primary | DM Sans | 13.5px | 600 | 1.5 | Role name, user name, title |
| Table Cell — Secondary | DM Sans | 13px | 400 | 1.55 | Description, contact info |
| Label | DM Sans | 12.5px | 500 | 1.4 | Form field labels |
| Input Value | DM Sans | 13.5px | 400 | 1.5 | Inside `<input>` |
| Button | DM Sans | 13–14px | 500–600 | 1 | All button text |
| Badge / Chip | DM Sans | 11px | 600 | 1 | Status badge text |
| Breadcrumb | DM Sans | 12px | 400/500 | 1 | Top bar breadcrumb |
| Footer | DM Sans | 11.5px | 400 | 1 | Footer copyright + links |
| Pagination Info | DM Sans | 11.5–12px | 400 | 1 | "Rows per page", count |

---

## 4. Spacing & Layout

### Base Unit: 4 px

| Token | Value | Usage |
|-------|-------|-------|
| `space-1` | 4px | Icon padding, tight gaps |
| `space-2` | 8px | Internal component padding |
| `space-3` | 12px | Button horizontal pad (small) |
| `space-4` | 16px | Table cell padding, form group gap |
| `space-5` | 20px | Section gap |
| `space-6` | 24px | Page section margins |
| `space-7` | 28px | Page content padding horizontal |
| `space-8` | 32px | Large section gaps |

### Layout Structure

```
┌────────────────────────────────────────────────────┐
│  SIDEBAR (220px fixed)  │  MAIN AREA (flex: 1)    │
│                          │  ┌─────────────────────┐ │
│  Logo (60px)             │  │  TOPBAR (60px)      │ │
│  Search                  │  ├─────────────────────┤ │
│  Nav                     │  │  CONTENT (scroll)   │ │
│                          │  │  padding: 26px 30px │ │
│                          │  ├─────────────────────┤ │
│                          │  │  FOOTER (42px)      │ │
│                          │  └─────────────────────┘ │
└────────────────────────────────────────────────────┘
```

| Area | Dimension |
|------|-----------|
| Sidebar width | `220px` |
| Topbar height | `60px` |
| Content padding | `26px 30px` |
| Footer height | `42px` |
| Card border-radius | `20px` (xl) |
| Card inner padding | `16px 22px` |
| Table row height | `~48px` (14px top+bottom pad) |

---

## 5. Border Radius

| Token | Value | Usage |
|-------|-------|-------|
| `--radius-sm` | `6px` | Buttons (small), icon buttons, row action buttons, checkboxes |
| `--radius-md` | `10px` | Buttons (standard), search box, form inputs, page number buttons |
| `--radius-lg` | `14px` | Module accordion, tab bar |
| `--radius-xl` | `20px` | Main cards / table wrappers |
| `--radius-full` | `9999px` | Status badges, avatar, notification dot |

---

## 6. Shadows & Elevation

| Token | Value | Usage |
|-------|-------|-------|
| `--shadow-sm` | `0 1px 3px rgba(18,18,42,.07)` | Cards, sidebar |
| `--shadow-md` | `0 4px 16px rgba(18,18,42,.10)` | Dropdowns, popovers |
| `--shadow-lg` | `0 12px 32px rgba(18,18,42,.13)` | Modals |
| Button glow (teal) | `0 2px 8px rgba(0,168,162,.25)` | CTA button resting |
| Button glow (accent) | `0 2px 8px rgba(108,99,255,.25)` | Accent button resting |
| Active page number | `0 2px 6px rgba(108,99,255,.30)` | Pagination active pill |

---

## 7. CSS Variables (Tokens)

```css
:root {
  /* Colors */
  --bg:              #F7F8FC;
  --surface:         #FFFFFF;
  --surface-2:       #F0F2FA;
  --border:          #E3E6F0;

  --text-primary:    #12122A;
  --text-secondary:  #5B5E7A;
  --text-muted:      #9295B0;

  --accent:          #6C63FF;
  --accent-soft:     #EDEEFF;
  --accent-hover:    #5449E0;

  --teal:            #00A8A2;
  --teal-hover:      #007F7A;
  --teal-soft:       #E0FAF8;

  --danger:          #FF5A5F;
  --danger-soft:     #FFF0F0;

  /* Typography */
  --font-head: 'Syne', sans-serif;
  --font-body: 'DM Sans', sans-serif;

  /* Border Radius */
  --radius-sm:  6px;
  --radius-md:  10px;
  --radius-lg:  14px;
  --radius-xl:  20px;

  /* Shadows */
  --shadow-sm: 0 1px 3px rgba(18,18,42,.07);
  --shadow-md: 0 4px 16px rgba(18,18,42,.10);
  --shadow-lg: 0 12px 32px rgba(18,18,42,.13);

  /* Layout */
  --sidebar-w: 220px;
  --header-h:  60px;

  /* Motion */
  --transition: .17s cubic-bezier(.4, 0, .2, 1);
}
```

---

## 8. Components

---

### 8.1 Sidebar Navigation

**Structure:** Fixed left column, `220px` wide, full viewport height, vertically scrollable.

**Anatomy:**
```
┌──────────────────────┐
│  [Logo Mark] VANGUARD│  ← 60px logo row
├──────────────────────┤
│  🔍 Search…          │  ← search input, 10px padding
├──────────────────────┤
│  [icon] Dashboard    │  ← nav-item
│                      │
│  CORE MODULE  ∨      │  ← nav-section (collapsible)
│    Org Levels        │
│    ● User Roles      │  ← active item
│    …                 │
│                      │
│  MARKETING MODULE ∨  │
│  …                   │
└──────────────────────┘
```

**States:**

| State | Style |
|-------|-------|
| Default | `color: --text-secondary`, no background |
| Hover | `background: --surface-2`, `color: --text-primary` |
| Active | `background: --accent-soft`, `color: --accent`, `font-weight: 500`, 3px left border in `--accent` |

**Nav Section (collapsible group label):**
- `font-size: 9.5px`, `font-weight: 700`, `text-transform: uppercase`, `letter-spacing: 0.1em`
- Chevron rotates 180° when open (`--transition`)
- Children collapse with `display: none`

---

### 8.2 Top Bar

**Height:** `60px` · **Background:** `--surface` · **Border-bottom:** `1px solid --border`

**Left:** Breadcrumb trail  
**Right:** Notification bell (with red dot badge) + Chat icon (with red dot badge) + Avatar

**Avatar:**
- `32×32px`, `border-radius: 50%`
- Gradient fill: `linear-gradient(135deg, #6C63FF, #00A8A2)` when no photo
- `border: 2px solid --border`, hover → `border-color: --accent`

**Notification dot:**
- `6×6px`, `background: --danger`, `border-radius: 50%`
- `border: 1.5px solid --surface` (white ring)

---

### 8.3 Buttons

#### Sizes

| Size | Height | Padding | Font |
|------|--------|---------|------|
| Default | `36px` | `0 13px` | `13px / 500` |
| Large (form footer) | `52px` | `0 20px` | `14px / 600` |

#### Variants

**Primary / CTA (Teal)**
```css
background: #00A8A2;
border: 1px solid #00A8A2;
color: #fff;
box-shadow: 0 2px 8px rgba(0,168,162,.25);
border-radius: var(--radius-md);
```
Hover: `background: #007F7A`, deeper shadow.  
Usage: Invite User, Create, Add New Role, Export.

**Accent (Purple)**
```css
background: #6C63FF;
border: 1px solid #6C63FF;
color: #fff;
box-shadow: 0 2px 8px rgba(108,99,255,.25);
```
Hover: `background: #5449E0`.  
Usage: Add New (in Risks Management).

**Outline / Ghost**
```css
background: #fff;
border: 1px solid var(--border);
color: var(--text-secondary);
```
Hover: `background: --surface-2`, `color: --text-primary`.  
Usage: Filters, Customize, Export (secondary), Cancel.

**Icon + Label:** Always `display: flex; align-items: center; gap: 6px`. Icon is `14–15px`.

---

### 8.4 Form Inputs

```
┌─────────────────────────────────────────┐
│  Administrator                          │
└─────────────────────────────────────────┘
```

```css
width: 100%;
max-width: 500px;
background: #fff;
border: 1px solid var(--border);      /* #E3E6F0 */
border-radius: var(--radius-md);      /* 10px */
padding: 9px 13px;
font-size: 13.5px;
color: var(--text-primary);
```

**Focus:**
```css
border-color: var(--accent);          /* #6C63FF */
box-shadow: 0 0 0 3px rgba(108,99,255,.10);
```

**Label:** `12.5px / 500 / --text-secondary`, `margin-bottom: 6px`  
**Required star:** `color: --danger` (`*`)

---

### 8.5 Search Box

Inline compound component: icon + `<input>` inside a shared border container.

```css
display: flex; align-items: center; gap: 7px;
background: #fff;
border: 1px solid var(--border);
border-radius: var(--radius-md);
padding: 0 11px;
height: 36px;
```

Focus-within:
```css
border-color: var(--accent);
box-shadow: 0 0 0 3px rgba(108,99,255,.10);
```

Input inside: `border: none; outline: none; background: transparent; font-size: 13px; width: 190px;`

---

### 8.6 Tabs

Container: `background: --surface`, `border: 1px solid --border`, `border-radius: --radius-lg`, `padding: 5px`, horizontal scroll.

**Tab item:**
```css
padding: 7px 14px;
border-radius: var(--radius-md);
font-size: 12.5px; font-weight: 500;
color: var(--text-secondary);
cursor: pointer;
white-space: nowrap;
transition: all var(--transition);
```

**Active tab:**
```css
background: var(--accent);    /* #6C63FF */
color: #fff;
box-shadow: 0 2px 8px rgba(108,99,255,.35);
```

---

### 8.7 Table

**Card wrapper:** `--radius-xl` (20px), `border: 1px solid --border`, `overflow: hidden`.

**`<thead>` row:**
```css
background: var(--surface-2);    /* #F0F2FA */
border-bottom: 1px solid var(--border);
```

**`<th>`:**
```css
padding: 10px 16px;
font-size: 10.5px; font-weight: 600;
letter-spacing: 0.07em;
text-transform: uppercase;
color: var(--text-muted);
text-align: left;
```

**`<tbody> <tr>`:**
```css
border-bottom: 1px solid var(--border);
transition: background var(--transition);
```
Hover: `background: --surface-2`  
Selected (checkbox): `background: --accent-soft`

**`<td>` padding:** `14px 16px`  
First column: `padding-left: 22px` · Last column: `padding-right: 22px`

**Column alignment:**
- Text columns: `text-align: left`
- Numeric columns (# Privileges, # Assigned Users): `text-align: center`
- Actions column: `text-align: right`

---

### 8.8 Pagination

Two patterns are used in this system:

---

#### Pattern A — Page-number style *(Risks Management, User Roles list)*

```
← Previous   [1] [2] [3] … [8] [9] [10]   Next →
```

Left side: Info text (`"Page 1 of 10 — 100 items"`, `11.5px / --text-muted`)  
Center: page number pills  
Right side: Previous / Next nav buttons

**Page number pill:**
```css
width: 30px; height: 30px;
border-radius: var(--radius-sm);   /* 6px */
font-size: 12px; font-weight: 500;
color: var(--text-secondary);
border: 1px solid transparent;
cursor: pointer;
transition: all var(--transition);
```

Active pill:
```css
background: var(--accent);
color: #fff;
border-color: var(--accent);
box-shadow: 0 2px 6px rgba(108,99,255,.30);
```

Prev / Next button:
```css
display: inline-flex; align-items: center; gap: 4px;
padding: 0 11px; height: 30px;
border-radius: var(--radius-sm);
font-size: 12px; font-weight: 500;
color: var(--text-secondary);
border: 1px solid var(--border);
background: var(--surface);
```
Hover: `background: --surface-2`

---

#### Pattern B — Rows-per-page style *(Users / Staffs list, default for data-heavy tables)*

```
Rows per page:  10 ▾        1–10 of 961        ← Previous    Next →
```

This is the **standard pagination** for all list pages with large datasets.

**Layout:** `display: flex; align-items: center; justify-content: flex-end; gap: 24px;`  
**Container:** `padding: 12px 22px; border-top: 1px solid --border; background: --surface`

**Rows per page selector:**
```css
display: inline-flex; align-items: center; gap: 6px;
font-size: 12.5px; color: var(--text-secondary);
```
Label: `"Rows per page:"` in `--text-secondary`  
Dropdown trigger: `font-size: 12.5px; font-weight: 500; color: --text-primary` + chevron icon `12px`
```css
.rows-select {
  border: none; outline: none;
  background: transparent;
  font-size: 12.5px; font-weight: 500;
  color: var(--text-primary);
  cursor: pointer;
  padding-right: 4px;
}
```

**Record range:**
```
1–10 of 961
```
```css
font-size: 12.5px;
color: var(--text-secondary);
letter-spacing: 0.01em;
```

**Previous / Next nav buttons:**
```css
display: inline-flex; align-items: center; gap: 5px;
font-size: 12.5px; font-weight: 500;
color: var(--text-secondary);
background: none; border: none;
cursor: pointer;
transition: color var(--transition);
padding: 4px 0;
```
Hover: `color: var(--text-primary)`  
Icon: `←` / `→` arrow, `14px`

Disabled state:
```css
color: var(--text-muted);
cursor: not-allowed;
pointer-events: none;
```

**Full HTML snippet (Pattern B):**
```html
<div class="pagination-bar">
  <span class="rows-label">Rows per page:</span>
  <select class="rows-select">
    <option>10</option>
    <option>25</option>
    <option>50</option>
  </select>
  <span class="record-range">1–10 of 961</span>
  <button class="nav-btn" disabled>
    <svg><!-- left arrow --></svg> Previous
  </button>
  <button class="nav-btn">
    Next <svg><!-- right arrow --></svg>
  </button>
</div>
```

```css
.pagination-bar {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 24px;
  padding: 12px 22px;
  border-top: 1px solid var(--border);
  background: var(--surface);
  font-family: var(--font-body);
}
.rows-label {
  font-size: 12.5px;
  color: var(--text-secondary);
}
.rows-select {
  border: none; outline: none; background: transparent;
  font-size: 12.5px; font-weight: 500;
  color: var(--text-primary); cursor: pointer;
  font-family: var(--font-body);
}
.record-range {
  font-size: 12.5px;
  color: var(--text-secondary);
}
.nav-btn {
  display: inline-flex; align-items: center; gap: 5px;
  font-size: 12.5px; font-weight: 500;
  color: var(--text-secondary);
  background: none; border: none;
  cursor: pointer; font-family: var(--font-body);
  transition: color var(--transition);
  padding: 4px 0;
}
.nav-btn:hover { color: var(--text-primary); }
.nav-btn:disabled {
  color: var(--text-muted);
  cursor: not-allowed;
  pointer-events: none;
}
```

**When to use which pattern:**

| Pattern | Use case |
|---------|----------|
| A — Page numbers | Smaller datasets (< 100 records), settings/config lists |
| B — Rows per page | Large datasets (100+ records), main data tables (Users, Policies, Claims) |

---

### 8.9 Status Badges

Inline pill — text only, no icon.

```css
display: inline-flex; align-items: center;
padding: 3px 10px;
border-radius: 9999px;
font-size: 11px; font-weight: 600;
```

| Status | Text Color | Background |
|--------|-----------|------------|
| Active | `#15803D` | `#DCFCE7` |
| Pending | `#B45309` | `#FEF3C7` |
| Cancelled | `#B91C1C` | `#FEE2E2` |
| Inactive | `#4B5563` | `#F3F4F6` |

---

### 8.10 Checkboxes

```css
width: 15px; height: 15px;
border: 1.5px solid var(--border);
border-radius: 4px;
appearance: none;
background: var(--surface);
cursor: pointer;
transition: all var(--transition);
position: relative;
```

Checked (standard):
```css
background: var(--accent);
border-color: var(--accent);
```

Checked (Access All — teal variant):
```css
background: var(--teal);
border-color: var(--teal);
```

Checkmark (pseudo-element):
```css
::after {
  content: '';
  position: absolute;
  left: 3px; top: 1px;
  width: 5px; height: 8px;
  border: 2px solid #fff;
  border-top: none; border-left: none;
  transform: rotate(45deg);
}
```

**Behavior:** "Access All" checkbox in privilege tables cascades to check/uncheck all permission columns in its row.

---

### 8.11 Module Accordion (Privileges)

Used in Add/Edit Role and Single Role View.

**Closed state:**
```css
.module-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 12px 18px;
  cursor: pointer;
  transition: background var(--transition);
}
```

**Open state:** `background: --surface-2`; chevron rotates 180°.

**With privilege checkbox (view):** Module header includes a teal checkbox showing whether any/all privileges are granted.

**Body:** Permission table with columns: Module Type Name · Access All · Create · Read · Update · Delete

---

### 8.12 Hierarchy / Org Chart Node

Used in **Staff Hierarchy View**.

```
┌─────────────────────┐
│   [Avatar 40px]     │
│   Olivia Rhye       │ ← font-weight: 600, 13px
│   106               │ ← ID, --text-muted, 11px
│   Founder & CEO     │ ← role/level, --text-secondary, 11px
│   (Level 1)         │
└─────────────────────┘
       [–]             ← teal collapse button, 20×20px
```

```css
.org-node {
  background: var(--surface);
  border: 1.5px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 14px 16px;
  text-align: center;
  min-width: 140px;
  box-shadow: var(--shadow-sm);
  position: relative;
}
```

Avatar: `40–44px` circle, gradient or photo, centered above node box.  
Connector lines: `2px solid var(--teal)`, `border-radius: 4px` on corners.  
Collapse button: `20×20px`, `background: var(--teal)`, `color: #fff`, `border-radius: 4px`, shows child count.  
3-dot menu: `position: absolute; top: 8px; right: 8px;`, hover reveals.

---

### 8.13 Cards

**Standard table card:**
```css
background: var(--surface);
border: 1px solid var(--border);
border-radius: var(--radius-xl);   /* 20px */
box-shadow: var(--shadow-sm);
overflow: hidden;
```

**Card header:**
```css
padding: 16px 22px;
border-bottom: 1px solid var(--border);
display: flex; align-items: center; justify-content: space-between;
```

Title: `Syne 700 15px`  
Optional record count chip: `background: --accent-soft; color: --accent; font-size: 11px; font-weight: 600; padding: 3px 9px; border-radius: 20px`

---

### 8.14 Breadcrumb

```
🏠  ›  Core Module  ›  …  ›  User Roles
```

```css
display: flex; align-items: center; gap: 5px;
font-size: 12px;
color: var(--text-muted);
```

Active/current crumb: `color: --accent; font-weight: 500`  
Separators (`›`): `font-size: 10px; color: --text-muted`  
Home icon: `13×13px`

---

### 8.15 Row Actions

Three icon buttons, right-aligned, revealed on row hover.

```css
.row-actions {
  display: flex; align-items: center; justify-content: flex-end; gap: 2px;
  opacity: 0;
  transition: opacity var(--transition);
}
tr:hover .row-actions { opacity: 1; }
```

**Each action button:**
```css
width: 28px; height: 28px;
border-radius: var(--radius-sm);
display: flex; align-items: center; justify-content: center;
```

| Button | Default | Hover bg | Hover color |
|--------|---------|----------|-------------|
| View (eye) | `--text-muted` | `--accent-soft` | `--accent` |
| Edit (pencil) | `--text-muted` | `--teal-soft` | `--teal` |
| Delete (trash) | `--text-muted` | `--danger-soft` | `--danger` |

**Three-dot menu** (Users table): single `⋮` button, `28×28px`, reveals dropdown on click.

---

## 9. Page Templates

### 9.1 List Page

```
TOPBAR
├── breadcrumb (left)
└── icon actions + avatar (right)

CONTENT (padding: 26px 30px)
├── PAGE HEADER
│   ├── <h1> Page Title (Syne 800 24px)
│   └── ACTIONS ROW (right-aligned)
│       ├── Search Box
│       ├── [Filters] btn-outline
│       ├── [Customize] btn-outline
│       ├── [Export] btn-outline
│       └── [+ Add New] btn-primary (teal)
│
├── TABS (optional, e.g. Risks Management)
│
└── CARD
    ├── Card Header (title + optional record count)
    ├── TABLE
    │   ├── thead (sticky, surface-2 bg)
    │   └── tbody (hover rows, row actions on hover)
    └── PAGINATION (Pattern A or B, see §8.8)

FOOTER (copyright · Terms · Privacy)
```

**Sub-header description** (Users page only):
```css
font-size: 13px; color: --text-secondary; margin-top: 4px;
```

---

### 9.2 Add / Edit Form Page

```
TOPBAR (breadcrumb updates to "Add New" or role name)

FORM CONTENT (scrollable)
├── <h1> "Add New [Entity]"   (Syne 800 22px)
├── FIELD: Role *
│   └── <input>
├── FIELD: Description
│   └── <input>
├── "List of all the privileges *"
└── MODULE ACCORDIONS (one per module)
    └── PRIVILEGE TABLE

FORM FOOTER (sticky bottom, full width)
├── [Cancel] — left half, outline/ghost
└── [Create] / [Edit] — right half, teal CTA
```

---

### 9.3 Single / Detail View Page

```
TOPBAR

DETAIL CONTENT
├── <h2> "User Roles"  (Syne 700)
├── METADATA GRID
│   ├── Role: [value]
│   ├── Description: [value]
│   ├── Number of Privileges: [n]
│   └── Number of Assigned Users: [n]
├── "List of all the privileges"
└── MODULE ACCORDIONS (read-only checkboxes, pre-checked)
    ├── Created By + Created Date
    └── Updated By + Updated Date

FORM FOOTER
├── [Cancel]
└── [✏ Edit]  ← teal
```

---

### 9.4 Hierarchy View Page

```
TOPBAR

CONTENT (full bleed, no padding card)
├── PAGE HEADER
│   ├── "Staff Hierarchy View" title
│   └── ACTIONS: Search · Filters · Customize · Export · [Staff Hierarchy View ▾] · [+ Add New Node]
│
└── ORG CHART CANVAS (SVG/Canvas or HTML absolute positioning)
    ├── ROOT NODE (Level 1, centered)
    ├── CONNECTOR LINES (teal, 2px, rounded corners)
    ├── LEVEL 2 NODES (horizontal row)
    ├── CONNECTOR LINES
    └── LEVEL 3+ NODES

FOOTER
```

---

## 10. Motion & Animation

### Principles
- **Subtle & purposeful** — motion aids comprehension, never distracts
- **CSS-first** — prefer CSS transitions/animations over JS
- **Consistent easing** — `cubic-bezier(.4, 0, .2, 1)` (Material standard ease)

### Tokens

```css
--transition: .17s cubic-bezier(.4, 0, .2, 1);  /* micro-interactions */
```

### Patterns

| Interaction | Animation |
|-------------|-----------|
| Page/card mount | `fadeUp` — `opacity 0→1 + translateY(10px→0)`, `0.3s` |
| Table row stagger | Each row delays `i * 40ms` on mount |
| Sidebar nav hover | `background` transition, `--transition` |
| Button hover | `background`, `box-shadow`, `--transition` |
| Accordion open/close | Chevron `transform: rotate(180deg)`, `--transition` |
| Row action reveal | `opacity 0→1`, `--transition` |
| Input focus | `border-color`, `box-shadow` (ring), `--transition` |

```css
@keyframes fadeUp {
  from { opacity: 0; transform: translateY(10px); }
  to   { opacity: 1; transform: translateY(0); }
}
```

---

## 11. Iconography

**Library:** Lucide Icons (stroke-based, `stroke-width: 1.8–2.5`)  
**Style:** Outlined, no fill (except checkboxes and logo mark)  
**Color:** Inherits from parent `color` (use `currentColor` for `stroke`)

### Standard Icon Sizes

| Context | Size |
|---------|------|
| Sidebar nav item | `14×14px` |
| Topbar action (bell, chat) | `17×18px` |
| Button icon | `14–15px` |
| Row action button | `13×13px` |
| Search box | `14–15px` |
| Breadcrumb home | `13×13px` |
| Pagination arrows | `12–14px` |
| Form field prefix | `14px` |

### Icon–to–label gap

Always `gap: 6–8px` between icon and label text.

---

## 12. Accessibility

| Guideline | Implementation |
|-----------|----------------|
| Color contrast | All text on white/surface-2 meets WCAG AA (4.5:1 for body, 3:1 for large text) |
| Focus styles | `box-shadow: 0 0 0 3px rgba(108,99,255,.15)` on all interactive elements |
| Labels | All `<input>` elements have associated `<label>` |
| Required fields | Marked with `*` in `--danger` AND `aria-required="true"` |
| Checkboxes | Keyboard accessible, `aria-checked` state |
| Tables | `<th scope="col">` on all column headers |
| Buttons | Descriptive `title` or `aria-label` on icon-only buttons |
| Status badges | Include `role="status"` or `aria-label` |
| Sidebar collapse | `aria-expanded` on collapsible sections |
| Pagination | `aria-current="page"` on active page button |

---

## 13. Do / Don't

### ✅ Do

- Use **Syne** for all headings and **DM Sans** for all body/UI text
- Apply `--teal` for primary CTAs (Add, Create, Invite, Save)
- Apply `--accent` (`#6C63FF`) for active/selected states and focus rings
- Use `--surface-2` for alternating/hover backgrounds, never a different color
- Keep table row actions hidden until hover (`opacity: 0 → 1`)
- Use Pattern B pagination (Rows per page) for large data tables
- Maintain `20px` border-radius on all card wrappers
- Keep sidebar at exactly `220px`; never allow content to shift it

### ❌ Don't

- Don't use `Inter`, `Roboto`, `Arial`, or system fonts
- Don't mix teal and purple buttons on the same action bar
- Don't show row actions without the hover trigger
- Don't use solid colored full-page backgrounds — always `#F7F8FC`
- Don't add borders to table rows on hover — use background only
- Don't omit the `box-shadow` glow on primary buttons
- Don't use custom colors for status badges — only the four defined semantic colors
- Don't change the sidebar width or collapse it automatically on desktop
- Don't use pattern A pagination for tables with > 100 records

---

*Vanguard X Design System — maintained by the Envoy product team.*
