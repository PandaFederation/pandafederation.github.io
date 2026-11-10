(function () {
  var bar = document.querySelector("[data-filter]");
  if (!bar) return;
  var cards = document.querySelectorAll("[data-family]");
  bar.addEventListener("click", function (e) {
    var btn = e.target.closest("button[data-value]");
    if (!btn) return;
    bar.querySelectorAll("button").forEach(function (b) {
      b.setAttribute("aria-pressed", b === btn ? "true" : "false");
    });
    var val = btn.getAttribute("data-value");
    cards.forEach(function (card) {
      var show = val === "all" || card.getAttribute("data-family") === val;
      card.hidden = !show;
    });
  });
})();
