import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  ShieldAlert,
  AlertTriangle,
  Activity,
  CheckCircle2,
  Clock,
  ArrowRight,
  TrendingUp,
  Server,
  Layers,
  Cpu
} from 'lucide-react';
import { api } from '../services/api';
import { AnalyticsSummary, Incident, AgentStatus, RecommendedAction } from '../types';
import { SeverityBadge, StatusBadge, ConfidenceBadge } from '../components/Badges';

export const CommandCentre: React.FC = () => {
  const navigate = useNavigate();
  const [analytics, setAnalytics] = useState<AnalyticsSummary | null>(null);
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [agents, setAgents] = useState<AgentStatus[]>([]);
  const [pendingActions, setPendingActions] = useState<RecommendedAction[]>([]);
  const [loading, setLoading] = useState(true);

  const loadData = async () => {
    try {
      const [anData, incData, agData, actData] = await Promise.all([
        api.getAnalyticsSummary(),
        api.getIncidents({ limit: 10 }),
        api.getAgentsStatus(),
        api.getRecommendedActions({ status: 'PENDING_APPROVAL' })
      ]);
      setAnalytics(anData);
      setIncidents(incData);
      setAgents(agData);
      setPendingActions(actData);
    } catch (err) {
      console.error('Failed to load Command Centre data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
    const handleRefresh = () => loadData();
    window.addEventListener('refresh_gas_data', handleRefresh);
    return () => window.removeEventListener('refresh_gas_data', handleRefresh);
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64 text-slate-400 text-xs font-mono">
        LOADING REAL-TIME SOC TELEMETRY...
      </div>
    );
  }

  const criticalCount = incidents.filter(i => i.severity === 'CRITICAL').length;

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header Banner */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-slate-900 tracking-tight">Security Command Centre</h2>
          <p className="text-xs text-slate-500">
            Real-time unified threat detection, multi-agent correlation, and human-in-the-loop governance
          </p>
        </div>
        <div className="text-right">
          <div className="text-xs font-mono text-slate-500">OPERATIONAL TICK</div>
          <div className="text-xs font-semibold text-slate-800">{new Date().toLocaleTimeString()} UTC</div>
        </div>
      </div>

      {/* Pending Human Approval Banner if consequential actions are queued */}
      {pendingActions.length > 0 && (
        <div className="bg-amber-50 border border-amber-300 rounded p-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-amber-200 text-amber-900 rounded">
              <AlertTriangle className="w-5 h-5" />
            </div>
            <div>
              <div className="text-xs font-bold text-amber-900 uppercase tracking-wide">
                HUMAN GOVERNANCE GATE: {pendingActions.length} RESPONSE ACTION(S) AWAITING ANALYST APPROVAL
              </div>
              <div className="text-xs text-amber-800">
                Deterministic policy enforces explicit human verification before consequential host isolation or account lockout.
              </div>
            </div>
          </div>
          <button
            onClick={() => navigate('/response')}
            className="px-3 py-1.5 bg-[#10243A] hover:bg-[#1C334D] text-white text-xs font-medium rounded transition flex items-center gap-1.5"
          >
            <span>Review & Authorize</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>
      )}

      {/* KPI Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white p-4 rounded border border-slate-200 shadow-xs">
          <div className="flex items-center justify-between text-slate-500 text-xs font-medium">
            <span>ACTIVE INCIDENTS</span>
            <ShieldAlert className="w-4 h-4 text-slate-400" />
          </div>
          <div className="mt-2 text-2xl font-bold text-slate-900">{analytics?.total_incidents || 0}</div>
          <div className="mt-1 flex items-center gap-1.5 text-[11px] text-red-600 font-medium">
            <span>{criticalCount} Critical priority</span>
          </div>
        </div>

        <div className="bg-white p-4 rounded border border-slate-200 shadow-xs">
          <div className="flex items-center justify-between text-slate-500 text-xs font-medium">
            <span>RAW EVENTS INGESTED</span>
            <Activity className="w-4 h-4 text-slate-400" />
          </div>
          <div className="mt-2 text-2xl font-bold text-slate-900">{analytics?.total_events || 0}</div>
          <div className="mt-1 flex items-center gap-1.5 text-[11px] text-slate-500">
            <span>From SIEM, EDR & Auth</span>
          </div>
        </div>

        <div className="bg-white p-4 rounded border border-slate-200 shadow-xs">
          <div className="flex items-center justify-between text-slate-500 text-xs font-medium">
            <span>ALERT FATIGUE REDUCTION</span>
            <TrendingUp className="w-4 h-4 text-emerald-600" />
          </div>
          <div className="mt-2 text-2xl font-bold text-emerald-700">{analytics?.alert_reduction_percent || 0}%</div>
          <div className="mt-1 flex items-center gap-1.5 text-[11px] text-emerald-600 font-medium">
            <span>Correlation deduplication</span>
          </div>
        </div>

        <div className="bg-white p-4 rounded border border-slate-200 shadow-xs">
          <div className="flex items-center justify-between text-slate-500 text-xs font-medium">
            <span>MULTI-AGENT STATUS</span>
            <Cpu className="w-4 h-4 text-[#1769AA]" />
          </div>
          <div className="mt-2 text-2xl font-bold text-slate-900">
            {agents.filter(a => a.status === 'HEALTHY' || a.status === 'READY').length} / 6
          </div>
          <div className="mt-1 flex items-center gap-1.5 text-[11px] text-emerald-600 font-medium">
            <span>100% Policy Integrity</span>
          </div>
        </div>
      </div>

      {/* Main Grid: Active Incidents & Six Agents Status */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Incidents Table (2 cols) */}
        <div className="lg:col-span-2 bg-white rounded border border-slate-200 shadow-xs overflow-hidden">
          <div className="p-4 border-b border-slate-100 flex items-center justify-between">
            <div>
              <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wide">Live Correlated Incidents</h3>
              <p className="text-[11px] text-slate-500">Multi-event incidents grouped by identity and temporal graphs</p>
            </div>
            <button
              onClick={() => navigate('/incidents')}
              className="text-xs text-[#1769AA] hover:underline font-medium flex items-center gap-1"
            >
              <span>View All</span>
              <ArrowRight className="w-3 h-3" />
            </button>
          </div>

          <div className="overflow-x-auto">
            {incidents.length === 0 ? (
              <div className="p-8 text-center text-slate-400 text-xs">
                No active security incidents. Run a demo scenario above to simulate realistic enterprise telemetry.
              </div>
            ) : (
              <table className="w-full text-left text-xs">
                <thead className="bg-[#F8FAFC] border-b border-slate-200 text-slate-500 uppercase tracking-wider font-semibold">
                  <tr>
                    <th className="py-2.5 px-3">Incident ID</th>
                    <th className="py-2.5 px-3">Severity</th>
                    <th className="py-2.5 px-3">Title & Primary Entities</th>
                    <th className="py-2.5 px-3">Risk</th>
                    <th className="py-2.5 px-3">Status</th>
                    <th className="py-2.5 px-3 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {incidents.slice(0, 6).map((inc) => (
                    <tr key={inc.incident_id} className="hover:bg-slate-50 transition-colors">
                      <td className="py-2.5 px-3 font-mono font-medium text-slate-900">{inc.incident_id}</td>
                      <td className="py-2.5 px-3">
                        <SeverityBadge severity={inc.severity} size="sm" />
                      </td>
                      <td className="py-2.5 px-3">
                        <div className="font-medium text-slate-900 truncate max-w-xs">{inc.title}</div>
                        <div className="text-[11px] text-slate-500 truncate max-w-xs">
                          {inc.correlated_event_ids.length} events • Users: {(inc.primary_entities.users || []).join(', ') || 'N/A'}
                        </div>
                      </td>
                      <td className="py-2.5 px-3 font-mono font-semibold text-slate-900">
                        {inc.risk_score} / 100
                      </td>
                      <td className="py-2.5 px-3">
                        <StatusBadge status={inc.status} />
                      </td>
                      <td className="py-2.5 px-3 text-right">
                        <button
                          onClick={() => navigate(`/investigation?incident_id=${inc.incident_id}`)}
                          className="px-2 py-1 bg-slate-100 hover:bg-[#1769AA] hover:text-white rounded text-slate-700 font-medium transition"
                        >
                          Investigate
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </div>

        {/* 6 Specialized Agents Status Panel (1 col) */}
        <div className="bg-white rounded border border-slate-200 shadow-xs flex flex-col">
          <div className="p-4 border-b border-slate-100 flex items-center justify-between">
            <div>
              <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wide">6 Core Analytics Agents</h3>
              <p className="text-[11px] text-slate-500">Logical division of investigative responsibilities</p>
            </div>
            <button
              onClick={() => navigate('/agents')}
              className="text-xs text-[#1769AA] hover:underline font-medium"
            >
              Inspect
            </button>
          </div>

          <div className="p-3 space-y-2 flex-1 overflow-y-auto">
            {agents.map((ag) => (
              <div key={ag.code} className="p-2.5 bg-slate-50 rounded border border-slate-200 text-xs">
                <div className="flex items-center justify-between">
                  <span className="font-semibold text-slate-900">{ag.name}</span>
                  <span className="px-1.5 py-0.5 rounded text-[10px] font-mono bg-emerald-100 text-emerald-800 border border-emerald-200 font-semibold">
                    {ag.status}
                  </span>
                </div>
                <div className="text-[11px] text-slate-500 mt-0.5">{ag.role}</div>
                <div className="mt-1 flex items-center justify-between text-[10px] font-mono text-slate-400">
                  <span>Tasks: {ag.tasks_processed}</span>
                  <span>Avg: {ag.avg_duration_ms.toFixed(1)} ms</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
