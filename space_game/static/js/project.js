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
  function initializeFilters() {
    const controls = document.querySelector("[data-post-filters]");
    if (!controls) return;
    const cards = [...document.querySelectorAll("[data-post-list] [data-post-kind]")];
    controls.hidden = false;
    controls.querySelectorAll("[data-post-count]").forEach(node => {
      node.textContent = cards.filter(card => node.dataset.postCount === "all" || card.dataset.postKind === node.dataset.postCount).length;
    });
    function select(kind) {
      if (!["news", "devlog"].includes(kind)) kind = "all";
      cards.forEach(card => card.hidden = kind !== "all" && card.dataset.postKind !== kind);
      controls.querySelectorAll("button").forEach(button => button.setAttribute("aria-pressed", String(button.dataset.postFilter === kind)));
      const url = new URL(location.href);
      if (kind === "all") url.searchParams.delete("type"); else url.searchParams.set("type", kind);
      history.replaceState(null, "", url);
    }
    controls.addEventListener("click", event => {
      const button = event.target.closest("[data-post-filter]");
      if (button) select(button.dataset.postFilter);
    });
    select(new URL(location.href).searchParams.get("type"));
  }
  function start() { initializeDesign(); initializeFilters(); }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", start, {once: true}); else start();
  let frame;
  new MutationObserver(() => { cancelAnimationFrame(frame); frame = requestAnimationFrame(initializeDesign); }).observe(document.documentElement, {childList: true, subtree: true});
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
