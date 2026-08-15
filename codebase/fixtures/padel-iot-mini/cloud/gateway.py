"""Cloud gateway for court sensors (software only)."""


def ingest_telemetry(device_id: str, payload: dict) -> dict:
    return {"device_id": device_id, "accepted": True, "payload": payload}


def authorize_remote_open(user_id: str, gate_id: str) -> dict:
    # Authorization policy for digital command only — not physical lock certification.
    return {"user_id": user_id, "gate_id": gate_id, "command": "open_request", "certainty": "software_only"}
