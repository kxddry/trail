import { formatUrl } from '../../sidepanel/ui/shared/format.js';
import { useDashboardData } from './useDashboardData.js';
import './fullview-dashboard.css';
import type { Url } from '../../../shared/types/ids.js';

type FullviewDashboardProps = {
  onOpenSpotlight: () => void;
};

function FaviconIcon({ src }: { src?: string }) {
  return (
    <div className="fv-card-icon">
      {src ? (
        <img src={src} alt="" width={16} height={16} />
      ) : (
        <div className="fv-card-icon-placeholder" />
      )}
    </div>
  );
}

export function FullviewDashboard({ onOpenSpotlight }: FullviewDashboardProps) {
  const { loading, continueItems, pinnedItems, activeTreeName, activeTreeNodeCount } = useDashboardData();

  return (
    <div className="fv-dashboard">
      {/* Search pill */}
      <button
        type="button"
        className="fv-search-pill"
        onClick={onOpenSpotlight}
      >
        <svg className="fv-search-pill-icon" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5">
          <circle cx="7" cy="7" r="4" />
          <line x1="10" y1="10" x2="13" y2="13" />
        </svg>
        <span className="fv-search-pill-text">Search pages or type &gt; for commands</span>
        <kbd className="fv-search-pill-kbd">&#8984;K</kbd>
      </button>

      {loading ? (
        <div className="fv-dashboard-loading">Loading...</div>
      ) : (
        <div className="fv-dashboard-content">
          {/* Continue Browsing */}
          {continueItems.length > 0 && (
            <section className="fv-section">
              <h2 className="fv-section-title">Continue Browsing</h2>
              <div className="fv-cards fv-cards--horizontal">
                {continueItems.map((item) => (
                  <a
                    key={item.key}
                    href={item.url}
                    className="fv-card"
                    title={item.title}
                  >
                    <FaviconIcon src={item.favicon} />
                    <div className="fv-card-title">{item.title}</div>
                    <div className="fv-card-url">{formatUrl(item.url as Url)}</div>
                  </a>
                ))}
              </div>
            </section>
          )}

          {/* Quick Access (Pins) */}
          {pinnedItems.length > 0 && (
            <section className="fv-section">
              <h2 className="fv-section-title">Quick Access</h2>
              <div className="fv-cards fv-cards--grid">
                {pinnedItems.map((item) => (
                  <a
                    key={item.key}
                    href={item.url}
                    className="fv-card fv-card--compact"
                    title={item.title}
                  >
                    <FaviconIcon src={item.favicon} />
                    <div className="fv-card-title">{item.title}</div>
                  </a>
                ))}
              </div>
            </section>
          )}

          {/* Active Tree */}
          {activeTreeName && (
            <section className="fv-section">
              <h2 className="fv-section-title">Active Tree</h2>
              <div className="fv-tree-info">
                <span className="fv-tree-name">{activeTreeName}</span>
                <span className="fv-tree-count">{activeTreeNodeCount} pages</span>
              </div>
            </section>
          )}
        </div>
      )}
    </div>
  );
}
