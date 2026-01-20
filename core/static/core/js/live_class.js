// Minimal panel toggle logic for live class UI.
document.addEventListener("DOMContentLoaded", function () {
  var panelButtons = document.querySelectorAll("[data-panel-toggle]");
  var panels = document.querySelectorAll(".side-panel[data-panel]");
  var closeButtons = document.querySelectorAll("[data-panel-close]");
  var collapseButtons = document.querySelectorAll("[data-panel-collapse]");

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

  collapseButtons.forEach(function (btn) {
    btn.addEventListener("click", function () {
      var panelName = btn.getAttribute("data-panel-collapse");
      var panel = document.querySelector(".side-panel[data-panel='" + panelName + "']");
      if (!panel) return;
      panel.classList.toggle("is-collapsed");
      btn.textContent = panel.classList.contains("is-collapsed") ? "▸" : "▾";
    });
  });
});
