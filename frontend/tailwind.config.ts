import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      colors: {
        brand: {
          DEFAULT: "#5b5df6",
          dark: "#2f316f",
        },
      },
    },
  },
  plugins: [],
};

export default config;
