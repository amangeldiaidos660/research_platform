(function () {
  const STORAGE_KEY = "rip-publications-search-timer";
  const form = document.querySelector("[data-search-form]");

  function readPayload() {
    try {
      const raw = sessionStorage.getItem(STORAGE_KEY);
      return raw ? JSON.parse(raw) : null;
    } catch {
      return null;
    }
  }

  function clearPayload() {
    sessionStorage.removeItem(STORAGE_KEY);
  }

  function logSearchDuration() {
    const payload = readPayload();
    if (!payload) {
      return;
    }

    const durationMs = Date.now() - payload.startedAt;
    const durationSeconds = (durationMs / 1000).toFixed(2);
    const currentUrl = window.location.pathname + window.location.search;

    if (payload.targetUrl !== currentUrl) {
      return;
    }

    console.log(
      "[RIP search timer] Search completed",
      {
        query: payload.query,
        targetUrl: payload.targetUrl,
        durationMs,
        durationSeconds
      }
    );
    clearPayload();
  }

  if (form) {
    form.addEventListener("submit", () => {
      const formData = new FormData(form);
      const params = new URLSearchParams();

      for (const [key, value] of formData.entries()) {
        if (typeof value === "string" && value !== "") {
          params.set(key, value);
        }
      }

      const targetUrl = form.action
        ? new URL(form.action, window.location.origin)
        : new URL(window.location.pathname, window.location.origin);

      const search = params.toString();
      const fullTargetUrl = targetUrl.pathname + (search ? `?${search}` : "");
      const query = String(formData.get("q") || "");

      sessionStorage.setItem(
        STORAGE_KEY,
        JSON.stringify({
          startedAt: Date.now(),
          query,
          targetUrl: fullTargetUrl
        })
      );

      console.log("[RIP search timer] Search started", {
        query,
        targetUrl: fullTargetUrl
      });
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", logSearchDuration, { once: true });
  } else {
    logSearchDuration();
  }
})();
