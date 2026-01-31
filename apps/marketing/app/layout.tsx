import type { Metadata } from "next";
import { Plus_Jakarta_Sans } from "next/font/google";
import "./globals.css";
import { marketingCopy } from "@trail/content";
import { RevealObserver } from "./components/RevealObserver";
import { VideoObserver } from "./components/VideoObserver";

const jakarta = Plus_Jakarta_Sans({
  subsets: ["latin"],
  display: "swap",
  variable: "--font-sans",
  weight: ["300", "400", "500", "600", "700"]
});

export const metadata: Metadata = {
  title: marketingCopy.meta.title,
  description: marketingCopy.meta.description,
  icons: {
    icon: [
      { url: "/assets/brand/trail-fork-light.svg", media: "(prefers-color-scheme: light)" },
      { url: "/assets/brand/trail-fork-dark.svg", media: "(prefers-color-scheme: dark)" }
    ]
  }
};

export default function RootLayout({
  children
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" data-theme="system" data-reveal-ready="true" className={jakarta.variable}>
      <body className="bg-bg text-ink">
        {children}
        <RevealObserver />
        <VideoObserver />
      </body>
    </html>
  );
}
