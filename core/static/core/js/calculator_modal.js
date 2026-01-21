(function () {
  document.addEventListener("DOMContentLoaded", function () {
    const modal = document.querySelector("[data-calculator-modal]");
    if (!modal) return;

    const openButtons = document.querySelectorAll("[data-calculator-open]");
    const closeButtons = modal.querySelectorAll("[data-calculator-close]");

    function openModal() {
      modal.hidden = false;
    }

    function closeModal() {
      modal.hidden = true;
    }

    openButtons.forEach((btn) => btn.addEventListener("click", openModal));
    closeButtons.forEach((btn) => btn.addEventListener("click", closeModal));
  });
})();
