# Test & Evaluation Report — Task Force 3 · CDO-02

<!-- Doc owner: CDO-02
     Status: v2.0 — W12 LIVE (2026-07-02)
     Phạm vi: CDO platform QA — telemetry → AI contract → safety → execute/deny → verify → audit -->

**Dự án:** TF3 Self-Heal Agent AWS — CDO-02  
**Report owner:** CDO-02  
**Ngày tạo:** 2026-06-29 · **Cập nhật:** 2026-07-02  
**Trạng thái:** v2.0 — **LIVE trên EKS thật, AI Engine V5, E2E `auto_resolved` đã verify**

> Scope: phần CDO platform. Không claim chất lượng model AI. Mọi `Measured/Actual` phải có evidence path hoặc command output đi kèm. Mock/stub evidence không được tính là real EKS evidence.

---

## 1. Test coverage

**Mục đích:** chứng minh Self-Heal loop đi được từ telemetry đầu vào đến action/audit đầu ra, và fail-safe khi AI response, tenant, action hoặc verify không đạt điều kiện an toàn.

Luồng CDO được test:

```text
Telemetry / Alertmanager
→ Forwarder (PII-scrub v3)
→ SQS buffer → Executor
→ AI /v1/detect
→ Pre-Decide Gate (confidence/severity/flapping)
→ Idempotency lock
→ AI /v1/decide
→ Safety Gate (3 lớp: app-level → RBAC → Kyverno)
→ Snapshot (rollback state)
→ Execute urgent K8s API  hoặc  deferred GitOps
→ AI /v1/verify (service_error_rate thật)
→ Audit stdout / S3 Object Lock / CloudWatch
```

| Test type | Tool / Method | Coverage / Scope | Status | Evidence |
|---|---|---|---|---|
| Unit — Safety Gate | `pytest executor/tests/test_safety_gate.py` | 8 cases: cross-tenant, action allow-list, blast-radius, verify-policy, scale-to-zero, pattern routing | **PASS local** | `evidence/qa-07/pytest_executor_tests.txt` |
| Unit — Circuit Breaker | `pytest executor/tests/test_circuit_breaker.py` | 5 cases: closed/trip/window/reset/half-open | **PASS local** | `evidence/qa-07/pytest_executor_tests.txt` |
| Unit — SQS Source | `pytest executor/tests/test_sqs_source.py` | group-by-ns/dep, malformed body, missing namespace | **PASS local** | `evidence/qa-07/pytest_executor_tests.txt` |
| Unit — Forwarder Alert Map | `pytest forwarder/tests/test_alert_map.py` | 9 cases: OOM→pod_oom_event, crashloop→restart_count, latency, PII-scrub, resolved skip, batch filter | **PASS local** | `evidence/qa-07/pytest_forwarder_tests.txt` |
| Contract / schema | Scenario JSON + AI API validation | telemetry schema (6 fields bắt buộc), 12 signal enum, detect/decide/verify response shape | PASS mock; real AI response confirm online chaos | request/response JSON trong executor logs |
| Integration — AI | Executor → AI `/v1/detect`, `/v1/decide`, `/v1/verify` | AI V5 contract compatibility, latency, error handling | **AI V5 live** theo §0 online chaos | executor logs + AI rollout output |
| E2E scenario | `executor/run_scenarios.py` (`sc01`–`sc14`) | 14 scenarios, ≥10 auto-resolve target | **PASS: 10/14 auto-resolve** | `evidence/qa-07/offline_scenario_run_14.txt` |
| Real EKS action | Online Boutique + podinfo + executor | RESTART urgent: tenant-a | **PASS live: tenant-a restart → auto_resolved** | kubectl rollout output + audit |
| Deferred GitOps | `executor/executors/deferred.py` + ADR-008 | SCALE_REPLICAS / ROTATE_SECRET | Designed + ADR; không claim full-real nếu chưa có ArgoCD output | ADR-008 + `08_adrs.md` |
| Security / RBAC | pytest + Safety Gate deny paths | cross-tenant deny, unsafe action deny, blast-radius | **PASS** app gate + sc11/sc12 deny | `evidence/qa-07/pytest_executor_tests.txt` |
| Observability / Forwarder | Alertmanager → Forwarder v3 → SQS | Alert → PII-scrub → queue → executor | **Forwarder v3 live** | forwarder log + SQS |
| Audit | stdout JSON lines, CloudWatch, S3 Object Lock | trace theo `correlation_id`, retention ≥90d | **PASS** 14/14 offline indexed; S3/CWL screenshot-backed live | `evidence/qa-07/audit_index.md`, `evidence/EVIDENCE_PACK_FINAL.md` |
| Load / soak | `run_scenarios.py --duration 4h` | repeated incident loop, auto-resolve stability | `--duration 4h` chạy; official raw log chưa đính kèm | SKIP nếu không có evidence chính thức |

### 1.1 Components under test

| Component | Source | Vai trò trong test |
|---|---|---|
| CDO Executor | `executor/main.py` | orchestration loop: detect → safety → execute → verify → audit |
| Pre-Decide Gate | `executor/pre_decide_gate.py` | discard/escalate trước decide nếu confidence thấp / flapping |
| Safety Gate | `executor/safety_gate.py` | chặn cross-tenant, action lạ, blast-radius, missing verify-policy |
| Circuit Breaker | `executor/circuit_breaker.py` | safety sub-checkpoint #5: open sau N failure liên tiếp |
| Idempotency Lock | `executor/idempotency.py` | in-memory (sandbox); DynamoDB production path (ADR-006) |
| K8s Client | `executor/k8s_client.py` | urgent actions: RESTART / PATCH_MEMORY / ROLLOUT_UNDO; mock khi `CDO_K8S_MOCK=true` |
| Urgent Executor | `executor/executors/urgent.py` | dry-run trước → execute K8s API |
| Deferred Executor | `executor/executors/deferred.py` | GitOps path (ADR-008); designed-only nếu chưa có ArgoCD output |
| Audit Logger | `executor/audit.py` | stdout JSON lines → S3 Object Lock / CloudWatch |
| Alert Forwarder v3 | `forwarder/forwarder.py` | Alertmanager → PII-scrub (7 pattern) → SQS |
| Alert Map | `forwarder/alert_map.py` | chuẩn hóa Alertmanager alert → telemetry signal đúng contract |
| AI Engine V5 | `manifests/ai-engine/deployment.yaml` | BOCPD + BARO RCA — real pod, không mock |
| Scenario Runner | `executor/run_scenarios.py` | chạy `sc01`–`sc14`, đo auto-resolve rate, exit code 0/1 |
| Mock AI Server | `executor/mock_ai_server.py` | scenario-driven mock cho offline deterministic run |

---

## 2. SLO evidence

| SLO / Requirement | Target | Measured | Window | Mode | Pass/Fail | Evidence |
|---|---:|---|---|---|---|---|
| Scenario count | ≥10 injected | **14 scenarios** | QA-07 local run | mock-offline | **PASS** | `evidence/qa-07/offline_scenario_run_14.txt` |
| Auto-resolve rate | ≥60% | **10/14 = 71.4%** | QA-07 local run | mock-offline deterministic | **PASS** | runner summary trong `offline_scenario_run_14.txt` |
| Unsafe action count | 0 | **0** unsafe mutation; sc11/sc12 denied | scenario set + online chaos | mixed | **PASS** | `evidence/qa-07/audit_index.md`, online chaos log |
| Cross-tenant mutation | 0 | **0**; sc11 deny + live tenant-b deny | sc11 + live | mixed | **PASS** | `audit_index.md`, `evidence/w12-scenario-sim/online_chaos_report.log` |
| Audit coverage | 100% incidents | **14/14** offline scenarios indexed; live audit screenshot-backed | QA-07 + AWS console | mixed | **PASS** for scenario set | `evidence/qa-07/audit_index.md`, `evidence/EVIDENCE_PACK_FINAL.md` |
| Real AI readiness | AI pod ready | **AI V5 live** — deploy rollout success | W12 live | full-real | **PASS** | AI rollout output + `/ready` |
| Real EKS mutation | ≥1 urgent action | **tenant-a restart → auto_resolved** | online chaos | full-real | **PASS** | online chaos log + kubectl rollout output |
| Tamper-evident audit | ≥90d retention | **S3 Object Lock Governance 90d** | W12 live | production | **PASS** | S3 Object Lock console evidence |
| PII / secret scrub | 0 raw PII in queue/audit | **9 forwarder tests pass**; 7 scrub patterns (email/card/SSN/AWS-key/token/password/IP) | QA-07 local | local + production design | **PASS** | `evidence/qa-07/pytest_forwarder_tests.txt` |
| Critical security findings | 0 | Unit / security logic tests pass; Trivy/gitleaks/kube-linter output chưa đính kèm | CI / local | CI/local | **TBD** | Trivy/gitleaks/kube-linter output cần bổ sung |
| Scenario window | ≥4h | `--duration 4h` arg; official raw log chưa đính kèm | soak | mock-offline | **SKIP** | bỏ qua nếu không có log chính thức |

### 2.1 SLO breach analysis

| Breach / Risk | Observed | Root cause | Fix / mitigation | Evidence |
|---|---|---|---|---|
| Verify rubber-stamp | verify từng trả DONE khi post-telemetry thiếu service health | post-telemetry chỉ có `container_resource_usage` | executor v8 gửi `service_error_rate` thật; AI verify phân biệt err=0→DONE, err=0.5→ESCALATE | executor/AI verify logs |
| PII lọt qua alert payload | forwarder chưa scrub đủ pattern | version cũ thiếu AWS-key/token/password pattern | forwarder v3 — 7 pattern, 9 test cases pass | `pytest_forwarder_tests.txt` |
| Cross-tenant AI/action risk | AI có thể trả target namespace sai | AI V5 không enforce CDO tenant boundary | Safety Gate deny trước execute + RBAC/Kyverno defense-in-depth (ADR-003, ADR-009) | sc11/live deny audit |
| Deferred SCALE/ROTATE chưa full-real | GitOps path designed/deferred | ArgoCD path chưa có sync output | ghi rõ designed-only; không tính là urgent live mutation | ADR-008 + `08_adrs.md` |
| Fresh `kubectl auth can-i` chưa thu thập | runtime RBAC evidence skip | tránh dùng blocked/local-context output làm submission evidence | dùng AWS console screenshot IRSA evidence; collect `auth can-i` khi có EKS context | `evidence/images/iam-irsa-executor.png` |

---

## 3. Load / soak test results

### 3.1 Test setup

Load/soak của CDO-02 là scenario loop, không phải HTTP RPS. Mục tiêu: hệ thống xử lý nhiều incident liên tiếp, giữ idempotency, không flap, không tạo unsafe action.

- **Load profile:** `executor/run_scenarios.py --duration 4h` — loop qua 14 scenario liên tiếp
- **Scenario set:** `sc01`–`sc14` (`executor/scenarios/sc*.json`)
- **Tenants simulated:** `tenant-a`, `tenant-b`
- **Runtime modes:** offline deterministic (mock AI) cho coverage; online chaos (full-real) cho ≥1 live flow
- **Target:** ≥10 scenarios, auto-resolve ≥60%, unsafe action = 0

### 3.2 Results

| Metric | Target | Achieved | Mode | Evidence |
|---|---:|---|---|---|
| Scenarios injected | ≥10 | **14** | mock-offline | `evidence/qa-07/offline_scenario_run_14.txt` |
| Scenario window | ≥4h | not measured; no official raw log | skipped | SKIP |
| Auto-resolved | ≥60% | **10/14 = 71.4%** | mock-offline | runner summary |
| Online chaos restart | ≥1 full-real mutation | **tenant-a restart → auto_resolved** | full-real | `online_chaos_report.log` |
| Cross-tenant deny | 0 mutation | **0 mutation; deny observed** | full-real + mocked safety | audit log |
| Unsafe action | 0 | **0 observed** | mixed | safety gate + audit |

**Scenario breakdown (14 scenarios):**

| sc | Scenario | Expected | Mode | Result |
|---|---|---|---|---|
| sc01 | OOM Kill → PATCH_MEMORY_LIMIT | auto_resolved | mock-offline | ✅ PASS |
| sc02 | CrashLoop tenant-a → RESTART | auto_resolved | mock-offline | ✅ PASS |
| sc03 | Latency spike → RESTART | auto_resolved | mock-offline | ✅ PASS |
| sc04 | Bad deploy → ROLLOUT_UNDO | auto_resolved | mock-offline | ✅ PASS |
| sc05 | Memory pressure → PATCH_MEMORY | auto_resolved | mock-offline | ✅ PASS |
| sc06 | OOM Kill tenant-b → PATCH_MEMORY | auto_resolved | mock-offline | ✅ PASS |
| sc07 | CrashLoop tenant-b → RESTART | auto_resolved | mock-offline | ✅ PASS |
| sc08 | Latency tenant-b → RESTART | auto_resolved | mock-offline | ✅ PASS |
| sc09 | OOM persist → verify ROLLBACK | rolled_back | mock-offline | ✅ PASS |
| sc10 | Scale capacity → SCALE_REPLICAS (deferred) | auto_resolved | mock-offline | ✅ PASS |
| sc11 | Cross-tenant AI target | escalated:denied_cross_tenant | mock-offline | ✅ PASS |
| sc12 | Unsafe action DELETE_NAMESPACE | escalated:denied_action_not_allowed | mock-offline | ✅ PASS |
| sc13 | Low confidence + low severity | low_confidence_no_action | mock-offline | ✅ PASS |
| sc14 | Verify escalate — error_rate 0.4 | escalated:verify_escalate | mock-offline | ✅ PASS |

> `auto_resolved` + `rolled_back` đều tính là resolved. sc11–sc14 là safety/failure scenarios — pass là deny/escalate đúng, không tính vào tử số auto-resolve.

### 3.3 Bottleneck identified

| Bottleneck / Risk | Symptom | Current mitigation | Evidence to collect |
|---|---|---|---|
| Sparse telemetry → verify rubber-stamp | AI detect false negative hoặc verify DONE sai | dense-window Prometheus trong executor v8; gửi `service_error_rate` thật | PromQL output + verify request body |
| AI endpoint timeout | executor escalate `ai_unavailable` | timeout handling + escalation path (AIError → circuit breaker) | executor audit theo `correlation_id` |
| Repeated alert flapping | duplicate execute | cooldown map (`CDO_HEAL_COOLDOWN_S`) + idempotency lock | executor log showing skip/cooldown |
| SQS/env wiring miss | alert không vào executor | forwarder v3 + SQS logs | forwarder log + SQS receive/delete metrics |
| Audit bucket retention drift | stdout only, không immutable | S3 Object Lock Governance 90d (ADR-004) | S3 retention command output |

---

## 4. Security test

### 4.1 Penetration touch points

| Touch point | Method | Expected result | Current status | Evidence |
|---|---|---|---|---|
| Cross-tenant target | incident `tenant-a`, action target `tenant-b` | `SafetyDenied("denied_cross_tenant")` before execute | **PASS:** sc11 deny + online live tenant-b deny | `audit_index.md`, online chaos log |
| Unsupported action | AI trả `DELETE_NAMESPACE` | `SafetyDenied("denied_action_not_allowed")` | **PASS:** sc12 denied; pytest `test_action_not_in_allow_list` | `pytest_executor_tests.txt` |
| Blast radius — replicas | replicas=50 | `SafetyDenied("blast_radius_exceeded")` | **PASS:** pytest `test_blast_radius_replicas` | `pytest_executor_tests.txt` |
| Blast radius — memory | memory=8192Mi | `SafetyDenied("blast_radius_exceeded")` | **PASS:** pytest `test_blast_radius_memory` | `pytest_executor_tests.txt` |
| Scale to zero | replicas=0 | `SafetyDenied("scale_to_zero_denied")` | **PASS:** pytest `test_scale_to_zero_denied` | `pytest_executor_tests.txt` |
| Missing verify policy | AI decide thiếu `verify_policy` | `SafetyDenied("missing_verify_policy")` | **PASS:** pytest `test_missing_verify_policy` | `pytest_executor_tests.txt` |
| Pattern routing mismatch | SCALE_REPLICAS trong urgent plan | `SafetyDenied("invalid_pattern_type")` | **PASS:** pytest `test_pattern_routing_mismatch` | `pytest_executor_tests.txt` |
| Duplicate incident | same idempotency key | skip duplicate execute | **PASS:** circuit breaker + SQS source unit tests | `pytest_executor_tests.txt` |
| PII/secret in alert | email/card/SSN/AWS-key/token/password in payload | scrub trước khi vào SQS/audit | **PASS:** 9 forwarder tests pass (7 pattern) | `pytest_forwarder_tests.txt` |
| RBAC forbidden verb | executor tries forbidden namespace/verb | Kubernetes denies | screenshot-backed; fresh `auth can-i` chưa thu thập | `evidence/images/iam-irsa-executor.png` |
| Kyverno admission | replicas>10 / memory>4Gi dry-run | admission deny | policy manifests live; fresh runtime output chưa thu thập | `manifests/kyverno/policies/` |

**3-layer defense:**

```text
Layer 1: Safety Gate (app-level)    — safety_gate.py — fail-closed, SafetyDenied trước execute
Layer 2: RBAC (verb-level)          — manifests/rbac/ — least-privilege, không có delete verb
Layer 3: Kyverno (value-level)      — manifests/kyverno/ — ClusterPolicy Enforce (ADR-009)
```

### 4.2 Vulnerability scan

| Item | Tool | Target | Expected | Current status | Evidence |
|---|---|---|---|---|---|
| Python lint / static | `ruff` / CI | `executor/`, `forwarder/` | no critical | CI output exists | CI log |
| Secret scan | `gitleaks` | repo | 0 committed secret | `.gitleaks.toml` present; scan output chưa đính kèm | scan output TBD |
| Container scan | Trivy | executor/forwarder/AI images | 0 CRITICAL | chưa đính kèm | Trivy output TBD |
| K8s manifest scan | kube-linter / kubeconform | `manifests/` | valid schema, no critical | chưa đính kèm | scan output TBD |

---

## 5. Multi-tenant isolation test

Cross-tenant mutation là SEV1. CDO không được mutate namespace khác tenant của incident, kể cả khi AI trả action sai.

| Test | Method | Expected | Current result | Evidence |
|---|---|---|---|---|
| AI trả target namespace khác incident | sc11 scenario + mock decide trả `tenant-b` | `denied_cross_tenant` before execute | **PASS:** sc11 + online live deny | `audit_index.md`, `online_chaos_report.log` |
| Tenant A SA mutate Tenant B | `kubectl auth can-i patch deployment -n tenant-b` | denied | screenshot-backed; fresh output chưa thu thập | `evidence/images/iam-irsa-executor.png` |
| Unsupported namespace mutation | Kyverno dry-run | admission deny | policy manifests live; output chưa thu thập | `manifests/kyverno/policies/` |
| SQS message wrong tenant_id | malformed/mismatch payload | reject/escalate, no execute | covered bởi SQS source tests + safety path | `pytest_executor_tests.txt` |
| Audit tenant trace | query `correlation_id` + `tenant_id` | full chain scoped to one tenant | **PASS** 14/14 offline indexed; live screenshot-backed | `audit_index.md`, `evidence/images/cwl-correlation-trace.png` |

**Pass conditions:**

```text
cross_tenant_mutation_count = 0
unsafe_action_count = 0
deny/escalate reason xuất hiện trong audit
không có Kubernetes event cho mutation ở namespace sai
```

---

## 6. Failure analysis

### 6.1 Failures encountered during W12

| # | Failure | Root cause | Fix | Verification |
|---|---|---|---|---|
| 1 | Verify rubber-stamp DONE | post-telemetry chỉ có `container_resource_usage`, thiếu signal health/error | executor v8 gửi `service_error_rate` thật; AI verify: err=0→DONE, err=0.5→ESCALATE | verify logs DONE/ESCALATE |
| 2 | PII lọt qua alert payload | forwarder v2 chưa scrub đủ pattern | forwarder v3: 7 pattern (email/card/SSN/AWS-key/token/password/IP), 9 test case | `pytest_forwarder_tests.txt` |
| 3 | Cross-tenant action risk | AI V5 có thể trả target namespace sai | Safety Gate deny trước execute + RBAC + Kyverno 3-layer (ADR-003, ADR-009) | sc11/live deny audit |
| 4 | Deferred SCALE/ROTATE chưa full-real proof | GitOps/ArgoCD path là designed/deferred | ghi rõ designed-only, không claim urgent live mutation | ADR-008 + `08_adrs.md` |

### 6.2 Test gaps acknowledged

| Gap | Impact | Owner | Mitigation |
|---|---|---|---|
| Trivy/gitleaks/kube-linter output chưa đính kèm | chưa chốt `Critical findings = 0` | CDO-02 | lấy CI output; scan Trivy trên executor/forwarder image |
| RBAC `kubectl auth can-i` fresh output | không có fresh runtime proof | CDO-02 | dùng AWS IRSA screenshot evidence hiện có; collect khi có EKS context |
| Kyverno admission deny fresh runtime | chỉ có policy manifests, không có deny output | CDO-02 | dry-run test trong safe window; manifests ở `manifests/kyverno/policies/` |
| Deferred GitOps chưa có ArgoCD sync output | không claim full-real SCALE/ROTATE | CDO-02 | giữ designed-only hoặc bổ sung ArgoCD sync evidence |
| Official 4h raw soak log chưa đính kèm | không claim `--duration 4h` window chính thức | CDO-02 | chạy `python run_scenarios.py --duration 4h` và lưu stdout |

---

## 7. Final summary

| Summary metric | Target | Actual | Mode mix | Pass/Fail |
|---|---:|---|---|---|
| Total scenarios injected | ≥10 | **14** | mock-offline | **PASS** |
| Scenario window | ≥4h | not measured; no official raw log | skipped | **SKIP** |
| Auto-resolve rate | ≥60% | **10/14 = 71.4%** | mock-offline | **PASS** |
| Unsafe actions | 0 | **0 observed** | mixed | **PASS** |
| Cross-tenant leaks | 0 | **0 observed** | mixed / full-real deny | **PASS** |
| Complete audit coverage | 100% | **14/14** offline indexed; live screenshot-backed | mixed | **PASS** for scenario set |
| Real AI scenarios | core flow | **AI V5 live** — online chaos verified | full-real | **PASS** |
| Real EKS mutation | ≥1 | **tenant-a restart → auto_resolved** | full-real | **PASS** |
| Critical security findings | 0 | unit/security logic tests pass; vuln scan TBD | CI/local | **TBD** |

**Conclusion:** CDO-02 đáp ứng core Pack #2 Self-Heal requirements — scenario count (14), auto-resolve rate (71.4% ≥ 60%), zero unsafe action, multi-tenant deny (sc11 + live), real AI V5 integration, và ≥1 full-real EKS mutation (tenant-a restart). QA-07 bổ sung pytest output (executor + forwarder), scenario runner output, và 14/14 audit index. Công việc còn lại: security/vulnerability scan output và fresh `kubectl auth can-i` / Kyverno runtime output khi có EKS context.

---

## Related documents

- [`02_infra_design.md`](02_infra_design.md) — SLO targets, Safety Gate design, multi-tenant flow
- [`03_security_design.md`](03_security_design.md) — RBAC, Kyverno, PII-scrub, 3-layer defense
- [`04_deployment_design.md`](04_deployment_design.md) — EKS cluster, namespace layout, forwarder
- [`06_runbook_library.md`](06_runbook_library.md) — runbook mapping per scenario
- [`08_adrs.md`](08_adrs.md) — ADR-003 tenant isolation, ADR-004 S3 audit, ADR-006 idempotency, ADR-008 GitOps, ADR-009 Kyverno
- [`09_deploy_runbook_live.md`](09_deploy_runbook_live.md) — live deploy steps
- `executor/run_scenarios.py` — scenario runner source
- `executor/safety_gate.py` — Safety Gate source
- `executor/tests/` — unit test suite
- `forwarder/tests/` — forwarder unit test suite
- `injectionplan.md` — scenario injection plan source
- `manifests/kyverno/policies/` — Kyverno ClusterPolicy
