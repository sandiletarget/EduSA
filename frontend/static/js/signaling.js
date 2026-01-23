// WebSocket signaling layer for EduSA live classes.
(function () {
  var layout = document.querySelector(".live-class-layout");
  if (!layout) return;

  var roomId = layout.getAttribute("data-room-id");
  var username = layout.getAttribute("data-username");
  var protocol = window.location.protocol === "https:" ? "wss" : "ws";
  var socket = new WebSocket(protocol + "://" + window.location.host + "/ws/live-class/" + roomId + "/");

  window.signalingSocket = socket;

  socket.addEventListener("open", function () {
    socket.send(JSON.stringify({ event: "join", user: username }));
    window.dispatchEvent(new CustomEvent("signaling_status", { detail: { state: "open" } }));
  });

  socket.addEventListener("message", function (event) {
    var data = JSON.parse(event.data);
    window.dispatchEvent(new CustomEvent("signaling", { detail: data }));
  });

  socket.addEventListener("close", function () {
    console.warn("Signaling socket closed.");
    window.dispatchEvent(new CustomEvent("signaling_status", { detail: { state: "closed" } }));
  });

  socket.addEventListener("error", function () {
    window.dispatchEvent(new CustomEvent("signaling_status", { detail: { state: "error" } }));
  });
})();
