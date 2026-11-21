// Keep the live preview isolated from Django admin styles and navigation.
document.addEventListener("DOMContentLoaded", () => {
  const frame = document.querySelector("[data-button-preview]");
  if (!frame) return;
  const form = frame.closest("form");
  const value = name => {
    const field = form.elements.namedItem(name);
    return field?.type === "checkbox" ? field.checked : field?.value || "";
  };
  frame.addEventListener("load", () => {
    const doc = frame.contentDocument;
    const stylesheet = doc.createElement("link");
    stylesheet.rel = "stylesheet";
    stylesheet.href = frame.dataset.stylesheet;
    doc.head.append(stylesheet);
    doc.documentElement.dataset.bsTheme = "dark";
    doc.body.style.cssText = "padding:24px;margin:0;background:var(--sg-bg);";
    const button = doc.createElement("a");
    button.href = "#";
    button.addEventListener("click", event => event.preventDefault());
    const buttons = doc.createElement("div");
    buttons.className = "sg-component-buttons";
    buttons.append(button);
    doc.body.append(buttons);
    const update = () => {
      const classes = [];
      const context = value("link_context");
      if (value("link_type") === "btn") {
        classes.push("btn");
        if (context) classes.push(`btn-${value("link_outline") ? "outline-" : ""}${context}`);
        if (context === "primary" && !value("link_outline")) classes.push("btn-galaxy");
      } else if (context) classes.push(`link-${context}`);
      if (value("link_size")) classes.push(value("link_size"));
      if (value("link_block")) classes.push("d-block");
      button.className = classes.join(" ");
      const label = doc.createElement("span");
      label.textContent = value("name") || "Link / Button";
      const icon = name => {
        const element = doc.createElement("i");
        let setting = value(name);
        try { setting = JSON.parse(setting); } catch { /* Plain icon class. */ }
        element.className = typeof setting === "object" && setting !== null
          ? setting.iconClass || "" : setting;
        if (typeof setting === "object" && setting !== null) element.textContent = setting.iconText || "";
        element.setAttribute("aria-hidden", "true");
        element.classList.add(name === "icon_left" ? "me-1" : "ms-1");
        return element;
      };
      if (value("icon_left")) label.prepend(icon("icon_left"));
      if (value("icon_right")) label.append(icon("icon_right"));
      button.replaceChildren(label);
    };
    form.addEventListener("input", update);
    form.addEventListener("change", update);
    update();
  });
  frame.srcdoc = '<!doctype html><html><head><meta charset="utf-8"></head><body></body></html>';
});
