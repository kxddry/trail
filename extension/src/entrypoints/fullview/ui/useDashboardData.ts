import { useState, useEffect } from 'react';
import { bootstrapSpotlight } from '../../../spotlight/rpc.js';
import type { SpotlightBootstrapData, SpotlightSearchResult } from '../../../spotlight/types.js';

type DashboardItem = {
  key: string;
  title: string;
  url: string;
  favicon?: string;
};

export type DashboardData = {
  loading: boolean;
  continueItems: DashboardItem[];
  pinnedItems: DashboardItem[];
  activeTreeName: string | null;
  activeTreeNodeCount: number;
};

function mapItem(item: SpotlightSearchResult): DashboardItem {
  switch (item.kind) {
    case 'tree':
      return { key: item.key, title: item.treeName, url: item.rootUrl, favicon: item.favicon };
    case 'node':
      return { key: item.key, title: item.title, url: item.url, favicon: item.favicon };
    case 'action':
      return { key: item.key, title: item.title, url: '' };
  }
}

function deriveDashboard(data: SpotlightBootstrapData): DashboardData {
  const continueSection = data.sections.find((s) => s.id === 'continue');
  const pinsSection = data.sections.find((s) => s.id === 'pins');

  return {
    loading: false,
    continueItems: (continueSection?.items ?? []).map(mapItem).slice(0, 4),
    pinnedItems: (pinsSection?.items ?? []).map(mapItem).slice(0, 8),
    activeTreeName: data.activeTreeName,
    activeTreeNodeCount: data.tree.nodeCount,
  };
}

const EMPTY_DASHBOARD: DashboardData = {
  loading: true,
  continueItems: [],
  pinnedItems: [],
  activeTreeName: null,
  activeTreeNodeCount: 0,
};

export function useDashboardData(): DashboardData {
  const [data, setData] = useState<DashboardData>(EMPTY_DASHBOARD);

  useEffect(() => {
    let cancelled = false;

    bootstrapSpotlight(20)
      .then((result) => {
        if (!cancelled) {
          setData(deriveDashboard(result));
        }
      })
      .catch(() => {
        if (!cancelled) {
          setData({ ...EMPTY_DASHBOARD, loading: false });
        }
      });

    return () => {
      cancelled = true;
    };
  }, []);

  return data;
}
