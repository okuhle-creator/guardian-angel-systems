import React, { useState, useEffect } from 'react';
import {
  Cpu,
  Activity,
  CheckCircle2,
  Clock,
  Layers,
  AlertTriangle,
  RefreshCw,
  Terminal,
  Code
} from 'lucide-react';
import { api } from '../services/api';
import { AgentStatus } from '../types';

export const AgentOperations: React.FC = () => {
  const [agents, setAgents] = useState<AgentStatus[]>([]);
  const [executions, setExecutions] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const loadData = async () => {
    setLoading(true);
    try {
      const [agData, exData] = await Promise.all([
        api.getAgentsStatus(),
        api.getAgentExecutions()
      ]);
      setAgents(agData);
      setExecutions(exData);
    } catch (err) {
      console.error('Failed to load agent operations data:', err);
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

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-slate-900 tracking-tight">Agent Operations Management</h2>
          <p className="text-xs text-slate-500">
            Real-time backend execution records, contract verification, and latency metrics across the six specialized agents
          </p>
        </div>
        <button
          onClick={loadData}
          className="flex items-center gap-1.5 px-3 py-1.5 bg-white border border-slate-300 rounded text-xs font-medium text-slate-700 hover:bg-slate-50 transition"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          <span>Refresh Records</span>
        </button>
      </div>

      {/* Six Agents Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {agents.map((ag) => (
          <div key={ag.code} className="bg-white rounded border border-slate-200 shadow-xs p-4 flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between">
                <span className="font-mono text-xs font-bold text-[#1769AA]">{ag.code}</span>
                <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-emerald-100 text-emerald-800 border border-emerald-200">
                  {ag.status}
                </span>
              </div>
              <h3 className="text-sm font-bold text-slate-900 mt-1">{ag.name}</h3>
              <p className="text-xs text-slate-600 mt-1">{ag.description}</p>
            </div>

            <div className="mt-4 pt-3 border-t border-slate-100 grid grid-cols-3 gap-2 text-center text-xs font-mono">
              <div className="bg-slate-50 p-1.5 rounded">
                <span className="text-[10px] text-slate-400 block font-sans">TASKS</span>
                <span className="font-bold text-slate-800">{ag.tasks_processed}</span>
              </div>
              <div className="bg-slate-50 p-1.5 rounded">
                <span className="text-[10px] text-slate-400 block font-sans">AVG TIME</span>
                <span className="font-bold text-slate-800">{ag.avg_duration_ms.toFixed(1)} ms</span>
              </div>
              <div className="bg-slate-50 p-1.5 rounded">
                <span className="text-[10px] text-slate-400 block font-sans">ERRORS</span>
                <span className={`font-bold ${ag.error_count > 0 ? 'text-red-600' : 'text-slate-800'}`}>
                  {ag.error_count}
                </span>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Real Execution Audit Table */}
      <div className="bg-white rounded border border-slate-200 shadow-xs overflow-hidden">
        <div className="p-3 bg-slate-50 border-b border-slate-200 text-xs font-semibold text-slate-600 flex justify-between items-center">
          <span>REAL BACKEND AGENT EXECUTION LOGS ({executions.length})</span>
          <span className="text-[11px] text-slate-400 font-mono">Verified Execution Traces (Never Fabricated)</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-[#F8FAFC] border-b border-slate-200 text-slate-500 uppercase tracking-wider font-semibold font-mono">
              <tr>
                <th className="py-2.5 px-3">Execution ID</th>
                <th className="py-2.5 px-3">Agent</th>
                <th className="py-2.5 px-3">Status</th>
                <th className="py-2.5 px-3">Task Description</th>
                <th className="py-2.5 px-3">Duration</th>
                <th className="py-2.5 px-3">Output Reference</th>
                <th className="py-2.5 px-3">Executed At</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 font-mono text-xs">
              {executions.length === 0 ? (
                <tr>
                  <td colSpan={7} className="p-8 text-center text-slate-400 font-sans">
                    No execution records yet. Trigger any scenario above to observe multi-agent task execution.
                  </td>
                </tr>
              ) : (
                executions.map((ex) => (
                  <tr key={ex.execution_id} className="hover:bg-slate-50">
                    <td className="py-2.5 px-3 font-semibold text-slate-900">{ex.execution_id}</td>
                    <td className="py-2.5 px-3 font-bold text-[#1769AA]">{ex.agent_name}</td>
                    <td className="py-2.5 px-3">
                      <span className="px-1.5 py-0.5 rounded text-[10px] font-bold bg-emerald-50 text-emerald-700 border border-emerald-200">
                        {ex.status}
                      </span>
                    </td>
                    <td className="py-2.5 px-3 font-sans text-slate-700 max-w-xs truncate">
                      {ex.task_description}
                    </td>
                    <td className="py-2.5 px-3 text-slate-800">{ex.duration_ms.toFixed(1)} ms</td>
                    <td className="py-2.5 px-3 text-slate-600 truncate max-w-xs">{ex.output_ref || '—'}</td>
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
