// Start with the Space Game dark palette; keep the user's later theme choice.
try {
  if (!localStorage.getItem("theme")) localStorage.setItem("theme", "dark");
} catch {
  // Django's stylesheet still follows the browser's preferred color scheme.
}
