import time
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any, Set
from sqlalchemy.orm import Session
from app.models.detection import Detection
from app.models.event import SecurityEvent
from app.models.incident import Incident
from app.models.agent import AgentExecution
from app.services.audit_service import AuditService

class CorrelationAgent:
    NAME = "AlertCorrelationAgent"
    ROLE = "Alert Deduplication & Incident Entity-Temporal Graph Correlation"

    def run(self, db: Session, detections: List[Detection]) -> List[Incident]:
        start_time = time.time()
        if not detections:
            return []

        # Map event_id to SecurityEvent for fast entity lookup
        all_event_ids: Set[str] = set()
        for d in detections:
            all_event_ids.update(d.event_ids)

        events_map: Dict[str, SecurityEvent] = {
            e.event_id: e for e in db.query(SecurityEvent).filter(SecurityEvent.event_id.in_(list(all_event_ids))).all()
        }

        # Deduplicate detections with identical rule_id and exact same entity targets
        unique_detections: List[Detection] = []
        seen_signatures: Set[str] = set()
        for d in detections:
            # Build signature based on rule_id and key evidence entities
            user_part = d.evidence.get("user_id") or ""
            host_part = d.evidence.get("host_id") or ""
            ip_part = d.evidence.get("source_ip") or d.evidence.get("indicator_value") or ""
            sig = f"{d.rule_id}::{user_part}::{host_part}::{ip_part}"
            if sig not in seen_signatures:
                seen_signatures.add(sig)
                unique_detections.append(d)

        # Cluster detections into correlated incidents based on shared entities and temporal proximity
        clusters: List[Dict[str, Any]] = []

        for det in unique_detections:
            # Extract entities from detection evidence and underlying events
            det_users = set()
            det_hosts = set()
            det_ips = set()

            if "user_id" in det.evidence and det.evidence["user_id"]:
                det_users.add(det.evidence["user_id"])
            if "host_id" in det.evidence and det.evidence["host_id"]:
                det_hosts.add(det.evidence["host_id"])
            if "source_ip" in det.evidence and det.evidence["source_ip"]:
                det_ips.add(det.evidence["source_ip"])
            if "indicator_value" in det.evidence and det.evidence["indicator_value"]:
                det_ips.add(det.evidence["indicator_value"])

            for ev_id in det.event_ids:
                ev = events_map.get(ev_id)
                if ev:
                    if ev.user_id: det_users.add(ev.user_id)
                    if ev.host_id: det_hosts.add(ev.host_id)
                    if ev.source_ip: det_ips.add(ev.source_ip)
                    if ev.destination_ip: det_ips.add(ev.destination_ip)

            matched_cluster = None
            for c in clusters:
                # Check for shared entity intersection
                has_shared_user = bool(c["users"].intersection(det_users))
                has_shared_host = bool(c["hosts"].intersection(det_hosts))
                has_shared_ip = bool(c["ips"].intersection(det_ips))

                # Check temporal window (e.g. within 2 hours of cluster's time bounds)
                time_diff = abs((det.timestamp - c["latest_ts"]).total_seconds())
                is_temporally_close = time_diff <= 7200

                # Must share at least one solid entity AND be temporally linked
                if (has_shared_user or has_shared_host or has_shared_ip) and is_temporally_close:
                    matched_cluster = c
                    break

            if matched_cluster:
                matched_cluster["detections"].append(det)
                matched_cluster["users"].update(det_users)
                matched_cluster["hosts"].update(det_hosts)
                matched_cluster["ips"].update(det_ips)
                matched_cluster["event_ids"].update(det.event_ids)
                matched_cluster["latest_ts"] = max(matched_cluster["latest_ts"], det.timestamp)
                matched_cluster["severities"].append(det.severity)
            else:
                clusters.append({
                    "detections": [det],
                    "users": det_users,
                    "hosts": det_hosts,
                    "ips": det_ips,
                    "event_ids": set(det.event_ids),
                    "earliest_ts": det.timestamp,
                    "latest_ts": det.timestamp,
                    "severities": [det.severity]
                })

        # Create or update Incidents from clusters
        incidents: List[Incident] = []
        for cluster in clusters:
            dets = cluster["detections"]
            sev_order = {"CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1, "INFO": 0}
            max_sev = max(cluster["severities"], key=lambda s: sev_order.get(s, 0))

            # Title synthesis
            users_str = ", ".join(cluster["users"]) if cluster["users"] else "Unidentified Identity"
            hosts_str = ", ".join(cluster["hosts"]) if cluster["hosts"] else "Network Perimeter"
            title = f"Security Incident: {dets[0].rule_name.split(':')[0]} affecting [{users_str}] on [{hosts_str}]"
            
            # Initial baseline risk calculation (refined later by Risk Agent)
            base_risk = 75.0 if max_sev == "CRITICAL" else (60.0 if max_sev == "HIGH" else 40.0)
            avg_conf = sum(d.confidence for d in dets) / len(dets)

            incident = Incident(
                incident_id=f"INC-{uuid.uuid4().hex[:8].upper()}",
                title=title,
                description=f"Correlated {len(dets)} alerts across {len(cluster['event_ids'])} security events involving user(s): {users_str}, host(s): {hosts_str}.",
                status="NEW",
                severity=max_sev,
                risk_score=base_risk,
                confidence_score=round(avg_conf, 2),
                primary_entities={
                    "users": list(cluster["users"]),
                    "hosts": list(cluster["hosts"]),
                    "ips": list(cluster["ips"])
                },
                correlated_event_ids=list(cluster["event_ids"]),
                detection_ids=[d.detection_id for d in dets],
                created_at=datetime.utcnow()
            )
            db.add(incident)
            incidents.append(incident)

        db.commit()
        for inc in incidents:
            db.refresh(inc)

        duration = (time.time() - start_time) * 1000.0

        # Log Agent Execution
        execution = AgentExecution(
            execution_id=f"EXEC-CORR-{uuid.uuid4().hex[:8].upper()}",
            agent_name=self.NAME,
            status="SUCCESS",
            task_description=f"Correlated {len(detections)} detections into {len(incidents)} distinct unified incidents",
            input_ref=f"{len(detections)} detections",
            output_ref=f"{len(incidents)} incidents",
            duration_ms=duration,
            details={"raw_detections": len(detections), "deduped": len(unique_detections), "incidents_created": len(incidents)},
            executed_at=datetime.utcnow()
        )
        db.add(execution)
        db.commit()

        # Audit record
        if incidents:
            AuditService.log_action(
                db=db,
                actor_id=self.NAME,
                actor_role="AI_AGENT",
                action="INCIDENTS_CORRELATED",
                target_type="INCIDENT_SET",
                target_id=f"COUNT-{len(incidents)}",
                details={"incident_ids": [i.incident_id for i in incidents]}
            )

        return incidents
