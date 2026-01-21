(function () {
  var loader = null;
  var pendingRequests = 0;

  function ensureLoader() {
    if (!loader) {
      loader = document.getElementById("globalLoader");
    }
    return loader;
  }

  function showLoader() {
    var el = ensureLoader();
    if (!el) return;
    el.classList.add("is-visible");
  }

  function hideLoader() {
    var el = ensureLoader();
    if (!el) return;
    el.classList.remove("is-visible");
  }

  function trackRequestStart() {
    pendingRequests += 1;
    showLoader();
  }

  function trackRequestEnd() {
    pendingRequests = Math.max(0, pendingRequests - 1);
    if (pendingRequests === 0) {
      hideLoader();
    }
  }

  window.EduSALoader = {
    show: showLoader,
    hide: hideLoader,
  };

  document.addEventListener("DOMContentLoaded", function () {
    showLoader();
  });

  window.addEventListener("load", function () {
    hideLoader();
  });

  var originalFetch = window.fetch;
  if (originalFetch) {
    window.fetch = function () {
      trackRequestStart();
      return originalFetch.apply(this, arguments)
        .then(function (response) {
          trackRequestEnd();
          return response;
        })
        .catch(function (error) {
          trackRequestEnd();
          throw error;
        });
    };
  }

  var originalOpen = XMLHttpRequest.prototype.open;
  XMLHttpRequest.prototype.open = function () {
    this.addEventListener("loadstart", trackRequestStart);
    this.addEventListener("loadend", trackRequestEnd);
    return originalOpen.apply(this, arguments);
  };
})();
