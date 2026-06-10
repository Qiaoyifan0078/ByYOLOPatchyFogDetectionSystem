const TOKEN_KEY = "patchy_fog_token";
const REQUEST_TIMEOUT_MS = 30000;

// Simple event bus for cross-component error/notification dispatch
const _listeners = {};
export const emitter = {
  on(event, fn) { (_listeners[event] = _listeners[event] || []).push(fn); },
  off(event, fn) { const arr = _listeners[event]; if (arr) { _listeners[event] = arr.filter(f => f !== fn); } },
  emit(event, payload) { (_listeners[event] || []).forEach(fn => fn(payload)); }
};

function getToken() {
  return localStorage.getItem(TOKEN_KEY) || "";
}

function setToken(token) {
  if (token) {
    localStorage.setItem(TOKEN_KEY, token);
  } else {
    localStorage.removeItem(TOKEN_KEY);
  }
}

async function request(url, options = {}) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), options.timeout || REQUEST_TIMEOUT_MS);

  const headers = options.headers || {};
  const token = getToken();
  if (token) headers.Authorization = "Bearer " + token;
  if (options.body && !(options.body instanceof FormData)) {
    headers["Content-Type"] = "application/json";
    options.body = JSON.stringify(options.body);
  }

  try {
    const response = await fetch(url, { ...options, headers, signal: controller.signal });
    clearTimeout(timer);

    const contentType = response.headers.get("content-type") || "";
    const isJson = contentType.includes("application/json");
    const payload = isJson ? await response.json().catch(() => ({})) : {};

    // Handle 401 globally
    if (response.status === 401) {
      setToken("");
      emitter.emit("auth-expired");
      throw new Error(payload.message || "Session expired");
    }

    if (!response.ok) {
      const msg = payload.message || "Request failed";
      emitter.emit("api-error", { status: response.status, message: msg });
      throw new Error(msg);
    }

    // Support both { data: ... } and bare responses
    return payload.data !== undefined ? payload.data : payload;

  } catch (err) {
    clearTimeout(timer);
    if (err.name === "AbortError") {
      emitter.emit("api-error", { status: 0, message: "Request timed out" });
      throw new Error("Request timed out");
    }
    throw err;
  }
}

export default {
  getToken,
  setToken,
  get(url) { return request(url); },
  post(url, body) { return request(url, { method: "POST", body }); },
  put(url, body) { return request(url, { method: "PUT", body }); },
  delete(url) { return request(url, { method: "DELETE" }); },
  upload(url, formData) { return request(url, { method: "POST", body: formData }); }
};
