"use client";

import Link from "next/link";
import type { ReactNode } from "react";

import { useAuth } from "@/lib/auth";
import { WorkspaceSwitcher } from "@/components/workspace-switcher";

const navigationItems = [
  { href: "/", label: "Copilot" },
  { href: "/#meetings", label: "Meetings" },
  { href: "/#knowledge", label: "Knowledge" },
  { href: "/settings", label: "Settings" },
];

export function AppShell({ children }: { children: ReactNode }) {
  const { user, logout } = useAuth();

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 lg:flex">
      <header className="border-b border-slate-800 bg-slate-950/90 backdrop-blur lg:hidden">
        <div className="flex items-center justify-between gap-4 px-6 py-4">
          <Link href="/" className="font-semibold tracking-tight text-white">
            MeetBridge <span className="text-violet-400">AI</span>
          </Link>
        </div>
      </header>
      <aside className="hidden w-64 shrink-0 flex-col border-r border-slate-800 bg-slate-950 p-5 lg:flex">
        <Link href="/" className="text-lg font-semibold tracking-tight text-white">
          MeetBridge <span className="text-violet-400">AI</span>
        </Link>
        <p className="mt-1 text-xs text-slate-500">Understand. Think. Respond.</p>
        <div className="mt-8"><WorkspaceSwitcher /></div>
        <nav aria-label="Primary navigation" className="mt-8 space-y-1 text-sm">
          {navigationItems.map((item) => (
            <Link
              key={item.label}
              href={item.href}
              className="block rounded-lg px-3 py-2.5 text-slate-300 transition hover:bg-slate-800 hover:text-white focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-violet-400"
            >
              {item.label}
            </Link>
          ))}
        </nav>
        <div className="mt-auto border-t border-slate-800 pt-4">
          <p className="truncate text-sm text-slate-300">{user?.email}</p>
          <button
            type="button"
            onClick={logout}
            className="mt-3 text-sm text-slate-400 transition hover:text-white focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-violet-400"
          >
            Sign out
          </button>
        </div>
      </aside>
      <div className="min-w-0 flex-1">{children}</div>
    </div>
  );
}
