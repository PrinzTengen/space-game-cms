(() => {
  function detectLanguage(source) {
    const text = source.trimStart();
    if (text.startsWith("{") || text.startsWith("[")) {
      try {
        JSON.parse(text);
        return "json";
      } catch {
        // An opening brace or bracket can also belong to another language.
      }
    }
    if (/^<(?:[a-z][\w:-]*(?=[\s/>])|!doctype\b|!--|\?xml\b)/i.test(text)) return "xml";
    // Multiple keyword arguments distinguish Python calls from Perl's bare function calls.
    if (/^[ \t]*(?:[a-z_]\w*\.)*[a-z_]\w*\(\s*[a-z_]\w*\s*=(?!=|>)[^,\r\n]+,\s*[a-z_]\w*\s*=(?!=|>)/im.test(text)) {
      return "python";
    }
    return undefined;
  }

  function initializeCodeBlocks() {
    const main = document.querySelector(".site-main");
    const highlighter = window.hljs;
    if (!main || !highlighter) return;

    function enhance() {
      main.querySelectorAll("pre > code").forEach((code) => {
        const pre = code.parentElement;
        if (pre.closest(".sg-code-block") || code.isContentEditable) return;

        const caption = document.createElement("figcaption");
        const figure = document.createElement("figure");
        const classes = `${code.className} ${pre.className}`;
        const requested = /(?:^|\s)lang(?:uage)?-([\w-]+)/i.exec(classes)?.[1];
        const source = code.childElementCount ? code.innerText : code.textContent;
        caption.textContent = "Code";

        if (source.trim() && !/(?:^|\s)no-?highlight(?:\s|$)/i.test(classes)) {
          const language = requested || detectLanguage(source);
          const result = language
            ? highlighter.getLanguage(language) && highlighter.highlight(source, { language })
            : highlighter.highlightAuto(source);
          if (result?.language) {
            code.innerHTML = result.value;
            caption.textContent = highlighter.getLanguage(result.language).name;
          }
        }

        figure.className = "sg-code-block";
        pre.before(figure);
        figure.append(caption, pre);
        if (!pre.hasAttribute("tabindex")) pre.tabIndex = 0;
      });
    }

    enhance();
    new MutationObserver(enhance).observe(main, { childList: true, subtree: true });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initializeCodeBlocks, { once: true });
  } else {
    initializeCodeBlocks();
  }
})();

(() => {
  function initializeNavigation() {
    const navbar = document.querySelector(".site-header .sg-navbar");
    if (!navbar) return;

    const brand = navbar.querySelector(".sg-brand");
    const toggle = navbar.querySelector(".sg-nav-toggle");
    const panel = navbar.querySelector(".sg-nav-panel");
    let desktopWidth;

    function setOpen(open) {
      navbar.toggleAttribute("data-nav-open", open);
      toggle.setAttribute("aria-expanded", String(open));
      panel.inert = navbar.hasAttribute("data-nav-mobile") && !open;
    }

    function updateLayout() {
      const styles = getComputedStyle(navbar);
      const availableWidth = navbar.getBoundingClientRect().width
        - parseFloat(styles.paddingLeft) - parseFloat(styles.paddingRight);
      const mobile = availableWidth < desktopWidth;
      if (mobile === navbar.hasAttribute("data-nav-mobile")) return;

      const focus = document.activeElement;
      navbar.toggleAttribute("data-nav-mobile", mobile);
      setOpen(false);
      if (mobile && panel.contains(focus)) toggle.focus();
      if (!mobile && focus === toggle) (panel.querySelector("a") ?? brand).focus();
    }

    function measureDesktopWidth() {
      navbar.setAttribute("data-nav-measuring", "");
      desktopWidth = brand.getBoundingClientRect().width + panel.getBoundingClientRect().width
        + parseFloat(getComputedStyle(navbar).columnGap);
      navbar.removeAttribute("data-nav-measuring");
      updateLayout();
    }

    navbar.setAttribute("data-nav-ready", "");
    measureDesktopWidth();
    new ResizeObserver(updateLayout).observe(navbar);
    document.fonts?.ready.then(measureDesktopWidth);

    toggle.addEventListener("click", () => setOpen(!navbar.hasAttribute("data-nav-open")));
    document.addEventListener("keydown", (event) => {
      if (event.key !== "Escape" || event.defaultPrevented || !navbar.hasAttribute("data-nav-open")) return;
      event.preventDefault();
      toggle.focus();
      setOpen(false);
    });
    document.addEventListener("focusin", (event) => {
      if (!navbar.contains(event.target) && navbar.hasAttribute("data-nav-open")) setOpen(false);
    });
    document.addEventListener("click", (event) => {
      if (!navbar.hasAttribute("data-nav-open")) return;
      if (panel.contains(event.target) && event.target.closest("a")) {
        toggle.focus();
        setOpen(false);
      } else if (!navbar.contains(event.target)) {
        setOpen(false);
      }
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initializeNavigation, { once: true });
  } else {
    initializeNavigation();
  }
})();

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

// Platform selection remains usable without JavaScript and during CMS editing.
(() => {
  const launchers = new Map();

  function enhance(module, panels, controls) {
    const events = new AbortController();
    const options = {signal: events.signal};
    controls.replaceChildren();
    const buttons = panels.map(panel => {
      const button = document.createElement("button");
      button.type = "button";
      button.className = "sg-platform";
      button.setAttribute("aria-controls", panel.id);
      const copy = document.createElement("span");
      const title = document.createElement("strong");
      const description = document.createElement("small");
      title.textContent = panel.dataset.launcherTitle;
      description.textContent = panel.dataset.launcherDescription;
      copy.append(title, description);
      const dot = document.createElement("span");
      dot.className = "sg-platform-dot";
      dot.setAttribute("aria-hidden", "true");
      button.append(copy, dot);
      controls.append(button);
      return button;
    });
    controls.hidden = panels.length < 2;
    module.classList.add("is-enhanced");

    function select(index, updateURL = false) {
      panels.forEach((panel, i) => {
        panel.hidden = i !== index;
        buttons[i].classList.toggle("is-active", i === index);
        buttons[i].setAttribute("aria-pressed", String(i === index));
      });
      if (updateURL) {
        const url = new URL(location.href);
        url.searchParams.set("platform", panels[index].dataset.launcherPlatform);
        history.replaceState(null, "", url);
      }
    }
    function readURL() {
      const selected = new URL(location.href).searchParams.get("platform");
      const index = panels.findIndex(panel => panel.dataset.launcherPlatform === selected);
      select(index < 0 ? 0 : index);
    }
    buttons.forEach((button, index) => button.addEventListener("click", () => select(index, true), options));
    window.addEventListener("popstate", readURL, options);
    readURL();
    return {
      panels, controls,
      destroy() {
        events.abort();
        panels.forEach(panel => { panel.hidden = false; });
        controls.replaceChildren();
        controls.hidden = true;
        module.classList.remove("is-enhanced");
      },
    };
  }

  function initialize() {
    launchers.forEach((launcher, module) => {
      if (!module.isConnected || module.hasAttribute("data-launcher-edit-mode")) {
        launcher.destroy();
        launchers.delete(module);
      }
    });
    document.querySelectorAll("[data-launcher]:not([data-launcher-edit-mode])").forEach(module => {
      const panels = [...module.querySelectorAll("[data-launcher-option]")];
      const controls = module.querySelector("[data-launcher-controls]");
      const old = launchers.get(module);
      if (old?.controls === controls && panels.length === old.panels.length
        && panels.every((panel, i) => panel === old.panels[i])) return;
      old?.destroy();
      launchers.delete(module);
      if (controls && panels.length) launchers.set(module, enhance(module, panels, controls));
    });
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", initialize, {once: true}); else initialize();
  let frame;
  new MutationObserver(() => {
    cancelAnimationFrame(frame);
    frame = requestAnimationFrame(initialize);
  }).observe(document.documentElement, {childList: true, subtree: true});
})();

// F2 Orbit effects translated from the supplied UI kit; no React or CDN runtime.
(() => {
  const enhanced = new WeakSet();
  const revealed = new WeakSet();
  const motion = matchMedia("(prefers-reduced-motion: reduce)");
  const random = (min, max) => Math.floor(Math.random() * (max - min + 1) + min);
  const make = (tag, className) => {
    const node = document.createElement(tag);
    node.className = className;
    return node;
  };
  const observer = new IntersectionObserver((entries) => entries.forEach(({target, isIntersecting}) => {
    if (!isIntersecting) return;
    observer.unobserve(target);
    if (motion.matches || document.querySelector(".cms-toolbar")) return;
    const order = [...target.parentElement.children].indexOf(target);
    target.animate([{opacity: 0, transform: "translateY(14px)"}, {opacity: 1, transform: "none"}], {
      duration: 600, delay: Math.min(order, 8) * 70, easing: "cubic-bezier(.2,.7,.2,1)",
    });
  }), {threshold: .08});
  motion.addEventListener("change", () => {
    if (motion.matches) document.getAnimations().forEach(animation => animation.cancel());
  });

  function initializeDesign() {
    document.querySelectorAll(".btn-galaxy:not(:disabled)").forEach(button => {
      if (enhanced.has(button)) return;
      enhanced.add(button);
      const fx = make("span", "sg-galaxy-fx");
      fx.setAttribute("aria-hidden", "true");
      const stars = make("span", "sg-galaxy-stars");
      for (let i = 0; i < 12; i++) {
        const star = document.createElement("i");
        const size = [1.5, 2, 2, 2.5, 3, 3.5][random(0, 5)];
        Object.assign(star.style, {left: `${random(3, 97)}%`, top: `${random(12, 88)}%`, width: `${size}px`, height: `${size}px`, animation: `sg-twinkle ${random(3, 7)}s -${random(0, 6)}s ease-in-out infinite`});
        if (size > 2.5) star.style.boxShadow = "0 0 6px 1px var(--sg-accent-hover)";
        stars.append(star);
      }
      const orbit = make("span", "sg-galaxy-orbit");
      const ring = document.createElement("span");
      for (let i = 0; i < 24; i++) {
        const star = document.createElement("i");
        const size = random(2, 4), distance = random(30, 170);
        star.style.setProperty("--d", `${distance}px`);
        star.style.setProperty("--duration", `${random(6, 20)}s`);
        star.style.setProperty("--delay", `-${random(1, 10)}s`);
        Object.assign(star.style, {width: `${size}px`, height: `${size}px`, opacity: random(60, 100) / 100, transform: `translate(-50%,-50%) rotate(10deg) translateY(${distance}px)`});
        ring.append(star);
      }
      orbit.append(ring);
      fx.append(stars, orbit);
      button.prepend(fx);
    });
    document.querySelectorAll("[data-reveal]").forEach(element => {
      if (revealed.has(element)) return;
      revealed.add(element);
      observer.observe(element);
    });
  }
  let filterController;
  const normalizeSearch = value => value.normalize("NFKD").replace(/\p{M}/gu, "").toLowerCase().replaceAll("ß", "ss");

  function initializeFilters() {
    const controls = document.querySelector("[data-post-filters]");
    const module = controls?.closest("[data-logbook]");
    const list = module?.querySelector("[data-post-list]");
    if (!controls || !list) {
      filterController?.destroy();
      filterController = null;
      return;
    }
    const cards = [...list.querySelectorAll("[data-post-kind]")];
    if (filterController?.controls === controls && filterController.list === list
      && cards.length === filterController.cards.length
      && cards.every((card, i) => card === filterController.cards[i])) return;
    filterController?.destroy();
    const events = new AbortController();
    const options = {signal: events.signal};
    const form = module.querySelector("[data-post-search-form]");
    const input = module.querySelector("[data-post-search]");
    const clear = module.querySelector("[data-post-search-clear]");
    const status = module.querySelector("[data-post-results]");
    const empty = module.querySelector("[data-post-empty]");
    const corpus = cards.map(card => normalizeSearch(card.dataset.postSearch || card.textContent));
    let kind = "all";
    let timer;
    controls.hidden = false;
    form.hidden = false;
    status.hidden = false;

    function apply(updateURL = true) {
      clearTimeout(timer);
      const terms = normalizeSearch(input.value).trim().split(/\s+/).filter(Boolean);
      const matches = cards.map((card, i) => terms.every(term => corpus[i].includes(term)));
      let count = 0;
      cards.forEach((card, i) => {
        card.hidden = !matches[i] || (kind !== "all" && card.dataset.postKind !== kind);
        if (!card.hidden) count++;
      });
      controls.querySelectorAll("[data-post-count]").forEach(node => {
        node.textContent = cards.filter((card, i) => matches[i]
          && (node.dataset.postCount === "all" || card.dataset.postKind === node.dataset.postCount)).length;
      });
      controls.querySelectorAll("button").forEach(button => button.setAttribute("aria-pressed", String(button.dataset.postFilter === kind)));
      clear.hidden = input.value.length === 0;
      empty.hidden = count !== 0;
      status.textContent = module.dataset.logbookResults.replace("{count}", count).replace("{total}", cards.length);
      if (!updateURL) return;
      const url = new URL(location.href);
      if (kind === "all") url.searchParams.delete("type"); else url.searchParams.set("type", kind);
      const query = input.value.trim();
      if (query) url.searchParams.set("q", query); else url.searchParams.delete("q");
      history.replaceState(null, "", url);
    }
    function readURL() {
      const params = new URL(location.href).searchParams;
      kind = ["news", "devlog"].includes(params.get("type")) ? params.get("type") : "all";
      input.value = params.get("q") || "";
      apply(false);
    }
    controls.addEventListener("click", event => {
      const button = event.target.closest("[data-post-filter]");
      if (button) { kind = button.dataset.postFilter; apply(); }
    }, options);
    input.addEventListener("input", () => { clearTimeout(timer); timer = setTimeout(apply, 150); }, options);
    input.addEventListener("search", () => apply(), options);
    form.addEventListener("submit", event => { event.preventDefault(); apply(); }, options);
    clear.addEventListener("click", () => { input.value = ""; apply(); input.focus(); }, options);
    module.querySelector("[data-post-reset]").addEventListener("click", () => {
      input.value = ""; kind = "all"; apply(); input.focus();
    }, options);
    window.addEventListener("popstate", readURL, options);
    filterController = {controls, list, cards, destroy() { events.abort(); clearTimeout(timer); }};
    readURL();
  }
  function start() { initializeDesign(); initializeFilters(); }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", start, {once: true}); else start();
  let frame;
  new MutationObserver(() => {
    cancelAnimationFrame(frame);
    frame = requestAnimationFrame(() => { initializeDesign(); initializeFilters(); });
  }).observe(document.documentElement, {childList: true, subtree: true});
})();

(() => {
  const galleries = new Map();
  const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
  const behavior = () => reducedMotion.matches ? "instant" : "smooth";
  const number = (value) => String(value).padStart(2, "0");

  function enhanceGallery(module, track, slides) {
    const events = new AbortController();
    const options = { signal: events.signal };
    const controls = module.querySelector("[data-gallery-controls]");
    const viewer = module.querySelector("[data-gallery-viewer]");
    const sidebar = module.querySelector("[data-gallery-sidebar]");
    const fullscreen = module.querySelector("[data-gallery-fullscreen]");
    const dialog = module.querySelector("[data-gallery-dialog]");
    const thumbnails = module.querySelector("[data-gallery-thumbnails]");
    const counter = module.querySelector("[data-gallery-count]");
    const status = module.querySelector("[data-gallery-status]");
    let current = -1;
    let scrollFrame;
    let trackWidth = track.clientWidth;
    thumbnails.replaceChildren();
    controls.hidden = slides.length < 2;
    sidebar.hidden = slides.length < 2;
    thumbnails.hidden = slides.length < 2;
    fullscreen.hidden = !slides.length;
    counter.hidden = !slides.length;
    viewer.classList.toggle("has-thumbnails", slides.length > 1);
    module.classList.add("is-ready");

    function select(index, announce = true) {
      if (current === index) return;
      current = index;
      slides.forEach((slide, i) => slide.classList.toggle("is-active", i === index));
      [...thumbnails.children].forEach((button, i) => {
        button.setAttribute("aria-current", String(i === index));
      });
      counter.textContent = `${number(index + 1)} / ${number(slides.length)}`;
      if (announce) {
        const caption = slides[index].querySelector("figcaption")?.textContent || "";
        status.textContent = `${module.dataset.gallerySlideLabel} ${index + 1} / ${slides.length}. ${caption}`;
      }
      const button = thumbnails.children[index];
      if (button) {
        thumbnails.scrollTo({
          top: thumbnails.scrollTop + button.getBoundingClientRect().top
            - thumbnails.getBoundingClientRect().top - (thumbnails.clientHeight - button.offsetHeight) / 2,
          behavior: behavior(),
        });
      }
    }

    function slideOffset(index) {
      return track.scrollLeft + slides[index].getBoundingClientRect().left
        - track.getBoundingClientRect().left - track.clientLeft;
    }

    function goTo(index) {
      if (!slides.length) return;
      index = (index + slides.length) % slides.length;
      track.scrollTo({
        left: slideOffset(index),
        behavior: behavior(),
      });
    }

    function syncFullscreen() {
      const expanded = document.fullscreenElement === viewer || dialog.open;
      viewer.classList.toggle("is-expanded", expanded);
      fullscreen.setAttribute("aria-pressed", String(expanded));
      fullscreen.setAttribute("aria-label", expanded
        ? module.dataset.galleryExitFullscreenLabel : module.dataset.galleryFullscreenLabel);
      // Expanding changes the slide width; align it before measuring the new state.
      trackWidth = track.clientWidth;
      if (current >= 0) track.scrollTo({ left: slideOffset(current), behavior: "instant" });
    }

    fullscreen.addEventListener("click", async () => {
      if (document.fullscreenElement === viewer) {
        await document.exitFullscreen();
      } else if (dialog.open) {
        dialog.close();
      } else {
        if (viewer.requestFullscreen && document.fullscreenEnabled) {
          try {
            await viewer.requestFullscreen();
            return;
          } catch {
            // A dialog also works when browser or iframe policy disallows fullscreen.
          }
        }
        dialog.append(viewer);
        dialog.showModal();
        syncFullscreen();
        fullscreen.focus({ preventScroll: true });
      }
    }, options);
    document.addEventListener("fullscreenchange", syncFullscreen, options);
    dialog.addEventListener("close", () => {
      dialog.before(viewer);
      syncFullscreen();
      fullscreen.focus({ preventScroll: true });
    }, options);

    slides.forEach((slide, i) => {
      slide.setAttribute("role", "group");
      slide.setAttribute("aria-label", `${module.dataset.gallerySlideLabel} ${i + 1} / ${slides.length}`);
      const button = document.createElement("button");
      button.type = "button";
      button.className = "gallery-thumbnail";
      button.setAttribute("aria-controls", track.id);
      const label = slide.querySelector("figcaption")?.textContent || slide.querySelector("img")?.alt || "";
      button.setAttribute("aria-label", `${module.dataset.galleryImageLabel} ${i + 1}: ${label}`);
      const photo = slide.querySelector("img");
      if (photo) {
        const preview = photo.cloneNode();
        preview.removeAttribute("class");
        preview.alt = "";
        button.append(preview);
      } else {
        button.textContent = number(i + 1);
      }
      button.addEventListener("click", () => goTo(i), options);
      thumbnails.append(button);
    });

    function nearestSlide() {
      if (!slides.length) return;
      const edge = track.getBoundingClientRect().left + track.clientLeft;
      let nearest = 0;
      let distance = Infinity;
      slides.forEach((slide, i) => {
        const offset = Math.abs(slide.getBoundingClientRect().left - edge);
        if (offset < distance) {
          nearest = i;
          distance = offset;
        }
      });
      select(nearest);
    }

    module.querySelector("[data-gallery-prev]").addEventListener("click", () => goTo(current - 1), options);
    module.querySelector("[data-gallery-next]").addEventListener("click", () => goTo(current + 1), options);
    viewer.addEventListener("keydown", (event) => {
      const destinations = { ArrowLeft: current - 1, ArrowRight: current + 1, Home: 0, End: slides.length - 1 };
      if (!(event.key in destinations) || event.altKey || event.ctrlKey || event.metaKey) return;
      event.preventDefault();
      goTo(destinations[event.key]);
    }, options);
    track.addEventListener("scroll", () => {
      cancelAnimationFrame(scrollFrame);
      scrollFrame = requestAnimationFrame(nearestSlide);
    }, { ...options, passive: true });
    const resize = new ResizeObserver(() => {
      if (track.clientWidth !== trackWidth && current >= 0) {
        trackWidth = track.clientWidth;
        // Retain the selected image when a breakpoint changes the slide width.
        track.scrollTo({
          left: slideOffset(current),
          behavior: "instant",
        });
      }
      nearestSlide();
    });
    resize.observe(track);
    if (slides.length) select(0, false);

    return {
      track, slides,
      destroy() {
        events.abort();
        if (document.fullscreenElement === viewer) document.exitFullscreen().catch(() => {});
        if (dialog.open) {
          dialog.close();
          dialog.before(viewer);
        }
        viewer.classList.remove("is-expanded", "has-thumbnails");
        fullscreen.setAttribute("aria-pressed", "false");
        fullscreen.setAttribute("aria-label", module.dataset.galleryFullscreenLabel);
        fullscreen.hidden = true;
        sidebar.hidden = true;
        counter.hidden = true;
        resize.disconnect();
        cancelAnimationFrame(scrollFrame);
        module.classList.remove("is-ready");
        controls.hidden = true;
        thumbnails.hidden = true;
        thumbnails.replaceChildren();
        status.textContent = "";
      },
    };
  }

  function initializeGalleries() {
    galleries.forEach((gallery, module) => {
      if (!module.isConnected || module.hasAttribute("data-gallery-edit-mode")) {
        gallery.destroy();
        galleries.delete(module);
      }
    });
    document.querySelectorAll("[data-gallery]").forEach((module) => {
      if (module.hasAttribute("data-gallery-edit-mode")) return;
      const track = module.querySelector("[data-gallery-track]");
      if (!track) return;
      const slides = [...track.querySelectorAll(":scope > [data-gallery-slide]")];
      const old = galleries.get(module);
      if (old?.track === track && old.slides.length === slides.length && old.slides.every((slide, i) => slide === slides[i])) return;
      old?.destroy();
      galleries.set(module, enhanceGallery(module, track, slides));
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initializeGalleries, { once: true });
  } else {
    initializeGalleries();
  }
  let refreshFrame;
  new MutationObserver(() => {
    cancelAnimationFrame(refreshFrame);
    refreshFrame = requestAnimationFrame(initializeGalleries);
  }).observe(document.documentElement, { childList: true, subtree: true });
})();
