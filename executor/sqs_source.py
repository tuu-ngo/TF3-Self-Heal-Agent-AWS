"""
SQS telemetry source — nguồn telemetry CHÍNH theo telemetry-contract §2.5.C.

Alert Forwarder (forwarder/) nhận webhook Alertmanager → chuẩn hóa thành telemetry
signal đúng schema §3 → SendMessage vào SQS buffer. Executor đọc SQS ở đây, gom các
signal theo (namespace, deployment) thành 1 incident `telemetry_window`, đưa vào
`Executor.handle_incident` (vòng detect→decide→execute→verify).

Mỗi SQS message body = 1 telemetry signal JSON (forwarder gửi 1 message / signal).
- Long-poll (WaitTimeSeconds) để giảm empty-receive cost.
- Message parse lỗi → KHÔNG ack → SQS redrive → DLQ sau maxReceiveCount (contract §2.5.B).
- Chỉ ack (DeleteMessage) sau khi incident xử lý xong (at-least-once, idempotency lock
  ở /v1/decide chống double-execute).

Degrade an toàn: thiếu boto3 hoặc CDO_TELEMETRY_QUEUE_URL rỗng → enabled=False, drain()=[].
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field

from config import CONFIG

try:
    import boto3
    _HAS_BOTO = True
except ImportError:  # dev/offline không cài boto3
    _HAS_BOTO = False


@dataclass
class SqsIncident:
    """1 incident gom từ các SQS message cùng (namespace, deployment)."""
    namespace: str
    deployment: str
    telemetry_window: list[dict] = field(default_factory=list)
    receipt_handles: list[str] = field(default_factory=list)


class SqsTelemetrySource:
    def __init__(self, cfg=CONFIG):
        self.cfg = cfg
        self._sqs = None
        if _HAS_BOTO and cfg.telemetry_queue_url:
            self._sqs = boto3.client("sqs", region_name=cfg.aws_region)

    @property
    def enabled(self) -> bool:
        return self._sqs is not None

    def drain(self) -> list[SqsIncident]:
        """
        Đọc 1 batch message (long-poll), gom theo (namespace, deployment).
        Trả [] nếu không bật hoặc không có message. KHÔNG raise — lỗi SQS → [] để
        watch_loop fallback sang watcher poll K8s.
        """
        if not self.enabled:
            return []
        try:
            resp = self._sqs.receive_message(
                QueueUrl=self.cfg.telemetry_queue_url,
                MaxNumberOfMessages=self.cfg.sqs_max_messages,
                WaitTimeSeconds=self.cfg.sqs_wait_time_s,
                MessageAttributeNames=["All"],
            )
        except Exception as e:  # noqa: BLE001 — fail-safe, để fallback watcher chạy
            print(f"[sqs] receive_message error: {e}")
            return []

        messages = resp.get("Messages", [])
        return self._group(messages)

    @staticmethod
    def _group(messages: list[dict]) -> list[SqsIncident]:
        by_key: dict[tuple[str, str], SqsIncident] = {}
        for m in messages:
            handle = m.get("ReceiptHandle", "")
            try:
                signal = json.loads(m.get("Body") or "{}")
            except (ValueError, TypeError):
                # body lỗi cú pháp → bỏ qua (không ack) → redrive → DLQ
                print("[sqs] bỏ qua message body malformed (sẽ về DLQ)")
                continue
            labels = signal.get("labels") or {}
            ns = labels.get("namespace")
            dep = labels.get("deployment", "")
            if not ns:
                # thiếu namespace → không định tuyến được tenant → bỏ qua (về DLQ)
                print("[sqs] bỏ qua message thiếu labels.namespace (sẽ về DLQ)")
                continue
            key = (ns, dep)
            inc = by_key.get(key)
            if inc is None:
                inc = SqsIncident(namespace=ns, deployment=dep)
                by_key[key] = inc
            inc.telemetry_window.append(signal)
            if handle:
                inc.receipt_handles.append(handle)
        return list(by_key.values())

    def ack(self, incident: SqsIncident) -> None:
        """Xóa các message của incident sau khi xử lý xong (at-least-once)."""
        if not self.enabled or not incident.receipt_handles:
            return
        entries = [{"Id": str(i), "ReceiptHandle": h}
                   for i, h in enumerate(incident.receipt_handles)]
        try:
            self._sqs.delete_message_batch(
                QueueUrl=self.cfg.telemetry_queue_url, Entries=entries)
        except Exception as e:  # noqa: BLE001
            print(f"[sqs] delete_message_batch error: {e}")
