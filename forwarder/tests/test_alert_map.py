"""Unit test alert_map — Alertmanager alert → telemetry signal đúng contract §3."""
from alert_map import alert_to_signal, alerts_to_signals

TENANT = "6c8b4b2b-4d45-4209-a1b4-4b532d56a31c"
_ENUM = {
    "service_error_rate", "service_latency_p95", "container_resource_usage",
    "application_log_event", "distributed_trace_error_event", "pod_oom_event",
    "service_unhealthy", "queue_backlog", "service_throughput_rps",
    "container_restart_count", "secret_expiry_warning", "db_connection_pool_saturation",
}


def _alert(alertname, **labels):
    base = {"alertname": alertname, "namespace": "tenant-a",
            "deployment": "cdo-sample-api", "pod": "cdo-sample-api-abc-xyz",
            "container": "main"}
    base.update(labels)
    return {"status": "firing", "labels": base, "annotations": {}}


def _assert_contract_shape(sig):
    for f in ("ts", "tenant_id", "service", "signal_name", "value", "labels"):
        assert f in sig, f"thiếu field bắt buộc {f}"
    assert sig["signal_name"] in _ENUM
    assert sig["labels"]["system"] == "K8S_NATIVE"
    assert sig["labels"]["namespace"] == "tenant-a"
    assert sig["ts"].endswith("Z")


def test_oom_maps_to_pod_oom_event_string():
    sig = alert_to_signal(_alert("PodOOMKilled"), TENANT)
    _assert_contract_shape(sig)
    assert sig["signal_name"] == "pod_oom_event"
    assert isinstance(sig["value"], str) and "OOMKilled" in sig["value"]


def test_crashloop_maps_to_restart_count_int():
    a = _alert("ContainerCrashLooping")
    a["annotations"]["value"] = "5"
    sig = alert_to_signal(a, TENANT)
    _assert_contract_shape(sig)
    assert sig["signal_name"] == "container_restart_count"
    assert sig["value"] == 5 and isinstance(sig["value"], int)


def test_latency_maps_to_float():
    a = _alert("HighLatencyP95")
    a["annotations"]["value"] = "1850.5"
    sig = alert_to_signal(a, TENANT)
    assert sig["signal_name"] == "service_latency_p95"
    assert sig["value"] == 1850.5


def test_imagepull_maps_to_service_unhealthy():
    sig = alert_to_signal(_alert("ImagePullBackOff", namespace="tenant-b"), TENANT)
    assert sig["signal_name"] == "service_unhealthy"
    assert sig["labels"]["namespace"] == "tenant-b"


def test_resolved_alert_skipped():
    a = _alert("PodOOMKilled")
    a["status"] = "resolved"
    assert alert_to_signal(a, TENANT) is None


def test_unknown_alertname_skipped():
    assert alert_to_signal(_alert("SomeRandomAlert"), TENANT) is None


def test_missing_namespace_skipped():
    a = {"status": "firing", "labels": {"alertname": "PodOOMKilled"}, "annotations": {}}
    assert alert_to_signal(a, TENANT) is None


def test_deployment_derived_from_pod_when_label_absent():
    a = {"status": "firing",
         "labels": {"alertname": "PodOOMKilled", "namespace": "tenant-a",
                    "pod": "cdo-sample-api-5f8d9b7c-xyz12"},
         "annotations": {}}
    sig = alert_to_signal(a, TENANT)
    assert sig["labels"]["deployment"] == "cdo-sample-api"


def test_batch_filters_invalid():
    payload = {"alerts": [
        _alert("PodOOMKilled"),
        {"status": "resolved", "labels": {"alertname": "PodOOMKilled", "namespace": "x"}},
        _alert("UnknownThing"),
    ]}
    sigs = alerts_to_signals(payload, TENANT)
    assert len(sigs) == 1
