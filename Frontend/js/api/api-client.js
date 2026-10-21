import { API_BASE, API_ORIGIN } from "../config.js?v=cartly-account-sidebar-20261021";

let csrfToken;

function contentTypeOf(response) {
  return response?.headers?.get?.("content-type") || "";
}

async function readResponse(response) {
  if (!response) {
    const error = new Error("No API response was received.");
    error.userMessage = "We’re having trouble loading the store. Please try again in a moment.";
    throw error;
  }
  const status = response.status ?? response.statusCode;
  if (status === 204) return null;

  const contentType = contentTypeOf(response);
  let body;
  try {
    if (typeof response.json === "function" && (
      contentType.includes("application/json") || typeof response.text !== "function"
    )) {
      body = await response.json();
    } else if (typeof response.text === "function") {
      const text = await response.text();
      try {
        body = JSON.parse(text);
      } catch {
        body = text;
      }
    } else if (response.data !== undefined) {
      body = response.data;
    } else {
      body = response;
    }
  } catch (cause) {
    console.error("Cartly could not read the API response.", cause);
    const error = new Error("The API response could not be read.");
    error.userMessage = "We couldn’t load the store just now. Please refresh and try again.";
    throw error;
  }

  const ok = response.ok ?? (Number.isFinite(status) && status >= 200 && status < 300);
  if (!ok) {
    const detail = messageFrom(body);
    const error = new Error(detail || `Request failed (${status || "unknown"}).`);
    error.status = status;
    error.data = body;
    if (status === 400) error.userMessage = detail || "Please check your details and try again.";
    else if (status === 401) error.userMessage = "Please sign in and try again.";
    else if (status === 403) error.userMessage = "We couldn’t verify that request. Refresh the page and try again.";
    else if (status === 404) error.userMessage = "That item is no longer available. Refresh the page and try again.";
    else if (status >= 500) error.userMessage = "The store is temporarily unavailable. Please try again shortly.";
    else error.userMessage = "We couldn’t complete that request. Please try again.";
    throw error;
  }
  return body;
}

export function friendlyErrorMessage(error, fallback = "We couldn’t complete that request. Please try again.") {
  return error?.userMessage || fallback;
}

function messageFrom(data) {
  if (typeof data === "string") return data;
  if (!data || typeof data !== "object") return "";
  if (typeof data.detail === "string") return data.detail;
  const messages = [];
  if (typeof data === "object") {
    for (const value of Object.values(data)) {
      if (Array.isArray(value) && value.length) {
        messages.push(...value.map((item) => (
          typeof item === "string" ? item : item?.message
        )).filter(Boolean));
      }
      if (typeof value === "string") messages.push(value);
    }
  }
  return messages.join(" ");
}

async function getCsrfToken() {
  const response = await request("/csrf/", { method: "GET" });
  const data = await readResponse(response);
  if (typeof data?.csrfToken !== "string" || !data.csrfToken) {
    throw new Error("The store did not provide a CSRF token. Refresh the page and try again.");
  }
  csrfToken = data.csrfToken;
  return csrfToken;
}

async function request(path, options = {}) {
  let response;
  const headers = new Headers(options.headers || {});
  headers.set("Accept", "application/json");
  try {
    response = await fetch(`${API_BASE}${path}`, {
      ...options,
      credentials: "include",
      ...(path === "/csrf/" ? { cache: "no-store" } : {}),
      headers,
    });
  } catch (error) {
    if (error instanceof TypeError) {
      console.error(`Cartly could not reach the store API at ${API_ORIGIN}.`, error);
      const friendlyError = new Error("Store connection failed.");
      friendlyError.userMessage = "We can’t reach the store right now. Please check your connection and try again.";
      throw friendlyError;
    }
    throw error;
  }

  const contentType = contentTypeOf(response);
  if (!contentType.includes("application/json")) {
    if (contentType.includes("text/html")) {
      console.error(`Cartly expected JSON from ${API_BASE}${path} but received HTML (HTTP ${response.status}).`);
      const error = new Error("Unexpected HTML response from the store API.");
      error.status = response.status;
      error.userMessage = response.status >= 500
        ? "The store is temporarily unavailable. Please try again shortly."
        : "We couldn’t load the store right now. Please refresh and try again.";
      throw error;
    }
  }
  return response;
}

export async function api(path, options = {}) {
  const method = (options.method || "GET").toUpperCase();
  const headers = new Headers(options.headers || {});
  let body = options.body;

  const isUnsafe = !["GET", "HEAD", "OPTIONS"].includes(method);
  if (isUnsafe) {
    // Always fetch a fresh token for auth mutations. Django rotates the CSRF
    // secret at login, registration, and logout boundaries.
    if (["/auth/login/", "/auth/register/", "/auth/logout/"].includes(path)) {
      csrfToken = undefined;
    }
    if (!csrfToken) await getCsrfToken();
    headers.set("X-CSRFToken", csrfToken);
    if (body !== undefined && !(body instanceof FormData)) {
      headers.set("Content-Type", "application/json");
      body = JSON.stringify(body);
    }
  }

  let response = await request(path, { ...options, method, headers, body });
  if (response?.status === 403 && isUnsafe) {
    const contentType = contentTypeOf(response);
    if (contentType.includes("application/json")) {
      let errorBody = null;
      if (typeof response.clone === "function") {
        const copy = response.clone();
        if (typeof copy?.json === "function") {
          try {
            errorBody = await copy.json();
          } catch {
            errorBody = null;
          }
        }
      }
      const csrfRejected = typeof errorBody?.detail === "string"
        && errorBody.detail.toLowerCase().includes("csrf");
      if (csrfRejected) {
        csrfToken = undefined;
        headers.set("X-CSRFToken", await getCsrfToken());
        response = await request(path, { ...options, method, headers, body });
      }
    }
  }
  const result = await readResponse(response);
  if (path === "/auth/login/" || path === "/auth/register/" || path === "/auth/logout/") {
    csrfToken = undefined;
  }
  return result;
}

export function clearCsrfToken() {
  csrfToken = undefined;
}
