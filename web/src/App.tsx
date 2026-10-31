import React, { useState, useEffect } from 'react';
import { fetchMetrics, fetchSystemInfo, fetchDiagnostics, MetricSnapshot, SystemInfo, Finding } from './api';
import { 
  Activity, Cpu, HardDrive, Shield, Server, Box, Terminal,
  RefreshCw, CheckCircle, AlertTriangle, AlertCircle
} from 'lucide-react';

export function App() {
  const [metrics, setMetrics] = useState<MetricSnapshot | null>(null);
  const [info, setInfo] = useState<SystemInfo | null>(null);
  const [findings, setFindings] = useState<Finding[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'overview' | 'diagnostics' | 'security'>('overview');

  const loadData = async () => {
    try {
      const [m, i, f] = await Promise.all([
        fetchMetrics().catch(() => null),
        fetchSystemInfo().catch(() => null),
        fetchDiagnostics().catch(() => [])
      ]);
      if (m) setMetrics(m);
      if (i) setInfo(i);
      setFindings(f || []);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
    const timer = setInterval(loadData, 3000);
    return () => clearInterval(timer);
  }, []);

  const cpuPercent = metrics?.cpu?.percent ?? 0;
  const memPercent = metrics?.memory?.percent ?? 0;
  const healthScore = Math.max(0, 100 - Math.round((cpuPercent * 0.4 + memPercent * 0.4)));

  return (
    <div className="flex h-screen bg-[#070a11] text-slate-100 overflow-hidden font-sans">
      {/* Sidebar */}
      <aside className="w-64 border-r border-slate-800/80 bg-[#0b0f19]/90 flex flex-col justify-between p-4">
        <div>
          <div className="flex items-center gap-3 px-2 py-4 border-b border-slate-800">
            <div className="w-9 h-9 rounded-lg bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center text-cyan-400">
              <Activity className="w-5 h-5 animate-pulse" />
            </div>
            <div>
              <div className="font-extrabold text-base tracking-wider bg-gradient-to-r from-cyan-400 to-sky-300 bg-clip-text text-transparent">
                NEXUS 2.0
              </div>
              <div className="text-[10px] text-slate-400 tracking-widest font-mono uppercase">Observability</div>
            </div>
          </div>

          <nav className="mt-6 space-y-1">
            <button
              onClick={() => setActiveTab('overview')}
              className={w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors \}
            >
              <Server className="w-4 h-4" /> Host Overview
            </button>
            <button
              onClick={() => setActiveTab('diagnostics')}
              className={w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors \}
            >
              <AlertTriangle className="w-4 h-4" /> Diagnostics ({findings.length})
            </button>
            <button
              onClick={() => setActiveTab('security')}
              className={w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors \}
            >
              <Shield className="w-4 h-4" /> Defensive Security
            </button>
          </nav>
        </div>

        <div className="border-t border-slate-800/80 pt-4 px-2 text-xs text-slate-500 font-mono">
          <div>Host: {info?.hostname || 'Connecting...'}</div>
          <div>OS: {info?.os || 'Local Platform'}</div>
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="flex-1 flex flex-col overflow-auto bg-gradient-to-b from-[#0b0f19] to-[#070a11]">
        {/* Top Header */}
        <header className="h-16 border-b border-slate-800/60 px-8 flex items-center justify-between backdrop-blur bg-[#0b0f19]/40 sticky top-0 z-10">
          <div className="flex items-center gap-3">
            <h1 className="font-bold text-lg text-slate-200 capitalize">{activeTab}</h1>
            <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping"></span> Live Telemetry
            </span>
          </div>
          <button 
            onClick={loadData}
            className="flex items-center gap-2 px-3 py-1.5 rounded-lg border border-slate-700 bg-slate-800/60 hover:bg-slate-700/60 text-xs font-medium text-slate-300 transition-colors"
          >
            <RefreshCw className={w-3.5 h-3.5 \} /> Sync
          </button>
        </header>

        {/* Content Body */}
        <div className="p-8 space-y-6 max-w-7xl w-full mx-auto">
          {/* Executive Metrics Grid */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="p-5 rounded-xl border border-slate-800 bg-[#101726]/70 backdrop-blur">
              <div className="text-xs uppercase tracking-wider text-slate-400 font-semibold mb-1 flex items-center justify-between">
                <span>Health Score</span>
                <CheckCircle className="w-4 h-4 text-emerald-400" />
              </div>
              <div className="text-3xl font-extrabold text-emerald-400 font-mono mt-2">
                {healthScore} <span className="text-sm font-normal text-slate-500">/ 100</span>
              </div>
              <div className="text-xs text-slate-500 mt-2">Deterministic multi-metric score</div>
            </div>

            <div className="p-5 rounded-xl border border-slate-800 bg-[#101726]/70 backdrop-blur">
              <div className="text-xs uppercase tracking-wider text-slate-400 font-semibold mb-1 flex items-center justify-between">
                <span>CPU Load</span>
                <Cpu className="w-4 h-4 text-cyan-400" />
              </div>
              <div className="text-3xl font-extrabold text-cyan-400 font-mono mt-2">
                {cpuPercent.toFixed(1)}%
              </div>
              <div className="text-xs text-slate-500 mt-2">{info?.logical_cores || 0} Cores Active</div>
            </div>

            <div className="p-5 rounded-xl border border-slate-800 bg-[#101726]/70 backdrop-blur">
              <div className="text-xs uppercase tracking-wider text-slate-400 font-semibold mb-1 flex items-center justify-between">
                <span>Memory Pressure</span>
                <HardDrive className="w-4 h-4 text-sky-400" />
              </div>
              <div className="text-3xl font-extrabold text-sky-400 font-mono mt-2">
                {memPercent.toFixed(1)}%
              </div>
              <div className="text-xs text-slate-500 mt-2">RAM utilization</div>
            </div>

            <div className="p-5 rounded-xl border border-slate-800 bg-[#101726]/70 backdrop-blur">
              <div className="text-xs uppercase tracking-wider text-slate-400 font-semibold mb-1 flex items-center justify-between">
                <span>Active Findings</span>
                <AlertCircle className="w-4 h-4 text-amber-400" />
              </div>
              <div className="text-3xl font-extrabold text-amber-400 font-mono mt-2">
                {findings.length}
              </div>
              <div className="text-xs text-slate-500 mt-2">System diagnostics</div>
            </div>
          </div>

          {/* Diagnostic Findings Section */}
          <div className="rounded-xl border border-slate-800 bg-[#101726]/70 p-6 backdrop-blur">
            <h2 className="text-base font-bold text-slate-200 mb-4 flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 text-amber-400" /> Diagnostic Evidence & Remediation
            </h2>
            {findings.length === 0 ? (
              <div className="py-8 text-center text-slate-500 text-sm">
                No active anomalies or resource bottlenecks detected. System operating inside optimal thresholds.
              </div>
            ) : (
              <div className="divide-y divide-slate-800/80">
                {findings.map((f, i) => (
                  <div key={i} className="py-3 flex items-start justify-between gap-4">
                    <div>
                      <div className="flex items-center gap-2">
                        <span className={px-2 py-0.5 rounded text-[10px] uppercase font-bold tracking-wider \}>
                          {f.severity}
                        </span>
                        <span className="font-semibold text-sm text-slate-200">{f.description}</span>
                      </div>
                      <div className="text-xs text-slate-400 mt-1 pl-1">
                        Remediation: <span className="text-cyan-400">{f.suggested_action || 'Inspect related host processes'}</span>
                      </div>
                    </div>
                    <div className="text-xs font-mono text-slate-500">[{f.category}]</div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
export default App;