// WebRTC mesh implementation for EduSA live classes.
// This is a foundation and should be enhanced for scale (SFU) in production.
(function () {
  var layout = document.querySelector(".live-class-layout");
  if (!layout) return;

  var role = layout.getAttribute("data-role");
  var username = layout.getAttribute("data-username");
  var localStream = null;
  var activeVideoTrack = null;
  var screenStream = null;
  var peerConnections = {};
  var videoGrid = document.getElementById("videoGrid");
  var localVideo = document.getElementById("localVideo");
  var localTile = document.getElementById("localTile");
  var screenVideo = document.getElementById("screenShare");
  var screenTile = document.getElementById("screenTile");

  var micButton = document.querySelector("[data-media-action='mic']");
  var cameraButton = document.querySelector("[data-media-action='camera']");
  var screenButton = document.querySelector("[data-media-action='screen']");
  var handButton = document.querySelector("[data-media-action='hand']");
  var handRaised = false;

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
    tile.tile.classList.add("has-stream");
  }

  async function initLocalMedia() {
    if (localStream) return localStream;
    localStream = await navigator.mediaDevices.getUserMedia({ audio: true, video: true });
    activeVideoTrack = localStream.getVideoTracks()[0] || activeVideoTrack;
    if (localVideo) {
      localVideo.srcObject = localStream;
      localVideo.play().catch(function () {});
    }
    if (localTile) {
      localTile.classList.add("has-stream");
    }
    attachLocalTracksToPeers();
    return localStream;
  }

  function attachLocalTracksToPeers() {
    Object.keys(peerConnections).forEach(function (peerId) {
      var pc = peerConnections[peerId];
      if (!pc) return;

      var senders = pc.getSenders();
      var audioTrack = localStream ? localStream.getAudioTracks()[0] : null;
      var videoTrack = activeVideoTrack || (localStream ? localStream.getVideoTracks()[0] : null);

      if (audioTrack && !senders.some(function (s) { return s.track && s.track.kind === "audio"; })) {
        pc.addTrack(audioTrack, localStream);
      }
      if (videoTrack && !senders.some(function (s) { return s.track && s.track.kind === "video"; })) {
        pc.addTrack(videoTrack, localStream || new MediaStream([videoTrack]));
      }
    });
  }

  function createPeerConnection(peerId) {
    var pc = new RTCPeerConnection(iceConfig);
    if (localStream || activeVideoTrack) {
      var audioTrack = localStream ? localStream.getAudioTracks()[0] : null;
      var videoTrack = activeVideoTrack || (localStream ? localStream.getVideoTracks()[0] : null);
      if (audioTrack) pc.addTrack(audioTrack, localStream);
      if (videoTrack) pc.addTrack(videoTrack, localStream || new MediaStream([videoTrack]));
    }

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
      payload.from = username;
      window.signalingSocket.send(JSON.stringify(payload));
    }
  }

  async function handleOffer(data) {
    if (data.target && data.target !== username) return;
    if (data.from === username) return;
    var pc = createPeerConnection(data.from);
    await pc.setRemoteDescription(new RTCSessionDescription(data.offer));
    var answer = await pc.createAnswer();
    await pc.setLocalDescription(answer);
    signalingSend({ event: "answer", target: data.from, answer: answer });
  }

  async function handleAnswer(data) {
    if (data.target && data.target !== username) return;
    if (data.from === username) return;
    var pc = peerConnections[data.from];
    if (!pc) return;
    await pc.setRemoteDescription(new RTCSessionDescription(data.answer));
  }

  async function handleIce(data) {
    if (data.target && data.target !== username) return;
    if (data.from === username) return;
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

  function renderChatMessage(payload) {
    var chat = document.getElementById("chatMessages");
    if (!chat) return;
    var msg = document.createElement("div");
    msg.className = "chat-message";
    var timestamp = payload.timestamp ? " <span class=\"chat-time\">" + payload.timestamp + "</span>" : "";
    msg.innerHTML = "<strong>" + (payload.user || "User") + ":</strong> " + payload.message + timestamp;
    chat.appendChild(msg);
    chat.scrollTop = chat.scrollHeight;
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
      renderChatMessage(data);
    } else if (data.event === "chat_history" && Array.isArray(data.messages)) {
      var chat = document.getElementById("chatMessages");
      if (chat) {
        chat.innerHTML = "";
        data.messages.forEach(renderChatMessage);
      }
    } else if (data.event === "join" && data.user && data.user !== username) {
      createOffer(data.user);
    }
  });

  window.addEventListener("signaling_status", function (event) {
    var status = event.detail || {};
    var label = document.getElementById("chatStatus");
    if (!label) return;
    if (status.state === "open") {
      label.textContent = "Connected";
    } else if (status.state === "closed") {
      label.textContent = "Disconnected";
    } else if (status.state === "error") {
      label.textContent = "Connection error";
    } else {
      label.textContent = "Connecting…";
    }
  });

  function updateButtonState(button, active, labelOn, labelOff) {
    if (!button) return;
    button.setAttribute("aria-pressed", active ? "true" : "false");
    if (labelOn && labelOff) {
      button.textContent = active ? labelOn : labelOff;
    }
  }

  if (micButton) {
    micButton.addEventListener("click", async function () {
      try {
        await initLocalMedia();
      } catch (err) {
        alert("Unable to access microphone.");
        return;
      }
      var audioTrack = localStream && localStream.getAudioTracks()[0];
      if (!audioTrack) return;
      audioTrack.enabled = !audioTrack.enabled;
      updateButtonState(micButton, audioTrack.enabled, "🎙️ Mic On", "🎙️ Mic Off");
      if (localTile) {
        localTile.classList.toggle("is-muted", !audioTrack.enabled);
      }
    });
  }

  if (cameraButton) {
    cameraButton.addEventListener("click", async function () {
      try {
        await initLocalMedia();
      } catch (err) {
        alert("Unable to access camera.");
        return;
      }
      var videoTrack = localStream && localStream.getVideoTracks()[0];
      if (!videoTrack) return;
      videoTrack.enabled = !videoTrack.enabled;
      updateButtonState(cameraButton, videoTrack.enabled, "🎥 Camera On", "🎥 Camera Off");
      if (localTile) {
        localTile.classList.toggle("has-stream", videoTrack.enabled);
      }
    });
  }

  if (screenButton) {
    screenButton.addEventListener("click", async function () {
      if (screenStream) {
        screenStream.getTracks().forEach(function (track) { track.stop(); });
        screenStream = null;
        activeVideoTrack = localStream ? localStream.getVideoTracks()[0] : null;
        if (screenVideo) screenVideo.srcObject = null;
        if (screenTile) screenTile.classList.remove("has-stream");
        updateButtonState(screenButton, false, "🖥️ Stop Share", "🖥️ Screen");
        replaceVideoTrack(activeVideoTrack);
        return;
      }

      try {
        screenStream = await navigator.mediaDevices.getDisplayMedia({ video: true });
        activeVideoTrack = screenStream.getVideoTracks()[0];
        if (screenVideo) {
          screenVideo.srcObject = screenStream;
          screenVideo.play().catch(function () {});
        }
        if (screenTile) screenTile.classList.add("has-stream");
        updateButtonState(screenButton, true, "🖥️ Stop Share", "🖥️ Screen");
        replaceVideoTrack(activeVideoTrack);

        activeVideoTrack.addEventListener("ended", function () {
          if (screenStream) {
            screenStream.getTracks().forEach(function (track) { track.stop(); });
          }
          screenStream = null;
          activeVideoTrack = localStream ? localStream.getVideoTracks()[0] : null;
          if (screenVideo) screenVideo.srcObject = null;
          if (screenTile) screenTile.classList.remove("has-stream");
          updateButtonState(screenButton, false, "🖥️ Stop Share", "🖥️ Screen");
          replaceVideoTrack(activeVideoTrack);
        });
      } catch (error) {
        alert("Screen sharing was blocked or cancelled.");
      }
    });
  }

  function replaceVideoTrack(track) {
    Object.keys(peerConnections).forEach(function (peerId) {
      var pc = peerConnections[peerId];
      if (!pc || !track) return;
      var sender = pc.getSenders().find(function (s) { return s.track && s.track.kind === "video"; });
      if (sender) {
        sender.replaceTrack(track);
      } else {
        pc.addTrack(track, localStream || new MediaStream([track]));
      }
    });
  }

  if (handButton) {
    handButton.addEventListener("click", function () {
      handRaised = !handRaised;
      updateButtonState(handButton, handRaised, "✋ Hand Raised", "✋ Hand");
      signalingSend({ event: "raise_hand", user: username, raised: handRaised });
    });
  }

  // Simple chat send (broadcast only).
  document.getElementById("sendChat")?.addEventListener("click", function () {
    var input = document.getElementById("chatInput");
    if (!input || !input.value) return;
    if (!window.signalingSocket || window.signalingSocket.readyState !== WebSocket.OPEN) {
      alert("Chat is not connected. Please wait for reconnection.");
      return;
    }
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

  // Attempt to initialize media if the user has already granted permission.
  navigator.permissions?.query({ name: "camera" }).then(function (status) {
    if (status.state === "granted") {
      initLocalMedia().catch(function () {});
    }
  }).catch(function () {});
})();
