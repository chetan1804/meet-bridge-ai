import "./globals.css";
import type { Metadata } from "next";

import { AuthProvider } from "@/lib/auth";

export const metadata: Metadata = {
  title: {
    default: "MeetBridge AI",
    template: "%s | MeetBridge AI",
  },
  description: "Real-time AI meeting copilot",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body><AuthProvider>{children}</AuthProvider></body>
    </html>
  );
}
