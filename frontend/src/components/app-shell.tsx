"use client";

import Link from "next/link";
import type { ReactNode } from "react";

import { useAuth } from "@/lib/auth";

const navigationItems = [
  { href: "/", label: "Copilot" },
  { href: "/#meetings", label: "Meetings" },
  { href: "/#knowledge", label: "Knowledge" },
];

export function AppShell({ children }: { children: ReactNode }) {
  const { user, logout } = useAuth();

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <header className="border-b border-slate-800 bg-slate-950/90 backdrop-blur">
        <div className="mx-auto flex max-w-7xl flex-wrap items-center justify-between gap-4 px-6 py-4">
          <Link href="/" className="font-semibold tracking-tight text-white">
            MeetBridge <span className="text-violet-400">AI</span>
          </Link>
          <nav aria-label="Primary navigation" className="flex items-center gap-1 text-sm">
            {navigationItems.map((item) => (
              <Link
                key={item.label}
                href={item.href}
                className="rounded-lg px-3 py-2 text-slate-300 transition hover:bg-slate-800 hover:text-white focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-violet-400"
              >
                {item.label}
              </Link>
            ))}
            {user && (
              <button
                type="button"
                onClick={logout}
                className="ml-2 rounded-lg border border-slate-700 px-3 py-2 text-slate-300 transition hover:border-slate-500 hover:text-white focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-violet-400"
              >
                Sign out
              </button>
            )}
          </nav>
        </div>
      </header>
      {children}
    </div>
  );
}
