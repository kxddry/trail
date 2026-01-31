import type { Metadata } from "next";

import { marketingCopy } from "@trail/content";
import { BackgroundArt } from "@trail/ui";

import { MarketingFooter } from "../components/MarketingFooter";
import { MarketingNav } from "../components/MarketingNav";
import { SupportFlow } from "./SupportFlow";

export const metadata: Metadata = {
  title: marketingCopy.support.meta.title,
  description: marketingCopy.support.meta.description,
};

export default function SupportPage() {
  return (
    <div className="min-h-screen bg-base text-ink">
      <MarketingNav />
      <main className="relative overflow-hidden">
        <BackgroundArt variant="signal" />
        <SupportFlow />
      </main>
      <MarketingFooter />
    </div>
  );
}
