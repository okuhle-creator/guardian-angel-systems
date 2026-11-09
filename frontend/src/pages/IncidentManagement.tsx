import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  FolderKanban,
  Search,
  Filter,
  ArrowRight,
  ShieldAlert,
  Clock,
  Layers,
  User,
  Monitor,
  Globe,
  FileSearch,
  CheckCircle2,
  AlertTriangle
} from 'lucide-react';
import { api } from '../services/api';
import { Incident, SecurityEvent } from '../types';
import { SeverityBadge, StatusBadge } from '../components/Badges';

export const IncidentManagement: React.FC = () => {
  const navigate = useNavigate();
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [selectedIncident, setSelectedIncident] = useState<Incident | null>(null);
  const [correlatedEvents, setCorrelatedEvents] = useState<SecurityEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState<string>('ALL');
  const [severityFilter, setSeverityFilter] = useState<string>('ALL');

  const loadIncidents = async () => {
    setLoading(true);
    try {
      const data = await api.getIncidents({
        status: statusFilter !== 'ALL' ? statusFilter : undefined,
        severity: severityFilter !== 'ALL' ? severityFilter : undefined,
      });
      setIncidents(data);
      if (data.length > 0 && !selectedIncident) {
        selectIncident(data[0]);
      }
    } catch (err) {
      console.error('Failed to load incidents:', err);
    } finally {
      setLoading(false);
    }
  };

  const selectIncident = async (inc: Incident) => {
    setSelectedIncident(inc);
    try {
      const evs = await api.getIncidentEvents(inc.incident_id);
      setCorrelatedEvents(evs);
    } catch (err) {
      console.error('Failed to load correlated events:', err);
    }
  };

  useEffect(() => {
    loadIncidents();
    const handleRefresh = () => loadIncidents();
    window.addEventListener('refresh_gas_data', handleRefresh);
    return () => window.removeEventListener('refresh_gas_data', handleRefresh);
  }, [statusFilter, severityFilter]);

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-slate-900 tracking-tight">Incident Management</h2>
          <p className="text-xs text-slate-500">
            Correlated multi-event clusters with entity graph linkages, timeline reconstruction, and containment status
          </p>
        </div>

        {/* Filter Toolbar */}
        <div className="flex items-center gap-3 text-xs">
          <div className="flex items-center gap-1.5 bg-white border border-slate-300 rounded px-2.5 py-1">
            <span className="text-slate-400 font-medium">Status:</span>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="bg-transparent font-semibold text-slate-700 outline-hidden"
            >
              <option value="ALL">All Statuses</option>
              <option value="NEW">New</option>
              <option value="INVESTIGATING">Investigating</option>
              <option value="CONTAINED">Contained</option>
              <option value="ESCALATED_HUMAN_REVIEW">Escalated to Human Review</option>
              <option value="FALSE_POSITIVE">False Positive</option>
              <option value="RESOLVED">Resolved</option>
            </select>
          </div>

          <div className="flex items-center gap-1.5 bg-white border border-slate-300 rounded px-2.5 py-1">
            <span className="text-slate-400 font-medium">Severity:</span>
            <select
              value={severityFilter}
              onChange={(e) => setSeverityFilter(e.target.value)}
              className="bg-transparent font-semibold text-slate-700 outline-hidden"
            >
              <option value="ALL">All Severities</option>
              <option value="CRITICAL">Critical</option>
              <option value="HIGH">High</option>
              <option value="MEDIUM">Medium</option>
              <option value="LOW">Low</option>
            </select>
          </div>
        </div>
      </div>

      {/* Main Grid: Incidents Master / Detail */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Master List (5 cols) */}
        <div className="lg:col-span-5 bg-white rounded border border-slate-200 shadow-xs flex flex-col h-[650px] overflow-hidden">
          <div className="p-3 bg-slate-50 border-b border-slate-200 text-xs font-semibold text-slate-600 flex justify-between items-center">
            <span>INCIDENTS ({incidents.length})</span>
            <span className="text-[11px] text-slate-400 font-mono">Agent 2: Correlation Output</span>
          </div>

          <div className="flex-1 overflow-y-auto divide-y divide-slate-100">
            {incidents.length === 0 ? (
              <div className="p-8 text-center text-slate-400 text-xs">
                No incidents match the active filters.
              </div>
            ) : (
              incidents.map((inc) => (
                <div
                  key={inc.incident_id}
                  onClick={() => selectIncident(inc)}
                  className={`p-3.5 cursor-pointer transition-colors text-xs ${
                    selectedIncident?.incident_id === inc.incident_id
                      ? 'bg-blue-50/80 border-l-4 border-l-[#1769AA]'
                      : 'hover:bg-slate-50 border-l-4 border-l-transparent'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <span className="font-mono font-bold text-slate-900">{inc.incident_id}</span>
                    <SeverityBadge severity={inc.severity} size="sm" />
                  </div>
                  <div className="font-medium text-slate-900 mt-1 line-clamp-1">{inc.title}</div>
                  <div className="flex items-center justify-between mt-2 text-[11px] text-slate-500 font-mono">
                    <span>Risk: {inc.risk_score} / 100</span>
                    <StatusBadge status={inc.status} />
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Detail Panel (7 cols) */}
        <div className="lg:col-span-7 bg-white rounded border border-slate-200 shadow-xs flex flex-col h-[650px] overflow-hidden">
          {selectedIncident ? (
            <div className="flex-1 overflow-y-auto p-5 space-y-5">
              {/* Incident Header */}
              <div className="border-b border-slate-200 pb-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-sm font-bold text-slate-900">{selectedIncident.incident_id}</span>
                    <SeverityBadge severity={selectedIncident.severity} />
                    <StatusBadge status={selectedIncident.status} />
                  </div>
                  <button
                    onClick={() => navigate(`/investigation?incident_id=${selectedIncident.incident_id}`)}
                    className="px-3 py-1.5 bg-[#1769AA] hover:bg-[#125387] text-white text-xs font-semibold rounded transition flex items-center gap-1.5 shadow-xs"
                  >
                    <FileSearch className="w-3.5 h-3.5" />
                    <span>Open Deep Investigation</span>
                  </button>
                </div>
                <h3 className="text-base font-bold text-slate-900 mt-2">{selectedIncident.title}</h3>
                <p className="text-xs text-slate-600 mt-1">{selectedIncident.description}</p>
              </div>

              {/* Primary Entity Graph Badges */}
              <div>
                <label className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block mb-2">
                  Correlated Identity & Network Entities
                </label>
                <div className="grid grid-cols-3 gap-3">
                  <div className="p-2.5 bg-slate-50 rounded border border-slate-200 text-xs">
                    <div className="flex items-center gap-1.5 text-slate-500 font-medium mb-1">
                      <User className="w-3.5 h-3.5 text-[#1769AA]" />
                      <span>Users ({selectedIncident.primary_entities.users?.length || 0})</span>
                    </div>
                    <div className="font-mono text-[11px] text-slate-800 font-semibold truncate">
                      {selectedIncident.primary_entities.users?.join(', ') || 'None'}
                    </div>
                  </div>

                  <div className="p-2.5 bg-slate-50 rounded border border-slate-200 text-xs">
                    <div className="flex items-center gap-1.5 text-slate-500 font-medium mb-1">
                      <Monitor className="w-3.5 h-3.5 text-emerald-600" />
                      <span>Hosts ({selectedIncident.primary_entities.hosts?.length || 0})</span>
                    </div>
                    <div className="font-mono text-[11px] text-slate-800 font-semibold truncate">
                      {selectedIncident.primary_entities.hosts?.join(', ') || 'None'}
                    </div>
                  </div>

                  <div className="p-2.5 bg-slate-50 rounded border border-slate-200 text-xs">
                    <div className="flex items-center gap-1.5 text-slate-500 font-medium mb-1">
                      <Globe className="w-3.5 h-3.5 text-amber-600" />
                      <span>IPs ({selectedIncident.primary_entities.ips?.length || 0})</span>
                    </div>
                    <div className="font-mono text-[11px] text-slate-800 font-semibold truncate">
                      {selectedIncident.primary_entities.ips?.join(', ') || 'None'}
                    </div>
                  </div>
                </div>
              </div>

              {/* Correlated Events Timeline */}
              <div>
                <label className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block mb-2">
                  Temporal Event Chain ({correlatedEvents.length} Events)
                </label>
                <div className="space-y-2">
                  {correlatedEvents.map((ev, index) => (
                    <div key={ev.event_id} className="p-3 bg-slate-50 rounded border border-slate-200 text-xs flex items-start gap-3">
                      <div className="w-5 h-5 rounded-full bg-[#10243A] text-white flex items-center justify-center font-mono text-[10px] shrink-0 mt-0.5">
                        {index + 1}
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center justify-between">
                          <span className="font-mono font-semibold text-slate-900">{ev.event_id}</span>
                          <span className="font-mono text-[10px] text-slate-400">
                            {new Date(ev.timestamp).toLocaleTimeString()}
                          </span>
                        </div>
                        <div className="font-medium text-slate-800 mt-0.5">
                          {ev.event_type} via {ev.source}
                        </div>
                        {ev.process && (
                          <div className="font-mono text-[11px] text-slate-600 bg-white p-1 rounded border border-slate-200 mt-1 truncate">
                            {ev.process}
                          </div>
                        )}
                        {ev.raw_payload && (
                          <div className="text-[11px] text-slate-500 mt-1 italic">
                            {ev.raw_payload}
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            <div className="flex items-center justify-center h-full text-slate-400 text-xs">
              Select an incident to view correlated entity graph and event timeline.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
