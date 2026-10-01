// frontend/src/App.jsx
import React, { useState, useEffect } from 'react';
import { apiService } from './services/api';

export default function App() {
  // Navigation & Session App States
  const [currentView, setCurrentView] = useState('signup'); // signup, login, dashboard
  const [currentUser, setCurrentUser] = useState(null);    // Stores the logged-in user object
  const [token, setToken] = useState(null);                // Stores the active JWT session token

  // Dashboard Form States
  const [authEmail, setAuthEmail] = useState("");
  const [authPassword, setAuthPassword] = useState("");
  const [apiKeys, setApiKeys] = useState([]);
  const [newKeyName, setNewKeyName] = useState("");
  const [loading, setLoading] = useState(false);
  const [fetching, setFetching] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");

  // --- 1. ACTION: Fetch keys for the current logged-in user id ---
  const loadUserKeys = async () => {
    if (!currentUser) return;
    setFetching(true);
    try {
      const data = await apiService.getUserKeys(currentUser.id);
      setApiKeys(data);
    } catch (err) {
      console.error("Failed to load keys:", err.message);
    } finally {
      setFetching(false);
    }
  };

  useEffect(() => {
    if (currentView === 'dashboard') {
      loadUserKeys();
    }
  }, [currentView, currentUser]);

  // --- 2. ACTION: Submit Account Creation (POST /api/signup) ---
  const handleSignupSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setErrorMessage("");
    try {
      // Register in PostgreSQL
      const user = await apiService.signup(authEmail, authPassword);
      setCurrentUser(user);
      // Clean password inputs and redirect to login phase automatically
      setAuthPassword("");
      setCurrentView('login');
      alert("Account registered successfully! Please log in.");
    } catch (err) {
      setErrorMessage(err.message);
    } finally {
      setLoading(false);
    }
  };

  // --- 3. ACTION: Submit Authentication Credentials (POST /api/login) ---
  const handleLoginSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setErrorMessage("");
    try {
      // Get secure signed JWT from backend encryption engine
      const sessionData = await apiService.login(authEmail, authPassword);
      setToken(sessionData.access_token);
      
      // If logging in after a fresh registration, we use that user object context.
      if (!currentUser) {
        // Fallback placeholder profile context if logging in directly to match the state flow
        setCurrentUser({ id: 1, email: authEmail });
      }

      setAuthEmail("");
      setAuthPassword("");
      setCurrentView('dashboard'); // Route directly to dashboard view
    } catch (err) {
      setErrorMessage(err.message);
    } finally {
      setLoading(false);
    }
  };

  // --- 4. ACTION: Create a key token row in PostgreSQL ---
  const handleCreateToken = async (e) => {
    e.preventDefault();
    if (!newKeyName.trim() || !currentUser) return;

    setLoading(true);
    try {
      await apiService.generateKey(currentUser.id, newKeyName);
      setNewKeyName("");
      await loadUserKeys();
    } catch (err) {
      alert("Error processing key token creation.");
    } finally {
      setLoading(false);
    }
  };

  // --- 5. ACTION: Revoke a token column status flag (PATCH) ---
  const handleRevokeToken = async (keyId) => {
    try {
      await apiService.deactivateKey(keyId);
      await loadUserKeys();
    } catch (err) {
      alert("Error changing active state.");
    }
  };

  const handleLogout = () => {
    setCurrentUser(null);
    setToken(null);
    setApiKeys([]);
    setCurrentView('signup');
  };

  return (
    <div className="min-h-screen bg-slate-50 text-slate-800 font-sans antialiased selection:bg-cyan-200 selection:text-slate-900">
      
      {/* GLOBAL APPTOP NAVBAR */}
      <nav className="border-b border-slate-200 bg-white sticky top-0 z-50 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="h-9 w-9 bg-gradient-to-tr from-cyan-600 to-blue-600 rounded-xl flex items-center justify-center font-bold text-white text-lg shadow-md">KS</div>
            <span className="text-xl font-bold text-slate-900">KeyShield</span>
          </div>
          
          <div className="flex items-center gap-4">
            {currentView === 'dashboard' && (
              <button 
                onClick={handleLogout}
                className="text-sm font-semibold text-slate-600 hover:text-slate-900 border border-slate-200 bg-white px-3 py-1.5 rounded-xl shadow-sm transition-all cursor-pointer"
              >
                Log Out
              </button>
            )}
            <span className="text-sm bg-slate-100 border border-slate-200 px-3 py-1.5 rounded-full text-slate-700 flex items-center gap-2 font-medium">
              <span className="h-2 w-2 rounded-full bg-cyan-600 animate-pulse"></span>
              Full-Stack Engaged
            </span>
          </div>
        </div>
      </nav>

      {/* CORE WORKSPACE VIEW ROUTER CONTROLLER */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
        <div className="max-w-4xl mx-auto">
          
          {errorMessage && (
            <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-xl text-sm font-semibold text-red-600 shadow-sm">
              ⚠️ Error: {errorMessage}
            </div>
          )}

          {/* 📍 VIEW A: RESPONSIVE USER SIGNUP PAGE CONTAINER */}
          {currentView === 'signup' && (
            <div className="max-w-md mx-auto bg-white border border-slate-200 p-8 rounded-2xl shadow-sm">
              <h2 className="text-2xl font-extrabold text-slate-900 mb-2">Create Developer Account</h2>
              <p className="text-sm text-slate-500 mb-6">Register to access your workspace token distribution engine.</p>
              <form onSubmit={handleSignupSubmit} className="space-y-4">
                <div>
                  <label className="block text-sm font-semibold text-slate-700 mb-1.5">Email Address</label>
                  <input 
                    type="email" required
                    placeholder="dev@example.com"
                    className="w-full bg-white border border-slate-300 rounded-xl px-4 py-2.5 text-slate-900 focus:outline-none focus:border-cyan-600"
                    value={authEmail} onChange={(e) => setAuthEmail(e.target.value)}
                  />
                </div>
                <div>
                  <label className="block text-sm font-semibold text-slate-700 mb-1.5">Password</label>
                  <input 
                    type="password" required minLength={6}
                    placeholder="••••••••"
                    className="w-full bg-white border border-slate-300 rounded-xl px-4 py-2.5 text-slate-900 focus:outline-none focus:border-cyan-600"
                    value={authPassword} onChange={(e) => setAuthPassword(e.target.value)}
                  />
                </div>
                <button type="submit" disabled={loading} className="w-full bg-gradient-to-r from-cyan-600 to-blue-600 text-white font-semibold py-3 rounded-xl shadow-md cursor-pointer hover:from-cyan-500 disabled:opacity-50">
                  {loading ? "Registering in PostgreSQL..." : "Create Free Account"}
                </button>
              </form>
              <p className="mt-4 text-center text-sm text-slate-600">
                Already have an account?{' '}
                <button onClick={() => { setErrorMessage(""); setCurrentView('login'); }} className="text-cyan-600 font-bold hover:underline cursor-pointer">Log In</button>
              </p>
            </div>
          )}

          {/* 📍 VIEW B: RESPONSIVE OAUTH2 LOGIN PAGE CONTAINER */}
          {currentView === 'login' && (
            <div className="max-w-md mx-auto bg-white border border-slate-200 p-8 rounded-2xl shadow-sm">
              <h2 className="text-2xl font-extrabold text-slate-900 mb-2">Developer Authentication</h2>
              <p className="text-sm text-slate-500 mb-6">Enter credentials to decode your workspace JWT access tokens.</p>
              <form onSubmit={handleLoginSubmit} className="space-y-4">
                <div>
                  <label className="block text-sm font-semibold text-slate-700 mb-1.5">Email Address</label>
                  <input 
                    type="email" required
                    placeholder="dev@example.com"
                    className="w-full bg-white border border-slate-300 rounded-xl px-4 py-2.5 text-slate-900 focus:outline-none focus:border-cyan-600"
                    value={authEmail} onChange={(e) => setAuthEmail(e.target.value)}
                  />
                </div>
                <div>
                  <label className="block text-sm font-semibold text-slate-700 mb-1.5">Password</label>
                  <input 
                    type="password" required
                    placeholder="••••••••"
                    className="w-full bg-white border border-slate-300 rounded-xl px-4 py-2.5 text-slate-900 focus:outline-none focus:border-cyan-600"
                    value={authPassword} onChange={(e) => setAuthPassword(e.target.value)}
                  />
                </div>
                <button type="submit" disabled={loading} className="w-full bg-gradient-to-r from-cyan-600 to-blue-600 text-white font-semibold py-3 rounded-xl shadow-md cursor-pointer hover:from-cyan-500 disabled:opacity-50">
                  {loading ? "Verifying hashes..." : "Sign In & Access Dashboard"}
                </button>
              </form>
            </div>
          )}
          {/* =========================================================================
              📍 VIEW C: DYNAMIC RESPONSIVE MAIN DEVELOPER COCKPIT DASHBOARD PANEL
              ========================================================================= */}
        {currentView === 'dashboard' && currentUser && (
          <div className="space-y-8 animate-fadeIn">
            
            {/* --- 1. USER METRICS PROFILE HEADER PANEL --- */}
            <header className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm flex flex-col sm:flex-row sm:items-center justify-between gap-4">
              <div className="space-y-1">
                <h1 className="text-2xl font-extrabold tracking-tight text-slate-900 sm:text-3xl">
                  Developer Cockpit
                </h1>
                <p className="text-sm text-slate-600 font-medium">
                  Authenticated Workspace Operator:{' '}
                  <span className="text-slate-900 font-bold bg-slate-100 border border-slate-200 px-2 py-0.5 rounded-md font-mono">
                    {currentUser.email}
                  </span>
                </p>
              </div>
              
              {/* Structural Account Reference Pill Badge */}
              <div className="flex-shrink-0 self-start sm:self-center">
                <span className="inline-flex items-center gap-1.5 text-xs font-semibold px-3 py-1.5 bg-cyan-50 border border-cyan-200 text-cyan-800 rounded-xl">
                  <span className="h-1.5 w-1.5 rounded-full bg-cyan-600"></span>
                  PostgreSQL Identity ID: #{currentUser.id}
                </span>
              </div>
            </header>

            {/* --- 2. TOKEN GENERATION CONSOLE FORM (MOBILE SIZES COMPLIANT) --- */}
            <section className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm">
              <div className="mb-4">
                <h2 className="text-lg font-bold text-slate-900">Mint New Developer Token</h2>
                <p className="text-sm text-slate-500 mt-0.5">
                  Provide a unique reference name identifier to map incoming access logs.
                </p>
              </div>

              {/* Input container forces full width stacking on mobile, side-by-side row on desktops */}
              <form className="flex flex-col sm:flex-row gap-3" onSubmit={handleCreateToken}>
                <input
                  type="text"
                  required
                  placeholder="e.g., Staging Payment Pipeline"
                  className="flex-1 bg-white border border-slate-300 rounded-xl px-4 py-3 text-slate-900 placeholder:text-slate-400 font-medium focus:outline-none focus:border-cyan-600 focus:ring-1 focus:ring-cyan-600 transition-all"
                  value={newKeyName}
                  onChange={(e) => setNewKeyName(e.target.value)}
                />
                <button 
                  type="submit"
                  disabled={loading}
                  className="w-full sm:w-auto bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white font-semibold px-6 py-3 rounded-xl shadow-sm active:scale-[0.98] disabled:opacity-50 transition-all cursor-pointer whitespace-nowrap"
                >
                  {loading ? "Writing to DB..." : "Generate Token String"}
                </button>
              </form>
            </section>

            {/* --- 3. ACTIVE TOKENS LEDGER DATA GRID LIST --- */}
            <section className="bg-white border border-slate-200 rounded-2xl overflow-hidden shadow-sm">
              <div className="px-6 py-4 border-b border-slate-200 bg-slate-50 flex items-center justify-between">
                <h3 className="text-base font-bold text-slate-900">
                  Your Managed Application Connections
                </h3>
                <span className="text-xs font-semibold text-slate-500 bg-slate-200 border border-slate-300 px-2 py-0.5 rounded-md font-mono">
                  Total: {apiKeys.length}
                </span>
              </div>
              
              <div className="divide-y divide-slate-200">
                {/* State Handler Case A: Async processing in progress */}
                {fetching ? (
                  <div className="p-10 text-center text-slate-500 font-medium animate-pulse tracking-wide">
                    Loading secure tokens ledger cache from PostgreSQL pipeline...
                  </div>
                ) : 
                /* State Handler Case B: Table empty */
                apiKeys.length === 0 ? (
                  <div className="p-12 text-center text-slate-400 font-medium italic space-y-2">
                    <p className="text-slate-500 font-semibold not-italic">No credential records discovered.</p>
                    <p className="text-xs text-slate-400">Mint your first unique API token using the generator cockpit above.</p>
                  </div>
                ) : (
                  /* State Handler Case C: Dynamic Rows Output */
                  apiKeys.map((key) => (
                    <div 
                      key={key.id} 
                      className="p-6 flex flex-col md:flex-row md:items-center justify-between gap-5 hover:bg-slate-50/60 transition-colors"
                    >
                      {/* Row Left: Text Metadata Metrics */}
                      <div className="space-y-2 flex-1 min-w-0">
                        <div className="flex items-center gap-3">
                          <h4 className="font-bold text-slate-900 truncate text-base">
                            {key.name}
                          </h4>
                          <span className={`inline-flex items-center text-xs font-bold px-2.5 py-0.5 rounded-full border ${
                            key.is_active 
                              ? 'bg-emerald-50 text-emerald-700 border-emerald-200' 
                              : 'bg-slate-100 text-slate-500 border-slate-200'
                          }`}>
                            {key.is_active ? 'Active' : 'Revoked'}
                          </span>
                        </div>
                        
                        {/* Safe Mobile Text Overflow Code Horizontal Row */}
                        <div className="w-full overflow-x-auto rounded-xl border border-slate-200 bg-slate-50 p-3 shadow-inner">
                          <code className="text-cyan-800 text-xs font-mono block whitespace-nowrap min-w-max select-all">
                            {key.key_value}
                          </code>
                        </div>
                      </div>
                      
                      {/* Row Right: Interactive State Mutators */}
                      <div className="flex-shrink-0 w-full md:w-auto self-end md:self-center">
                        {key.is_active ? (
                          <button 
                            onClick={() => handleRevokeToken(key.id)}
                            className="w-full md:w-auto border border-red-200 text-red-600 hover:bg-red-50 px-4 py-2 rounded-xl text-sm font-semibold transition-colors active:scale-[0.98] cursor-pointer"
                          >
                            Revoke Key Permissions
                          </button>
                        ) : (
                          <span className="text-sm text-slate-400 font-semibold italic block text-center md:text-right md:px-4">
                            Permanently Inactive
                          </span>
                        )}
                      </div>
                    </div>
                  ))
                )}
              </div>
            </section>
          </div>
        )}
      </div>
      </main> 
    </div> 
  )}
