// Toggle sidebar on small screens.
document.addEventListener("DOMContentLoaded", function () {
  var toggle = document.querySelector("[data-sidebar-toggle]");
  if (!toggle) return;

  toggle.addEventListener("click", function () {
    document.body.classList.toggle("sidebar-open");
  });
});
