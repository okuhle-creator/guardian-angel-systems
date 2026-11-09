import React, { useState, useEffect } from 'react';
import {
  FileText,
  ShieldCheck,
  CheckCircle,
  AlertTriangle,
  RefreshCw,
  Lock,
  Search,
  Hash,
  Link
} from 'lucide-react';
import { api } from '../services/api';
import { AuditRecord } from '../types';

export const AuditCentre: React.FC = () => {
  const [records, setRecords] = useState<AuditRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [verifying, setVerifying] = useState(false);
  const [verifyResult, setVerifyResult] = useState<{
    total_records: number;
    is_valid: boolean;
    verified_records_count: number;
    tampered_records: string[];
    root_hash: string;
    latest_hash: string;
    message: string;
  } | null>(null);

  const loadData = async () => {
    setLoading(true);
    try {
      const data = await api.getAuditRecords(100);
      setRecords(data);
    } catch (err) {
      console.error('Failed to load audit records:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleVerifyChain = async () => {
    setVerifying(true);
    try {
      const res = await api.verifyAuditLedger();
      setVerifyResult(res);
    } catch (err: any) {
      alert(`Verification error: ${err.message}`);
    } finally {
      setVerifying(false);
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
          <h2 className="text-xl font-bold text-slate-900 tracking-tight">Immutable Cryptographic Audit Ledger</h2>
          <p className="text-xs text-slate-500">
            Append-only, SHA-256 hash-chained verification of all telemetry ingestions, AI decisions, analyst approvals, and responses
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={handleVerifyChain}
            disabled={verifying}
            className="flex items-center gap-1.5 px-3 py-1.5 bg-[#1769AA] hover:bg-[#125387] text-white text-xs font-semibold rounded transition shadow-xs disabled:opacity-50"
          >
            <ShieldCheck className="w-3.5 h-3.5" />
            <span>{verifying ? 'Verifying Hashes...' : 'Verify Cryptographic Chain'}</span>
          </button>

          <button
            onClick={loadData}
            className="flex items-center gap-1.5 px-3 py-1.5 bg-white border border-slate-300 rounded text-xs font-medium text-slate-700 hover:bg-slate-50 transition"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            <span>Refresh</span>
          </button>
        </div>
      </div>

      {/* Verification Results Card */}
      {verifyResult && (
        <div className={`p-4 rounded border text-xs ${
          verifyResult.is_valid
            ? 'bg-emerald-50 border-emerald-300 text-emerald-950'
            : 'bg-red-50 border-red-300 text-red-950'
        }`}>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 font-bold uppercase tracking-wide">
              {verifyResult.is_valid ? (
                <>
                  <CheckCircle className="w-4 h-4 text-emerald-600" />
                  <span>AUDIT LEDGER INTEGRITY VERIFIED (100% UNBROKEN)</span>
                </>
              ) : (
                <>
                  <AlertTriangle className="w-4 h-4 text-red-600" />
                  <span>INTEGRITY TAMPERING DETECTED IN AUDIT LEDGER</span>
                </>
              )}
            </div>
            <span className="font-mono text-[11px]">
              {verifyResult.verified_records_count} / {verifyResult.total_records} Records Verified
            </span>
          </div>

          <div className="mt-2 text-[11px] leading-relaxed">
            {verifyResult.message}
          </div>

          <div className="mt-3 grid grid-cols-1 md:grid-cols-2 gap-2 text-[10px] font-mono bg-white/70 p-2 rounded border border-emerald-200">
            <div>
              <span className="text-slate-500 block">GENESIS / ROOT HASH:</span>
              <span className="text-slate-900 truncate block">{verifyResult.root_hash}</span>
            </div>
            <div>
              <span className="text-slate-500 block">LATEST BLOCK RECORD HASH:</span>
              <span className="text-slate-900 truncate block">{verifyResult.latest_hash}</span>
            </div>
          </div>
        </div>
      )}

      {/* Audit Records Table */}
      <div className="bg-white rounded border border-slate-200 shadow-xs overflow-hidden">
        <div className="p-3 bg-slate-50 border-b border-slate-200 text-xs font-semibold text-slate-600 flex justify-between items-center">
          <span>AUDIT TRAIL LEDGER ({records.length} Entries)</span>
          <span className="text-[11px] text-slate-400 font-mono">Merkle/Hash Chained Sequential Verification</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-mono">
            <thead className="bg-[#F8FAFC] border-b border-slate-200 text-slate-500 uppercase tracking-wider font-semibold">
              <tr>
                <th className="py-2.5 px-3">Record ID</th>
                <th className="py-2.5 px-3">Actor & Role</th>
                <th className="py-2.5 px-3">Action</th>
                <th className="py-2.5 px-3">Target</th>
                <th className="py-2.5 px-3">Previous Hash</th>
                <th className="py-2.5 px-3">Record Hash (SHA-256)</th>
                <th className="py-2.5 px-3">Timestamp</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-xs">
              {records.length === 0 ? (
                <tr>
                  <td colSpan={7} className="p-8 text-center text-slate-400 font-sans">
                    No audit records registered.
                  </td>
                </tr>
              ) : (
                records.map((rec) => (
                  <tr key={rec.record_id} className="hover:bg-slate-50 transition-colors">
                    <td className="py-2.5 px-3 font-semibold text-slate-900">{rec.record_id}</td>
                    <td className="py-2.5 px-3">
                      <span className="font-sans font-bold text-slate-800">{rec.actor_id}</span>
                      <span className="block text-[10px] text-slate-400 font-sans">[{rec.actor_role}]</span>
                    </td>
                    <td className="py-2.5 px-3">
                      <span className="px-1.5 py-0.5 rounded text-[10px] font-bold bg-slate-100 text-slate-700 border border-slate-200">
                        {rec.action}
                      </span>
                    </td>
                    <td className="py-2.5 px-3 text-slate-700">
                      <span className="font-sans text-[11px] font-medium">{rec.target_type}: </span>
                      <span className="font-mono text-[#1769AA] font-bold">{rec.target_id}</span>
                    </td>
                    <td className="py-2.5 px-3 text-slate-400 text-[10px] truncate max-w-[120px]" title={rec.previous_hash}>
                      {rec.previous_hash.substring(0, 12)}...
                    </td>
                    <td className="py-2.5 px-3 text-[#10243A] font-semibold text-[10px] truncate max-w-[140px]" title={rec.record_hash}>
                      {rec.record_hash.substring(0, 14)}...
                    </td>
                    <td className="py-2.5 px-3 text-slate-400 text-[11px]">
                      {new Date(rec.timestamp).toLocaleTimeString()}
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
