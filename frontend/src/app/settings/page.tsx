"use client";

import { useEffect, useState } from "react";

import { AppShell } from "@/components/app-shell";
import { RequireAuth } from "@/components/require-auth";
import { apiEndpoint } from "@/lib/api";
import { useAuth } from "@/lib/auth";

type Integration = {
  key: string;
  name: string;
  description: string;
  credential_label: string;
  connected: boolean;
  credential_preview?: string | null;
};

export default function SettingsPage() {
  return (
    <RequireAuth>
      <SettingsContent />
    </RequireAuth>
  );
}

function SettingsContent() {
  const { user } = useAuth();
  const [integrations, setIntegrations] = useState<Integration[]>([]);
  const [connectingKey, setConnectingKey] = useState<string | null>(null);

  useEffect(() => {
    const token = window.localStorage.getItem("meetbridge_access_token");
    if (!token) {
      return;
    }

    void fetch(apiEndpoint("/api/integrations"), {
      headers: { Authorization: `Bearer ${token}` },
      cache: "no-store",
    })
      .then((response) => response.json())
      .then((data) => setIntegrations(data as Integration[]))
      .catch(() => setIntegrations([]));
  }, []);

  const handleConnect = async (key: string) => {
    const token = window.localStorage.getItem("meetbridge_access_token");
    if (!token) {
      return;
    }

    setConnectingKey(key);
    try {
      const response = await fetch(
        apiEndpoint(`/api/integrations/${key}/connect`),
        {
          method: "POST",
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ token: `demo-${key}-token-1234` }),
        },
      );

      if (response.ok) {
        const nextIntegration = (await response.json()) as Integration;
        setIntegrations((current) =>
          current.map((item) => (item.key === key ? nextIntegration : item)),
        );
      }
    } finally {
      setConnectingKey(null);
    }
  };

  return (
    <AppShell>
      <main className="mx-auto max-w-4xl px-6 py-10">
        <p className="text-sm uppercase tracking-[0.2em] text-violet-400">
          Account
        </p>
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
          <div className="flex items-center justify-between gap-4">
            <h2 className="text-lg font-semibold">Integrations</h2>
            <span className="rounded-full border border-violet-500/30 bg-violet-500/10 px-2 py-1 text-xs uppercase tracking-[0.2em] text-violet-200">
              secure
            </span>
          </div>
          <div className="mt-5 space-y-4">
            {integrations.length === 0 ? (
              <p className="text-sm text-slate-400">
                No integrations are configured yet.
              </p>
            ) : (
              integrations.map((integration) => (
                <div
                  key={integration.key}
                  className="rounded-xl border border-slate-800 bg-slate-950 p-4"
                >
                  <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                    <div>
                      <h3 className="text-base font-semibold text-white">
                        {integration.name}
                      </h3>
                      <p className="mt-1 text-sm text-slate-400">
                        {integration.description}
                      </p>
                    </div>
                    <button
                      type="button"
                      onClick={() => void handleConnect(integration.key)}
                      disabled={connectingKey === integration.key}
                      className="rounded-lg border border-violet-500 bg-violet-500/15 px-3 py-2 text-sm font-medium text-violet-100 transition hover:bg-violet-500/25 disabled:cursor-not-allowed disabled:opacity-60"
                    >
                      {connectingKey === integration.key
                        ? "Connecting..."
                        : integration.connected
                          ? "Reconnect"
                          : "Connect"}
                    </button>
                  </div>
                  <div className="mt-3 flex flex-wrap items-center gap-3 text-xs text-slate-300">
                    <span
                      className={`rounded-full px-2 py-1 ${integration.connected ? "bg-emerald-500/10 text-emerald-300" : "bg-slate-700 text-slate-300"}`}
                    >
                      {integration.connected ? "Connected" : "Not connected"}
                    </span>
                    <span>{integration.credential_label}</span>
                    {integration.credential_preview ? (
                      <span className="font-mono text-slate-400">
                        {integration.credential_preview}
                      </span>
                    ) : null}
                  </div>
                </div>
              ))
            )}
          </div>
        </section>
      </main>
    </AppShell>
  );
}
