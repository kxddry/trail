import { toast } from "sonner";
import { i18n } from "#i18n";
import { createNewTree } from "../../api/tree.js";
import { showOperationError } from "./show-operation-error.js";

let creating = false;

/**
 * Create a fresh tree and switch to it, from anywhere in the side panel.
 *
 * The underlying RPC stashes the current tree (no data loss) and swaps the
 * active one, so the success toast reassures the user their previous tree
 * was saved, not discarded. The new tree starts unnamed (renameable via
 * F2 / double-click), so every quick entry point — toolbar button,
 * Shift+N, command palette, the toolbar icon's right-click menu — is a
 * single action with no dialog.
 *
 * A module-level in-flight guard makes concurrent triggers (holding
 * Shift+N, a double-click, button + shortcut at once) a no-op so they
 * can't create two trees back to back.
 */
export async function createTree(): Promise<void> {
  if (creating) return;
  creating = true;
  try {
    await createNewTree(i18n.t("sidepanel.treesDropdown.unnamedTree"));
    toast.success(i18n.t("trees.toast.created"));
  } catch (error) {
    showOperationError(i18n.t("sidepanel.operations.createTree"), error);
  } finally {
    creating = false;
  }
}
