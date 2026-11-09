import React, { useState } from 'react';
import { NavLink, Outlet, useLocation } from 'react-router-dom';
import {
  ShieldAlert,
  LayoutDashboard,
  Search,
  FolderKanban,
  FileSearch,
  Database,
  Cpu,
  CheckCircle,
  FileText,
  BarChart3,
  Play,
  RotateCcw,
  Check,
  AlertTriangle,
  UserCheck,
  ChevronDown
} from 'lucide-react';
import { api } from '../services/api';

const NAV_ITEMS = [
  { path: '/', label: 'Command Centre', icon: LayoutDashboard },
  { path: '/detection', label: 'Threat Detection', icon: Search },
  { path: '/incidents', label: 'Incident Management', icon: FolderKanban },
  { path: '/investigation', label: 'Investigation Workspace', icon: FileSearch },
  { path: '/intel', label: 'Threat Intelligence', icon: Database },
  { path: '/agents', label: 'Agent Operations', icon: Cpu },
  { path: '/response', label: 'Response Centre', icon: CheckCircle },
  { path: '/audit', label: 'Audit Centre', icon: FileText },
  { path: '/analytics', label: 'Analytics & Evaluation', icon: BarChart3 },
];

export const AppLayout: React.FC = () => {
  const [scenarioLoading, setScenarioLoading] = useState(false);
  const [scenarioBanner, setScenarioBanner] = useState<{ msg: string; type: 'success' | 'warn' } | null>(null);
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const location = useLocation();

  const handleRunScenario = async (scenarioType: string) => {
    setScenarioLoading(true);
    setDropdownOpen(false);
    try {
      const res = await api.runScenario(scenarioType, false);
      setScenarioBanner({
        msg: `Executed ${res.scenario_name}: Generated ${res.events_generated} events, triggered ${res.detections_triggered} detections, created ${res.incidents_created} incident(s).`,
        type: res.uncertainty_flagged ? 'warn' : 'success'
      });
      // Force page refresh or let state update
      setTimeout(() => {
        window.dispatchEvent(new Event('refresh_gas_data'));
      }, 300);
    } catch (err: any) {
      setScenarioBanner({ msg: `Scenario error: ${err.message}`, type: 'warn' });
    } finally {
      setScenarioLoading(false);
    }
  };

  const handleReset = async () => {
    if (!window.confirm("Reset demonstration database back to clean baseline state?")) return;
    setScenarioLoading(true);
    try {
      await api.resetDatabase();
      setScenarioBanner({ msg: 'Database reset cleanly to baseline state.', type: 'success' });
      window.dispatchEvent(new Event('refresh_gas_data'));
    } catch (err: any) {
      setScenarioBanner({ msg: `Reset error: ${err.message}`, type: 'warn' });
    } finally {
      setScenarioLoading(false);
    }
  };

  return (
    <div className="flex h-screen bg-[#F8FAFC] overflow-hidden text-slate-800">
      {/* Sidebar Navigation */}
      <aside className="w-64 bg-[#10243A] text-slate-200 flex flex-col border-r border-slate-800 shrink-0">
        {/* Brand Header */}
        <div className="p-4 border-b border-slate-800 flex items-center gap-3">
          <div className="bg-[#1769AA] p-2 rounded text-white shadow-sm">
            <ShieldAlert className="w-6 h-6" />
          </div>
          <div>
            <h1 className="font-bold text-sm tracking-wide text-white uppercase">GUARDIAN ANGEL</h1>
            <p className="text-[10px] text-slate-400 font-mono">GAS PLATFORM • TECHgium '26</p>
          </div>
        </div>

        {/* Sub-Brand Metadata */}
        <div className="px-4 py-2 bg-[#0A1929] text-[11px] text-slate-400 border-b border-slate-800 flex justify-between items-center">
          <span>L&T Technology Services</span>
          <span className="font-mono text-emerald-400 font-medium">LIVE</span>
        </div>

        {/* Navigation Links */}
        <nav className="flex-1 overflow-y-auto py-3 px-2 space-y-1">
          {NAV_ITEMS.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.path || (item.path !== '/' && location.pathname.startsWith(item.path));
            return (
              <NavLink
                key={item.path}
                to={item.path}
                className={`flex items-center gap-3 px-3 py-2.5 text-xs font-medium rounded transition-colors ${
                  isActive
                    ? 'bg-[#1769AA] text-white font-semibold shadow-sm'
                    : 'text-slate-300 hover:bg-[#1C334D] hover:text-white'
                }`}
              >
                <Icon className={`w-4 h-4 ${isActive ? 'text-white' : 'text-slate-400'}`} />
                <span>{item.label}</span>
              </NavLink>
            );
          })}
        </nav>

        {/* Core Philosophy Footer */}
        <div className="p-3 border-t border-slate-800 text-[10px] text-slate-400 bg-[#0A1929] leading-tight">
          <div className="font-semibold text-slate-300 uppercase tracking-wider mb-1">Guiding Principle</div>
          <div className="font-mono text-[9px] text-[#4B8FCB]">DETECT • CORRELATE • INVESTIGATE • EXPLAIN • GOVERN • PROTECT</div>
        </div>
      </aside>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        {/* Top Operational Bar */}
        <header className="h-14 bg-white border-b border-slate-200 px-6 flex items-center justify-between shrink-0 shadow-xs">
          <div className="flex items-center gap-4">
            <div className="text-xs font-semibold text-slate-700 uppercase tracking-wider">
              Security Operations Centre
            </div>
            <div className="h-4 w-px bg-slate-200"></div>
            <div className="flex items-center gap-2 text-xs text-emerald-700 bg-emerald-50 px-2.5 py-1 rounded border border-emerald-200 font-medium">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
              All 6 Multi-Agent Subsystems Active
            </div>
          </div>

          {/* Quick Scenario Runner Controls */}
          <div className="flex items-center gap-3">
            <div className="relative">
              <button
                onClick={() => setDropdownOpen(!dropdownOpen)}
                disabled={scenarioLoading}
                className="flex items-center gap-2 px-3 py-1.5 bg-[#1769AA] hover:bg-[#125387] text-white text-xs font-medium rounded transition shadow-xs disabled:opacity-50"
              >
                <Play className="w-3.5 h-3.5 fill-current" />
                <span>Run Demo Scenario</span>
                <ChevronDown className="w-3.5 h-3.5" />
              </button>

              {dropdownOpen && (
                <div className="absolute right-0 mt-1 w-72 bg-white rounded border border-slate-200 shadow-lg py-1 z-50 text-xs">
                  <div className="px-3 py-1.5 font-semibold text-slate-500 uppercase tracking-wider border-b border-slate-100">
                    Repeatable Attack Scenarios
                  </div>
                  <button
                    onClick={() => handleRunScenario('SCENARIO_A_PHISHING')}
                    className="w-full text-left px-3 py-2 hover:bg-slate-50 flex flex-col text-slate-800"
                  >
                    <span className="font-semibold text-slate-900">Scenario A: Phishing & Credential Compromise</span>
                    <span className="text-[11px] text-slate-500">Phish lure, 3 brute fails, compromise & C2 beacon</span>
                  </button>
                  <button
                    onClick={() => handleRunScenario('SCENARIO_B_LATERAL')}
                    className="w-full text-left px-3 py-2 hover:bg-slate-50 flex flex-col text-slate-800 border-t border-slate-100"
                  >
                    <span className="font-semibold text-slate-900">Scenario B: Lateral Movement</span>
                    <span className="text-[11px] text-slate-500">Encoded PS, local admin elevation, PsExec on DB host</span>
                  </button>
                  <button
                    onClick={() => handleRunScenario('SCENARIO_C_FALSE_POSITIVE')}
                    className="w-full text-left px-3 py-2 hover:bg-slate-50 flex flex-col text-slate-800 border-t border-slate-100"
                  >
                    <span className="font-semibold text-slate-900">Scenario C: Benign Activity (False Positive)</span>
                    <span className="text-[11px] text-slate-500">Automated backup script context analysis</span>
                  </button>
                  <button
                    onClick={() => handleRunScenario('SCENARIO_D_MALFORMED')}
                    className="w-full text-left px-3 py-2 hover:bg-slate-50 flex flex-col text-slate-800 border-t border-slate-100"
                  >
                    <span className="font-semibold text-purple-900">Scenario D: Missing/Manipulated Telemetry</span>
                    <span className="text-[11px] text-slate-500">Missing timestamps, untrusted proxy, human review escalation</span>
                  </button>
                </div>
              )}
            </div>

            <button
              onClick={handleReset}
              disabled={scenarioLoading}
              title="Reset database to baseline"
              className="flex items-center gap-1.5 px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-medium rounded border border-slate-300 transition"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              <span>Reset</span>
            </button>

            <div className="h-4 w-px bg-slate-200"></div>

            {/* Analyst Account */}
            <div className="flex items-center gap-2 pl-2">
              <div className="w-7 h-7 rounded bg-[#10243A] text-white flex items-center justify-center font-bold text-xs">
                SJ
              </div>
              <div className="text-left text-xs">
                <div className="font-semibold text-slate-900">Sarah Jenkins</div>
                <div className="text-[10px] text-slate-500">Senior SOC Analyst</div>
              </div>
            </div>
          </div>
        </header>

        {/* Global Scenario Banner Notification */}
        {scenarioBanner && (
          <div
            className={`px-6 py-2 text-xs flex items-center justify-between border-b ${
              scenarioBanner.type === 'warn'
                ? 'bg-amber-50 text-amber-900 border-amber-200'
                : 'bg-emerald-50 text-emerald-900 border-emerald-200'
            }`}
          >
            <div className="flex items-center gap-2">
              {scenarioBanner.type === 'warn' ? (
                <AlertTriangle className="w-4 h-4 text-amber-600 shrink-0" />
              ) : (
                <Check className="w-4 h-4 text-emerald-600 shrink-0" />
              )}
              <span>{scenarioBanner.msg}</span>
            </div>
            <button
              onClick={() => setScenarioBanner(null)}
              className="font-bold text-slate-400 hover:text-slate-600 ml-4"
            >
              ✕
            </button>
          </div>
        )}

        {/* Page Content */}
        <main className="flex-1 overflow-y-auto p-6 bg-[#F8FAFC]">
          <Outlet />
        </main>
      </div>
    </div>
  );
};
