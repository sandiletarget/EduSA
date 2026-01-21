(function () {
  function renderFormulas(panel, formulas) {
    const list = panel.querySelector("[data-formula-list]");
    if (!list) return;
    if (!formulas.length) {
      list.innerHTML = '<p class="formula-empty">No formulas available for this selection.</p>';
      return;
    }

    const isReadOnly = panel.dataset.readonly === "true";

    list.innerHTML = formulas
      .map((formula) => {
        const highlightButton = isReadOnly
          ? ""
          : '<button type="button" class="formula-btn" data-highlight>Highlight</button>';
        return `
          <div class="formula-item" data-formula-item>
            <p class="formula-topic">${formula.topic}</p>
            <p class="formula-text">${formula.formula_text}</p>
            <p class="formula-explanation">${formula.explanation || ""}</p>
            <div class="formula-actions">
              <button type="button" class="formula-btn" data-insert>Insert</button>
              <button type="button" class="formula-btn" data-copy>Copy</button>
              ${highlightButton}
            </div>
          </div>
        `;
      })
      .join("");

    list.querySelectorAll("[data-insert]").forEach((btn, index) => {
      btn.addEventListener("click", function () {
        const formulaText = formulas[index].formula_text;
        insertFormula(panel, formulaText);
      });
    });

    list.querySelectorAll("[data-copy]").forEach((btn, index) => {
      btn.addEventListener("click", function () {
        navigator.clipboard?.writeText(formulas[index].formula_text);
      });
    });

    list.querySelectorAll("[data-highlight]").forEach((btn) => {
      btn.addEventListener("click", function () {
        const card = btn.closest("[data-formula-item]");
        card?.classList.toggle("is-highlighted");
      });
    });
  }

  function insertFormula(panel, text) {
    const targetId = panel.dataset.targetCalculator;
    if (!targetId || !window.EduCalculatorRegistry) return;
    const calc = window.EduCalculatorRegistry[targetId];
    if (!calc) return;
    calc.insertText(text);
  }

  function loadFormulas(panel) {
    const apiUrl = panel.dataset.apiUrl;
    const gradeSelect = panel.querySelector("[data-formula-grade]");
    const subjectSelect = panel.querySelector("[data-formula-subject]");

    if (!apiUrl || !gradeSelect || !subjectSelect) return;

    const grade = gradeSelect.value;
    const subject = subjectSelect.value;

    fetch(`${apiUrl}?grade=${grade}&subject=${subject}`)
      .then((response) => response.json())
      .then((data) => renderFormulas(panel, data.formulas || []))
      .catch(() => {
        const list = panel.querySelector("[data-formula-list]");
        if (list) list.innerHTML = '<p class="formula-empty">Unable to load formulas.</p>';
      });
  }

  function setupPanel(panel) {
    const gradeSelect = panel.querySelector("[data-formula-grade]");
    const subjectSelect = panel.querySelector("[data-formula-subject]");
    const copyAll = panel.querySelector(".formula-copy-all");

    if (gradeSelect && panel.dataset.defaultGrade) {
      gradeSelect.value = panel.dataset.defaultGrade;
    }
    if (subjectSelect && panel.dataset.defaultSubject) {
      subjectSelect.value = panel.dataset.defaultSubject;
    }

    gradeSelect?.addEventListener("change", () => loadFormulas(panel));
    subjectSelect?.addEventListener("change", () => loadFormulas(panel));
    copyAll?.addEventListener("click", () => {
      const formulas = panel.querySelectorAll(".formula-text");
      const text = Array.from(formulas)
        .map((node) => node.textContent.trim())
        .filter(Boolean)
        .join("\n");
      navigator.clipboard?.writeText(text);
    });

    loadFormulas(panel);
  }

  document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll("[data-formula-panel]").forEach(setupPanel);
  });
})();
