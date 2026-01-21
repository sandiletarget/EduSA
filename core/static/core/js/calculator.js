(function () {
  if (!window.EduCalculatorRegistry) {
    window.EduCalculatorRegistry = {};
  }

  function isOperator(char) {
    return ["+", "-", "*", "/", "^"].includes(char);
  }

  function formatResult(value) {
    if (typeof value !== "number" || !isFinite(value)) {
      return "Math Error";
    }
    const rounded = Math.round(value * 1e10) / 1e10;
    return String(rounded);
  }

  function factorial(n) {
    if (n < 0 || !Number.isFinite(n)) return NaN;
    if (Math.floor(n) !== n) return NaN;
    let result = 1;
    for (let i = 2; i <= n; i += 1) result *= i;
    return result;
  }

  function replaceFactorials(expr) {
    let pattern = /([0-9.]+|\([^()]+\))!/;
    while (pattern.test(expr)) {
      expr = expr.replace(pattern, "fact($1)");
    }
    return expr;
  }

  function transformExpression(expr) {
    let result = expr;
    result = result.replace(/×/g, "*").replace(/÷/g, "/");
    result = result.replace(/\^/g, "**");
    result = result.replace(/\bpi\b/g, "pi");
    result = result.replace(/\be\b/g, "E_CONST");
    result = result.replace(/sin\(/g, "sind(");
    result = result.replace(/cos\(/g, "cosd(");
    result = result.replace(/tan\(/g, "tand(");
    result = result.replace(/asin\(/g, "asind(");
    result = result.replace(/acos\(/g, "acosd(");
    result = result.replace(/atan\(/g, "atand(");
    result = result.replace(/log\(/g, "log10(");
    result = result.replace(/ln\(/g, "ln(");
    result = replaceFactorials(result);
    return result;
  }

  function evaluateExpression(expr) {
    const transformed = transformExpression(expr);
    const fn = new Function(
      "sind",
      "cosd",
      "tand",
      "asind",
      "acosd",
      "atand",
      "log10",
      "ln",
      "sqrt",
      "fact",
      "pi",
      "E_CONST",
      `return (${transformed});`
    );

    return fn(
      (x) => Math.sin((x * Math.PI) / 180),
      (x) => Math.cos((x * Math.PI) / 180),
      (x) => Math.tan((x * Math.PI) / 180),
      (x) => (Math.asin(x) * 180) / Math.PI,
      (x) => (Math.acos(x) * 180) / Math.PI,
      (x) => (Math.atan(x) * 180) / Math.PI,
      (x) => Math.log10(x),
      (x) => Math.log(x),
      (x) => Math.sqrt(x),
      factorial,
      Math.PI,
      Math.E
    );
  }

  function setupCalculator(root) {
    const display = root.querySelector("[data-calc-display]");
    const memoryIndicator = root.querySelector("[data-memory-indicator]");
    const id = root.getAttribute("data-calculator-id");
    let expression = "";
    let memory = 0;

    function updateDisplay(value) {
      display.value = value || "0";
    }

    function setMemoryIndicator() {
      if (!memoryIndicator) return;
      memoryIndicator.hidden = memory === 0;
    }

    function insert(value) {
      if (display.value === "Math Error" || display.value === "Syntax Error") {
        expression = "";
      }

      if (!expression && value === "-" && display.value === "0") {
        expression = "-";
        updateDisplay(expression);
        return;
      }

      if (expression === "0" && /[0-9]/.test(value)) {
        expression = value;
      } else {
        expression += value;
      }
      updateDisplay(expression);
    }

    function clearAll() {
      expression = "";
      updateDisplay("0");
    }

    function backspace() {
      expression = expression.slice(0, -1);
      updateDisplay(expression || "0");
    }

    function toggleSign() {
      if (!expression) return;
      expression = expression.startsWith("-") ? expression.slice(1) : `-${expression}`;
      updateDisplay(expression);
    }

    function evaluate() {
      if (!expression) return;
      try {
        const result = evaluateExpression(expression);
        if (!isFinite(result)) {
          updateDisplay("Math Error");
          expression = "";
          return;
        }
        const formatted = formatResult(result);
        updateDisplay(formatted);
        expression = formatted;
      } catch (error) {
        updateDisplay("Syntax Error");
        expression = "";
      }
    }

    root.addEventListener("click", function (event) {
      const target = event.target.closest("button");
      if (!target) return;

      if (target.dataset.insert) {
        insert(target.dataset.insert);
        return;
      }

      if (target.dataset.action) {
        const action = target.dataset.action;
        if (action === "clear") clearAll();
        if (action === "delete") backspace();
        if (action === "evaluate") evaluate();
        if (action === "percent") insert("/100");
        if (action === "toggle-sign") toggleSign();
        if (action === "mc") memory = 0;
        if (action === "mr") insert(String(memory));
        if (action === "mplus") memory += Number(display.value || 0);
        if (action === "mminus") memory -= Number(display.value || 0);
        setMemoryIndicator();
      }
    });

    root.addEventListener("click", function () {
      window.EduCalculatorRegistry.activeId = id;
    });

    window.EduCalculatorRegistry[id] = {
      insertText: insert,
      setValue: (value) => {
        expression = String(value || "");
        updateDisplay(expression || "0");
      },
    };

    setMemoryIndicator();
  }

  document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll("[data-calculator]").forEach(setupCalculator);

    document.addEventListener("keydown", function (event) {
      const activeId = window.EduCalculatorRegistry.activeId;
      if (!activeId || !window.EduCalculatorRegistry[activeId]) return;
      const calc = window.EduCalculatorRegistry[activeId];

      if (/^[0-9]$/.test(event.key)) {
        calc.insertText(event.key);
      } else if (["+", "-", "*", "/", "^", "(", ")", "."].includes(event.key)) {
        calc.insertText(event.key);
      } else if (event.key === "Enter") {
        event.preventDefault();
        const root = document.querySelector(`[data-calculator-id='${activeId}']`);
        if (root) {
          root.querySelector("[data-action='evaluate']")?.click();
        }
      } else if (event.key === "Backspace") {
        const root = document.querySelector(`[data-calculator-id='${activeId}']`);
        root?.querySelector("[data-action='delete']")?.click();
      } else if (event.key === "Escape") {
        const root = document.querySelector(`[data-calculator-id='${activeId}']`);
        root?.querySelector("[data-action='clear']")?.click();
      }
    });
  });
})();
