import type { ReactNode } from "react";
import Image from "next/image";
import {
  Grid3X3,
  Search,
  Share2,
  Sparkles,
  Timer
} from "lucide-react";
import { marketingCopy } from "@trail/content";
import { BentoCard, BentoGrid } from "../ui/bento-grid";

const iconMap = {
  capture: Timer,
  views: Grid3X3,
  search: Search,
  share: Share2,
  polish: Sparkles
};

const backgrounds: Record<string, ReactNode> = {
  capture: (
    <>
      <Image
        className="absolute inset-0 object-cover opacity-40"
        src="https://images.unsplash.com/photo-1498050108023-c5249f4df085?auto=format&fit=crop&w=900&q=80"
        alt=""
        aria-hidden="true"
        fill
        sizes="(min-width: 1024px) 420px, 100vw"
      />
    </>
  ),
  views: (
    <>
      <Image
        className="absolute inset-0 object-cover opacity-35"
        src="https://images.unsplash.com/photo-1523475472560-d2df97ec485c?auto=format&fit=crop&w=900&q=80"
        alt=""
        aria-hidden="true"
        fill
        sizes="(min-width: 1024px) 420px, 100vw"
      />
    </>
  ),
  search: (
    <>
      <Image
        className="absolute inset-0 object-cover opacity-35"
        src="https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?auto=format&fit=crop&w=900&q=80"
        alt=""
        aria-hidden="true"
        fill
        sizes="(min-width: 1024px) 420px, 100vw"
      />
    </>
  ),
  share: (
    <>
      <Image
        className="absolute inset-0 object-cover opacity-35"
        src="https://images.unsplash.com/photo-1521737604893-d14cc237f11d?auto=format&fit=crop&w=900&q=80"
        alt=""
        aria-hidden="true"
        fill
        sizes="(min-width: 1024px) 420px, 100vw"
      />
    </>
  ),
  polish: (
    <>
      <Image
        className="absolute inset-0 object-cover opacity-35"
        src="https://images.unsplash.com/photo-1517245386807-bb43f82c33c4?auto=format&fit=crop&w=900&q=80"
        alt=""
        aria-hidden="true"
        fill
        sizes="(min-width: 1024px) 420px, 100vw"
      />
    </>
  )
};

export function BentoFeatures() {
  const { features } = marketingCopy;

  return (
    <section id="features" className="px-6 py-20">
      <div className="mx-auto max-w-6xl">
        <div className="flex flex-col gap-4">
          <span className="trail-eyebrow">{features.eyebrow}</span>
          <p className="trail-copy max-w-2xl">{features.summary}</p>
        </div>

        <div className="mt-10">
          <BentoGrid className="lg:grid-rows-3">
            {features.items.map((feature) => {
              const Icon =
                iconMap[feature.id as keyof typeof iconMap] || Sparkles;
              const { id, ...card } = feature;
              const background = backgrounds[id] ?? backgrounds.capture;
              return (
                <BentoCard
                  key={feature.name}
                  {...card}
                  Icon={Icon}
                  background={background}
                />
              );
            })}
          </BentoGrid>
        </div>
      </div>
    </section>
  );
}
