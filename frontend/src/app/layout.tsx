import type { Metadata } from "next";
import { ClerkProvider } from "@clerk/nextjs";
import "@/styles/globals.css";

export const metadata: Metadata = {
  title: "Agency SaaS — Reporting Platform",
  description:
    "AI-powered client reporting for agencies. Connect GA4 and Google Ads, generate branded PDF reports, and chat with your data.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <ClerkProvider>
      <html lang="en">
        <body>{children}</body>
      </html>
    </ClerkProvider>
  );
}
