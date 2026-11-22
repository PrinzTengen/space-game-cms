document.addEventListener("input", (event) => {
  const textarea = event.target;
  if (!textarea.matches("textarea[data-contributor-counter]")) return;
  const counter = document.getElementById(textarea.dataset.contributorCounter);
  counter.querySelector("[data-contributor-length]").textContent = Array.from(textarea.value).length;
});
