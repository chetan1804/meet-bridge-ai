"use client";

import Link from "next/link";
import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";

import { useAuth } from "@/lib/auth";

type AuthFormProps = {
  mode: "login" | "register";
};

export function AuthForm({ mode }: AuthFormProps) {
  const isRegistration = mode === "register";
  const { login, register } = useAuth();
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setIsSubmitting(true);
    try {
      await (isRegistration ? register(email, password) : login(email, password));
      router.replace("/");
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Unable to continue.");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <main className="grid min-h-screen place-items-center bg-slate-950 px-6 py-12 text-slate-100">
      <section className="w-full max-w-md rounded-2xl border border-slate-800 bg-slate-900 p-7 shadow-xl shadow-slate-950/30">
        <Link href="/" className="text-sm font-semibold tracking-tight text-white">
          MeetBridge <span className="text-violet-400">AI</span>
        </Link>
        <h1 className="mt-6 text-2xl font-semibold">{isRegistration ? "Create your account" : "Welcome back"}</h1>
        <p className="mt-2 text-sm text-slate-400">
          {isRegistration ? "Start using your meeting copilot." : "Sign in to continue to your meeting copilot."}
        </p>

        <form className="mt-6 space-y-4" onSubmit={handleSubmit}>
          <div>
            <label className="text-sm font-medium" htmlFor="email">Email address</label>
            <input
              id="email"
              type="email"
              autoComplete="email"
              required
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              className="mt-2 w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2.5 outline-none transition focus:border-violet-400 focus:ring-2 focus:ring-violet-400/30"
            />
          </div>
          <div>
            <label className="text-sm font-medium" htmlFor="password">Password</label>
            <input
              id="password"
              type="password"
              autoComplete={isRegistration ? "new-password" : "current-password"}
              minLength={12}
              required
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              className="mt-2 w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2.5 outline-none transition focus:border-violet-400 focus:ring-2 focus:ring-violet-400/30"
            />
            {isRegistration && <p className="mt-1.5 text-xs text-slate-400">Use at least 12 characters.</p>}
          </div>
          {error && <p role="alert" className="rounded-lg bg-rose-500/10 p-3 text-sm text-rose-200">{error}</p>}
          <button
            type="submit"
            disabled={isSubmitting}
            className="w-full rounded-lg bg-violet-600 px-4 py-2.5 font-medium text-white transition hover:bg-violet-500 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {isSubmitting ? "Please wait…" : isRegistration ? "Create account" : "Sign in"}
          </button>
        </form>

        <p className="mt-6 text-center text-sm text-slate-400">
          {isRegistration ? "Already have an account?" : "New to MeetBridge?"} {" "}
          <Link href={isRegistration ? "/login" : "/register"} className="text-violet-300 hover:text-violet-200">
            {isRegistration ? "Sign in" : "Create an account"}
          </Link>
        </p>
      </section>
    </main>
  );
}
