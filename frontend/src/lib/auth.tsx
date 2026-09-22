"use client";

import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";

import { apiEndpoint } from "@/lib/api";

const tokenStorageKey = "meetbridge_access_token";

type AuthUser = {
  id: string;
  email: string;
  is_active: boolean;
};

type AuthContextValue = {
  user: AuthUser | null;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string) => Promise<void>;
  logout: () => void;
};

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const loadUser = useCallback(async (token: string) => {
    const response = await fetch(apiEndpoint("/api/auth/me"), {
      headers: { Authorization: `Bearer ${token}` },
      cache: "no-store",
    });
    if (!response.ok) {
      throw new Error("Your session is no longer valid. Please sign in again.");
    }
    return (await response.json()) as AuthUser;
  }, []);

  const establishSession = useCallback(
    async (token: string) => {
      const nextUser = await loadUser(token);
      window.localStorage.setItem(tokenStorageKey, token);
      setUser(nextUser);
    },
    [loadUser],
  );

  useEffect(() => {
    const token = window.localStorage.getItem(tokenStorageKey);
    if (!token) {
      setIsLoading(false);
      return;
    }

    void loadUser(token)
      .then(setUser)
      .catch(() => window.localStorage.removeItem(tokenStorageKey))
      .finally(() => setIsLoading(false));
  }, [loadUser]);

  const authenticate = useCallback(
    async (path: string, email: string, password: string) => {
      const response = await fetch(apiEndpoint(path), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });
      const body = (await response.json()) as { access_token?: string; detail?: string };
      if (!response.ok || !body.access_token) {
        throw new Error(body.detail ?? "We could not complete that request.");
      }
      await establishSession(body.access_token);
    },
    [establishSession],
  );

  const logout = useCallback(() => {
    window.localStorage.removeItem(tokenStorageKey);
    setUser(null);
  }, []);

  const value = useMemo(
    () => ({
      user,
      isLoading,
      login: (email: string, password: string) => authenticate("/api/auth/login", email, password),
      register: (email: string, password: string) => authenticate("/api/auth/register", email, password),
      logout,
    }),
    [authenticate, isLoading, logout, user],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within AuthProvider.");
  }
  return context;
}
