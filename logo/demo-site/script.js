const root = document.documentElement;

function nextTheme(current) {
  return current === "dark" ? "light" : "dark";
}

function toggleTheme() {
  const theme = root.getAttribute("data-theme") || "dark";
  root.setAttribute("data-theme", nextTheme(theme));
}

function toggleMotion() {
  const motion = root.getAttribute("data-motion") || "on";
  root.setAttribute("data-motion", motion === "on" ? "off" : "on");
}

document.addEventListener("click", (event) => {
  const target = event.target;
  if (!(target instanceof HTMLElement)) return;

  const button = target.closest("[data-action]");
  if (!(button instanceof HTMLElement)) return;

  const action = button.getAttribute("data-action");
  if (action === "toggle-theme") toggleTheme();
  if (action === "toggle-motion") toggleMotion();
});

