variable "grafana_admin_password" {
  description = "Mật khẩu admin Grafana (sandbox). Production: dùng Secrets Manager / random."
  type        = string
  default     = "cdo-grafana-dev"
  sensitive   = true
}

variable "forwarder_webhook_url" {
  description = "URL webhook Alert Forwarder để Alertmanager đẩy alert (in-cluster)."
  type        = string
  default     = "http://cdo-telemetry-forwarder.monitoring.svc.cluster.local:8080/alerts"
}
