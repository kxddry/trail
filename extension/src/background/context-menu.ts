import { i18n } from "#i18n";
import { createLogger } from "@shared/lib/logger.js";
import { openSidebarForTab } from "@shared/platform/webext.js";
import { createNewTreeWithLabel } from "./messaging/handlers/tree-lifecycle-handlers.js";

const log = createLogger("context-menu");
const NEW_TREE_MENU_ID = "trail-new-tree";

/**
 * Right-click "New tree" on the toolbar icon.
 *
 * The icon's left-click is already reserved — Chrome opens the side panel
 * via `openPanelOnActionClick`, Firefox toggles the sidebar — so a
 * context-menu item is the non-disruptive way to make a tree straight from
 * the toolbar. Mirrors the in-panel entry points: creates an unnamed tree
 * (renameable via F2 / double-click) and surfaces it by opening the panel.
 */
export function initContextMenu(): void {
  if (!chrome.contextMenus?.create) return;

  // contextMenus.create must run on install/update and throws on a
  // duplicate id across SW restarts — removeAll() first to stay idempotent.
  chrome.runtime.onInstalled.addListener(() => {
    chrome.contextMenus.removeAll(() => {
      // Reading lastError clears the "nothing to remove" warning noise.
      void chrome.runtime.lastError;
      chrome.contextMenus.create({
        id: NEW_TREE_MENU_ID,
        title: i18n.t("trees.newTree"),
        // Chrome MV3 uses the "action" context; Firefox uses "browser_action".
        contexts: [import.meta.env.FIREFOX ? "browser_action" : "action"],
      });
    });
  });

  // Registered synchronously at SW startup so a cold-start click wakes the
  // worker and reaches this handler.
  chrome.contextMenus.onClicked.addListener((info, tab) => {
    if (info.menuItemId !== NEW_TREE_MENU_ID) return;
    void handleNewTreeClick(tab?.id);
  });
}

async function handleNewTreeClick(tabId: number | undefined): Promise<void> {
  try {
    await createNewTreeWithLabel(i18n.t("sidepanel.treesDropdown.unnamedTree"));
    if (tabId != null) {
      await openSidebarForTab(tabId);
    }
  } catch (error) {
    log.warn("New tree from toolbar menu failed", {
      error: error instanceof Error ? error.message : String(error),
    });
  }
}
