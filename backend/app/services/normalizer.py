import uuid
from datetime import datetime
from typing import Dict, Any, Tuple, List
from app.models.event import SecurityEvent

class TelemetryNormalizer:
    """
    Normalises raw telemetry from multiple sources (SIEM, Endpoint, Firewall, Auth, Email)
    into standard SecurityEvent schema.
    Detects missing fields, malformed formats, and potential telemetry tampering.
    """

    REQUIRED_FIELDS = ["event_type", "source"]

    @classmethod
    def normalize_record(cls, raw: Dict[str, Any]) -> Tuple[Dict[str, Any], bool, List[str]]:
        anomaly_flags = []
        is_malformed = False

        # Check required fields
        for field in cls.REQUIRED_FIELDS:
            if not raw.get(field):
                anomaly_flags.append(f"MISSING_REQUIRED_FIELD_{field.upper()}")
                is_malformed = True

        # Timestamp handling
        ts_val = raw.get("timestamp")
        parsed_ts = None
        if not ts_val:
            anomaly_flags.append("MISSING_TIMESTAMP")
            parsed_ts = datetime.utcnow()
        elif isinstance(ts_val, datetime):
            parsed_ts = ts_val
        elif isinstance(ts_val, str):
            try:
                # Handle ISO format
                parsed_ts = datetime.fromisoformat(ts_val.replace("Z", "+00:00")).replace(tzinfo=None)
            except Exception:
                try:
                    parsed_ts = datetime.strptime(ts_val, "%Y-%m-%d %H:%M:%S")
                except Exception:
                    anomaly_flags.append("MALFORMED_TIMESTAMP_FORMAT")
                    parsed_ts = datetime.utcnow()

        # Telemetry consistency checks (Detecting manipulated/inconsistent telemetry)
        auth_result = raw.get("authentication_result")
        if auth_result and auth_result not in ["SUCCESS", "FAILURE", "CHALLENGE", "BLOCKED"]:
            anomaly_flags.append(f"UNRECOGNIZED_AUTH_RESULT_{auth_result}")

        # Check contradictory event states (e.g. Failure with severity INFO or Success with failure codes)
        if raw.get("event_type") == "AUTHENTICATION" and auth_result == "FAILURE" and raw.get("severity") == "LOW":
            # Possible manipulated lower severity
            anomaly_flags.append("SUSPICIOUS_LOW_SEVERITY_ON_AUTH_FAILURE")

        # Untrusted or unexpected sources
        source = str(raw.get("source", "UNKNOWN")).upper()
        if source in ["UNKNOWN", "ANONYMOUS_PROXY", "UNVERIFIED_FORWARDER"]:
            anomaly_flags.append("UNTRUSTED_TELEMETRY_SOURCE")

        event_id = raw.get("event_id") or f"EVT-{uuid.uuid4().hex[:10].upper()}"

        normalized = {
            "event_id": event_id,
            "timestamp": parsed_ts,
            "source": source,
            "event_type": str(raw.get("event_type", "UNKNOWN")).upper(),
            "user_id": raw.get("user_id"),
            "host_id": raw.get("host_id"),
            "source_ip": raw.get("source_ip"),
            "destination_ip": raw.get("destination_ip"),
            "process": raw.get("process"),
            "authentication_result": auth_result,
            "severity": str(raw.get("severity", "INFO")).upper(),
            "confidence": float(raw.get("confidence", 1.0) if not anomaly_flags else max(0.2, float(raw.get("confidence", 1.0)) - (0.2 * len(anomaly_flags)))),
            "raw_reference": raw.get("raw_reference") or f"ref-{uuid.uuid4().hex[:8]}",
            "raw_payload": str(raw),
            "is_malformed": is_malformed,
            "anomaly_flags": anomaly_flags
        }

        return normalized, is_malformed, anomaly_flags
