"use client";

import { useEffect, useState } from "react";

import { apiEndpoint } from "@/lib/api";
import { useAuth } from "@/lib/auth";

type Workspace = {
  id: string;
  name: string;
  is_personal: boolean;
  role: "OWNER" | "ADMIN" | "MEMBER";
};

const workspaceStorageKey = "meetbridge_workspace_id";

export function WorkspaceSwitcher() {
  const { user } = useAuth();
  const [workspaces, setWorkspaces] = useState<Workspace[]>([]);
  const [selectedWorkspaceId, setSelectedWorkspaceId] = useState("");

  useEffect(() => {
    const token = window.localStorage.getItem("meetbridge_access_token");
    if (!token || !user) {
      return;
    }

    void fetch(apiEndpoint("/api/organizations"), {
      headers: { Authorization: `Bearer ${token}` },
      cache: "no-store",
    })
      .then(async (response) => (response.ok ? ((await response.json()) as Workspace[]) : []))
      .then((nextWorkspaces) => {
        setWorkspaces(nextWorkspaces);
        const savedWorkspaceId = window.localStorage.getItem(workspaceStorageKey);
        const selected = nextWorkspaces.find((workspace) => workspace.id === savedWorkspaceId)
          ?? nextWorkspaces[0];
        if (selected) {
          setSelectedWorkspaceId(selected.id);
          window.localStorage.setItem(workspaceStorageKey, selected.id);
        }
      })
      .catch(() => setWorkspaces([]));
  }, [user]);

  if (!workspaces.length) {
    return <p className="text-xs text-slate-500">Loading workspaces…</p>;
  }

  return (
    <label className="block text-xs font-medium uppercase tracking-[0.16em] text-slate-500">
      Workspace
      <select
        aria-label="Current workspace"
        value={selectedWorkspaceId}
        onChange={(event) => {
          setSelectedWorkspaceId(event.target.value);
          window.localStorage.setItem(workspaceStorageKey, event.target.value);
        }}
        className="mt-2 w-full rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 text-sm normal-case tracking-normal text-slate-100 outline-none focus:border-violet-400 focus:ring-2 focus:ring-violet-400/30"
      >
        {workspaces.map((workspace) => (
          <option key={workspace.id} value={workspace.id}>
            {workspace.name} · {workspace.role.toLowerCase()}
          </option>
        ))}
      </select>
    </label>
  );
}
