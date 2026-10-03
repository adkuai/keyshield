const BASE_URL = "http://127.0.0.1:8000";

export const apiService = {
  setToken(token) { localStorage.setItem("ks_token", token); },
  getToken() { return localStorage.getItem("ks_token"); },
  clearToken() { localStorage.removeItem("ks_token"); },
  
  getHeaders() {
    const token = this.getToken();
    return token ? { "Authorization": `Bearer ${token}`, "Content-Type": "application/json" } : { "Content-Type": "application/json" };
  },

  async signup(email, password) {
    const res = await fetch(`${BASE_URL}/api/auth/register`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ email, password }) });
    if (!res.ok) throw new Error((await res.json()).detail || "Signup transaction failed.");
    return res.json();
  },

  async login(email, password) {
    const params = new URLSearchParams();
    params.append("username", email);
    params.append("password", password);
    const res = await fetch(`${BASE_URL}/api/auth/login`, { method: "POST", headers: { "Content-Type": "application/x-www-form-urlencoded" }, body: params });
    if (!res.ok) throw new Error((await res.json()).detail || "Login credentials authentication failed.");
    const data = await res.json();
    this.setToken(data.access_token);
    return data;
  },

  async listProjects() {
    const res = await fetch(`${BASE_URL}/api/projects`, { method: "GET", headers: this.getHeaders() });
    return res.json();
  },

  async createProject(name, rpm) {
    const res = await fetch(`${BASE_URL}/api/projects`, { method: "POST", headers: this.getHeaders(), body: JSON.stringify({ name, rate_limit_rpm: rpm }) });
    return res.json();
  },

  async getKeys(projectId) {
    const res = await fetch(`${BASE_URL}/api/projects/${projectId}/keys`, { method: "GET", headers: this.getHeaders() });
    return res.json();
  },

  async generateKey(projectId, name, environment, scopes) {
    const res = await fetch(`${BASE_URL}/api/projects/${projectId}/keys`, { method: "POST", headers: this.getHeaders(), body: JSON.stringify({ name, environment, scopes }) });
    return res.json();
  },

  async deactivateKey(projectId, keyId) {
    const res = await fetch(`${BASE_URL}/api/projects/${projectId}/keys/${keyId}/deactivate`, { method: "PATCH", headers: this.getHeaders() });
    return res.json();
  },

  async rotateKey(projectId, keyId) {
    const res = await fetch(`${BASE_URL}/api/projects/${projectId}/keys/${keyId}/rotate`, { method: "POST", headers: this.getHeaders() });
    return res.json();
  },

  async getAnalytics(projectId) {
    const res = await fetch(`${BASE_URL}/api/projects/${projectId}/analytics`, { method: "GET", headers: this.getHeaders() });
    return res.json();
  },

  async getLogs(projectId) {
    const res = await fetch(`${BASE_URL}/api/projects/${projectId}/logs`, { method: "GET", headers: this.getHeaders() });
    return res.json();
  },

    // 5. Playground Handler: Smart slash sanitization layer
  async triggerGatewayMock(endpoint, method, apiKeyString) {
    const headers = { 
      "X-API-Key": apiKeyString,
      "Content-Type": "application/json"
    };
    
    // Clean up any double slashes or missing slashes from the input box automatically
    let cleanEndpoint = endpoint.trim();
    if (cleanEndpoint.startsWith('/')) {
      cleanEndpoint = cleanEndpoint.substring(1); // Strip leading slash to avoid double-slashing
    }
    
    // Assembles perfectly to: http://127.0.0
    const targetUrl = "http://127.0.0.1:8000/api/v1/" + cleanEndpoint;
    
    const res = await fetch(targetUrl, { 
      method: method, 
      headers: headers 
    });
    
    if (!res.ok) return { error: true, status: res.status, payload: await res.json() };
    return { error: false, status: res.status, payload: await res.json() };
  }

};
