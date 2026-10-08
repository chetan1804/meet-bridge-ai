"use client";

import { createContext, useContext, useEffect, useState } from "react";

export type Theme = "dark" | "light";

type ThemeContextValue = {
  theme: Theme;
  setTheme: (theme: Theme) => void;
  highContrast: boolean;
  setHighContrast: (enabled: boolean) => void;
  fontScale: number;
  setFontScale: (scale: number) => void;
};

const storageKey = "meetbridge_theme";
const contrastStorageKey = "meetbridge_high_contrast";
const fontScaleStorageKey = "meetbridge_font_scale";
const ThemeContext = createContext<ThemeContextValue | null>(null);

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  const [theme, setThemeState] = useState<Theme>("dark");
  const [highContrast, setHighContrastState] = useState(false);
  const [fontScale, setFontScaleState] = useState(100);

  useEffect(() => {
    const storedTheme = window.localStorage.getItem(storageKey);
    if (storedTheme === "light" || storedTheme === "dark") {
      setThemeState(storedTheme);
      document.documentElement.dataset.theme = storedTheme;
    }

    const storedContrast =
      window.localStorage.getItem(contrastStorageKey) === "true";
    setHighContrastState(storedContrast);
    document.documentElement.dataset.contrast = storedContrast
      ? "high"
      : "normal";

    const storedFontScale = Number(
      window.localStorage.getItem(fontScaleStorageKey),
    );
    if (storedFontScale >= 80 && storedFontScale <= 150) {
      setFontScaleState(storedFontScale);
      document.documentElement.style.fontSize = `${storedFontScale}%`;
    }
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

  const setFontScale = (scale: number) => {
    const nextScale = Math.min(150, Math.max(80, scale));
    setFontScaleState(nextScale);
    document.documentElement.style.fontSize = `${nextScale}%`;
    window.localStorage.setItem(fontScaleStorageKey, String(nextScale));
  };

  return (
    <ThemeContext.Provider
      value={{
        theme,
        setTheme,
        highContrast,
        setHighContrast,
        fontScale,
        setFontScale,
      }}
    >
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
