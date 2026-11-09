import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AppLayout } from './layouts/AppLayout';
import { CommandCentre } from './pages/CommandCentre';
import { ThreatDetection } from './pages/ThreatDetection';
import { IncidentManagement } from './pages/IncidentManagement';
import { InvestigationWorkspace } from './pages/InvestigationWorkspace';
import { ThreatIntelligence } from './pages/ThreatIntelligence';
import { AgentOperations } from './pages/AgentOperations';
import { ResponseCentre } from './pages/ResponseCentre';
import { AuditCentre } from './pages/AuditCentre';
import { AnalyticsEvaluation } from './pages/AnalyticsEvaluation';

export const App: React.FC = () => {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<AppLayout />}>
          <Route index element={<CommandCentre />} />
          <Route path="detection" element={<ThreatDetection />} />
          <Route path="incidents" element={<IncidentManagement />} />
          <Route path="investigation" element={<InvestigationWorkspace />} />
          <Route path="intel" element={<ThreatIntelligence />} />
          <Route path="agents" element={<AgentOperations />} />
          <Route path="response" element={<ResponseCentre />} />
          <Route path="audit" element={<AuditCentre />} />
          <Route path="analytics" element={<AnalyticsEvaluation />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
};

export default App;
