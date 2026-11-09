import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import {
  FileSearch,
  CheckCircle2,
  AlertCircle,
  HelpCircle,
  ShieldAlert,
  Save,
  Layers,
  ArrowRight,
  GitBranch,
  Split,
  Tag,
  AlertTriangle
} from 'lucide-react';
import { api } from '../services/api';
import { Incident, Investigation, RiskAssessment } from '../types';
import { SeverityBadge, StatusBadge, ConfidenceBadge } from '../components/Badges';

export const InvestigationWorkspace: React.FC = () => {
  const [searchParams] = useSearchParams();
  const incidentIdParam = searchParams.get('incident_id');

  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [selectedIncidentId, setSelectedIncidentId] = useState<string>('');
  const [incident, setIncident] = useState<Incident | null>(null);
  const [investigation, setInvestigation] = useState<Investigation | null>(null);
  const [risk, setRisk] = useState<RiskAssessment | null>(null);
  const [analystNotes, setAnalystNotes] = useState('');
  const [savingNotes, setSavingNotes] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);
  const [loading, setLoading] = useState(true);

  const loadAll = async () => {
    setLoading(true);
    try {
      const incList = await api.getIncidents();
      setIncidents(incList);
      const targetId = incidentIdParam || (incList.length > 0 ? incList[0].incident_id : '');
      if (targetId) {
        setSelectedIncidentId(targetId);
        await loadIncidentDetail(targetId);
      }
    } catch (err) {
      console.error('Failed to load investigation workspace:', err);
    } finally {
      setLoading(false);
    }
  };

  const loadIncidentDetail = async (id: string) => {
    try {
      const [incData, invData, riskData] = await Promise.all([
        api.getIncident(id),
        api.getInvestigation(id),
        api.getRiskAssessment(id)
      ]);
      setIncident(incData);
      setInvestigation(invData);
      setRisk(riskData);
      setAnalystNotes(invData.analyst_notes || '');
    } catch (err) {
      console.error('Failed to load incident detail:', err);
    }
  };

  useEffect(() => {
    loadAll();
  }, [incidentIdParam]);

  const handleSelectIncident = (id: string) => {
    setSelectedIncidentId(id);
    loadIncidentDetail(id);
  };

  const handleSaveNotes = async () => {
    if (!incident) return;
    setSavingNotes(true);
    try {
      await api.updateNotes(incident.incident_id, analystNotes);
      setSaveSuccess(true);
      setTimeout(() => setSaveSuccess(false), 2000);
    } catch (err) {
      alert('Failed to save notes');
    } finally {
      setSavingNotes(false);
    }
  };

  if (loading) {
    return <div className="p-8 text-center text-xs text-slate-400 font-mono">LOADING INVESTIGATION WORKSPACE...</div>;
  }

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Workspace Header & Incident Selector */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-white p-4 rounded border border-slate-200 shadow-xs">
        <div>
          <h2 className="text-xl font-bold text-slate-900 tracking-tight flex items-center gap-2">
            <FileSearch className="w-5 h-5 text-[#1769AA]" />
            <span>Investigation Workspace</span>
          </h2>
          <p className="text-xs text-slate-500">
            Agents 3 & 4: Deep Kill-Chain Progression, MITRE ATT&CK Mapping & Evidence Explanations
          </p>
        </div>

        {/* Incident Selector Dropdown */}
        <div className="flex items-center gap-2 text-xs">
          <span className="font-semibold text-slate-600">Active Incident:</span>
          <select
            value={selectedIncidentId}
            onChange={(e) => handleSelectIncident(e.target.value)}
            className="p-1.5 border border-slate-300 rounded font-mono font-bold text-slate-800 bg-white"
          >
            {incidents.map((i) => (
              <option key={i.incident_id} value={i.incident_id}>
                {i.incident_id} — {i.title.substring(0, 45)}... ({i.severity})
              </option>
            ))}
          </select>
        </div>
      </div>

      {incident && investigation ? (
        <div className="space-y-6">
          {/* Incident Metadata & Uncertainty Escalation Alert */}
          {risk?.is_escalated === 'ESCALATE_HUMAN_REVIEW' && (
            <div className="p-4 bg-purple-50 border border-purple-300 rounded text-purple-950 flex items-start gap-3">
              <AlertTriangle className="w-5 h-5 text-purple-700 shrink-0 mt-0.5" />
              <div>
                <div className="text-xs font-bold uppercase tracking-wider">
                  SYSTEM STATE: UNCERTAIN — ESCALATE TO HUMAN REVIEW
                </div>
                <div className="text-xs mt-0.5 text-purple-900 leading-relaxed">
                  Antigravity detected significant missing telemetry gaps or contradictory evidence signals. Autonomous response recommendations have been halted. Manual review required.
                </div>
              </div>
            </div>
          )}

          {/* Risk & Confidence Dual Gauge */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-white p-4 rounded border border-slate-200 shadow-xs">
              <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">Risk Score</span>
              <div className="mt-1 text-2xl font-bold text-slate-900">{incident.risk_score} <span className="text-xs font-normal text-slate-500">/ 100</span></div>
              <div className="mt-1 text-xs">
                <SeverityBadge severity={incident.severity} size="sm" />
              </div>
            </div>

            <div className="bg-white p-4 rounded border border-slate-200 shadow-xs">
              <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">Confidence Score</span>
              <div className="mt-1 text-2xl font-bold text-slate-900">{Math.round(incident.confidence_score * 100)}%</div>
              <div className="mt-1 text-xs text-slate-500">Evidence ground-truth rating</div>
            </div>

            <div className="bg-white p-4 rounded border border-slate-200 shadow-xs">
              <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">Uncertainty Metric</span>
              <div className="mt-1 text-2xl font-bold text-purple-700">
                {risk ? Math.round(risk.uncertainty_score * 100) : 15}%
              </div>
              <div className="mt-1 text-xs text-slate-500">Based on telemetry completeness</div>
            </div>

            <div className="bg-white p-4 rounded border border-slate-200 shadow-xs">
              <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">Recommended Priority</span>
              <div className="mt-1 text-2xl font-bold text-[#1769AA]">{risk?.recommended_priority || 'P2'}</div>
              <div className="mt-1 text-xs text-slate-500">Operational triage queue</div>
            </div>
          </div>

          {/* Agent 4: Evidence-Grounded Synthesised Explanation */}
          <div className="bg-white rounded border border-slate-200 shadow-xs p-5">
            <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wide border-b border-slate-100 pb-2 flex items-center justify-between">
              <span>Agent 4: Evidence & Grounded Explanation</span>
              <span className="text-[11px] font-mono text-slate-400">Strictly Traceable to Raw Telemetry</span>
            </h3>
            <div className="mt-3 text-xs text-slate-700 leading-relaxed whitespace-pre-wrap font-sans bg-slate-50 p-4 rounded border border-slate-200">
              {investigation.explanation || 'Generating explanation from underlying telemetry events...'}
            </div>
          </div>

          {/* MITRE ATT&CK Technique Mapping Matrix */}
          <div className="bg-white rounded border border-slate-200 shadow-xs overflow-hidden">
            <div className="p-4 border-b border-slate-100 flex items-center justify-between">
              <div>
                <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wide">
                  Agent 3: MITRE ATT&CK Matrix Technique Mapping
                </h3>
                <p className="text-[11px] text-slate-500">
                  Every technique includes verified technique identifiers and supporting telemetry citations
                </p>
              </div>
              <span className="px-2 py-0.5 rounded text-xs font-mono bg-blue-50 text-[#1769AA] border border-blue-200 font-semibold">
                {investigation.mitre_mappings.length} Techniques Identified
              </span>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-[#F8FAFC] border-b border-slate-200 text-slate-500 uppercase tracking-wider font-semibold">
                  <tr>
                    <th className="py-2.5 px-3">Tactic</th>
                    <th className="py-2.5 px-3">Technique ID</th>
                    <th className="py-2.5 px-3">Technique Name</th>
                    <th className="py-2.5 px-3">Confidence</th>
                    <th className="py-2.5 px-3">Supporting Telemetry Evidence</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 font-mono">
                  {investigation.mitre_mappings.map((m) => (
                    <tr key={m.technique_id} className="hover:bg-slate-50">
                      <td className="py-2.5 px-3 font-sans font-semibold text-slate-800">{m.tactic}</td>
                      <td className="py-2.5 px-3 font-bold text-[#1769AA]">{m.technique_id}</td>
                      <td className="py-2.5 px-3 font-sans text-slate-900">{m.technique_name}</td>
                      <td className="py-2.5 px-3 font-sans">
                        <ConfidenceBadge confidence={m.confidence} />
                      </td>
                      <td className="py-2.5 px-3 font-sans text-[11px] text-slate-600">
                        {m.supporting_evidence.join('; ')}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Kill-Chain Progression & Telemetry Limitations Side-by-Side */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Attack Progression Stages */}
            <div className="bg-white rounded border border-slate-200 shadow-xs p-5">
              <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wide border-b border-slate-100 pb-2">
                Reconstructed Attack Kill-Chain Stages
              </h3>
              <div className="mt-3 space-y-3">
                {investigation.attack_progression.map((stage, idx) => (
                  <div key={idx} className="p-3 bg-slate-50 rounded border border-slate-200 text-xs">
                    <div className="flex items-center justify-between font-semibold text-slate-900">
                      <span className="flex items-center gap-1.5">
                        <span className="w-2 h-2 rounded-full bg-[#1769AA]"></span>
                        Stage {idx + 1}: {stage.stage}
                      </span>
                      <span className="font-mono text-[10px] text-slate-400">
                        {new Date(stage.timestamp).toLocaleTimeString()}
                      </span>
                    </div>
                    <div className="mt-1 text-slate-600 text-[11px]">{stage.description}</div>
                    <div className="mt-2 text-[10px] font-mono text-slate-400">
                      Entities: {stage.entities.join(', ') || 'N/A'}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Confirmed Facts vs Hypotheses vs Missing Telemetry */}
            <div className="bg-white rounded border border-slate-200 shadow-xs p-5 flex flex-col justify-between">
              <div>
                <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wide border-b border-slate-100 pb-2">
                  Facts vs Working Hypotheses
                </h3>
                
                <div className="mt-3 space-y-3">
                  <div>
                    <span className="text-[10px] font-bold text-emerald-700 uppercase block mb-1">
                      Confirmed Ground Evidence ({investigation.confirmed_evidence.length})
                    </span>
                    <div className="max-h-28 overflow-y-auto space-y-1 font-mono text-[10px] text-slate-600 bg-emerald-50/50 p-2 rounded border border-emerald-200">
                      {investigation.confirmed_evidence.map((f, i) => (
                        <div key={i} className="truncate">• {f.fact}</div>
                      ))}
                    </div>
                  </div>

                  <div>
                    <span className="text-[10px] font-bold text-amber-700 uppercase block mb-1">
                      Analyst Hypotheses Requiring Validation ({investigation.hypotheses.length})
                    </span>
                    <div className="space-y-1 text-xs">
                      {investigation.hypotheses.map((h, i) => (
                        <div key={i} className="p-2 bg-amber-50 rounded border border-amber-200 text-amber-900 text-[11px]">
                          <div className="font-semibold">{h.hypothesis}</div>
                          <div className="text-[10px] text-amber-700 mt-0.5">Need: {h.verification_needed}</div>
                        </div>
                      ))}
                    </div>
                  </div>

                  {investigation.missing_evidence.length > 0 && (
                    <div>
                      <span className="text-[10px] font-bold text-purple-700 uppercase block mb-1">
                        Identified Telemetry Gaps
                      </span>
                      <div className="bg-purple-50 p-2 rounded border border-purple-200 text-purple-900 text-[11px] space-y-1 font-mono">
                        {investigation.missing_evidence.map((gap, i) => (
                          <div key={i}>⚠ {gap}</div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>

              {/* Analyst Notes Section */}
              <div className="mt-4 pt-4 border-t border-slate-200">
                <div className="flex items-center justify-between mb-1.5">
                  <label className="text-xs font-bold text-slate-800 uppercase tracking-wide">
                    Human Analyst Case Notes
                  </label>
                  <button
                    onClick={handleSaveNotes}
                    disabled={savingNotes}
                    className="flex items-center gap-1 px-2.5 py-1 bg-[#10243A] hover:bg-[#1C334D] text-white text-xs font-medium rounded transition"
                  >
                    <Save className="w-3 h-3" />
                    <span>{savingNotes ? 'Saving...' : saveSuccess ? 'Saved!' : 'Save Notes'}</span>
                  </button>
                </div>
                <textarea
                  rows={3}
                  value={analystNotes}
                  onChange={(e) => setAnalystNotes(e.target.value)}
                  placeholder="Record your corroboration findings, interview notes, or containment rationale..."
                  className="w-full p-2.5 border border-slate-300 rounded text-xs text-slate-800 bg-white"
                />
              </div>
            </div>
          </div>
        </div>
      ) : (
        <div className="p-12 text-center text-slate-400 text-xs">
          Select an incident to view investigation workspace.
        </div>
      )}
    </div>
  );
};
