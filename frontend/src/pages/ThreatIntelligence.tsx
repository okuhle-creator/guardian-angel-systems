import React, { useState, useEffect } from 'react';
import {
  Database,
  Plus,
  Shield,
  Globe,
  Hash,
  User,
  Search,
  ExternalLink,
  Tag
} from 'lucide-react';
import { api } from '../services/api';
import { ThreatIndicator } from '../types';

export const ThreatIntelligence: React.FC = () => {
  const [indicators, setIndicators] = useState<ThreatIndicator[]>([]);
  const [loading, setLoading] = useState(true);
  const [filterType, setFilterType] = useState('ALL');
  const [showAddModal, setShowAddModal] = useState(false);

  // Form State
  const [newType, setNewType] = useState('IP');
  const [newValue, setNewValue] = useState('');
  const [newScore, setNewScore] = useState(80);
  const [newCategory, setNewCategory] = useState('COMMAND_AND_CONTROL');
  const [newDesc, setNewDesc] = useState('');

  const loadData = async () => {
    setLoading(true);
    try {
      const data = await api.getThreatIndicators(filterType !== 'ALL' ? filterType : undefined);
      setIndicators(data);
    } catch (err) {
      console.error('Failed to load indicators:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
    const handleRefresh = () => loadData();
    window.addEventListener('refresh_gas_data', handleRefresh);
    return () => window.removeEventListener('refresh_gas_data', handleRefresh);
  }, [filterType]);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.createThreatIndicator({
        type: newType,
        value: newValue,
        threat_score: Number(newScore),
        category: newCategory,
        description: newDesc,
        tags: [newCategory.toLowerCase(), newType.toLowerCase()]
      });
      setShowAddModal(false);
      setNewValue('');
      setNewDesc('');
      loadData();
    } catch (err: any) {
      alert(`Error: ${err.message}`);
    }
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-slate-900 tracking-tight">Threat Intelligence Repository</h2>
          <p className="text-xs text-slate-500">
            Local Indicators of Compromise (IoCs), adversary infrastructure, and signature correlation feeds
          </p>
        </div>

        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1.5 bg-white border border-slate-300 rounded px-2.5 py-1 text-xs">
            <span className="text-slate-400 font-medium">Type:</span>
            <select
              value={filterType}
              onChange={(e) => setFilterType(e.target.value)}
              className="bg-transparent font-semibold text-slate-700 outline-hidden"
            >
              <option value="ALL">All Types</option>
              <option value="IP">IP Addresses</option>
              <option value="DOMAIN">Domains</option>
              <option value="HASH">Hashes</option>
              <option value="USER">User Identities</option>
            </select>
          </div>

          <button
            onClick={() => setShowAddModal(true)}
            className="flex items-center gap-1.5 px-3 py-1.5 bg-[#1769AA] hover:bg-[#125387] text-white text-xs font-semibold rounded transition shadow-xs"
          >
            <Plus className="w-3.5 h-3.5" />
            <span>Add IoC Indicator</span>
          </button>
        </div>
      </div>

      {/* IoCs Table */}
      <div className="bg-white rounded border border-slate-200 shadow-xs overflow-hidden">
        <div className="p-3 bg-slate-50 border-b border-slate-200 text-xs font-semibold text-slate-600 flex justify-between items-center">
          <span>STORED INDICATORS ({indicators.length})</span>
          <span className="text-[11px] text-slate-400 font-mono">Autonomous Local Knowledge Base (No External API Dependency)</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-[#F8FAFC] border-b border-slate-200 text-slate-500 uppercase tracking-wider font-semibold font-mono">
              <tr>
                <th className="py-2.5 px-3">Type</th>
                <th className="py-2.5 px-3">Indicator Value</th>
                <th className="py-2.5 px-3">Category</th>
                <th className="py-2.5 px-3">Threat Score</th>
                <th className="py-2.5 px-3">Description</th>
                <th className="py-2.5 px-3">Source & Tags</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 font-mono">
              {indicators.length === 0 ? (
                <tr>
                  <td colSpan={6} className="p-8 text-center text-slate-400 font-sans text-xs">
                    No threat indicators found.
                  </td>
                </tr>
              ) : (
                indicators.map((ind) => (
                  <tr key={ind.indicator_id} className="hover:bg-slate-50">
                    <td className="py-2.5 px-3">
                      <span className="px-1.5 py-0.5 rounded text-[10px] font-bold bg-slate-100 text-slate-700 border border-slate-200">
                        {ind.type}
                      </span>
                    </td>
                    <td className="py-2.5 px-3 font-bold text-slate-900 truncate max-w-xs">{ind.value}</td>
                    <td className="py-2.5 px-3 text-slate-700 font-sans text-[11px]">{ind.category}</td>
                    <td className="py-2.5 px-3">
                      <span className={`px-2 py-0.5 rounded text-xs font-bold ${
                        ind.threat_score >= 90 ? 'bg-red-100 text-red-800' :
                        ind.threat_score >= 75 ? 'bg-orange-100 text-orange-800' : 'bg-amber-100 text-amber-800'
                      }`}>
                        {ind.threat_score} / 100
                      </span>
                    </td>
                    <td className="py-2.5 px-3 font-sans text-[11px] text-slate-600 truncate max-w-sm">
                      {ind.description || 'Verified threat indicator in local intelligence corpus'}
                    </td>
                    <td className="py-2.5 px-3 font-sans text-[10px] text-slate-500">
                      <div>{ind.source}</div>
                      <div className="flex gap-1 mt-0.5">
                        {(ind.tags || []).map((t, idx) => (
                          <span key={idx} className="bg-slate-100 text-slate-600 px-1 py-0.2 rounded text-[9px] font-mono">
                            #{t}
                          </span>
                        ))}
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Add Indicator Modal */}
      {showAddModal && (
        <div className="fixed inset-0 bg-slate-900/50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded border border-slate-200 shadow-xl max-w-md w-full p-6 text-xs">
            <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wide border-b border-slate-100 pb-2">
              Add New Threat Indicator (IoC)
            </h3>
            <form onSubmit={handleCreate} className="mt-4 space-y-3">
              <div>
                <label className="block font-semibold text-slate-700 mb-1">Indicator Type</label>
                <select
                  value={newType}
                  onChange={(e) => setNewType(e.target.value)}
                  className="w-full p-2 border border-slate-300 rounded bg-white text-slate-800"
                >
                  <option value="IP">IP Address</option>
                  <option value="DOMAIN">Domain Name</option>
                  <option value="HASH">SHA-256 / MD5 Hash</option>
                  <option value="USER">User Identity</option>
                </select>
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">Indicator Value</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. 198.51.100.44 or malware.exe"
                  value={newValue}
                  onChange={(e) => setNewValue(e.target.value)}
                  className="w-full p-2 border border-slate-300 rounded font-mono text-slate-800"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block font-semibold text-slate-700 mb-1">Category</label>
                  <select
                    value={newCategory}
                    onChange={(e) => setNewCategory(e.target.value)}
                    className="w-full p-2 border border-slate-300 rounded bg-white text-slate-800"
                  >
                    <option value="COMMAND_AND_CONTROL">COMMAND_AND_CONTROL</option>
                    <option value="BRUTE_FORCE_HOST">BRUTE_FORCE_HOST</option>
                    <option value="PHISHING_DOMAIN">PHISHING_DOMAIN</option>
                    <option value="MALWARE_PAYLOAD">MALWARE_PAYLOAD</option>
                    <option value="SUSPICIOUS_IDENTITY">SUSPICIOUS_IDENTITY</option>
                  </select>
                </div>

                <div>
                  <label className="block font-semibold text-slate-700 mb-1">Threat Score (0-100)</label>
                  <input
                    type="number"
                    min="1"
                    max="100"
                    value={newScore}
                    onChange={(e) => setNewScore(Number(e.target.value))}
                    className="w-full p-2 border border-slate-300 rounded text-slate-800"
                  />
                </div>
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">Advisory Description</label>
                <textarea
                  rows={2}
                  value={newDesc}
                  onChange={(e) => setNewDesc(e.target.value)}
                  placeholder="Describe adversary association or tactical context..."
                  className="w-full p-2 border border-slate-300 rounded text-slate-800"
                />
              </div>

              <div className="flex justify-end gap-2 pt-2 border-t border-slate-100">
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  className="px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 font-medium rounded transition"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-1.5 bg-[#1769AA] hover:bg-[#125387] text-white font-semibold rounded transition shadow-xs"
                >
                  Save Indicator
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
