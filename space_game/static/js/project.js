(() => {
  const initialized = new WeakSet();

  function initializeCards() {
    document.querySelectorAll("[data-card-module]").forEach((module) => {
      if (initialized.has(module)) return;
      initialized.add(module);
      const cards = [...module.querySelector("[data-card-list]").children];
      const button = module.querySelector("[data-load-all-cards]");
      // Editors must be able to see and reorder every card in the structure view.
      if (module.hasAttribute("data-card-edit-mode") || cards.length <= 6) return;
      cards.slice(6).forEach((card) => { card.hidden = true; });
      button.hidden = false;
      button.addEventListener("click", () => {
        cards.forEach((card) => { card.hidden = false; });
        button.setAttribute("aria-expanded", "true");
        button.hidden = true;
        module.querySelector("[data-cards-status]").textContent = module.dataset.cardsLoadedLabel;
        cards[6].focus();
      });
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initializeCards, { once: true });
  } else {
    initializeCards();
  }
  // CMS refreshes can replace plugin markup without a full page reload.
  new MutationObserver(initializeCards).observe(document.documentElement, {
    childList: true,
    subtree: true,
  });
})();
