"""Unit test SqsTelemetrySource._group — gom message theo (namespace, deployment)."""
import json

from sqs_source import SqsTelemetrySource


def _msg(ns, dep, signal_name, handle):
    body = {
        "ts": "2026-06-30T10:00:00.000Z",
        "tenant_id": "6c8b4b2b-4d45-4209-a1b4-4b532d56a31c",
        "service": dep,
        "signal_name": signal_name,
        "value": 1,
        "labels": {"system": "K8S_NATIVE", "namespace": ns, "deployment": dep},
    }
    return {"Body": json.dumps(body), "ReceiptHandle": handle}


def test_group_by_namespace_deployment():
    msgs = [
        _msg("tenant-a", "cdo-sample-api", "pod_oom_event", "h1"),
        _msg("tenant-a", "cdo-sample-api", "container_restart_count", "h2"),
        _msg("tenant-b", "notification-service", "service_unhealthy", "h3"),
    ]
    incidents = SqsTelemetrySource._group(msgs)
    incidents.sort(key=lambda i: i.namespace)
    assert len(incidents) == 2
    a = incidents[0]
    assert a.namespace == "tenant-a" and a.deployment == "cdo-sample-api"
    assert len(a.telemetry_window) == 2
    assert set(a.receipt_handles) == {"h1", "h2"}
    b = incidents[1]
    assert b.namespace == "tenant-b"
    assert len(b.telemetry_window) == 1


def test_group_skips_malformed_body():
    msgs = [
        {"Body": "{not json", "ReceiptHandle": "bad"},
        _msg("tenant-a", "cdo-sample-api", "pod_oom_event", "h1"),
    ]
    incidents = SqsTelemetrySource._group(msgs)
    assert len(incidents) == 1
    assert incidents[0].receipt_handles == ["h1"]


def test_group_skips_missing_namespace():
    bad = {"Body": json.dumps({"signal_name": "x", "labels": {"system": "K8S_NATIVE"}}),
           "ReceiptHandle": "h"}
    assert SqsTelemetrySource._group([bad]) == []
