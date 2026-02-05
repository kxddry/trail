# Account App Rewrite Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Rewrite the account app UI from scratch while preserving routes and data contracts, and add `/getting-started`, `/activity`, and `/sessions`.

**Architecture:** Rebuild the shell and page layouts using `@trail/ui` primitives and a shared `PageHeader` component. Keep pages as server components by default, isolate client logic in existing client components, and refresh global theming with new tokens and backgrounds.

**Tech Stack:** Next.js 16, React 19, Tailwind CSS, @trail/ui, tRPC, Auth0.

---

### Task 1: Shell, Typography, and Page Header

**Files:**
- Create: `apps/account/app/components/PageHeader.tsx`
- Modify: `apps/account/app/layout.tsx`, `apps/account/app/globals.css`, `apps/account/tailwind.config.ts`
- Modify: `apps/account/app/components/AppShell.tsx`, `apps/account/app/components/Sidebar.tsx`, `apps/account/app/components/Footer.tsx`
- Modify: `apps/account/components/ui/sidebar.tsx`
- Modify: `packages/content/src/account/en.ts`
- Test: `apps/account/app/components/__tests__/page-header.test.tsx`
- Test: `apps/account/app/components/__tests__/app-shell.test.tsx`
- Test: `apps/account/app/components/__tests__/sidebar.test.tsx`

**Step 1: Write the failing tests**

Create `apps/account/app/components/__tests__/page-header.test.tsx`:

```tsx
import { render, screen } from "@testing-library/react";
import { PageHeader } from "../PageHeader";

describe("PageHeader", () => {
  it("renders title, subtitle, and actions", () => {
    render(
      <PageHeader
        eyebrow="overview"
        title="account"
        subtitle="manage your trail"
        actions={<button type="button">action</button>}
      />
    );

    expect(screen.getByText("overview")).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "account" })).toBeInTheDocument();
    expect(screen.getByText("manage your trail")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "action" })).toBeInTheDocument();
  });
});
```

Create `apps/account/app/components/__tests__/app-shell.test.tsx`:

```tsx
import React from "react";
import { render, screen } from "@testing-library/react";
import { vi } from "vitest";
import { AppShell } from "../AppShell";

vi.mock("next/link", () => ({
  default: ({ href, children, ...props }: { href: string; children: React.ReactNode }) => (
    <a href={href} {...props}>
      {children}
    </a>
  )
}));

vi.mock("next/navigation", () => ({
  usePathname: () => "/dashboard"
}));

describe("AppShell", () => {
  it("renders a skip link and main content", () => {
    render(
      <AppShell>
        <div>main content</div>
      </AppShell>
    );

    expect(screen.getByText("Skip to main content")).toBeInTheDocument();
    expect(screen.getByRole("main")).toHaveTextContent("main content");
  });
});
```

Create `apps/account/app/components/__tests__/sidebar.test.tsx`:

```tsx
import React from "react";
import { render, screen } from "@testing-library/react";
import { vi } from "vitest";
import { accountCopy } from "@trail/content";
import { Sidebar } from "../Sidebar";

vi.mock("next/link", () => ({
  default: ({ href, children, ...props }: { href: string; children: React.ReactNode }) => (
    <a href={href} {...props}>
      {children}
    </a>
  )
}));

vi.mock("next/navigation", () => ({
  usePathname: () => "/dashboard"
}));

describe("Sidebar", () => {
  it("renders nav links and marks the active route", () => {
    render(<Sidebar />);

    const dashboardLink = screen.getByRole("link", { name: accountCopy.nav.dashboard });
    const activityLink = screen.getByRole("link", { name: accountCopy.nav.activity });
    const gettingStartedLink = screen.getByRole("link", {
      name: accountCopy.nav.gettingStarted
    });
    const sessionsLink = screen.getByRole("link", { name: accountCopy.nav.sessions });
    const billingLink = screen.getByRole("link", { name: accountCopy.nav.billing });

    expect(dashboardLink).toHaveAttribute("aria-current", "page");
    expect(activityLink).toBeInTheDocument();
    expect(gettingStartedLink).toBeInTheDocument();
    expect(sessionsLink).toBeInTheDocument();
    expect(billingLink).not.toHaveAttribute("aria-current");
    expect(screen.getByRole("link", { name: accountCopy.nav.signOut })).toBeInTheDocument();
  });
});
```

**Step 2: Run test to verify it fails**

Run: `pnpm -C apps/account test`

Expected: FAIL (missing PageHeader export and updated shell markup)

**Step 3: Write minimal implementation**

Create `apps/account/app/components/PageHeader.tsx`:

```tsx
import * as React from "react";
import { cn } from "@/lib/utils";

type PageHeaderProps = {
  eyebrow?: string;
  title: string;
  subtitle?: string;
  actions?: React.ReactNode;
  meta?: React.ReactNode;
  className?: string;
};

export function PageHeader({
  eyebrow,
  title,
  subtitle,
  actions,
  meta,
  className
}: PageHeaderProps) {
  return (
    <div
      className={cn(
        "flex flex-wrap items-end justify-between gap-4 border-b border-border/60 pb-4",
        className
      )}
    >
      <div className="space-y-2">
        {eyebrow ? <p className="trail-eyebrow">{eyebrow}</p> : null}
        <h1 className="trail-title">{title}</h1>
        {subtitle ? <p className="trail-copy max-w-2xl">{subtitle}</p> : null}
        {meta ? (
          <div className="flex flex-wrap items-center gap-2 text-xs text-ink-muted">
            {meta}
          </div>
        ) : null}
      </div>
      {actions ? <div className="flex flex-wrap items-center gap-2">{actions}</div> : null}
    </div>
  );
}
```

Update `packages/content/src/account/en.ts` (nav + new pages copy):

```ts
  nav: {
    dashboard: "dashboard",
    activity: "activity",
    gettingStarted: "getting started",
    sessions: "sessions",
    settings: "account",
    billing: "billing",
    extension: "extension",
    signIn: "sign in",
    signOut: "sign out"
  },
  gettingStarted: {
    title: "getting started",
    subtitle: "complete the setup to unlock your first trails.",
    cta: "connect extension",
    stepsTitle: "setup checklist",
    stepsSubtitle: "finish these steps to start syncing trails.",
    progress: "0/3",
    steps: [
      {
        title: "connect the extension",
        description: "approve the connection from your browser."
      },
      {
        title: "capture a trail",
        description: "record a flow to populate the dashboard."
      },
      {
        title: "review and share",
        description: "organize trails and prepare to invite teammates."
      }
    ],
    next: {
      eyebrow: "what happens next",
      title: "unlock activity and sessions",
      subtitle: "once you sync, trails appear across activity and sessions.",
      items: [
        "activity timeline fills with new trails",
        "sessions list tracks devices and last seen",
        "coverage starts to appear automatically"
      ]
    },
    support: {
      eyebrow: "need help?",
      title: "talk to us",
      subtitle: "we are here to help you finish setup.",
      cta: "contact support"
    }
  },
  activity: {
    title: "activity",
    subtitle: "review recent trails, usage, and sync history.",
    stream: {
      eyebrow: "stream",
      title: "recent trails",
      subtitle: "activity appears after the first sync.",
      filters: ["today", "this week", "all time"]
    },
    empty: {
      title: "no activity yet",
      description: "connect the extension to start capturing real workflows.",
      items: [
        "see synced trails in chronological order",
        "filter by date or device",
        "share when your team is ready"
      ],
      cta: "connect extension",
      secondaryCta: "getting started"
    },
    next: {
      eyebrow: "next sync",
      title: "stay ready to capture",
      subtitle: "the extension keeps your timeline fresh.",
      cta: "open extension"
    },
    coverage: {
      eyebrow: "coverage",
      title: "coverage snapshot",
      subtitle: "coverage appears after your first trail."
    }
  },
  sessions: {
    title: "sessions",
    subtitle: "devices and access control in one place.",
    list: {
      eyebrow: "devices",
      title: "active sessions",
      subtitle: "review devices connected to your account.",
      emptyTitle: "no sessions yet",
      emptyDescription: "sessions appear once the extension connects.",
      emptyItems: [
        "see device name and last seen",
        "revoke access instantly",
        "confirm permission scopes"
      ]
    },
    posture: {
      eyebrow: "security",
      title: "access posture",
      subtitle: "we will flag unusual device changes.",
      items: [
        { label: "permissions", value: "approved" },
        { label: "last review", value: "pending" },
        { label: "alerts", value: "none" }
      ]
    },
    guidance: {
      title: "need to revoke access?",
      description: "open the extension to sign out devices instantly.",
      cta: "open extension"
    }
  },
```

Update `apps/account/app/components/AppShell.tsx`:

```tsx
import * as React from "react";
import { Sidebar } from "./Sidebar";
import { Footer } from "./Footer";

export function AppShell({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-bg text-ink">
      <a
        href="#main-content"
        className="sr-only rounded-full border border-border/60 bg-bg px-3 py-1 text-xs font-semibold text-ink focus-visible:not-sr-only focus-visible:absolute focus-visible:left-4 focus-visible:top-4 focus-visible:z-[60] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent/40 focus-visible:ring-offset-2 focus-visible:ring-offset-bg"
      >
        Skip to main content
      </a>
      <div data-noise="true" className="min-h-screen trail-app">
        <div className="flex min-h-screen flex-col lg:flex-row">
          <Sidebar />
          <div className="flex min-h-screen flex-1 flex-col">
            <main
              id="main-content"
              role="main"
              tabIndex={-1}
              className="flex-1 px-4 py-6 focus-visible:outline-none lg:px-10 lg:py-8"
            >
              <div className="mx-auto w-full max-w-6xl">{children}</div>
            </main>
            <Footer />
          </div>
        </div>
      </div>
    </div>
  );
}
```

Update `apps/account/components/ui/sidebar.tsx` (type only):

```tsx
// ...existing imports

// add below Links interface

type SidebarLinkProps = {
  link: Links;
  className?: string;
} & Omit<LinkProps, "href"> &
  Omit<React.ComponentPropsWithoutRef<"a">, "href">;

// ...existing SidebarLink

export const SidebarLink = ({ link, className, ...props }: SidebarLinkProps) => {
  const { open, animate } = useSidebar();
  return (
    <Link
      href={link.href}
      className={cn(
        "group/sidebar flex items-center justify-start gap-2 rounded-lg px-3 py-2 text-sm font-medium text-ink-muted transition hover:bg-surface-high hover:text-ink focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent/40 focus-visible:ring-offset-2 focus-visible:ring-offset-bg",
        className
      )}
      aria-label={link.label}
      {...props}
    >
      {link.icon}
      <motion.span
        animate={{
          display: animate ? (open ? "inline-block" : "none") : "inline-block",
          opacity: animate ? (open ? 1 : 0) : 1
        }}
        className="whitespace-pre text-sm transition duration-150 group-hover/sidebar:translate-x-1"
      >
        {link.label}
      </motion.span>
    </Link>
  );
};
```

Update `apps/account/app/components/Sidebar.tsx`:

```tsx
"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { accountCopy } from "@trail/content";
import { TrailLogo, cn } from "@trail/ui";
import { Sidebar as SidebarRoot, SidebarBody, SidebarLink } from "@/components/ui/sidebar";
import {
  Activity,
  Compass,
  CreditCard,
  LayoutDashboard,
  LogOut,
  Plug,
  Shield,
  Settings
} from "lucide-react";

const navGroups = [
  {
    label: "core",
    links: [
      {
        label: accountCopy.nav.dashboard,
        href: "/dashboard",
        icon: <LayoutDashboard className="h-5 w-5" />
      },
      {
        label: accountCopy.nav.activity,
        href: "/activity",
        icon: <Activity className="h-5 w-5" />
      },
      {
        label: accountCopy.nav.gettingStarted,
        href: "/getting-started",
        icon: <Compass className="h-5 w-5" />
      }
    ]
  },
  {
    label: "access",
    links: [
      {
        label: accountCopy.nav.sessions,
        href: "/sessions",
        icon: <Shield className="h-5 w-5" />
      },
      {
        label: accountCopy.nav.extension,
        href: "/extension",
        icon: <Plug className="h-5 w-5" />
      }
    ]
  },
  {
    label: "account",
    links: [
      {
        label: accountCopy.nav.settings,
        href: "/settings",
        icon: <Settings className="h-5 w-5" />
      },
      {
        label: accountCopy.nav.billing,
        href: "/billing",
        icon: <CreditCard className="h-5 w-5" />
      }
    ]
  }
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <SidebarRoot animate>
      <SidebarBody className="gap-8" showMobile>
        <div className="flex flex-1 flex-col gap-6">
          <Link
            href="/dashboard"
            className="flex items-center gap-3 rounded-2xl border border-border/60 bg-surface/80 px-3 py-2 text-sm font-semibold lowercase text-ink transition hover:bg-surface"
          >
            <span className="flex h-9 w-9 items-center justify-center rounded-xl border border-border/60 bg-bg">
              <TrailLogo className="h-5 w-5" />
            </span>
            <span>{accountCopy.brand.name}</span>
          </Link>

          <div className="flex flex-col gap-6">
            {navGroups.map((group) => (
              <div key={group.label} className="space-y-2">
                <p className="text-[0.65rem] font-semibold uppercase tracking-[0.2em] text-ink-subtle">
                  {group.label}
                </p>
                <div className="flex flex-col gap-1">
                  {group.links.map((link) => {
                    const isActive = pathname.startsWith(link.href);
                    return (
                      <SidebarLink
                        key={link.href}
                        link={link}
                        aria-current={isActive ? "page" : undefined}
                        className={cn(
                          "rounded-2xl px-3 py-2 text-sm",
                          isActive
                            ? "bg-surface-high text-ink"
                            : "text-ink-muted hover:text-ink"
                        )}
                      />
                    );
                  })}
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="border-t border-border/60 pt-4">
          <SidebarLink
            link={{
              label: accountCopy.nav.signOut,
              href: "/auth/logout",
              icon: <LogOut className="h-5 w-5" />
            }}
            className="rounded-2xl px-3 py-2 text-sm text-ink-muted hover:text-ink"
          />
        </div>
      </SidebarBody>
    </SidebarRoot>
  );
}
```

Update `apps/account/app/components/Footer.tsx`:

```tsx
import Link from "next/link";
import { accountCopy } from "@trail/content";

export function Footer() {
  const { footer } = accountCopy;

  return (
    <footer className="border-t border-border/60 bg-bg/70 px-4 py-4 text-xs text-ink-muted backdrop-blur lg:px-10">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex flex-wrap items-center gap-2">
          <a
            href={`mailto:${footer.supportEmail}`}
            className="text-ink transition hover:text-ink"
          >
            {footer.supportEmail}
          </a>
          <span className="text-ink-muted">•</span>
          <span className="inline-flex items-center gap-2">
            <span className="h-2 w-2 rounded-full bg-emerald-500" />
            {footer.statusText}
          </span>
        </div>
        <div className="flex flex-wrap items-center gap-3">
          <Link href="/settings" className="transition hover:text-ink">
            {accountCopy.nav.settings}
          </Link>
          <Link href="/billing" className="transition hover:text-ink">
            {accountCopy.nav.billing}
          </Link>
          <Link href="/extension" className="transition hover:text-ink">
            {accountCopy.nav.extension}
          </Link>
        </div>
      </div>
    </footer>
  );
}
```

Update `apps/account/app/layout.tsx`:

```tsx
import type { Metadata } from "next";
import { Fraunces, Instrument_Sans } from "next/font/google";
import "./globals.css";
import { accountCopy } from "@trail/content";
import { Providers } from "./providers";

const display = Fraunces({
  subsets: ["latin"],
  display: "swap",
  variable: "--font-display",
  weight: ["400", "500", "600", "700"]
});

const sans = Instrument_Sans({
  subsets: ["latin"],
  display: "swap",
  variable: "--font-sans",
  weight: ["400", "500", "600", "700"]
});

export const metadata: Metadata = {
  title: accountCopy.meta.title,
  description: accountCopy.meta.description,
  icons: {
    icon: [
      { url: "/brand/trail-fork-light.svg", media: "(prefers-color-scheme: light)" },
      { url: "/brand/trail-fork-dark.svg", media: "(prefers-color-scheme: dark)" }
    ]
  }
};

export default function RootLayout({
  children
}: {
  children: React.ReactNode;
}) {
  return (
    <html
      lang="en"
      data-theme="system"
      suppressHydrationWarning
      className={`${display.variable} ${sans.variable}`}
    >
      <body className="bg-bg text-ink">
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
```

Update `apps/account/tailwind.config.ts` (extend fonts only):

```ts
// ...existing imports

const config: Config = {
  presets: [preset],
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./src/**/*.{ts,tsx}",
    "../../packages/ui/src/**/*.{ts,tsx}",
    "../../packages/content/src/**/*.{ts,tsx}",
    "../../packages/trpc/src/**/*.{ts,tsx}"
  ],
  theme: {
    extend: {
      colors: {
        base: "rgb(var(--base) / <alpha-value>)",
        surface: "rgb(var(--surface) / <alpha-value>)",
        "surface-strong": "rgb(var(--surface-strong) / <alpha-value>)",
        stroke: "rgb(var(--stroke) / <alpha-value>)",
        "ink-subtle": "rgb(var(--ink-subtle) / <alpha-value>)",
        cta: "rgb(var(--cta) / <alpha-value>)",
        "cta-hover": "rgb(var(--cta-hover) / <alpha-value>)",
        "cta-fg": "rgb(var(--cta-fg) / <alpha-value>)",
        accent: "rgb(var(--accent) / <alpha-value>)",
        "accent-soft": "rgb(var(--accent-soft) / <alpha-value>)"
      },
      fontFamily: {
        sans: ["var(--font-sans)", "Instrument Sans", "system-ui", "sans-serif"],
        display: ["var(--font-display)", "Fraunces", "serif"]
      },
      boxShadow: {
        card: "var(--trail-elev-2)"
      }
    }
  }
};

export default config;
```

Update `apps/account/app/globals.css`:

```css
@config "../tailwind.config.ts";
@import "tailwindcss";
@source "../../../packages/ui/src";
@source "../../../packages/content/src";
@import "@trail/ui/styles/tokens.css";
@import "@trail/ui/styles/base.css";
@import "@trail/ui/styles/animations.css";

:root,
[data-theme="light"] {
  color-scheme: light;
  --base: 243 239 231;
  --surface: 255 252 247;
  --surface-strong: 236 228 214;
  --stroke: 209 196 177;
  --ink: 27 30 36;
  --ink-muted: 92 98 108;
  --ink-subtle: 132 137 146;
  --cta: 196 150 58;
  --cta-hover: 174 128 43;
  --cta-fg: 17 20 25;
  --accent: 186 126 52;
  --accent-soft: 233 207 160;
  --font-display: var(--font-display);

  --trail-bg: var(--base);
  --trail-surface: var(--surface);
  --trail-surface-high: var(--surface-strong);
  --trail-surface-low: 247 245 240;
  --trail-border: var(--stroke);
  --trail-ink: var(--ink);
  --trail-ink-muted: var(--ink-muted);
  --trail-accent: var(--accent);
  --trail-accent-contrast: var(--cta-fg);
  --trail-highlight: 238 226 207;
  --trail-glass: var(--surface);
  --trail-glass-strong: var(--surface-strong);
  --trail-elev-1: 0 1px 0 rgba(20, 22, 26, 0.06);
  --trail-elev-2: 0 4px 18px rgba(20, 22, 26, 0.08);
  --trail-elev-3: 0 8px 28px rgba(20, 22, 26, 0.12);
  --trail-ring: var(--accent);
  --trail-gradient-1: radial-gradient(60% 60% at 12% 8%, rgba(196, 150, 58, 0.18), transparent 70%);
  --trail-gradient-2: radial-gradient(50% 50% at 88% 0%, rgba(27, 30, 36, 0.08), transparent 70%);
}

[data-theme="dark"] {
  color-scheme: dark;
  --base: 13 16 22;
  --surface: 22 27 36;
  --surface-strong: 30 37 49;
  --stroke: 52 60 74;
  --ink: 244 238 228;
  --ink-muted: 190 182 168;
  --ink-subtle: 150 144 132;
  --cta: 210 171 84;
  --cta-hover: 187 146 66;
  --cta-fg: 12 16 22;
  --accent: 210 171 84;
  --accent-soft: 86 64 32;

  --trail-bg: var(--base);
  --trail-surface: var(--surface);
  --trail-surface-high: var(--surface-strong);
  --trail-surface-low: 16 20 28;
  --trail-border: var(--stroke);
  --trail-ink: var(--ink);
  --trail-ink-muted: var(--ink-muted);
  --trail-accent: var(--accent);
  --trail-accent-contrast: var(--cta-fg);
  --trail-highlight: 44 52 66;
  --trail-glass: var(--surface);
  --trail-glass-strong: var(--surface-strong);
  --trail-elev-1: 0 1px 0 rgba(0, 0, 0, 0.4);
  --trail-elev-2: 0 6px 18px rgba(0, 0, 0, 0.4);
  --trail-elev-3: 0 10px 32px rgba(0, 0, 0, 0.5);
  --trail-ring: var(--accent);
  --trail-gradient-1: radial-gradient(60% 60% at 15% 10%, rgba(210, 171, 84, 0.18), transparent 72%);
  --trail-gradient-2: radial-gradient(50% 50% at 85% 0%, rgba(0, 0, 0, 0.35), transparent 70%);
}

@media (prefers-color-scheme: dark) {
  [data-theme="system"] {
    color-scheme: dark;
    --base: 13 16 22;
    --surface: 22 27 36;
    --surface-strong: 30 37 49;
    --stroke: 52 60 74;
    --ink: 244 238 228;
    --ink-muted: 190 182 168;
    --ink-subtle: 150 144 132;
    --cta: 210 171 84;
    --cta-hover: 187 146 66;
    --cta-fg: 12 16 22;
    --accent: 210 171 84;
    --accent-soft: 86 64 32;

    --trail-bg: var(--base);
    --trail-surface: var(--surface);
    --trail-surface-high: var(--surface-strong);
    --trail-surface-low: 16 20 28;
    --trail-border: var(--stroke);
    --trail-ink: var(--ink);
    --trail-ink-muted: var(--ink-muted);
    --trail-accent: var(--accent);
    --trail-accent-contrast: var(--cta-fg);
    --trail-highlight: 44 52 66;
    --trail-glass: var(--surface);
    --trail-glass-strong: var(--surface-strong);
    --trail-elev-1: 0 1px 0 rgba(0, 0, 0, 0.4);
    --trail-elev-2: 0 6px 18px rgba(0, 0, 0, 0.4);
    --trail-elev-3: 0 10px 32px rgba(0, 0, 0, 0.5);
    --trail-ring: var(--accent);
    --trail-gradient-1: radial-gradient(60% 60% at 15% 10%, rgba(210, 171, 84, 0.18), transparent 72%);
    --trail-gradient-2: radial-gradient(50% 50% at 85% 0%, rgba(0, 0, 0, 0.35), transparent 70%);
  }
}

@media (prefers-color-scheme: light) {
  [data-theme="system"] {
    color-scheme: light;
    --base: 243 239 231;
    --surface: 255 252 247;
    --surface-strong: 236 228 214;
    --stroke: 209 196 177;
    --ink: 27 30 36;
    --ink-muted: 92 98 108;
    --ink-subtle: 132 137 146;
    --cta: 196 150 58;
    --cta-hover: 174 128 43;
    --cta-fg: 17 20 25;
    --accent: 186 126 52;
    --accent-soft: 233 207 160;

    --trail-bg: var(--base);
    --trail-surface: var(--surface);
    --trail-surface-high: var(--surface-strong);
    --trail-surface-low: 247 245 240;
    --trail-border: var(--stroke);
    --trail-ink: var(--ink);
    --trail-ink-muted: var(--ink-muted);
    --trail-accent: var(--accent);
    --trail-accent-contrast: var(--cta-fg);
    --trail-highlight: 238 226 207;
    --trail-glass: var(--surface);
    --trail-glass-strong: var(--surface-strong);
    --trail-elev-1: 0 1px 0 rgba(20, 22, 26, 0.06);
    --trail-elev-2: 0 4px 18px rgba(20, 22, 26, 0.08);
    --trail-elev-3: 0 8px 28px rgba(20, 22, 26, 0.12);
    --trail-ring: var(--accent);
    --trail-gradient-1: radial-gradient(60% 60% at 12% 8%, rgba(196, 150, 58, 0.18), transparent 70%);
    --trail-gradient-2: radial-gradient(50% 50% at 88% 0%, rgba(27, 30, 36, 0.08), transparent 70%);
  }
}

.trail-app {
  background-image: var(--trail-gradient-1), var(--trail-gradient-2);
  background-repeat: no-repeat;
  background-attachment: fixed;
}

.app-shell {
  min-height: 100vh;
}
```

**Step 4: Run test to verify it passes**

Run: `pnpm -C apps/account test`

Expected: PASS

**Step 5: Commit**

```bash
git add apps/account/app/components apps/account/components/ui/sidebar.tsx apps/account/app/layout.tsx apps/account/app/globals.css apps/account/tailwind.config.ts
git commit -m "Redesign account shell"
```

---

### Task 2: Getting Started Page

**Files:**
- Create: `apps/account/app/(app)/getting-started/page.tsx`
- Test: `apps/account/app/(app)/getting-started/__tests__/getting-started-page.test.tsx`

**Step 1: Write the failing test**

Create `apps/account/app/(app)/getting-started/__tests__/getting-started-page.test.tsx`:

```tsx
import React from "react";
import { render, screen } from "@testing-library/react";
import { accountCopy } from "@trail/content";
import GettingStartedPage from "../page";

describe("GettingStartedPage", () => {
  it("renders the checklist and header", () => {
    render(<GettingStartedPage />);

    expect(
      screen.getByRole("heading", { name: accountCopy.gettingStarted.title })
    ).toBeInTheDocument();
    expect(screen.getByText(accountCopy.gettingStarted.stepsTitle)).toBeInTheDocument();
  });
});
```

**Step 2: Run test to verify it fails**

Run: `pnpm -C apps/account test`

Expected: FAIL (new page not implemented)

**Step 3: Write minimal implementation**

Create `apps/account/app/(app)/getting-started/page.tsx`:

```tsx
import Link from "next/link";
import { Button, SectionHeader, StepList } from "@trail/ui";
import { accountCopy } from "@trail/content";
import { PageHeader } from "@/app/components/PageHeader";

export default function GettingStartedPage() {
  const { gettingStarted } = accountCopy;

  return (
    <section className="space-y-10">
      <PageHeader
        eyebrow={accountCopy.nav.gettingStarted}
        title={gettingStarted.title}
        subtitle={gettingStarted.subtitle}
        actions={
          <Button.AsChild size="sm">
            <Link href="/extension">{gettingStarted.cta}</Link>
          </Button.AsChild>
        }
      />

      <div className="grid gap-4 lg:grid-cols-[1.4fr_1fr]">
        <div className="trail-card p-5">
          <SectionHeader
            title={gettingStarted.stepsTitle}
            subtitle={gettingStarted.stepsSubtitle}
            actions={<span className="trail-pill">{gettingStarted.progress}</span>}
          />
          <StepList className="mt-4" steps={gettingStarted.steps} />
        </div>

        <div className="trail-card p-5">
          <p className="trail-eyebrow">{gettingStarted.next.eyebrow}</p>
          <p className="text-sm font-semibold text-ink">{gettingStarted.next.title}</p>
          <p className="text-xs text-ink-muted">{gettingStarted.next.subtitle}</p>
          <ul className="mt-4 space-y-2 text-xs text-ink-muted">
            {gettingStarted.next.items.map((item) => (
              <li key={item} className="flex items-start gap-2">
                <span className="mt-1 h-1.5 w-1.5 rounded-full bg-accent" />
                <span>{item}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>

      <div className="trail-card p-5">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <p className="trail-eyebrow">{gettingStarted.support.eyebrow}</p>
            <p className="text-sm font-semibold text-ink">{gettingStarted.support.title}</p>
            <p className="text-xs text-ink-muted">{gettingStarted.support.subtitle}</p>
          </div>
          <Button.AsChild size="sm" variant="outline">
            <a href={`mailto:${accountCopy.footer.supportEmail}`}>
              {gettingStarted.support.cta}
            </a>
          </Button.AsChild>
        </div>
      </div>
    </section>
  );
}
```

**Step 4: Run test to verify it passes**

Run: `pnpm -C apps/account test`

Expected: PASS

**Step 5: Commit**

```bash
git add apps/account/app/(app)/getting-started
git commit -m "Add getting started page"
```

---

### Task 3: Activity Page

**Files:**
- Create: `apps/account/app/(app)/activity/page.tsx`
- Test: `apps/account/app/(app)/activity/__tests__/activity-page.test.tsx`

**Step 1: Write the failing test**

Create `apps/account/app/(app)/activity/__tests__/activity-page.test.tsx`:

```tsx
import React from "react";
import { render, screen } from "@testing-library/react";
import { accountCopy } from "@trail/content";
import ActivityPage from "../page";

describe("ActivityPage", () => {
  it("renders the activity header and empty state", () => {
    render(<ActivityPage />);

    expect(
      screen.getByRole("heading", { name: accountCopy.activity.title })
    ).toBeInTheDocument();
    expect(screen.getByText(accountCopy.activity.empty.title)).toBeInTheDocument();
  });
});
```

**Step 2: Run test to verify it fails**

Run: `pnpm -C apps/account test`

Expected: FAIL (new page not implemented)

**Step 3: Write minimal implementation**

Create `apps/account/app/(app)/activity/page.tsx`:

```tsx
import Link from "next/link";
import { Button, EmptyState } from "@trail/ui";
import { accountCopy } from "@trail/content";
import { PageHeader } from "@/app/components/PageHeader";

export default function ActivityPage() {
  const { activity } = accountCopy;
  const hasActivity = false;

  return (
    <section className="space-y-10">
      <PageHeader
        eyebrow={accountCopy.nav.activity}
        title={activity.title}
        subtitle={activity.subtitle}
        actions={
          <Button.AsChild size="sm" variant="outline">
            <Link href="/getting-started">{activity.empty.secondaryCta}</Link>
          </Button.AsChild>
        }
      />

      <div className="grid gap-4 lg:grid-cols-[1.6fr_1fr]">
        <div className="trail-card p-5">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div>
              <p className="trail-eyebrow">{activity.stream.eyebrow}</p>
              <p className="text-sm font-semibold text-ink">{activity.stream.title}</p>
              <p className="text-xs text-ink-muted">{activity.stream.subtitle}</p>
            </div>
            <div className="flex flex-wrap items-center gap-2">
              {activity.stream.filters.map((filter) => (
                <span key={filter} className="trail-pill">
                  {filter}
                </span>
              ))}
            </div>
          </div>

          {hasActivity ? (
            <div className="mt-4 text-xs text-ink-muted">activity list goes here</div>
          ) : (
            <div className="mt-5">
              <EmptyState
                title={activity.empty.title}
                description={activity.empty.description}
                icon={<span className="h-5 w-5 rounded-full border border-border/60" />}
                items={activity.empty.items}
                action={
                  <Button.AsChild size="sm">
                    <Link href="/extension">{activity.empty.cta}</Link>
                  </Button.AsChild>
                }
                secondaryAction={
                  <Button.AsChild size="sm" variant="outline">
                    <Link href="/getting-started">{activity.empty.secondaryCta}</Link>
                  </Button.AsChild>
                }
              />
            </div>
          )}
        </div>

        <div className="space-y-4">
          <div className="trail-card p-5">
            <p className="trail-eyebrow">{activity.next.eyebrow}</p>
            <p className="text-sm font-semibold text-ink">{activity.next.title}</p>
            <p className="text-xs text-ink-muted">{activity.next.subtitle}</p>
            <div className="mt-4">
              <Button.AsChild size="sm" variant="outline">
                <Link href="/extension">{activity.next.cta}</Link>
              </Button.AsChild>
            </div>
          </div>

          <div className="trail-card p-5">
            <p className="trail-eyebrow">{activity.coverage.eyebrow}</p>
            <p className="text-sm font-semibold text-ink">{activity.coverage.title}</p>
            <p className="text-xs text-ink-muted">{activity.coverage.subtitle}</p>
          </div>
        </div>
      </div>
    </section>
  );
}
```

**Step 4: Run test to verify it passes**

Run: `pnpm -C apps/account test`

Expected: PASS

**Step 5: Commit**

```bash
git add apps/account/app/(app)/activity
git commit -m "Add activity page"
```

---

### Task 4: Sessions Page

**Files:**
- Create: `apps/account/app/(app)/sessions/page.tsx`
- Test: `apps/account/app/(app)/sessions/__tests__/sessions-page.test.tsx`

**Step 1: Write the failing test**

Create `apps/account/app/(app)/sessions/__tests__/sessions-page.test.tsx`:

```tsx
import React from "react";
import { render, screen } from "@testing-library/react";
import { accountCopy } from "@trail/content";
import SessionsPage from "../page";

describe("SessionsPage", () => {
  it("renders the sessions header and empty state", () => {
    render(<SessionsPage />);

    expect(
      screen.getByRole("heading", { name: accountCopy.sessions.title })
    ).toBeInTheDocument();
    expect(screen.getByText(accountCopy.sessions.list.emptyTitle)).toBeInTheDocument();
  });
});
```

**Step 2: Run test to verify it fails**

Run: `pnpm -C apps/account test`

Expected: FAIL (new page not implemented)

**Step 3: Write minimal implementation**

Create `apps/account/app/(app)/sessions/page.tsx`:

```tsx
import Link from "next/link";
import { Button, EmptyState } from "@trail/ui";
import { accountCopy } from "@trail/content";
import { PageHeader } from "@/app/components/PageHeader";

export default function SessionsPage() {
  const { sessions } = accountCopy;
  const hasSessions = false;

  return (
    <section className="space-y-10">
      <PageHeader
        eyebrow={accountCopy.nav.sessions}
        title={sessions.title}
        subtitle={sessions.subtitle}
        actions={
          <Button.AsChild size="sm">
            <Link href="/extension">{sessions.guidance.cta}</Link>
          </Button.AsChild>
        }
      />

      <div className="grid gap-4 lg:grid-cols-[1.5fr_1fr]">
        <div className="trail-card p-5">
          <div>
            <p className="trail-eyebrow">{sessions.list.eyebrow}</p>
            <p className="text-sm font-semibold text-ink">{sessions.list.title}</p>
            <p className="text-xs text-ink-muted">{sessions.list.subtitle}</p>
          </div>

          {hasSessions ? (
            <div className="mt-4 text-xs text-ink-muted">sessions list goes here</div>
          ) : (
            <div className="mt-5">
              <EmptyState
                title={sessions.list.emptyTitle}
                description={sessions.list.emptyDescription}
                icon={<span className="h-5 w-5 rounded-full border border-border/60" />}
                items={sessions.list.emptyItems}
                action={
                  <Button.AsChild size="sm">
                    <Link href="/extension">{sessions.guidance.cta}</Link>
                  </Button.AsChild>
                }
              />
            </div>
          )}
        </div>

        <div className="trail-card p-5">
          <div>
            <p className="trail-eyebrow">{sessions.posture.eyebrow}</p>
            <p className="text-sm font-semibold text-ink">{sessions.posture.title}</p>
            <p className="text-xs text-ink-muted">{sessions.posture.subtitle}</p>
          </div>
          <div className="mt-4 grid gap-3">
            {sessions.posture.items.map((item) => (
              <div key={item.label} className="flex items-center justify-between text-xs">
                <span className="text-ink-muted">{item.label}</span>
                <span className="trail-status">{item.value}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="trail-card p-5">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <p className="text-sm font-semibold text-ink">{sessions.guidance.title}</p>
            <p className="text-xs text-ink-muted">{sessions.guidance.description}</p>
          </div>
          <Button.AsChild size="sm" variant="outline">
            <Link href="/extension">{sessions.guidance.cta}</Link>
          </Button.AsChild>
        </div>
      </div>
    </section>
  );
}
```

**Step 4: Run test to verify it passes**

Run: `pnpm -C apps/account test`

Expected: PASS

**Step 5: Commit**

```bash
git add apps/account/app/(app)/sessions
git commit -m "Add sessions page"
```

---

### Task 5: Dashboard Rewrite

**Files:**
- Modify: `apps/account/app/(app)/dashboard/page.tsx`
- Modify: `apps/account/app/(app)/dashboard/DashboardClient.tsx`
- Test: `apps/account/app/(app)/dashboard/__tests__/dashboard-page.test.tsx`
- Test: `apps/account/app/(app)/dashboard/__tests__/dashboard-client.test.tsx`

**Step 1: Write the failing tests**

Create `apps/account/app/(app)/dashboard/__tests__/dashboard-page.test.tsx`:

```tsx
import React from "react";
import { render, screen } from "@testing-library/react";
import { vi } from "vitest";
import { accountCopy } from "@trail/content";
import DashboardPage from "../page";

vi.mock("next/link", () => ({
  default: ({ href, children, ...props }: { href: string; children: React.ReactNode }) => (
    <a href={href} {...props}>
      {children}
    </a>
  )
}));

vi.mock("../DashboardClient", () => ({
  DashboardClient: () => <div>DashboardClient</div>
}));

describe("DashboardPage", () => {
  it("renders the page header and onboarding", () => {
    render(<DashboardPage />);

    expect(
      screen.getByRole("heading", { name: accountCopy.dashboard.title })
    ).toBeInTheDocument();
    expect(screen.getByText(accountCopy.dashboard.onboarding.title)).toBeInTheDocument();
  });
});
```

Create `apps/account/app/(app)/dashboard/__tests__/dashboard-client.test.tsx`:

```tsx
import React from "react";
import { render, screen } from "@testing-library/react";
import { vi } from "vitest";
import { accountCopy } from "@trail/content";
import { DashboardClient } from "../DashboardClient";

vi.mock("@/src/trpc/client", () => ({
  trpc: {
    health: {
      useQuery: () => ({ data: { ok: false } })
    },
    me: {
      useQuery: () => ({ data: { user: { name: "Alex Trail", email: "alex@trail.net" } } })
    }
  }
}));

describe("DashboardClient", () => {
  it("renders empty state and status fallback", () => {
    render(<DashboardClient />);

    expect(screen.getByText(accountCopy.dashboard.empty.title)).toBeInTheDocument();
    expect(screen.getByText(accountCopy.dashboard.status.lastSyncFallback)).toBeInTheDocument();
  });
});
```

**Step 2: Run test to verify it fails**

Run: `pnpm -C apps/account test`

Expected: FAIL (new layout not yet present)

**Step 3: Write minimal implementation**

Update `apps/account/app/(app)/dashboard/page.tsx`:

```tsx
import Link from "next/link";
import { ArrowRightIcon, LightningBoltIcon } from "@radix-ui/react-icons";
import { Button, SectionHeader, StepList } from "@trail/ui";
import { accountCopy } from "@trail/content";
import { PageHeader } from "@/app/components/PageHeader";
import { DashboardClient } from "./DashboardClient";

export default function DashboardPage() {
  const { dashboard } = accountCopy;

  return (
    <section className="space-y-10">
      <PageHeader
        eyebrow={accountCopy.nav.dashboard}
        title={dashboard.title}
        subtitle={dashboard.subtitle}
        actions={
          <Button.AsChild size="sm">
            <Link href="/extension">{dashboard.cta}</Link>
          </Button.AsChild>
        }
      />

      <div className="grid gap-4 lg:grid-cols-[1.4fr_1fr]">
        <Link
          href="/extension"
          className="group trail-card relative overflow-hidden p-5 transition hover:border-border"
        >
          <div className="flex items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <span className="flex h-10 w-10 items-center justify-center rounded-2xl border border-border/60 bg-bg">
                <LightningBoltIcon className="h-4 w-4" />
              </span>
              <div>
                <p className="trail-eyebrow">{dashboard.activation.eyebrow}</p>
                <p className="text-sm font-semibold text-ink">{dashboard.activation.title}</p>
                <p className="text-xs text-ink-muted">{dashboard.activation.subtitle}</p>
              </div>
            </div>
            <span className="inline-flex items-center gap-2 text-xs font-medium text-ink">
              {dashboard.activation.cta}
              <ArrowRightIcon className="h-3 w-3 transition group-hover:translate-x-0.5" />
            </span>
          </div>
        </Link>

        <div className="trail-card p-5">
          <SectionHeader
            title={dashboard.onboarding.title}
            subtitle={dashboard.onboarding.subtitle}
            actions={<span className="trail-pill">{dashboard.onboarding.progress}</span>}
          />
          <StepList className="mt-4" steps={dashboard.onboarding.steps} />
        </div>
      </div>

      <DashboardClient />
    </section>
  );
}
```

Update `apps/account/app/(app)/dashboard/DashboardClient.tsx`:

```tsx
"use client";

import Link from "next/link";
import {
  BackpackIcon,
  BarChartIcon,
  ClockIcon,
  DesktopIcon,
  LightningBoltIcon,
  RocketIcon
} from "@radix-ui/react-icons";
import { Button, EmptyState, StatCard } from "@trail/ui";
import { accountCopy } from "@trail/content";
import { trpc } from "@/src/trpc/client";

export function DashboardClient() {
  const { dashboard } = accountCopy;
  const health = trpc.health.useQuery();
  const me = trpc.me.useQuery();

  const recentTrails: Array<{
    id: string;
    title: string;
    summary: string;
    timestamp: string;
  }> = [];

  const hasTrails = recentTrails.length > 0;
  const displayName =
    me.data?.user?.name?.trim() ||
    me.data?.user?.email?.split("@")[0] ||
    accountCopy.settings.profile.fallbackName;

  const statusLabel = health.data?.ok ? dashboard.status.online : dashboard.status.checking;
  const lastSync = health.data?.timestamp
    ? new Date(health.data.timestamp).toLocaleString()
    : dashboard.status.lastSyncFallback;

  return (
    <div className="space-y-8">
      <section className="trail-card p-5">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <p className="trail-eyebrow">{dashboard.recent.eyebrow}</p>
            <p className="text-sm font-semibold text-ink">{dashboard.recent.title}</p>
            <p className="text-xs text-ink-muted">{dashboard.recent.subtitle}</p>
          </div>
          <span className="trail-status">
            {hasTrails ? dashboard.recent.activeCount : dashboard.recent.emptyCount}
          </span>
        </div>

        {hasTrails ? (
          <div className="mt-4 grid gap-3 md:grid-cols-2">
            {recentTrails.map((trail) => (
              <div key={trail.id} className="trail-card-compact p-4">
                <div className="flex items-center justify-between gap-3">
                  <p className="text-sm font-semibold text-ink">{trail.title}</p>
                  <span className="trail-status">{trail.timestamp}</span>
                </div>
                <p className="mt-2 text-xs text-ink-muted">{trail.summary}</p>
              </div>
            ))}
          </div>
        ) : (
          <div className="mt-5">
            <EmptyState
              title={dashboard.empty.title}
              description={dashboard.empty.description}
              icon={<BackpackIcon className="h-5 w-5" />}
              items={dashboard.empty.items}
              action={
                <Button.AsChild size="sm">
                  <Link href="/extension">{dashboard.empty.cta}</Link>
                </Button.AsChild>
              }
              secondaryAction={
                <Button.AsChild size="sm" variant="outline">
                  <Link href="/settings">{dashboard.empty.secondaryCta}</Link>
                </Button.AsChild>
              }
            />
          </div>
        )}
      </section>

      <section className="grid gap-4 lg:grid-cols-[2fr_1fr]">
        <div className="trail-card p-5">
          <div>
            <p className="trail-eyebrow">{dashboard.status.eyebrow}</p>
            <p className="text-sm font-semibold text-ink">{dashboard.status.title}</p>
            <p className="text-xs text-ink-muted">{dashboard.status.subtitle}</p>
          </div>
          <div className="mt-4 grid gap-3 md:grid-cols-3">
            <StatCard
              label={dashboard.status.stats.sync}
              value={statusLabel}
              caption={lastSync}
              icon={<LightningBoltIcon className="h-4 w-4" />}
            />
            <StatCard
              label={dashboard.status.stats.sessions}
              value={hasTrails ? "2" : "0"}
              caption={dashboard.status.stats.sessionsCaption}
              icon={<DesktopIcon className="h-4 w-4" />}
            />
            <StatCard
              label={dashboard.status.stats.trails}
              value={hasTrails ? "12" : "0"}
              caption={dashboard.status.stats.trailsCaption}
              icon={<BarChartIcon className="h-4 w-4" />}
            />
          </div>
          <div className="mt-4 flex flex-wrap items-center gap-3 text-xs text-ink-muted">
            <Link href="/extension" className="text-ink transition hover:text-ink">
              {dashboard.status.actions.extension}
            </Link>
            <span>•</span>
            <Link href="/settings" className="text-ink transition hover:text-ink">
              {dashboard.status.actions.settings}
            </Link>
            <span>•</span>
            <Link href="/billing" className="text-ink transition hover:text-ink">
              {dashboard.status.actions.billing}
            </Link>
          </div>
        </div>

        <div className="trail-card p-5">
          <div>
            <p className="trail-eyebrow">{dashboard.insights.eyebrow}</p>
            <p className="text-sm font-semibold text-ink">{dashboard.insights.title}</p>
            <p className="text-xs text-ink-muted">{dashboard.insights.subtitle}</p>
          </div>
          <div className="mt-4 grid gap-3">
            <StatCard
              label={dashboard.insights.stats.coverage}
              value={hasTrails ? "68%" : dashboard.insights.stats.emptyValue}
              caption={dashboard.insights.stats.coverageCaption}
              icon={<RocketIcon className="h-4 w-4" />}
            />
            <StatCard
              label={dashboard.insights.stats.lastTrail}
              value={hasTrails ? "2h" : dashboard.insights.stats.emptyValue}
              caption={dashboard.insights.stats.lastTrailCaption}
              icon={<ClockIcon className="h-4 w-4" />}
            />
          </div>
          <p className="mt-3 text-xs text-ink-muted">
            {hasTrails
              ? dashboard.insights.footerActive.replace("{name}", displayName)
              : dashboard.insights.footerEmpty}
          </p>
        </div>
      </section>
    </div>
  );
}
```

**Step 4: Run test to verify it passes**

Run: `pnpm -C apps/account test`

Expected: PASS

**Step 5: Commit**

```bash
git add apps/account/app/(app)/dashboard
git commit -m "Redesign dashboard"
```

---

### Task 6: Extension Page Rewrite

**Files:**
- Modify: `apps/account/app/(app)/extension/page.tsx`
- Test: `apps/account/app/(app)/extension/__tests__/extension-page.test.tsx`

**Step 1: Write the failing test**

Create `apps/account/app/(app)/extension/__tests__/extension-page.test.tsx`:

```tsx
import React from "react";
import { render, screen } from "@testing-library/react";
import { vi } from "vitest";
import { accountCopy } from "@trail/content";
import ExtensionPage from "../page";

vi.mock("next/navigation", () => ({
  redirect: vi.fn()
}));

vi.mock("@/src/lib/auth0", () => ({
  getAuthSession: async () => ({ user: { name: "Alex Trail", email: "alex@trail.net" } }),
  isAuthBypassed: () => false
}));

vi.mock("@/src/server/user", () => ({
  ensureUser: async () => ({ id: "user_1" })
}));

vi.mock("@/src/server/extension-login", () => ({
  createExtensionLoginCode: async () => "CODE123"
}));

describe("ExtensionPage", () => {
  it("renders the extension headers", async () => {
    const node = await ExtensionPage({ searchParams: Promise.resolve({}) });
    render(node);

    expect(
      screen.getByRole("heading", { name: accountCopy.extension.title })
    ).toBeInTheDocument();
    expect(screen.getByText(accountCopy.extension.status.title)).toBeInTheDocument();
  });
});
```

**Step 2: Run test to verify it fails**

Run: `pnpm -C apps/account test`

Expected: FAIL (new layout not yet present)

**Step 3: Write minimal implementation**

Update `apps/account/app/(app)/extension/page.tsx`:

```tsx
import { redirect } from "next/navigation";
import {
  DesktopIcon,
  LaptopIcon,
  Link2Icon,
  LockClosedIcon
} from "@radix-ui/react-icons";
import { Button, EmptyState, StatCard } from "@trail/ui";
import { accountCopy } from "@trail/content";
import { PageHeader } from "@/app/components/PageHeader";
import { getAuthSession, isAuthBypassed } from "@/src/lib/auth0";
import { ensureUser } from "@/src/server/user";
import { createExtensionLoginCode } from "@/src/server/extension-login";

export const runtime = "nodejs";

type ExtensionPageProps = {
  searchParams: Promise<{
    code?: string;
  }>;
};

type ExtensionSession = {
  id: string;
  device: string;
  location: string;
  lastSeen: string;
  status: string;
};

export default async function ExtensionPage({ searchParams }: ExtensionPageProps) {
  const resolvedSearchParams = await searchParams;
  const queryCode =
    typeof resolvedSearchParams?.code === "string" ? resolvedSearchParams.code : null;
  const returnTo = queryCode ? `/extension?code=${queryCode}` : "/extension";
  const authBypassed = isAuthBypassed();

  const session = await getAuthSession();
  if (!session?.user && !authBypassed) {
    redirect(`/auth/login?${new URLSearchParams({ returnTo })}`);
  }

  const user = session?.user ? await ensureUser(session.user) : null;
  if (!user && !authBypassed) {
    redirect(`/auth/login?${new URLSearchParams({ returnTo })}`);
  }

  let connectionReady = false;

  if (queryCode && user && !authBypassed) {
    try {
      const stored = await createExtensionLoginCode(user.id, queryCode);
      if (stored !== queryCode) {
        redirect(`/extension?code=${stored}`);
      }
      connectionReady = true;
    } catch {
      const newCode = await createExtensionLoginCode(user.id);
      redirect(`/extension?code=${newCode}`);
    }
  }

  const sessions: ExtensionSession[] = [];

  return (
    <section className="space-y-10">
      <PageHeader
        eyebrow={accountCopy.nav.extension}
        title={accountCopy.extension.title}
        subtitle={accountCopy.extension.subtitle}
        actions={
          <Button.AsChild size="sm">
            <a href={accountCopy.extension.empty.ctaHref}>{accountCopy.extension.cta}</a>
          </Button.AsChild>
        }
      />

      <div className="grid gap-4 lg:grid-cols-[1.5fr_1fr]">
        <div className="trail-card p-5">
          <div>
            <p className="trail-eyebrow">{accountCopy.extension.status.eyebrow}</p>
            <p className="text-sm font-semibold text-ink">
              {accountCopy.extension.status.title}
            </p>
            <p className="text-xs text-ink-muted">{accountCopy.extension.status.subtitle}</p>
          </div>
          <div className="mt-4">
            {connectionReady ? (
              <div className="grid gap-3 md:grid-cols-2">
                <StatCard
                  label={accountCopy.extension.connected.stats.status}
                  value={accountCopy.extension.connected.stats.value}
                  caption={accountCopy.extension.connected.stats.caption}
                  icon={<Link2Icon className="h-4 w-4" />}
                />
                <StatCard
                  label={accountCopy.extension.connected.stats.permissions}
                  value={accountCopy.extension.connected.stats.permissionsValue}
                  caption={accountCopy.extension.connected.stats.permissionsCaption}
                  icon={<LockClosedIcon className="h-4 w-4" />}
                />
              </div>
            ) : (
              <EmptyState
                title={accountCopy.extension.empty.title}
                description={accountCopy.extension.empty.description}
                icon={<LaptopIcon className="h-5 w-5" />}
                items={accountCopy.extension.empty.items}
                className="rounded-none border-0 bg-transparent p-0"
                action={
                  <a
                    href={accountCopy.extension.empty.ctaHref}
                    className="inline-flex items-center gap-2 rounded-full border border-border/60 px-4 py-2 text-xs font-semibold text-ink"
                  >
                    {accountCopy.extension.empty.cta}
                  </a>
                }
              />
            )}
          </div>
        </div>

        <div className="trail-card p-5">
          <div>
            <p className="trail-eyebrow">{accountCopy.extension.device.eyebrow}</p>
            <p className="text-sm font-semibold text-ink">
              {accountCopy.extension.device.title}
            </p>
            <p className="text-xs text-ink-muted">{accountCopy.extension.device.subtitle}</p>
          </div>
          <div className="mt-4 grid gap-3">
            <StatCard
              label={accountCopy.extension.device.primaryDevice}
              value={connectionReady ? accountCopy.extension.device.connected : "—"}
              caption={accountCopy.extension.device.primaryDeviceCaption}
              icon={<DesktopIcon className="h-4 w-4" />}
            />
            <StatCard
              label={accountCopy.extension.device.lastSeen}
              value={connectionReady ? accountCopy.extension.device.lastSeenValue : "—"}
              caption={accountCopy.extension.device.lastSeenCaption}
              icon={<LaptopIcon className="h-4 w-4" />}
            />
          </div>
        </div>
      </div>

      <div className="trail-card p-5">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <p className="trail-eyebrow">{accountCopy.extension.sessions.eyebrow}</p>
            <p className="text-sm font-semibold text-ink">
              {accountCopy.extension.sessions.title}
            </p>
            <p className="text-xs text-ink-muted">
              {accountCopy.extension.sessions.subtitle}
            </p>
          </div>
          <span className="trail-status">{accountCopy.extension.sessions.comingSoon}</span>
        </div>
        {sessions.length ? (
          <div className="mt-4 divide-y divide-border/40">
            {sessions.map((item) => (
              <div
                key={item.id}
                className="flex flex-wrap items-center justify-between gap-4 py-3"
              >
                <div>
                  <p className="text-sm font-semibold text-ink">{item.device}</p>
                  <p className="text-xs text-ink-muted">{item.location}</p>
                </div>
                <span className="trail-status">{item.lastSeen}</span>
              </div>
            ))}
          </div>
        ) : (
          <div className="mt-4 border-t border-border/40 pt-3 text-xs text-ink-muted">
            {accountCopy.extension.sessions.empty}
          </div>
        )}
      </div>
    </section>
  );
}
```

**Step 4: Run test to verify it passes**

Run: `pnpm -C apps/account test`

Expected: PASS

**Step 5: Commit**

```bash
git add apps/account/app/(app)/extension
git commit -m "Redesign extension page"
```

---

### Task 7: Settings Page Rewrite

**Files:**
- Modify: `apps/account/app/(app)/settings/page.tsx`
- Test: `apps/account/app/(app)/settings/__tests__/settings-page.test.tsx`

**Step 1: Write the failing test**

Create `apps/account/app/(app)/settings/__tests__/settings-page.test.tsx`:

```tsx
import React from "react";
import { render, screen } from "@testing-library/react";
import { vi } from "vitest";
import { accountCopy } from "@trail/content";
import SettingsPage from "../page";

vi.mock("next/navigation", () => ({
  redirect: vi.fn()
}));

vi.mock("@/src/lib/auth0", () => ({
  getAuthSession: async () => ({
    user: { name: "Alex Trail", email: "alex@trail.net", picture: null }
  })
}));

describe("SettingsPage", () => {
  it("renders the settings headers", async () => {
    const node = await SettingsPage();
    render(node);

    expect(
      screen.getByRole("heading", { name: accountCopy.settings.title })
    ).toBeInTheDocument();
    expect(screen.getByText(accountCopy.settings.profile.title)).toBeInTheDocument();
  });
});
```

**Step 2: Run test to verify it fails**

Run: `pnpm -C apps/account test`

Expected: FAIL (new layout not yet present)

**Step 3: Write minimal implementation**

Update `apps/account/app/(app)/settings/page.tsx`:

```tsx
import { redirect } from "next/navigation";
import Image, { type ImageLoaderProps } from "next/image";
import { accountCopy } from "@trail/content";
import { Button } from "@trail/ui";
import { PageHeader } from "@/app/components/PageHeader";
import { getAuthSession } from "@/src/lib/auth0";

const avatarLoader = ({ src }: ImageLoaderProps) => src;

export default async function SettingsPage() {
  const { settings } = accountCopy;
  const session = await getAuthSession();

  if (!session?.user) {
    redirect("/auth/login");
  }

  const user = session.user;
  const initialsSource = user.name || user.email || settings.profile.fallbackName;
  const initials = initialsSource
    .split(" ")
    .filter(Boolean)
    .slice(0, 2)
    .map((chunk) => chunk[0]?.toLowerCase())
    .join("");

  const auth0Domain = process.env.AUTH0_DOMAIN
    ? `https://${process.env.AUTH0_DOMAIN}`
    : null;
  const auth0ProfileUrl = auth0Domain ? `${auth0Domain}/u/me` : "https://auth0.com/";

  const sessions = [
    {
      id: "current",
      device: settings.security.currentSession,
      location: settings.security.currentLocation,
      lastSeen: settings.security.currentActivity
    }
  ];

  return (
    <section className="space-y-10">
      <PageHeader
        eyebrow={accountCopy.nav.settings}
        title={settings.title}
        subtitle={settings.subtitle}
        actions={
          <Button.AsChild size="sm" variant="outline">
            <a href={auth0ProfileUrl} target="_blank" rel="noreferrer">
              {settings.profile.manageCta}
            </a>
          </Button.AsChild>
        }
      />

      <div className="grid gap-4 lg:grid-cols-[1.2fr_1fr]">
        <div id="profile" className="trail-card p-5">
          <div>
            <p className="trail-eyebrow">{settings.profile.eyebrow}</p>
            <p className="text-sm font-semibold text-ink">{settings.profile.title}</p>
            <p className="text-xs text-ink-muted">{settings.profile.subtitle}</p>
          </div>
          <div className="mt-5 flex items-center gap-4">
            <div className="flex h-12 w-12 items-center justify-center overflow-hidden rounded-full border border-border/60 bg-surface text-sm font-semibold text-ink">
              {user.picture ? (
                <Image
                  loader={avatarLoader}
                  unoptimized
                  src={user.picture}
                  alt={user.name ?? settings.profile.avatarAlt}
                  width={48}
                  height={48}
                  sizes="48px"
                  className="h-full w-full object-cover"
                />
              ) : (
                initials
              )}
            </div>
            <div>
              <p className="text-sm font-semibold lowercase text-ink">
                {user.name ?? settings.profile.fallbackName}
              </p>
              <p className="text-xs lowercase text-ink-muted">
                {user.email ?? settings.profile.fallbackEmail}
              </p>
            </div>
          </div>
          <div className="mt-4 flex flex-wrap gap-3">
            <Button.AsChild size="sm" variant="outline">
              <a href={auth0ProfileUrl} target="_blank" rel="noreferrer">
                {settings.profile.manageCta}
              </a>
            </Button.AsChild>
            <Button.AsChild size="sm" variant="ghost">
              <a href="/auth/logout">{settings.profile.signOutCta}</a>
            </Button.AsChild>
          </div>
        </div>

        <div id="security" className="trail-card p-5">
          <div>
            <p className="trail-eyebrow">{settings.security.eyebrow}</p>
            <p className="text-sm font-semibold text-ink">{settings.security.title}</p>
            <p className="text-xs text-ink-muted">{settings.security.subtitle}</p>
          </div>
          <div className="mt-4 divide-y divide-border/40">
            {sessions.map((sessionItem) => (
              <div
                key={sessionItem.id}
                className="flex flex-wrap items-center justify-between gap-4 py-3"
              >
                <div>
                  <p className="text-sm font-semibold text-ink">{sessionItem.device}</p>
                  <p className="text-xs text-ink-muted">{sessionItem.location}</p>
                </div>
                <span className="trail-status">{sessionItem.lastSeen}</span>
              </div>
            ))}
          </div>
          <div className="mt-4 flex flex-wrap items-center gap-3 text-xs text-ink-muted">
            <a href={auth0ProfileUrl} target="_blank" rel="noreferrer" className="text-ink">
              {settings.security.changePasswordCta}
            </a>
            <span>•</span>
            <span>{settings.security.signOutEverywhereCta}</span>
          </div>
        </div>
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <div id="workspace" className="trail-card p-5">
          <div>
            <p className="trail-eyebrow">{settings.workspace.eyebrow}</p>
            <p className="text-sm font-semibold text-ink">{settings.workspace.title}</p>
            <p className="text-xs text-ink-muted">{settings.workspace.subtitle}</p>
          </div>
          <div className="mt-4 divide-y divide-border/40">
            <div className="flex items-center justify-between gap-4 py-3">
              <div>
                <p className="text-sm font-semibold text-ink">{settings.workspace.soloTitle}</p>
                <p className="text-xs text-ink-muted">{settings.workspace.soloDescription}</p>
              </div>
              <span className="trail-status">{settings.workspace.soloBadge}</span>
            </div>
            <div className="flex items-center justify-between gap-4 py-3 text-ink-muted">
              <div>
                <p className="text-sm font-semibold text-ink">{settings.workspace.teamTitle}</p>
                <p className="text-xs text-ink-muted">{settings.workspace.teamDescription}</p>
              </div>
              <span className="text-[0.7rem] font-semibold lowercase text-ink-muted">
                {settings.workspace.comingSoon}
              </span>
            </div>
          </div>
        </div>

        <div id="notifications" className="trail-card p-5">
          <div>
            <p className="trail-eyebrow">{settings.notifications.eyebrow}</p>
            <p className="text-sm font-semibold text-ink">{settings.notifications.title}</p>
            <p className="text-xs text-ink-muted">{settings.notifications.subtitle}</p>
          </div>
          <div className="mt-4 divide-y divide-border/40 text-xs text-ink-muted">
            {settings.notifications.items.map((item) => (
              <div
                key={item}
                className="flex items-center justify-between gap-4 py-3"
              >
                <span>{item}</span>
                <span className="text-[0.7rem] font-semibold lowercase text-ink-muted">
                  {settings.notifications.status}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div id="data-privacy" className="trail-card p-5">
        <div>
          <p className="trail-eyebrow">{settings.data.eyebrow}</p>
          <p className="text-sm font-semibold text-ink">{settings.data.title}</p>
          <p className="text-xs text-ink-muted">{settings.data.subtitle}</p>
        </div>
        <div className="mt-4 grid gap-6 md:grid-cols-2 md:divide-x md:divide-border/40">
          <div className="space-y-2 md:pr-6">
            <p className="text-sm font-semibold text-ink">{settings.data.exportTitle}</p>
            <p className="text-xs text-ink-muted">{settings.data.exportDescription}</p>
            <a
              href={settings.data.exportHref}
              className="mt-3 inline-flex text-xs font-semibold text-ink"
            >
              {settings.data.exportCta}
            </a>
          </div>
          <div className="space-y-2 md:pl-6">
            <p className="text-sm font-semibold text-ink">{settings.data.deleteTitle}</p>
            <p className="text-xs text-ink-muted">{settings.data.deleteDescription}</p>
            <a
              href={settings.data.deleteHref}
              className="mt-3 inline-flex text-xs font-semibold text-ink"
            >
              {settings.data.deleteCta}
            </a>
          </div>
        </div>
        <div className="mt-4 flex flex-wrap items-center gap-2 text-xs text-ink-muted">
          <span>{settings.data.supportText}</span>
          <a href="mailto:support@gettrail.net" className="text-ink">
            {settings.data.supportCta}
          </a>
        </div>
      </div>
    </section>
  );
}
```

**Step 4: Run test to verify it passes**

Run: `pnpm -C apps/account test`

Expected: PASS

**Step 5: Commit**

```bash
git add apps/account/app/(app)/settings
git commit -m "Redesign settings page"
```

---

### Task 8: Billing Page Rewrite

**Files:**
- Modify: `apps/account/app/(app)/billing/page.tsx`
- Test: `apps/account/app/(app)/billing/__tests__/billing-page.test.tsx`

**Step 1: Write the failing test**

Create `apps/account/app/(app)/billing/__tests__/billing-page.test.tsx`:

```tsx
import React from "react";
import { render, screen } from "@testing-library/react";
import { vi } from "vitest";
import BillingPage from "../page";

vi.mock("@/src/server/account-snapshot", () => ({
  listPlans: () => [
    {
      id: "starter",
      name: "starter",
      priceMonthly: 0,
      features: ["feature one"],
      highlight: false
    },
    {
      id: "pro",
      name: "pro",
      priceMonthly: 29,
      features: ["feature two"],
      highlight: true
    }
  ]
}));

describe("BillingPage", () => {
  it("renders plan cards", () => {
    render(<BillingPage />);

    expect(screen.getByText("starter")).toBeInTheDocument();
    expect(screen.getByText("pro")).toBeInTheDocument();
  });
});
```

**Step 2: Run test to verify it fails**

Run: `pnpm -C apps/account test`

Expected: FAIL (new layout not yet present)

**Step 3: Write minimal implementation**

Update `apps/account/app/(app)/billing/page.tsx`:

```tsx
import { CheckIcon } from "@radix-ui/react-icons";
import { Badge, Button, WaitlistDialog, cn } from "@trail/ui";
import { accountCopy } from "@trail/content";
import { PageHeader } from "@/app/components/PageHeader";
import { listPlans } from "@/src/server/account-snapshot";

export default function BillingPage() {
  const { billing } = accountCopy;
  const plans = listPlans();

  return (
    <section className="space-y-10">
      <PageHeader
        eyebrow={accountCopy.nav.billing}
        title={billing.title}
        subtitle={billing.subtitle}
        meta={
          <>
            <Badge className="bg-surface-strong text-xs font-medium text-ink">
              {billing.badgeEarly}
            </Badge>
            <Badge className="bg-surface-strong text-xs font-medium text-ink">
              {billing.badgePreview}
            </Badge>
          </>
        }
        actions={
          <WaitlistDialog
            triggerLabel={billing.cta}
            title={billing.waitlistDialogTitle}
            description={billing.waitlistDialogDescription}
            source="billing"
            buttonVariant="outline"
          />
        }
      />

      <div className="grid gap-4 lg:grid-cols-3">
        {plans.map((plan) => {
          const isHighlighted = "highlight" in plan && plan.highlight;
          return (
            <div
              key={plan.id}
              className={cn(
                "flex h-full flex-col rounded-2xl border border-border/60 bg-surface/70 p-5",
                isHighlighted && "border-accent/40"
              )}
            >
              <div className="flex items-center justify-between">
                <p className="text-sm font-semibold lowercase text-ink">{plan.name}</p>
                {isHighlighted ? (
                  <Badge className="bg-cta text-xs font-semibold text-cta-fg">
                    {billing.planHighlight}
                  </Badge>
                ) : (
                  <span className="trail-pill">{billing.planCta}</span>
                )}
              </div>
              <div className="mt-3">
                <p className="text-2xl font-semibold text-ink">
                  {plan.priceMonthly === 0 ? billing.planFree : `$${plan.priceMonthly}`}
                </p>
                <p className="text-xs text-ink-muted">{billing.planPerMonth}</p>
              </div>
              <ul className="mt-4 space-y-2 text-xs text-ink-muted lowercase">
                {plan.features.map((feature) => (
                  <li key={feature} className="flex items-start gap-2">
                    <CheckIcon className="mt-0.5 h-3 w-3 text-ink" />
                    <span>{feature}</span>
                  </li>
                ))}
              </ul>
              <div className="mt-6">
                <Button size="sm" variant={isHighlighted ? "default" : "outline"}>
                  {billing.cta}
                </Button>
              </div>
            </div>
          );
        })}
      </div>

      <div className="border-t border-border/40 pt-3 text-xs text-ink-muted lowercase">
        {billing.waitlistNote}
      </div>
    </section>
  );
}
```

**Step 4: Run test to verify it passes**

Run: `pnpm -C apps/account test`

Expected: PASS

**Step 5: Commit**

```bash
git add apps/account/app/(app)/billing
git commit -m "Redesign billing page"
```

---

### Task 9: Final Verification

**Files:**
- None

**Step 1: Run tests**

Run: `pnpm -C apps/account test`

Expected: PASS

**Step 2: Run typecheck**

Run: `pnpm -C apps/account typecheck`

Expected: PASS

**Step 3: Run build**

Run: `pnpm -C apps/account build`

Expected: PASS
