import { useReactFlow } from "@xyflow/react";
import { Icons } from "@ui/components/icons";
import { Button } from "@ui/components/ui/button";
import { ButtonTooltip } from "@ui/components/button-tooltip";
import type { WheelMode } from "@shared/types/settings.js";

type GraphControlsProps = {
  /**
   * Focus the current node, falling back to the last-visited node (or
   * root) when no tab is active. Disabled only when neither has landed
   * in the layout yet.
   */
  onFocusCurrentOrFallback: () => void;
  canFocus: boolean;
  /** Grab-hand pan tool — true while the tool is active. */
  panToolActive: boolean;
  onTogglePanTool: () => void;
  /** Current scroll-wheel mode (drives the cycle button's icon + label). */
  wheelMode: WheelMode;
  /**
   * Advance `wheelMode` to the next mode. Omitted by read-only hosts
   * (e.g. the public share page), which hide the toggle entirely.
   */
  onCycleWheelMode?: () => void;
};

const WHEEL_MODE_LABEL: Record<WheelMode, string> = {
  pan: "Scroll: pan",
  scroll: "Scroll: vertical",
  scrollHorizontal: "Scroll: horizontal",
  zoom: "Scroll: zoom",
};

function WheelModeIcon({ mode }: { mode: WheelMode }) {
  switch (mode) {
    case "pan":
      return <Icons.Move />;
    case "scroll":
      return <Icons.ArrowsVertical />;
    case "scrollHorizontal":
      return <Icons.ArrowsHorizontal />;
    case "zoom":
      return <Icons.ZoomIn />;
  }
}

export function GraphControls({
  onFocusCurrentOrFallback,
  canFocus,
  panToolActive,
  onTogglePanTool,
  wheelMode,
  onCycleWheelMode,
}: GraphControlsProps) {
  const { zoomIn, zoomOut } = useReactFlow();

  return (
    <div className="absolute right-3 bottom-3 z-10 flex flex-col gap-1.5">
      <ButtonTooltip label="Zoom in" side="left">
        <Button
          variant="outline"
          size="icon"
          aria-label="Zoom in"
          onClick={() => zoomIn({ duration: 200 })}
        >
          <Icons.Plus />
        </Button>
      </ButtonTooltip>
      <ButtonTooltip label="Zoom out" side="left">
        <Button
          variant="outline"
          size="icon"
          aria-label="Zoom out"
          onClick={() => zoomOut({ duration: 200 })}
        >
          <Icons.Minus />
        </Button>
      </ButtonTooltip>
      <ButtonTooltip label="Focus current node" side="left">
        <Button
          variant="outline"
          size="icon"
          aria-label="Focus current node"
          disabled={!canFocus}
          onClick={onFocusCurrentOrFallback}
        >
          <Icons.LocateFixed />
        </Button>
      </ButtonTooltip>
      <ButtonTooltip
        label={panToolActive ? "Pan tool — on (drag to move)" : "Pan tool — drag to move"}
        side="left"
      >
        <Button
          variant={panToolActive ? "secondary" : "outline"}
          size="icon"
          aria-label="Pan tool"
          aria-pressed={panToolActive}
          onClick={onTogglePanTool}
        >
          <Icons.Hand />
        </Button>
      </ButtonTooltip>
      {onCycleWheelMode && (
        <ButtonTooltip label={`${WHEEL_MODE_LABEL[wheelMode]} · click to change`} side="left">
          <Button
            variant="outline"
            size="icon"
            aria-label={WHEEL_MODE_LABEL[wheelMode]}
            onClick={onCycleWheelMode}
          >
            <WheelModeIcon mode={wheelMode} />
          </Button>
        </ButtonTooltip>
      )}
    </div>
  );
}
