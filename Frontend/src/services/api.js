// frontend/src/services/api.js

// 1. Establish the clean master base URI namespace once at the top
const BASE_URL = "http://127.0.0.1:8000";

export const apiService = {
  
  // 2. POST /api/signup
  async signup(email, password) {
    const response = await fetch(`${BASE_URL}/api/signup`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || "Signup failed.");
    }
    return response.json();
  },

  // 3. POST /api/login
  async login(email, password) {
    const formData = new URLSearchParams();
    formData.append("username", email);
    formData.append("password", password);

    const response = await fetch(`${BASE_URL}/api/login`, {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: formData,
    });
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || "Login failed.");
    }
    return response.json();
  },

  // 4. GET /api/users/{userId}/keys
  async getUserKeys(userId) {
    const response = await fetch(`${BASE_URL}/api/users/${userId}/keys`, {
      method: "GET"
    });
    if (!response.ok) throw new Error("Failed to fetch keys ledger.");
    return response.json();
  },

  // 5. POST /api/users/{userId}/keys
  async generateKey(userId, keyName) {
    const response = await fetch(`${BASE_URL}/api/users/${userId}/keys`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name: keyName }),
    });
    if (!response.ok) throw new Error("Failed to generate token.");
    return response.json();
  },

  // 6. PATCH /api/keys/{keyId}/deactivate
  async deactivateKey(keyId) {
    const response = await fetch(`${BASE_URL}/api/keys/${keyId}/deactivate`, {
      method: "PATCH",
    });
    if (!response.ok) throw new Error("Failed to revoke key.");
    return response.json();
  }
};
