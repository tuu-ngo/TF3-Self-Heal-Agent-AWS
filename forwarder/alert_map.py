"""
Ánh xạ Alertmanager alert → telemetry signal đúng telemetry-contract §3.

Alert do PrometheusRule (manifests/monitoring/prometheus-rules.yaml) sinh ra; alertname
khớp catalog runbook (docs/06_runbook_library.md §3). Forwarder chỉ chuẩn hóa + đẩy SQS,
KHÔNG gọi AI (executor mới chạy vòng detect→decide→verify).

Schema output mirror executor/watcher.py:_signal():
  { ts, tenant_id, service, signal_name, value, labels{system,namespace,deployment,...} }

value đúng kiểu theo contract §4:
  - container_restart_count       → int
  - container_resource_usage      → int (bytes)
  - service_latency_p95           → number (ms)
  - service_error_rate            → number (0..1)
  - pod_oom_event / service_unhealthy → string mô tả
"""
from __future__ import annotations

import time
from typing import Any

# alertname → (signal_name enum §3, value_kind)
ALERT_SIGNAL_MAP: dict[str, tuple[str, str]] = {
    "PodOOMKilled":          ("pod_oom_event", "str"),
    "ContainerCrashLooping": ("container_restart_count", "int"),
    "ImagePullBackOff":      ("service_unhealthy", "str"),
    "HighContainerMemory":   ("container_resource_usage", "int"),
    "HighLatencyP95":        ("service_latency_p95", "float"),
    "HighErrorRate":         ("service_error_rate", "float"),
    "ServiceUnhealthy":      ("service_unhealthy", "str"),
}


def _now_rfc3339_ms() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime()) + \
        f".{int((time.time() % 1) * 1000):03d}Z"


def _deployment_of(labels: dict[str, str]) -> str:
    """Lấy deployment từ label; nếu chỉ có pod → strip 2 hash suffix (rs-<h>-<h>)."""
    for k in ("deployment", "workload", "label_app"):
        if labels.get(k):
            return labels[k]
    pod = labels.get("pod") or labels.get("pod_name") or ""
    parts = pod.rsplit("-", 2)
    return parts[0] if len(parts) == 3 else (pod or "unknown")


def _coerce(kind: str, raw: Any) -> Any:
    if kind == "int":
        try:
            return int(float(raw))
        except (TypeError, ValueError):
            return 1
    if kind == "float":
        try:
            return float(raw)
        except (TypeError, ValueError):
            return 0.0
    return str(raw) if raw is not None else ""


def alert_to_signal(alert: dict, tenant_id: str) -> dict | None:
    """
    1 alert (firing) → 1 telemetry signal. Trả None nếu:
      - status != firing (resolved → bỏ qua)
      - alertname không nằm trong map
      - thiếu namespace (không định tuyến được tenant)
    """
    if alert.get("status", "firing") != "firing":
        return None

    labels = alert.get("labels", {}) or {}
    annotations = alert.get("annotations", {}) or {}
    alertname = labels.get("alertname", "")
    mapped = ALERT_SIGNAL_MAP.get(alertname)
    if mapped is None:
        return None

    namespace = labels.get("namespace")
    if not namespace:
        return None

    signal_name, kind = mapped
    deployment = _deployment_of(labels)
    service = labels.get("service") or labels.get("label_app") or deployment

    # value: ưu tiên annotations.value (PrometheusRule set), else mô tả/giá trị mặc định
    if kind == "str":
        value = annotations.get("description") or _default_text(signal_name, labels)
    else:
        value = _coerce(kind, annotations.get("value"))

    out_labels: dict[str, str] = {
        "system": "K8S_NATIVE",
        "namespace": namespace,
        "deployment": deployment,
    }
    for src, dst in (("pod", "pod_name"), ("container", "container")):
        if labels.get(src):
            out_labels[dst] = labels[src]

    return {
        "ts": _now_rfc3339_ms(),
        "tenant_id": tenant_id,
        "service": service,
        "signal_name": signal_name,
        "value": value,
        "labels": out_labels,
    }


def _default_text(signal_name: str, labels: dict[str, str]) -> str:
    pod = labels.get("pod", "?")
    container = labels.get("container", "main")
    if signal_name == "pod_oom_event":
        return f"OOMKilled: Pod {pod}, Container {container}, Exit Code 137"
    return f"{labels.get('alertname', 'unhealthy')}: {labels.get('namespace')}/{pod}"


def alerts_to_signals(payload: dict, tenant_id: str) -> list[dict]:
    """Alertmanager webhook payload {alerts:[...]} → list telemetry signal hợp lệ."""
    out = []
    for alert in payload.get("alerts", []) or []:
        sig = alert_to_signal(alert, tenant_id)
        if sig is not None:
            out.append(sig)
    return out
