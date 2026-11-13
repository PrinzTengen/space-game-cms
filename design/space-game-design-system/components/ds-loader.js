// Lädt die Komponenten: zuerst das generierte Bundle (_ds_bundle.js), sonst direkt aus den .jsx-Dateien (Babel im Browser).
(function () {
  var FILES = ["actions/IconButton","actions/Button","surfaces/Window","surfaces/MediaFrame","surfaces/ImagePanel","navigation/Brand","navigation/Navbar","navigation/Segment","navigation/Footer","content/Eyebrow","content/SectionHeader","content/Tag","content/PostCard","content/FeatureCard","content/Accordion","content/SpecList","content/DataTable","content/UserChip","forms/RadioCard","feedback/StatusDot","feedback/Spinner","feedback/Notice","feedback/Stepper"];
  function find() {
    for (var k of Object.keys(window)) { try { var v = window[k]; if (v && typeof v === 'object' && v.Button && v.Window) return v; } catch (e) {} }
    return null;
  }
  window.getSpaceGameDS = async function (base) {
    var ns = find(); if (ns) return ns;
    await new Promise(function (res) { var s = document.createElement('script'); s.src = base + '_ds_bundle.js'; s.onload = res; s.onerror = function () { s.remove(); res(); }; document.head.appendChild(s); });
    ns = find(); if (ns) return ns;
    var lib = {}, code = '';
    for (var f of FILES) {
      var src = await (await fetch(base + 'components/' + f + '.jsx')).text();
      var names = Array.from(src.matchAll(/^export function (\w+)/gm)).map(function (m) { return m[1]; });
      src = src.replace(/^import .*$/gm, '').replace(/^export /gm, '');
      code += 'with(__lib){(function(){' + src + '\nObject.assign(__lib,{' + names.join(',') + '});})();}\n';
    }
    var out = Babel.transform(code, { presets: ['react'], sourceType: 'script' }).code;
    new Function('React', '__lib', out)(React, lib);
    window.SpaceGameDS = lib;
    return lib;
  };
})();
