/* Load the 3D hero only when it can help: wide screen, WebGL, no reduced motion,
   no data saver, and only after the page is idle. Otherwise the still image stays. */
(function () {
  var hero = document.querySelector(".hero");
  if (!hero) return;
  var c = navigator.connection || {};
  var skip = window.matchMedia("(prefers-reduced-motion: reduce)").matches ||
    !window.matchMedia("(min-width: 900px)").matches ||
    c.saveData || /(^|-)2g$/.test(c.effectiveType || "");
  if (skip) { hero.classList.add("no-webgl"); return; }
  function load(src, cb) {
    var s = document.createElement("script");
    s.src = src; s.async = true; s.onload = cb;
    s.onerror = function () { hero.classList.add("no-webgl"); };
    document.head.appendChild(s);
  }
  function go() {
    load("https://cdn.jsdelivr.net/npm/three@0.160.1/build/three.min.js", function () { load("js/hero.js"); });
  }
  var idle = window.requestIdleCallback || function (f) { return setTimeout(f, 1200); };
  if (document.readyState === "complete") idle(go); else window.addEventListener("load", function () { idle(go); });
})();
