"use client";

import { useTheme, type Theme } from "@/lib/theme";

const themes: Theme[] = ["light", "dark"];

export function ThemeToggle() {
  const { theme, setTheme } = useTheme();

  return (
    <div aria-label="Color theme" className="inline-flex rounded-lg border border-slate-700 bg-slate-950 p-1" role="group">
      {themes.map((option) => (
        <button
          key={option}
          type="button"
          aria-pressed={theme === option}
          onClick={() => setTheme(option)}
          className={`rounded-md px-3 py-1.5 text-xs font-medium capitalize transition focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-violet-400 ${theme === option ? "bg-slate-800 text-slate-100" : "text-slate-400 hover:text-slate-100"}`}
        >
          {option}
        </button>
      ))}
    </div>
  );
}