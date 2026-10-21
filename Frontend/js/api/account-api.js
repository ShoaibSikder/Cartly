import { api } from "./api-client.js?v=cartly-auth-csrf-20261021";

export function getCurrentUser() {
  return api("/auth/me/");
}

export function signIn(credentials) {
  return api("/auth/login/", { method: "POST", body: credentials });
}

export function registerAccount(details) {
  return api("/auth/register/", { method: "POST", body: details });
}

export function getProfile() {
  return api("/auth/profile/");
}

export function updateProfile(details) {
  return api("/auth/profile/", { method: "PATCH", body: details });
}

export function signOut() {
  return api("/auth/logout/", { method: "POST" });
}
