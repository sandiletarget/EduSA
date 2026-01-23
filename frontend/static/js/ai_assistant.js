// AI assistant WebSocket integration (UI only).
(function () {
  var layout = document.querySelector(".live-class-layout");
  if (!layout) return;

  var roomId = layout.getAttribute("data-room-id");
  var role = layout.getAttribute("data-role");
  var protocol = window.location.protocol === "https:" ? "wss" : "ws";
  var socket = new WebSocket(protocol + "://" + window.location.host + "/ws/ai/live-class/" + roomId + "/");

  var keyPoints = document.getElementById("aiKeyPoints");
  var aiSummary = document.getElementById("aiSummary");
  var aiAnswers = document.getElementById("aiAnswers");
  var askButton = document.getElementById("askAi");
  var input = document.getElementById("aiQuestionInput");
  var toggleAi = document.getElementById("toggleAi");
  var toggleMode = document.getElementById("toggleMode");

  socket.addEventListener("message", function (event) {
    var data = JSON.parse(event.data);
    if (data.event === "summary_ready" && aiSummary) {
      aiSummary.textContent = data.summary;
    }
    if (data.event === "ai_answer" && aiAnswers) {
      var item = document.createElement("div");
      item.className = "ai-answer";
      item.innerHTML = "<strong>Q:</strong> " + data.question + "<br><strong>A:</strong> " + data.answer;
      aiAnswers.appendChild(item);
    }
    if (data.event === "moderation_alert" && keyPoints) {
      var li = document.createElement("li");
      li.textContent = "Alert: " + data.message;
      keyPoints.appendChild(li);
    }
  });

  askButton?.addEventListener("click", function () {
    if (!input || !input.value) return;
    socket.send(JSON.stringify({ event: "question", question: input.value }));
    input.value = "";
  });

  toggleAi?.addEventListener("click", function () {
    var enabled = toggleAi.dataset.enabled !== "false";
    var next = !enabled;
    toggleAi.dataset.enabled = String(next);
    toggleAi.textContent = next ? "Disable AI" : "Enable AI";
    socket.send(JSON.stringify({ event: "toggle_ai", enabled: next }));
  });

  toggleMode?.addEventListener("click", function () {
    toggleMode.textContent = toggleMode.textContent.includes("Passive") ? "Mode: Active" : "Mode: Passive";
  });
})();
