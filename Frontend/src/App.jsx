import React, { useState, useEffect } from 'react';
import { apiService } from './services/api';

export default function App() {
  const [view, setView] = useState('signup'); // signup, login, dashboard
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [projects, setProjects] = useState([]);
  const [activeProject, setActiveProject] = useState(null);
  const [keys, setKeys] = useState([]);
  const [analytics, setAnalytics] = useState(null);
  const [logs, setLogs] = useState([]);
  
  // Creation States
  const [projName, setProjName] = useState('');
  const [projRpm, setProjRpm] = useState(60);
  const [keyName, setKeyName] = useState('');
  const [keyEnv, setKeyEnv] = useState('Development');
  const [keyScopes, setKeyScopes] = useState(['read']);
  const [latestRawKey, setLatestRawKey] = useState(null);

  // Playground States
  const [playEndpoint, setPlayEndpoint] = useState('/products');
  const [playMethod, setPlayMethod] = useState('GET');
  const [playToken, setPlayToken] = useState('');
  const [playResponse, setPlayResponse] = useState(null);

  useEffect(() => {
    if (apiService.getToken()) { setView('dashboard'); loadWorkspace(); }
  }, []);

  useEffect(() => {
    if (activeProject) { loadProjectDetails(activeProject.id); }
  }, [activeProject]);

  const loadWorkspace = async () => {
    try {
      const data = await apiService.listProjects();
      
      // ✅ Critical Safety Rule: If data is an error or not an array, wipe the state
      if (!Array.isArray(data)) {
        handleLogout();
        return;
      }
      
      setProjects(data);
      if (data.length > 0 && !activeProject) {
        setActiveProject(data[0]); // Explicitly bind the first project object element
      }
    } catch (e) { 
      handleLogout(); 
    }
  };

  const loadProjectDetails = async (pId) => {
    setLatestRawKey(null);
    setKeys(await apiService.getKeys(pId));
    setAnalytics(await apiService.getAnalytics(pId));
    setLogs(await apiService.getLogs(pId));
  };

  const handleSignup = async (e) => {
    e.preventDefault();
    try { await apiService.signup(email, password); setView('login'); alert("Registered successfully!"); } 
    catch (err) { alert(err.message); }
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    try { await apiService.login(email, password); setView('dashboard'); loadWorkspace(); } 
    catch (err) { alert(err.message); }
  };

  const handleCreateProject = async (e) => {
    e.preventDefault();
    await apiService.createProject(projName, projRpm);
    setProjName('');
    loadWorkspace();
  };

  const handleGenerateKey = async (e) => {
    e.preventDefault();
    const data = await apiService.generateKey(activeProject.id, keyName, keyEnv, keyScopes);
    setKeyName('');
    setLatestRawKey(data.raw_key);
    loadProjectDetails(activeProject.id);
  };

  const handleDeactivateKey = async (kId) => {
    await apiService.deactivateKey(activeProject.id, kId);
    loadProjectDetails(activeProject.id);
  };

  const handleRotateKey = async (kId) => {
    const data = await apiService.rotateKey(activeProject.id, kId);
    setLatestRawKey(data.raw_key);
    loadProjectDetails(activeProject.id);
  };

  const handleTriggerPlayground = async () => {
    // 1. Fire the playground gateway simulator call
    const res = await apiService.triggerGatewayMock(playEndpoint, playMethod, playToken);
    setPlayResponse(res);
    
    // 2. ✅ Auto-Refresh: Instantly pull newly computed backend numbers out of PostgreSQL
    if (activeProject) {
      setTimeout(() => {
        loadProjectDetails(activeProject.id);
      }, 150); // Small 150ms buffer to allow the async background task to commit the row cleanly
    }
  };



  const handleLogout = () => {
    apiService.clearToken(); setProjects([]); setActiveProject(null); setKeys([]); setAnalytics(null); setLogs([]); setView('signup');
  };

  return (
    <div className="min-h-screen bg-slate-50 text-slate-800 font-sans antialiased selection:bg-cyan-200">
      <nav className="border-b border-slate-200 bg-white sticky top-0 z-50 shadow-sm px-6 h-16 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="h-9 w-9 bg-gradient-to-tr from-cyan-600 to-blue-600 rounded-xl flex items-center justify-center font-bold text-white shadow-md">KS</div>
          <span className="text-xl font-bold text-slate-900">KeyShield Advanced SaaS Console</span>
        </div>
        {view === 'dashboard' && (
          <button onClick={handleLogout} className="text-sm font-semibold text-slate-600 hover:text-slate-900 border border-slate-200 px-3 py-1.5 rounded-xl bg-white shadow-sm cursor-pointer">Log Out</button>
        )}
      </nav>

      <main className="max-w-7xl mx-auto px-4 py-10">
        {view === 'signup' && (
          <div className="max-w-md mx-auto bg-white border border-slate-200 p-8 rounded-2xl shadow-sm">
            <h2 className="text-2xl font-extrabold text-slate-900 mb-6">Create Account</h2>
            <form onSubmit={handleSignup} className="space-y-4">
              <input type="email" placeholder="email@example.com" className="w-full border border-slate-300 rounded-xl px-4 py-2.5" value={email} onChange={e => setEmail(e.target.value)} required />
              <input type="password" placeholder="••••••••" className="w-full border border-slate-300 rounded-xl px-4 py-2.5" value={password} onChange={e => setPassword(e.target.value)} required />
              <button type="submit" className="w-full bg-gradient-to-r from-cyan-600 to-blue-600 text-white font-semibold py-3 rounded-xl cursor-pointer">Register Profile</button>
            </form>
            <p className="mt-4 text-center text-sm">Have an account? <button onClick={() => setView('login')} className="text-cyan-600 font-bold hover:underline">Log In</button></p>
          </div>
        )}

        {view === 'login' && (
          <div className="max-w-md mx-auto bg-white border border-slate-200 p-8 rounded-2xl shadow-sm">
            <h2 className="text-2xl font-extrabold text-slate-900 mb-6">Developer Authentication</h2>
            <form onSubmit={handleLogin} className="space-y-4">
              <input type="email" placeholder="email@example.com" className="w-full border border-slate-300 rounded-xl px-4 py-2.5" value={email} onChange={e => setEmail(e.target.value)} required />
              <input type="password" placeholder="••••••••" className="w-full border border-slate-300 rounded-xl px-4 py-2.5" value={password} onChange={e => setPassword(e.target.value)} required />
              <button type="submit" className="w-full bg-gradient-to-r from-cyan-600 to-blue-600 text-white font-semibold py-3 rounded-xl cursor-pointer">Access Console</button>
            </form>
          </div>
        )}

        {view === 'dashboard' && (
          <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
            <div className="space-y-6">
              <div className="bg-white border border-slate-200 p-6 rounded-2xl shadow-sm">
                <h3 className="font-bold text-slate-900 mb-3">Your Projects</h3>
                <div className="space-y-2">
                  {projects.map(p => (
                    <button key={p.id} onClick={() => setActiveProject(p)} className={`w-full text-left px-4 py-2.5 rounded-xl text-sm font-semibold border ${activeProject?.id === p.id ? 'bg-cyan-50 border-cyan-200 text-cyan-800' : 'bg-white border-slate-200 text-slate-700 hover:bg-slate-50'}`}>{p.name}</button>
                  ))}
                </div>
                <form onSubmit={handleCreateProject} className="mt-4 space-y-2 pt-4 border-t border-slate-100">
                  <input type="text" placeholder="Project Name" className="w-full border border-slate-200 rounded-lg px-3 py-1.5 text-sm" value={projName} onChange={e => setProjName(e.target.value)} required />
                  <input type="number" placeholder="RPM Limit" className="w-full border border-slate-200 rounded-lg px-3 py-1.5 text-sm" value={projRpm} onChange={e => setProjRpm(e.target.value)} required />
                  <button type="submit" className="w-full bg-slate-900 text-white rounded-lg py-2 text-xs font-bold cursor-pointer">Add Project</button>
                </form>
              </div>
            </div>

            <div className="lg:grid-cols-1 lg:col-span-3 space-y-8">
              {activeProject && (
                <>
                  <div className="bg-white border border-slate-200 p-6 rounded-2xl shadow-sm">
                    <h2 className="text-2xl font-black text-slate-900 mb-1">{activeProject.name} Workspace Dashboard</h2>
                    <p className="text-slate-500 text-sm">Configured Max Rate Limit Strategy Constraints: **{activeProject.rate_limit_rpm} RPM**</p>
                  </div>
                
                  {analytics && (
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                      <div className="bg-white border border-slate-200 p-4 rounded-xl shadow-sm"><p className="text-xs font-bold text-slate-500 uppercase">Total Logged Calls</p><p className="text-2xl font-black text-slate-900 mt-1">{analytics.total_requests}</p></div>
                      <div className="bg-white border border-slate-200 p-4 rounded-xl shadow-sm"><p className="text-xs font-bold text-slate-500 uppercase">Success (2xx)</p><p className="text-2xl font-black text-emerald-600 mt-1">{analytics.success_count}</p></div>
                      <div className="bg-white border border-slate-200 p-4 rounded-xl shadow-sm"><p className="text-xs font-bold text-slate-500 uppercase">Failed Errors</p><p className="text-2xl font-black text-red-600 mt-1">{analytics.failed_count}</p></div>
                      <div className="bg-white border border-slate-200 p-4 rounded-xl shadow-sm">
                          <p className="text-xs font-bold text-slate-500 uppercase">Avg Response Duration</p>
                          <p className="text-2xl font-black text-cyan-600 mt-1">
                            {analytics && analytics.avg_response_time_ms !== undefined 
                              ? `${Number(analytics.avg_response_time_ms).toFixed(1)} ms` 
                              : '0.0 ms'}
                          </p>
                        </div>
                      </div>
                  )}

                  {latestRawKey && (
                    <div className="p-4 bg-amber-50 border border-amber-200 text-amber-800 rounded-xl space-y-2">
                      <p className="text-sm font-bold">⚠️ Security Notice: Copy your raw secret key now. It will never be displayed again.</p>
                    </div>  
                  )}
                                    {/* --- 1. GENERATE STRUCTURAL ENVIRONMENT KEY FORM --- */}
                  <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm">
                    <h3 className="font-bold text-slate-900 mb-4">Generate Structural Environment Key</h3>
                    <form onSubmit={handleGenerateKey} className="flex flex-wrap gap-4 items-center">
                      <input 
                        type="text" 
                        placeholder="Key Descriptor" 
                        className="border border-slate-300 rounded-xl px-3 py-2 text-sm focus:outline-none focus:border-cyan-600" 
                        value={keyName} 
                        onChange={e => setKeyName(e.target.value)} 
                        required 
                      />
                      <select 
                        className="border border-slate-300 rounded-xl px-3 py-2 text-sm bg-white focus:outline-none focus:border-cyan-600" 
                        value={keyEnv} 
                        onChange={e => setKeyEnv(e.target.value)}
                      >
                        <option value="Development">Development</option>
                        <option value="Staging">Staging</option>
                        <option value="Production">Production</option>
                      </select>
                      
                      <div className="flex gap-3 text-xs font-bold text-slate-700">
                        {['read', 'write', 'delete'].map(s => (
                          <label key={s} className="flex items-center gap-1.5 cursor-pointer">
                            <input 
                              type="checkbox" 
                              className="accent-cyan-600"
                              checked={keyScopes.includes(s)} 
                              onChange={e => setKeyScopes(e.target.checked ? [...keyScopes, s] : keyScopes.filter(x => x !== s))} 
                            /> 
                            {s.toUpperCase()}
                          </label>
                        ))}
                      </div>
                      
                      <button type="submit" className="bg-cyan-600 text-white text-xs font-bold px-4 py-2 rounded-xl shadow-sm cursor-pointer ml-auto hover:bg-cyan-500 transition-colors">
                        Mint Key
                      </button>
                    </form>
                  </div>

                  {/* --- 2. ACTIVE STRUCTURAL KEY REGISTRY LIST --- */}
                  <div className="bg-white border border-slate-200 rounded-2xl overflow-hidden shadow-sm">
                    <div className="px-6 py-4 bg-slate-50 border-b border-slate-200">
                      <h3 className="font-bold text-slate-900">Active Structural Key Registry</h3>
                    </div>
                    <div className="divide-y divide-slate-200">
                      {keys.map(k => (
                        <div key={k.id} className="p-6 flex flex-col md:flex-row md:items-center justify-between gap-4">
                          <div className="space-y-1">
                            <div className="flex items-center gap-2">
                              <h4 className="font-bold text-slate-900">{k.name}</h4>
                              <span className="text-xs bg-slate-100 border border-slate-200 px-2 py-0.5 rounded font-bold text-slate-600">
                                {k.environment}
                              </span>
                              <span className={`text-xs border px-2 py-0.5 rounded font-bold ${
                                k.is_active 
                                  ? 'bg-emerald-50 text-emerald-700 border-emerald-200' 
                                  : 'bg-slate-100 text-slate-400 border-slate-200'
                              }`}>
                                {k.is_active ? 'Live' : 'Revoked'}
                              </span>
                            </div>
                            <div className="flex gap-4 text-xs font-mono text-slate-500">
                              <span>Prefix: <code>{k.key_prefix}</code></span>
                              <span>Scopes: <code>{k.scopes}</code></span>
                            </div>
                          </div>
                          
                          {k.is_active && (
                            <div className="flex gap-2">
                              <button onClick={() => handleRotateKey(k.id)} className="border border-slate-200 text-slate-700 hover:bg-slate-50 px-3 py-1.5 rounded-lg text-xs font-bold cursor-pointer transition-colors">
                                Rotate
                              </button>
                              <button onClick={() => handleDeactivateKey(k.id)} className="border border-red-200 text-red-600 hover:bg-red-50 px-3 py-1.5 rounded-lg text-xs font-bold cursor-pointer transition-colors">
                                Revoke
                              </button>
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* --- 3. DEVELOPER SANDBOX INGEST TESTING PLAYGROUND --- */}
                  <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm space-y-4">
                    <h3 className="font-bold text-slate-900">Developer Ingest Testing Playground</h3>
                    <div className="flex flex-wrap gap-4 items-center">
                      <select 
                        className="border border-slate-300 rounded-xl px-3 py-2 text-sm bg-white focus:outline-none focus:border-cyan-600" 
                        value={playMethod} 
                        onChange={e => setPlayMethod(e.target.value)}
                      >
                        <option value="GET">GET</option>
                        <option value="POST">POST</option>
                        <option value="DELETE">DELETE</option>
                      </select>
                      <input 
                        type="text" 
                        className="border border-slate-300 rounded-xl px-3 py-2 text-sm flex-1 min-w-[200px] focus:outline-none focus:border-cyan-600" 
                        value={playEndpoint} 
                        onChange={e => setPlayEndpoint(e.target.value)} 
                        placeholder="/products or /products/1" 
                      />
                      <input 
                        type="text" 
                        className="border border-slate-300 rounded-xl px-3 py-2 text-sm w-64 focus:outline-none focus:border-cyan-600" 
                        value={playToken} 
                        onChange={e => setPlayToken(e.target.value)} 
                        placeholder="Paste X-API-Key (ks_...)" 
                      />
                      <button onClick={handleTriggerPlayground} className="bg-slate-900 text-white px-4 py-2 rounded-xl text-xs font-bold cursor-pointer hover:bg-slate-800 transition-colors">
                        Send Request
                      </button>
                    </div>
                    
                    {playResponse && (
                      <div className="rounded-xl border border-slate-200 bg-slate-950 p-4 font-mono text-xs text-cyan-400 space-y-1">
                        <p className="font-bold text-slate-400">
                          Response Status: <span className={playResponse.error ? 'text-red-400' : 'text-emerald-400'}>{playResponse.status}</span>
                        </p>
                        <pre className="overflow-x-auto whitespace-pre-wrap">{JSON.stringify(playResponse.payload, null, 2)}</pre>
                      </div>
                    )}
                  </div>
                </> 
              )}
            </div>
          </div> 
        )}
      </main>

    </div>
  )}
  