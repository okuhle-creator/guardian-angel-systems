import React, { useState, useEffect } from 'react';
import {
  CheckCircle,
  XCircle,
  Play,
  ShieldAlert,
  AlertTriangle,
  RefreshCw,
  Server,
  UserX,
  Lock,
  Radio,
  FileCheck2
} from 'lucide-react';
import { api } from '../services/api';
import { RecommendedAction, ResponseExecution, ApprovalRecord } from '../types';

export const ResponseCentre: React.FC = () => {
  const [actions, setActions] = useState<RecommendedAction[]>([]);
  const [executions, setExecutions] = useState<ResponseExecution[]>([]);
  const [approvals, setApprovals] = useState<ApprovalRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [actionNotes, setActionNotes] = useState<Record<string, string>>({});
  const [executingActionId, setExecutingActionId] = useState<string | null>(null);

  const loadData = async () => {
    setLoading(true);
    try {
      const [actData, exData, apData] = await Promise.all([
        api.getRecommendedActions(),
        api.getExecutions(),
        api.getApprovals()
      ]);
      setActions(actData);
      setExecutions(exData);
      setApprovals(apData);
    } catch (err) {
      console.error('Failed to load response centre:', err);
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

  const handleDecision = async (actionId: string, decision: 'APPROVED' | 'REJECTED') => {
    const notes = actionNotes[actionId] || `Authorized decision ${decision} by Senior Analyst`;
    try {
      await api.submitApprovalDecision(actionId, decision, notes);
      await loadData();
    } catch (err: any) {
      alert(`Approval error: ${err.message}`);
    }
  };

  const handleExecute = async (actionId: string) => {
    setExecutingActionId(actionId);
    try {
      await api.executeSimulatedAction(actionId);
      await loadData();
    } catch (err: any) {
      alert(`Execution error: ${err.message}`);
    } finally {
      setExecutingActionId(null);
    }
  };

  const pendingActions = actions.filter((a) => a.status === 'PENDING_APPROVAL');
  const processedActions = actions.filter((a) => a.status !== 'PENDING_APPROVAL');

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-slate-900 tracking-tight">Response & Human Governance Centre</h2>
          <p className="text-xs text-slate-500">
            Agent 6: Policy enforcement, deterministic human approval gates, and simulated containment execution
          </p>
        </div>
        <button
          onClick={loadData}
          className="flex items-center gap-1.5 px-3 py-1.5 bg-white border border-slate-300 rounded text-xs font-medium text-slate-700 hover:bg-slate-50 transition"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          <span>Refresh Queue</span>
        </button>
      </div>

      {/* Deterministic Policy Notice */}
      <div className="p-4 bg-blue-50 border border-blue-200 rounded text-xs text-blue-900 flex items-start gap-3">
        <ShieldAlert className="w-5 h-5 text-[#1769AA] shrink-0 mt-0.5" />
        <div>
          <div className="font-bold uppercase tracking-wider">Deterministic Policy Enforcement Active</div>
          <div className="mt-0.5 leading-relaxed text-blue-800">
            GAS strictly prohibits autonomous execution of disruptive containment operations (Account Deactivation, Host Quarantine, Firewall ACL injection). Every consequential action is held in queue until a verified human analyst renders an immutable sign-off.
          </div>
        </div>
      </div>

      {/* Pending Actions Queue */}
      <div className="bg-white rounded border border-slate-200 shadow-xs overflow-hidden">
        <div className="p-3 bg-amber-50 border-b border-amber-200 text-xs font-bold text-amber-900 flex justify-between items-center">
          <span className="flex items-center gap-1.5">
            <AlertTriangle className="w-4 h-4 text-amber-700" />
            ACTIONS AWAITING HUMAN APPROVAL ({pendingActions.length})
          </span>
          <span className="font-mono text-[11px] text-amber-700">Governance Gate: REQUIRES_HUMAN_APPROVAL</span>
        </div>

        <div className="divide-y divide-slate-100">
          {pendingActions.length === 0 ? (
            <div className="p-8 text-center text-slate-400 text-xs">
              No actions currently pending approval. All recommended measures have been processed or none are active.
            </div>
          ) : (
            pendingActions.map((act) => (
              <div key={act.action_id} className="p-5 flex flex-col md:flex-row md:items-center justify-between gap-4 hover:bg-slate-50/80 transition-colors">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <span className="font-mono font-bold text-xs text-slate-900">{act.action_id}</span>
                    <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-100 text-amber-800 border border-amber-300 font-mono">
                      {act.action_type}
                    </span>
                    <span className="text-[10px] text-slate-500 font-mono">Incident: {act.incident_id}</span>
                  </div>

                  <div className="mt-1 font-semibold text-xs text-slate-900">
                    Target: <span className="font-mono text-[#1769AA]">{act.target_entity}</span> ({act.target_type})
                  </div>
                  <div className="mt-1 text-xs text-slate-600 leading-relaxed">{act.rationale}</div>

                  <div className="mt-2.5 flex items-center gap-2">
                    <input
                      type="text"
                      placeholder="Enter analyst justification notes (optional)..."
                      value={actionNotes[act.action_id] || ''}
                      onChange={(e) => setActionNotes({ ...actionNotes, [act.action_id]: e.target.value })}
                      className="px-2.5 py-1 text-xs border border-slate-300 rounded w-80 text-slate-800 bg-white"
                    />
                  </div>
                </div>

                {/* Human Approval / Rejection Buttons */}
                <div className="flex items-center gap-2 shrink-0">
                  <button
                    onClick={() => handleDecision(act.action_id, 'REJECTED')}
                    className="px-3 py-1.5 bg-white border border-red-300 hover:bg-red-50 text-red-700 font-semibold text-xs rounded transition flex items-center gap-1.5"
                  >
                    <XCircle className="w-3.5 h-3.5" />
                    <span>Reject</span>
                  </button>
                  <button
                    onClick={() => handleDecision(act.action_id, 'APPROVED')}
                    className="px-3 py-1.5 bg-emerald-700 hover:bg-emerald-800 text-white font-semibold text-xs rounded transition flex items-center gap-1.5 shadow-xs"
                  >
                    <CheckCircle className="w-3.5 h-3.5" />
                    <span>Authorize Approval</span>
                  </button>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Approved Actions Ready for Simulated Execution */}
      <div className="bg-white rounded border border-slate-200 shadow-xs overflow-hidden">
        <div className="p-3 bg-slate-50 border-b border-slate-200 text-xs font-semibold text-slate-600 flex justify-between items-center">
          <span>AUTHORIZED ACTIONS QUEUE ({processedActions.filter(a => a.status === 'APPROVED').length} Approved)</span>
          <span className="text-[11px] text-slate-400 font-mono">Simulated Safe Environment</span>
        </div>

        <div className="divide-y divide-slate-100">
          {processedActions.filter(a => a.status === 'APPROVED').length === 0 ? (
            <div className="p-6 text-center text-slate-400 text-xs">
              No approved actions waiting to execute.
            </div>
          ) : (
            processedActions.filter(a => a.status === 'APPROVED').map((act) => (
              <div key={act.action_id} className="p-4 flex items-center justify-between hover:bg-slate-50 text-xs">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="font-mono font-bold text-slate-900">{act.action_id}</span>
                    <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-100 text-emerald-800 border border-emerald-200 font-mono">
                      APPROVED BY HUMAN
                    </span>
                    <span className="font-mono text-slate-500">{act.action_type}</span>
                  </div>
                  <div className="text-slate-700 mt-1">Target: <span className="font-mono font-semibold">{act.target_entity}</span></div>
                </div>

                <button
                  onClick={() => handleExecute(act.action_id)}
                  disabled={executingActionId === act.action_id}
                  className="px-4 py-1.5 bg-[#10243A] hover:bg-[#1C334D] text-white font-semibold text-xs rounded transition flex items-center gap-1.5 shadow-xs disabled:opacity-50"
                >
                  <Play className="w-3.5 h-3.5 fill-current" />
                  <span>{executingActionId === act.action_id ? 'Simulating...' : 'Execute Simulated Response'}</span>
                </button>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Response Execution Audit History */}
      <div className="bg-white rounded border border-slate-200 shadow-xs overflow-hidden">
        <div className="p-3 bg-slate-50 border-b border-slate-200 text-xs font-semibold text-slate-600 flex justify-between items-center">
          <span>SIMULATED EXECUTION RECORDS ({executions.length})</span>
          <span className="text-[11px] text-slate-400 font-mono">Zero Destructive Real-World Side Effects</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-mono">
            <thead className="bg-[#F8FAFC] border-b border-slate-200 text-slate-500 uppercase tracking-wider font-semibold">
              <tr>
                <th className="py-2.5 px-3">Execution ID</th>
                <th className="py-2.5 px-3">Type</th>
                <th className="py-2.5 px-3">Target</th>
                <th className="py-2.5 px-3">Status</th>
                <th className="py-2.5 px-3">Verification</th>
                <th className="py-2.5 px-3">Executed By</th>
                <th className="py-2.5 px-3">Timestamp</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {executions.length === 0 ? (
                <tr>
                  <td colSpan={7} className="p-8 text-center text-slate-400 font-sans">
                    No simulated executions recorded yet.
                  </td>
                </tr>
              ) : (
                executions.map((ex) => (
                  <tr key={ex.execution_id} className="hover:bg-slate-50">
                    <td className="py-2.5 px-3 font-semibold text-slate-900">{ex.execution_id}</td>
                    <td className="py-2.5 px-3 font-bold text-[#1769AA]">{ex.execution_type}</td>
                    <td className="py-2.5 px-3 text-slate-800">{ex.target}</td>
                    <td className="py-2.5 px-3">
                      <span className="px-1.5 py-0.5 rounded text-[10px] font-bold bg-emerald-100 text-emerald-800 border border-emerald-200">
                        {ex.status}
                      </span>
                    </td>
                    <td className="py-2.5 px-3">
                      <span className="px-1.5 py-0.5 rounded text-[10px] font-bold bg-blue-50 text-blue-700 border border-blue-200">
                        {ex.verification_status}
                      </span>
                    </td>
                    <td className="py-2.5 px-3 font-sans text-slate-700">{ex.executed_by}</td>
                    <td className="py-2.5 px-3 text-slate-400 text-[11px]">
                      {new Date(ex.executed_at).toLocaleTimeString()}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
