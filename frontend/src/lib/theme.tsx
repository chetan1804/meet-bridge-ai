"use client";

import { createContext, useContext, useEffect, useState } from "react";

export type Theme = "dark" | "light";

type ThemeContextValue = {
  theme: Theme;
  setTheme: (theme: Theme) => void;
  highContrast: boolean;
  setHighContrast: (enabled: boolean) => void;
};

const storageKey = "meetbridge_theme";
const contrastStorageKey = "meetbridge_high_contrast";
const ThemeContext = createContext<ThemeContextValue | null>(null);

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  const [theme, setThemeState] = useState<Theme>("dark");
  const [highContrast, setHighContrastState] = useState(false);

  useEffect(() => {
    const storedTheme = window.localStorage.getItem(storageKey);
    if (storedTheme === "light" || storedTheme === "dark") {
      setThemeState(storedTheme);
      document.documentElement.dataset.theme = storedTheme;
    }

    const storedContrast = window.localStorage.getItem(contrastStorageKey) === "true";
    setHighContrastState(storedContrast);
    document.documentElement.dataset.contrast = storedContrast ? "high" : "normal";
  }, []);

  const setTheme = (nextTheme: Theme) => {
    setThemeState(nextTheme);
    document.documentElement.dataset.theme = nextTheme;
    window.localStorage.setItem(storageKey, nextTheme);
  };

  const setHighContrast = (enabled: boolean) => {
    setHighContrastState(enabled);
    document.documentElement.dataset.contrast = enabled ? "high" : "normal";
    window.localStorage.setItem(contrastStorageKey, String(enabled));
  };

  return (
    <ThemeContext.Provider value={{ theme, setTheme, highContrast, setHighContrast }}>
      {children}
    </ThemeContext.Provider>
  );
}

export function useTheme(): ThemeContextValue {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error("useTheme must be used within ThemeProvider.");
  }
  return context;
}
