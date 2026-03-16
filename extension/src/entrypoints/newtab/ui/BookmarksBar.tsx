import { useCallback, useEffect, useRef, useState } from 'react';
import { Folder, Globe } from 'lucide-react';
import { getFaviconUrl } from '@shared/utils/favicon.js';
import type { Url } from '@shared/types/ids.js';
import type { BookmarkItem } from './useBookmarks.js';

// ---------------------------------------------------------------------------
// Sub-components
// ---------------------------------------------------------------------------

function BookmarkFavicon({ url }: { url: string }) {
  const [failed, setFailed] = useState(false);

  if (failed) {
    return <Globe size={20} className="newtab-bookmark-icon" />;
  }

  return (
    <img
      src={getFaviconUrl(url as Url, 20)}
      alt=""
      width={20}
      height={20}
      className="newtab-bookmark-favicon"
      onError={() => setFailed(true)}
    />
  );
}

function BookmarkLink({ item }: { item: BookmarkItem }) {
  return (
    <a href={item.url!} className="newtab-bookmark-item" title={item.title}>
      <BookmarkFavicon url={item.url!} />
      <span className="newtab-bookmark-title">{item.title}</span>
    </a>
  );
}

function DropdownItem({ item }: { item: BookmarkItem }) {
  if (item.children) {
    return <NestedFolder folder={item} />;
  }

  return (
    <a href={item.url!} className="newtab-bookmark-dropdown-item" title={item.title}>
      <BookmarkFavicon url={item.url!} />
      <span className="newtab-bookmark-dropdown-title">{item.title}</span>
    </a>
  );
}

function NestedFolder({ folder }: { folder: BookmarkItem }) {
  const children = folder.children ?? [];

  return (
    <>
      <div className="newtab-bookmark-dropdown-folder-label">
        <Folder size={12} />
        {folder.title}
      </div>
      {children.length === 0 ? (
        <div className="newtab-bookmark-dropdown-empty">Empty</div>
      ) : (
        children.map((child) => <DropdownItem key={child.id} item={child} />)
      )}
    </>
  );
}

function BookmarkFolder({ item }: { item: BookmarkItem }) {
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLButtonElement>(null);

  const toggle = useCallback(() => setOpen((prev) => !prev), []);

  // Close on click outside
  useEffect(() => {
    if (!open) return;
    const handler = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) {
        setOpen(false);
      }
    };
    document.addEventListener('mousedown', handler, true);
    return () => document.removeEventListener('mousedown', handler, true);
  }, [open]);

  const children = item.children ?? [];

  return (
    <button
      ref={ref}
      type="button"
      className="newtab-bookmark-item newtab-bookmark-folder"
      onClick={toggle}
      title={item.title}
    >
      <Folder size={20} className="newtab-bookmark-icon" />
      <span className="newtab-bookmark-title">{item.title}</span>

      {open && (
        <div className="newtab-bookmark-dropdown">
          {children.length === 0 ? (
            <div className="newtab-bookmark-dropdown-empty">Empty folder</div>
          ) : (
            children.map((child) => <DropdownItem key={child.id} item={child} />)
          )}
        </div>
      )}
    </button>
  );
}

// ---------------------------------------------------------------------------
// Main component
// ---------------------------------------------------------------------------

type BookmarksBarProps = {
  readonly bookmarks: readonly BookmarkItem[];
};

export function BookmarksBar({ bookmarks }: BookmarksBarProps) {
  if (bookmarks.length === 0) return null;

  return (
    <div className="newtab-bookmarks">
      {bookmarks.map((item) =>
        item.url ? (
          <BookmarkLink key={item.id} item={item} />
        ) : (
          <BookmarkFolder key={item.id} item={item} />
        ),
      )}
    </div>
  );
}
