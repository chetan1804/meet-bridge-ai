import "./globals.css";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "MeetBridge AI",
  description: "Real-time AI meeting copilot",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
