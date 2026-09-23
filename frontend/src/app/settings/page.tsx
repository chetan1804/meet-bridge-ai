"use client";

import { AppShell } from "@/components/app-shell";
import { RequireAuth } from "@/components/require-auth";
import { useAuth } from "@/lib/auth";

export default function SettingsPage() {
  return (
    <RequireAuth>
      <SettingsContent />
    </RequireAuth>
  );
}

function SettingsContent() {
  const { user } = useAuth();

  return (
    <AppShell>
      <main className="mx-auto max-w-4xl px-6 py-10">
        <p className="text-sm uppercase tracking-[0.2em] text-violet-400">Account</p>
        <h1 className="mt-2 text-3xl font-semibold">Settings</h1>
        <section className="mt-8 rounded-2xl border border-slate-800 bg-slate-900 p-6">
          <h2 className="text-lg font-semibold">Profile</h2>
          <dl className="mt-5 space-y-4 text-sm">
            <div className="flex flex-wrap justify-between gap-2 border-b border-slate-800 pb-4">
              <dt className="text-slate-400">Email address</dt>
              <dd>{user?.email}</dd>
            </div>
            <div className="flex flex-wrap justify-between gap-2">
              <dt className="text-slate-400">Account status</dt>
              <dd className="text-emerald-300">Active</dd>
            </div>
          </dl>
        </section>
        <section className="mt-6 rounded-2xl border border-slate-800 bg-slate-900 p-6">
          <h2 className="text-lg font-semibold">Workspace and privacy</h2>
          <p className="mt-2 text-sm leading-6 text-slate-400">
            Workspace management, recording consent, and AI preferences will be added as their related features are introduced.
          </p>
        </section>
      </main>
    </AppShell>
  );
}
