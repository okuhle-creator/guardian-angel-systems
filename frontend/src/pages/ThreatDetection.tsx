import React, { useState, useEffect } from 'react';
import {
  Upload,
  PlusCircle,
  FileCode,
  AlertOctagon,
  CheckCircle2,
  Filter,
  RefreshCw,
  Eye,
  ShieldCheck,
  ChevronRight
} from 'lucide-react';
import { api } from '../services/api';
import { SecurityEvent, Detection } from '../types';
import { SeverityBadge, ConfidenceBadge } from '../components/Badges';

export const ThreatDetection: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'events' | 'detections' | 'ingest'>('events');
  const [events, setEvents] = useState<SecurityEvent[]>([]);
  const [detections, setDetections] = useState<Detection[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedEvent, setSelectedEvent] = useState<SecurityEvent | null>(null);

  // Manual Ingest Form State
  const [formSource, setFormSource] = useState('ENDPOINT');
  const [formEventType, setFormEventType] = useState('PROCESS_CREATION');
  const [formUserId, setFormUserId] = useState('analyst_user');
  const [formHostId, setFormHostId] = useState('wkst-sec-01');
  const [formProcess, setFormProcess] = useState('powershell.exe -enc JAB3AGgAbwBhAG0AaQA=');
  const [formSeverity, setFormSeverity] = useState('HIGH');
  const [ingestStatus, setIngestStatus] = useState<string | null>(null);

  const loadData = async () => {
    setLoading(true);
    try {
      const [evData, detData] = await Promise.all([
        api.getEvents({ limit: 50 }),
        api.getDetections()
      ]);
      setEvents(evData);
      setDetections(detData);
      if (evData.length > 0 && !selectedEvent) {
        setSelectedEvent(evData[0]);
      }
    } catch (err) {
      console.error('Failed to load telemetry:', err);
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

  const handleManualIngest = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await api.ingestEvent({
        source: formSource,
        event_type: formEventType,
        user_id: formUserId,
        host_id: formHostId,
        process: formProcess,
        severity: formSeverity,
        raw_payload: `Manual SOC simulation event submitted via console: ${formProcess}`
      });
      setIngestStatus(`Processed event successfully! Detections triggered: ${res.detections_triggered}`);
      loadData();
      setActiveTab('events');
    } catch (err: any) {
      setIngestStatus(`Error: ${err.message}`);
    }
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-slate-900 tracking-tight">Telemetry Ingestion & Threat Detection</h2>
          <p className="text-xs text-slate-500">
            Multi-source log normalisation, signature inspection, and explainable rule-based detection engine
          </p>
        </div>
        <button
          onClick={loadData}
          className="flex items-center gap-1.5 px-3 py-1.5 bg-white border border-slate-300 rounded text-xs font-medium text-slate-700 hover:bg-slate-50 transition"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          <span>Refresh</span>
        </button>
      </div>

      {/* Navigation Tabs */}
      <div className="flex border-b border-slate-200">
        <button
          onClick={() => setActiveTab('events')}
          className={`py-2 px-4 text-xs font-semibold border-b-2 transition ${
            activeTab === 'events'
              ? 'border-[#1769AA] text-[#1769AA]'
              : 'border-transparent text-slate-500 hover:text-slate-800'
          }`}
        >
          Normalised Telemetry Events ({events.length})
        </button>
        <button
          onClick={() => setActiveTab('detections')}
          className={`py-2 px-4 text-xs font-semibold border-b-2 transition ${
            activeTab === 'detections'
              ? 'border-[#1769AA] text-[#1769AA]'
              : 'border-transparent text-slate-500 hover:text-slate-800'
          }`}
        >
          Detections Triggered ({detections.length})
        </button>
        <button
          onClick={() => setActiveTab('ingest')}
          className={`py-2 px-4 text-xs font-semibold border-b-2 transition ${
            activeTab === 'ingest'
              ? 'border-[#1769AA] text-[#1769AA]'
              : 'border-transparent text-slate-500 hover:text-slate-800'
          }`}
        >
          + Ingest Custom Telemetry
        </button>
      </div>

      {/* Tab 1: Normalised Telemetry Events & Raw Inspector */}
      {activeTab === 'events' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Events Table (2 cols) */}
          <div className="lg:col-span-2 bg-white rounded border border-slate-200 shadow-xs overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-[#F8FAFC] border-b border-slate-200 text-slate-500 uppercase tracking-wider font-semibold">
                  <tr>
                    <th className="py-2 px-3">Event ID</th>
                    <th className="py-2 px-3">Timestamp</th>
                    <th className="py-2 px-3">Source & Type</th>
                    <th className="py-2 px-3">Identity / Host</th>
                    <th className="py-2 px-3">Severity</th>
                    <th className="py-2 px-3">Quality</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 font-mono">
                  {events.length === 0 ? (
                    <tr>
                      <td colSpan={6} className="p-6 text-center text-slate-400 font-sans">
                        No telemetry loaded. Run a scenario or ingest custom telemetry.
                      </td>
                    </tr>
                  ) : (
                    events.map((ev) => (
                      <tr
                        key={ev.event_id}
                        onClick={() => setSelectedEvent(ev)}
                        className={`cursor-pointer transition-colors ${
                          selectedEvent?.event_id === ev.event_id ? 'bg-blue-50/70' : 'hover:bg-slate-50'
                        }`}
                      >
                        <td className="py-2 px-3 font-semibold text-slate-900">{ev.event_id}</td>
                        <td className="py-2 px-3 text-slate-500 text-[11px]">
                          {new Date(ev.timestamp).toLocaleTimeString()}
                        </td>
                        <td className="py-2 px-3">
                          <span className="font-sans font-medium text-slate-800">{ev.event_type}</span>
                          <span className="block text-[10px] text-slate-400">{ev.source}</span>
                        </td>
                        <td className="py-2 px-3 text-[11px] text-slate-700 font-sans">
                          {ev.user_id || '—'} @ {ev.host_id || ev.source_ip || '—'}
                        </td>
                        <td className="py-2 px-3">
                          <SeverityBadge severity={ev.severity} size="sm" />
                        </td>
                        <td className="py-2 px-3">
                          {ev.is_malformed || ev.anomaly_flags?.length > 0 ? (
                            <span className="px-1.5 py-0.5 rounded text-[10px] bg-amber-100 text-amber-800 border border-amber-200 font-sans font-medium">
                              ANOMALY
                            </span>
                          ) : (
                            <span className="px-1.5 py-0.5 rounded text-[10px] bg-emerald-50 text-emerald-700 border border-emerald-200 font-sans">
                              VALID
                            </span>
                          )}
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>

          {/* Telemetry Inspector Panel (1 col) */}
          <div className="bg-white rounded border border-slate-200 shadow-xs p-4 flex flex-col">
            <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wide border-b border-slate-100 pb-2 flex items-center justify-between">
              <span>Telemetry Normaliser Inspector</span>
              {selectedEvent && <span className="font-mono text-[#1769AA]">{selectedEvent.event_id}</span>}
            </h3>

            {selectedEvent ? (
              <div className="mt-3 space-y-3 text-xs overflow-y-auto">
                <div>
                  <label className="text-[10px] font-bold text-slate-400 uppercase">Normalized Fields</label>
                  <div className="bg-slate-50 p-2.5 rounded border border-slate-200 space-y-1.5 font-mono text-[11px]">
                    <div><span className="text-slate-400">source:</span> {selectedEvent.source}</div>
                    <div><span className="text-slate-400">event_type:</span> {selectedEvent.event_type}</div>
                    <div><span className="text-slate-400">user_id:</span> {selectedEvent.user_id || 'null'}</div>
                    <div><span className="text-slate-400">host_id:</span> {selectedEvent.host_id || 'null'}</div>
                    <div><span className="text-slate-400">source_ip:</span> {selectedEvent.source_ip || 'null'}</div>
                    <div><span className="text-slate-400">destination_ip:</span> {selectedEvent.destination_ip || 'null'}</div>
                    <div><span className="text-slate-400">process:</span> {selectedEvent.process || 'null'}</div>
                    <div><span className="text-slate-400">auth_result:</span> {selectedEvent.authentication_result || 'null'}</div>
                    <div><span className="text-slate-400">confidence:</span> {selectedEvent.confidence}</div>
                  </div>
                </div>

                {selectedEvent.anomaly_flags?.length > 0 && (
                  <div>
                    <label className="text-[10px] font-bold text-amber-700 uppercase">Data Quality / Anomaly Flags</label>
                    <div className="bg-amber-50 p-2.5 rounded border border-amber-200 space-y-1 text-amber-900 font-mono text-[11px]">
                      {selectedEvent.anomaly_flags.map((flag, idx) => (
                        <div key={idx} className="flex items-center gap-1.5">
                          <AlertOctagon className="w-3.5 h-3.5 text-amber-600 shrink-0" />
                          <span>{flag}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                <div>
                  <label className="text-[10px] font-bold text-slate-400 uppercase">Original Raw Telemetry Reference</label>
                  <pre className="bg-[#10243A] text-slate-200 p-2.5 rounded font-mono text-[10px] overflow-x-auto whitespace-pre-wrap">
                    {selectedEvent.raw_payload || selectedEvent.raw_reference || 'N/A'}
                  </pre>
                </div>
              </div>
            ) : (
              <div className="p-8 text-center text-slate-400 text-xs">
                Select an event from the table to inspect normalisation attributes.
              </div>
            )}
          </div>
        </div>
      )}

      {/* Tab 2: Detections Feed */}
      {activeTab === 'detections' && (
        <div className="bg-white rounded border border-slate-200 shadow-xs overflow-hidden">
          <div className="p-4 border-b border-slate-100 flex items-center justify-between">
            <div>
              <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wide">
                Agent 1: Detection Agent Output
              </h3>
              <p className="text-[11px] text-slate-500">Suspicious activities triggered by explainable deterministic rules & IoCs</p>
            </div>
            <span className="font-mono text-xs bg-slate-100 px-2.5 py-1 rounded text-slate-700">
              {detections.length} Total Alerts
            </span>
          </div>

          <div className="divide-y divide-slate-100">
            {detections.length === 0 ? (
              <div className="p-8 text-center text-slate-400 text-xs">
                No detections recorded. Run a demonstration scenario or submit an attack payload.
              </div>
            ) : (
              detections.map((det) => (
                <div key={det.detection_id} className="p-4 hover:bg-slate-50 transition-colors">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <span className="font-mono font-bold text-xs text-slate-900">{det.detection_id}</span>
                      <SeverityBadge severity={det.severity} size="sm" />
                      <ConfidenceBadge confidence={det.confidence} />
                      <span className="text-xs font-mono text-slate-400">[{det.rule_id}]</span>
                    </div>
                    <span className="text-[11px] font-mono text-slate-400">
                      {new Date(det.timestamp).toLocaleString()}
                    </span>
                  </div>

                  <div className="mt-1.5 font-semibold text-xs text-slate-900">{det.rule_name}</div>
                  <div className="mt-1 text-xs text-slate-600">{det.explanation}</div>

                  <div className="mt-2.5 bg-slate-50 p-2 rounded border border-slate-200 text-[11px] font-mono flex items-center justify-between">
                    <div>
                      <span className="text-slate-400">Supporting Events: </span>
                      <span className="text-slate-700 font-semibold">{det.event_ids.join(', ')}</span>
                    </div>
                    <div className="text-slate-500">Category: {det.detection_category}</div>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      )}

      {/* Tab 3: Custom Telemetry Ingestion Form */}
      {activeTab === 'ingest' && (
        <div className="bg-white rounded border border-slate-200 shadow-xs p-6 max-w-2xl mx-auto">
          <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wide border-b border-slate-100 pb-2">
            Submit Raw Telemetry Record
          </h3>
          <p className="text-xs text-slate-500 mt-1">
            Test the live ingestion pipeline, normalisation rules, and Detection Agent response.
          </p>

          {ingestStatus && (
            <div className="mt-4 p-3 rounded bg-blue-50 border border-blue-200 text-xs text-blue-900 font-medium">
              {ingestStatus}
            </div>
          )}

          <form onSubmit={handleManualIngest} className="mt-4 space-y-4 text-xs">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block font-semibold text-slate-700 mb-1">Source</label>
                <select
                  value={formSource}
                  onChange={(e) => setFormSource(e.target.value)}
                  className="w-full p-2 border border-slate-300 rounded bg-white text-slate-800"
                >
                  <option value="ENDPOINT">ENDPOINT (EDR)</option>
                  <option value="SIEM">SIEM</option>
                  <option value="FIREWALL">FIREWALL</option>
                  <option value="AUTH_SERVICE">AUTH_SERVICE</option>
                  <option value="EMAIL_GATEWAY">EMAIL_GATEWAY</option>
                  <option value="ANONYMOUS_PROXY">ANONYMOUS_PROXY (Untrusted)</option>
                </select>
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">Event Type</label>
                <select
                  value={formEventType}
                  onChange={(e) => setFormEventType(e.target.value)}
                  className="w-full p-2 border border-slate-300 rounded bg-white text-slate-800"
                >
                  <option value="PROCESS_CREATION">PROCESS_CREATION</option>
                  <option value="AUTHENTICATION">AUTHENTICATION</option>
                  <option value="NETWORK_FLOW">NETWORK_FLOW</option>
                  <option value="PRIVILEGE_ESCALATION">PRIVILEGE_ESCALATION</option>
                  <option value="EMAIL">EMAIL</option>
                </select>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block font-semibold text-slate-700 mb-1">User Identity</label>
                <input
                  type="text"
                  value={formUserId}
                  onChange={(e) => setFormUserId(e.target.value)}
                  className="w-full p-2 border border-slate-300 rounded text-slate-800"
                />
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">Target Host ID</label>
                <input
                  type="text"
                  value={formHostId}
                  onChange={(e) => setFormHostId(e.target.value)}
                  className="w-full p-2 border border-slate-300 rounded text-slate-800"
                />
              </div>
            </div>

            <div>
              <label className="block font-semibold text-slate-700 mb-1">Command / Process Invocation</label>
              <input
                type="text"
                value={formProcess}
                onChange={(e) => setFormProcess(e.target.value)}
                placeholder="e.g. powershell.exe -enc ... or psexec.exe"
                className="w-full p-2 border border-slate-300 rounded font-mono text-slate-800"
              />
            </div>

            <div>
              <label className="block font-semibold text-slate-700 mb-1">Severity Flag</label>
              <select
                value={formSeverity}
                onChange={(e) => setFormSeverity(e.target.value)}
                className="w-full p-2 border border-slate-300 rounded bg-white text-slate-800"
              >
                <option value="CRITICAL">CRITICAL</option>
                <option value="HIGH">HIGH</option>
                <option value="MEDIUM">MEDIUM</option>
                <option value="LOW">LOW</option>
                <option value="INFO">INFO</option>
              </select>
            </div>

            <button
              type="submit"
              className="w-full py-2.5 bg-[#1769AA] hover:bg-[#125387] text-white font-semibold rounded transition shadow-xs text-xs uppercase tracking-wide"
            >
              Execute Ingestion & Trigger Multi-Agent Pipeline
            </button>
          </form>
        </div>
      )}
    </div>
  );
};
