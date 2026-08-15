from cloud.gateway import ingest_telemetry


def test_ingest():
    assert ingest_telemetry("d1", {"temp": 1})["accepted"] is True
