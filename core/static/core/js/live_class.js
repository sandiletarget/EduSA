// Minimal panel toggle logic for live class UI.
document.addEventListener("DOMContentLoaded", function () {
  var panelButtons = document.querySelectorAll("[data-panel-toggle]");
  var panels = document.querySelectorAll(".side-panel");
  var closeButtons = document.querySelectorAll("[data-panel-close]");

  function showPanel(panelName) {
    panels.forEach(function (panel) {
      var isTarget = panel.getAttribute("data-panel") === panelName;
      panel.classList.toggle("is-hidden", !isTarget);
    });
  }

  panelButtons.forEach(function (btn) {
    btn.addEventListener("click", function () {
      var target = btn.getAttribute("data-panel-toggle");
      showPanel(target);
    });
  });

  closeButtons.forEach(function (btn) {
    btn.addEventListener("click", function () {
      panels.forEach(function (panel) {
        panel.classList.remove("is-hidden");
      });
    });
  });
});
