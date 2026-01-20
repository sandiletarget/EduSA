// WebRTC mesh implementation for EduSA live classes.
// This is a foundation and should be enhanced for scale (SFU) in production.
(function () {
  var layout = document.querySelector(".live-class-layout");
  if (!layout) return;

  var role = layout.getAttribute("data-role");
  var localStream = null;
  var peerConnections = {};
  var videoGrid = document.getElementById("videoGrid");

  var iceConfig = {
    iceServers: [
      { urls: "stun:stun.l.google.com:19302" },
      { urls: "stun:stun1.l.google.com:19302" },
      // TURN servers should be added here for production.
    ],
  };

  function createVideoTile(id, label) {
    var tile = document.createElement("div");
    tile.className = "video-tile";
    tile.id = "tile-" + id;

    var video = document.createElement("video");
    video.autoplay = true;
    video.playsInline = true;
    video.className = "video-element";

    var placeholder = document.createElement("div");
    placeholder.className = "video-placeholder";
    placeholder.innerHTML = "<span>Connecting...</span>";

    var caption = document.createElement("div");
    caption.className = "video-label";
    caption.textContent = label;

    tile.appendChild(video);
    tile.appendChild(placeholder);
    tile.appendChild(caption);
    videoGrid.appendChild(tile);

    return { tile: tile, video: video, placeholder: placeholder };
  }

  function attachStream(tile, stream) {
    tile.video.srcObject = stream;
    tile.video.style.display = "block";
    tile.placeholder.style.display = "none";
  }

  async function initLocalMedia() {
    localStream = await navigator.mediaDevices.getUserMedia({ audio: true, video: true });
    var selfTile = createVideoTile("local", "You");
    attachStream(selfTile, localStream);
  }

  function createPeerConnection(peerId) {
    var pc = new RTCPeerConnection(iceConfig);

    localStream.getTracks().forEach(function (track) {
      pc.addTrack(track, localStream);
    });

    pc.onicecandidate = function (event) {
      if (event.candidate) {
        signalingSend({
          event: "ice",
          target: peerId,
          candidate: event.candidate,
        });
      }
    };

    var tile = createVideoTile(peerId, peerId);
    pc.ontrack = function (event) {
      attachStream(tile, event.streams[0]);
    };

    peerConnections[peerId] = pc;
    return pc;
  }

  function signalingSend(payload) {
    if (window.signalingSocket && window.signalingSocket.readyState === WebSocket.OPEN) {
      window.signalingSocket.send(JSON.stringify(payload));
    }
  }

  async function handleOffer(data) {
    var pc = createPeerConnection(data.from);
    await pc.setRemoteDescription(new RTCSessionDescription(data.offer));
    var answer = await pc.createAnswer();
    await pc.setLocalDescription(answer);
    signalingSend({ event: "answer", target: data.from, answer: answer });
  }

  async function handleAnswer(data) {
    var pc = peerConnections[data.from];
    if (!pc) return;
    await pc.setRemoteDescription(new RTCSessionDescription(data.answer));
  }

  async function handleIce(data) {
    var pc = peerConnections[data.from];
    if (!pc) return;
    await pc.addIceCandidate(new RTCIceCandidate(data.candidate));
  }

  async function createOffer(peerId) {
    var pc = createPeerConnection(peerId);
    var offer = await pc.createOffer();
    await pc.setLocalDescription(offer);
    signalingSend({ event: "offer", target: peerId, offer: offer });
  }

  window.addEventListener("signaling", function (event) {
    var data = event.detail;
    if (data.event === "offer") {
      handleOffer(data);
    } else if (data.event === "answer") {
      handleAnswer(data);
    } else if (data.event === "ice") {
      handleIce(data);
    } else if (data.event === "chat") {
      var chat = document.getElementById("chatMessages");
      if (chat) {
        var msg = document.createElement("div");
        msg.className = "chat-message";
        msg.innerHTML = "<strong>" + (data.user || "User") + ":</strong> " + data.message;
        chat.appendChild(msg);
      }
    } else if (data.event === "join" && data.user) {
      if (data.user !== layout.getAttribute("data-username")) {
        createOffer(data.user);
      }
    }
  });

  // UI controls.
  document.getElementById("toggleMic")?.addEventListener("click", function () {
    if (!localStream) return;
    localStream.getAudioTracks().forEach(function (track) {
      track.enabled = !track.enabled;
    });
  });

  document.getElementById("toggleCamera")?.addEventListener("click", function () {
    if (!localStream) return;
    localStream.getVideoTracks().forEach(function (track) {
      track.enabled = !track.enabled;
    });
  });

  document.getElementById("shareScreen")?.addEventListener("click", async function () {
    if (!navigator.mediaDevices.getDisplayMedia) return;
    var screenStream = await navigator.mediaDevices.getDisplayMedia({ video: true });
    var screenVideo = document.getElementById("screenShare");
    if (screenVideo) {
      screenVideo.srcObject = screenStream;
      screenVideo.style.display = "block";
    }
  });

  // Simple chat send (broadcast only).
  document.getElementById("sendChat")?.addEventListener("click", function () {
    var input = document.getElementById("chatInput");
    if (!input || !input.value) return;
    signalingSend({ event: "chat", message: input.value, user: layout.getAttribute("data-username") });
    input.value = "";
  });

  // Panel toggles.
  document.querySelectorAll("[data-panel-toggle]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var target = btn.getAttribute("data-panel-toggle");
      document.querySelectorAll(".side-panel").forEach(function (panel) {
        panel.classList.toggle("is-hidden", panel.getAttribute("data-panel") !== target);
      });
    });
  });

  document.querySelectorAll("[data-panel-close]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      document.querySelectorAll(".side-panel").forEach(function (panel) {
        panel.classList.remove("is-hidden");
      });
    });
  });

  initLocalMedia().catch(function (err) {
    console.error("Failed to get local media", err);
  });
})();
