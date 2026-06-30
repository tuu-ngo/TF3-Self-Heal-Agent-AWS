# Evidence Pack - CDO-02 Task Force 3 Self-Heal Engine

> Tài liệu hướng dẫn submission evidence cho **CDO-02** trong capstone W11-W12.
> Đề tài: **Self-Heal Agent for Kubernetes Workloads on AWS EKS**.
> Customize từ `CAPSTONE_EVIDENCE_PACK_FORMAT.md` cho project cụ thể của nhóm.

---

## 1. Mục Đích & Nguyên Tắc Cốt Lõi

Document trail = công cụ chính để show **process thinking**, không chỉ "đoạn code chạy được". Reviewer chấm dựa trên **3 layer evidence**:

1. **Document quality** — thinking, trade-off analysis, justification (đây là evidence pack)
2. **Build artifacts** — code executor, infra Terraform, K8s manifests working
3. **Buổi chấm performance** — present + Q&A + individual defense

Doc artifact đóng góp **~40% điểm W11** và **~30% điểm W12** (plus là input chính để reviewer hiểu trước buổi chấm T5 W12).

### 3 Quy tắc "Sống còn" cho CDO-02

| Quy tắc | Áp dụng cụ thể cho CDO-02 |
|---|---|
| **Live in repo** | Tất cả 7 docs nằm trong `docs/`, commit lịch sử đều đặn — KHÔNG viết 1 cục cuối T6/T4. Git history là bằng chứng process. |
| **Focus on WHY** | Tại sao chọn K8s-heavy angle? Tại sao namespace-based isolation thay vì cluster-per-tenant? Tại sao CDO executor là execution boundary, không để AI gọi K8s trực tiếp? |
| **Implementable** | Doc đủ chi tiết: ai đọc xong có thể `terraform apply` + `kubectl apply` + deploy executor + chạy scenario test lại được. |

---

## 2. Timeline Checkpoint cho CDO-02

```
W11 T2 ─── T3 ─── T4 ─── T5 ─── T6           W12 T2 ─── T3 ─── T4
                  ▲              ▲                  ▲              ▲
              [Progress #1]  [Evidence #1]    [Progress #2]   [Evidence #2]
              light check    MAIN ⭐           light check     MAIN ⭐
```

### 4 Checkpoint

| # | Khi | Bắt buộc gì (CDO-02 cụ thể) | Scoring |
|---|---|---|---|
| **Progress #1** (light) | EOD T4 W11 | `01_requirements_analysis.md` draft + `02_infra_design.md` draft (K8s-heavy angle declared, multi-tenant approach) + `08_adrs.md` ≥2 ADRs | Sanity check, không chấm chính thức |
| **Evidence Pack #1** ⭐ | EOD T6 W11 | TẤT CẢ 6 doc Pack #1 + VPC/EKS/Observability base infra chạy được | **~40% điểm W11** |
| **Progress #2** (light) | EOD T2 W12 | AI engine integration started + tenant onboarding flow draft + docs updated | Sanity check |
| **Evidence Pack #2** ⭐ | EOD T4 W12 (code freeze 18h) | TẤT CẢ 7 doc final + `05_cost_analysis.md` measured + `07_test_eval_report.md` với chaos response evidence + git tag `final` | **~30% điểm W12** + input chính cho buổi chấm T5 |

**Light progress check**: review qua repo commits + WhatsApp standup, không cần buổi formal. Mục đích phát hiện nhóm tụt sớm.

---

## 3. Document Set — CDO-02 (7 Documents)

CDO-02 cần submit tổng cộng **7 files** trong thư mục `docs/`:

| # | File | Pack #1 W11 | Pack #2 W12 | Mục tiêu | Trạng thái hiện tại |
|---|---|---|---|---|---|
| 1 | `01_requirements_analysis.md` | ✓ | ✓ refined | Phân tích đề tài Self-Heal từ infra/platform perspective | Ready (~30KB, ~4000+ từ) |
| 2 | `02_infra_design.md` | ✓ draft | ✓ updated | Architecture + K8s-heavy angle + multi-tenant approach | Ready (~32KB, comprehensive) |
| 3 | `03_security_design.md` | ✓ draft | ✓ refined | IAM · RBAC · NetworkPolicy · Audit · Tenant isolation | Ready (~15KB) |
| 4 | `04_deployment_design.md` | ✓ draft | ✓ working | Terraform IaC + ArgoCD GitOps + deployment strategy | Ready (~29KB, comprehensive) |
| 5 | `05_cost_analysis.md` | (skeleton) | ✓ **measured** | Per-tenant cost model + actual AWS spend | Draft — cần actual measured data W12 |
| 6 | `07_test_eval_report.md` | - | ✓ **new** | SLO evidence + scenario test + chaos response + security test | Draft — cần execution evidence W12 |
| 7 | `08_adrs.md` | ✓ ongoing | ✓ final (≥5) | Architecture Decision Records | ✅ Ready (7 ADRs, có thể cần thêm W12) |

### Contracts (do AI team own, CDO review + accept)

| Contract | File | Trạng thái |
|---|---|---|
| Telemetry Contract | `new-contract/telemetry-contract.md` | ✅ Signed 2026-06-25 |
| AI API Contract | `new-contract/ai-api-contract.md` | ✅ Signed 2026-06-25 |
| Deployment Contract | `new-contract/deployment-contract.md` | ✅ Signed 2026-06-25 |

---

## 4. Template & Word Count — CDO-02 Specific

### Word Count Tier

| Tier | Word target | Docs CDO-02 |
|---|---|---|
| **Light** | 800-1500 từ | `01_requirements_analysis.md`, `05_cost_analysis.md`, `08_adrs.md` |
| **Medium** | 1000-2500 từ | `02_infra_design.md`, `03_security_design.md`, `04_deployment_design.md`, `07_test_eval_report.md` |

> **Cảnh báo**: `< 500 từ` trong Light/Medium = thiếu depth, không pass. `> word target × 1.5` = fluff hoặc nên split sub-doc.

### 4.1 Template: `01_requirements_analysis.md`

**Tier: Light (800-1500 từ)** — Phân tích đề tài Self-Heal Engine từ CDO/infra perspective.

```markdown
# Requirements Analysis - Task Force 3 Self-Heal Engine - CDO-02

## 1. Bối cảnh đề tài
- Client: VP Engineering, SaaS B2B, 200+ microservices trên EKS
- Problem: On-call quá tải, 2-4 page/đêm, 80% known patterns lặp lại
- Pipeline mong muốn: detect → match runbook → execute audited action → verify → escalate nếu fail

## 2. Phạm vi CDO-02 phụ trách
- Platform architecture, K8s sandbox, multi-tenant isolation
- Safety gate, execution layer, audit, observability
- AI integration: consume 3 contracts, gọi AI endpoint

## 3. Yêu cầu phi chức năng (NFR) cho infra
- Multi-tenant: ≥ 2 tenants, namespace-based isolation
- Auto-resolve rate: ≥ 60% trên ≥ 10 scenarios
- Zero unsafe action
- Audit retention: ≥ 90 ngày
- Safety checkpoints: dry-run, blast-radius, verify, rollback, circuit breaker

## 4. Hướng khác biệt (Differentiation Angle) — KEY
- Angle: K8s-heavy / Kubernetes Workflow Orchestration
- Why: TF3 là bài toán self-heal trên K8s, CDO-02 chọn thao tác trực tiếp K8s workload
- Trade-off: Chi phí + complexity > serverless-first, nhưng sát đề + dễ demo RBAC/isolation

## 5. So sánh với nhóm cùng task force
- CDO khác angle: ... → khác nhau ở chỗ ...
- Cạnh tranh trên reliability + operational control

## 6. Ngoài phạm vi
- Không build AI model
- Không cho AI gọi K8s trực tiếp
- Chỉ sandbox + synthetic workload
```

### 4.2 Template: `02_infra_design.md`

**Tier: Medium (1000-2500 từ)** — Architecture chi tiết + K8s-heavy angle deep-dive.

```markdown
# Infrastructure Design - Task Force 3 Self-Heal Engine - CDO-02

## 1. Architecture diagram
Mermaid hoặc PNG — CDO executor, AI Engine, EKS, Safety Gate, Audit, Observability.
Caption bắt buộc + 2-3 dòng giải thích.

## 2. Component table
| Component | Service | Vai trò | Ghi chú |
|---|---|---|---|
| EKS Cluster | Amazon EKS | Kubernetes sandbox | Target chính của self-heal |
| CDO Executor | Pod/Deployment | Orchestrate workflow | CDO own |
| Safety Gate | Module trong executor | Validate tenant, namespace, blast-radius | Chặn unsafe action |
| Kyverno | Admission Webhook | Enforce replicas ≤ 10, memory ≤ 4Gi | Layer 3 defense |
| Audit Storage | S3 Object Lock | Tamper-evident audit | Retention ≥ 90 days |
| DynamoDB | Idempotency Lock | Prevent duplicate execution | Conditional write |
| SQS | Telemetry Buffer | CDO-internal buffer | AI không pull từ SQS |

## 3. Differentiation angle deep-dive — K8s-heavy
- Tại sao K8s-heavy? Self-heal cần thao tác trực tiếp RBAC, namespace, workload
- Vượt trội: demo safety gate + RBAC isolation + blast-radius thật trên K8s

## 4. Multi-tenant approach
- Namespace-based: tenant-a, tenant-b, self-heal-system
- Isolation: RBAC, NetworkPolicy, Kyverno admission
- Noisy neighbor mitigation: rate-limit per tenant (≤100 RPS detect, ≤10 RPS decide/verify)

## 5. Alternatives considered (KEY section — lấy điểm)
- Serverless-first: ít ops nhưng không sát K8s workload
- Managed-services heavy: khó thể hiện operator control
- Event-driven hybrid: over-engineer trong scope capstone

## 6. Luồng xử lý chính (Data flow)
alert → telemetry → SQS buffer → AI /v1/detect → Pre-Decide Gate → AI /v1/decide → Safety Gate → dry-run → execute → AI /v1/verify → audit

## 7. Failure modes + recovery
| Failure | Detection | Recovery | RTO/RPO |
|---|---|---|---|
| AI timeout/503 | HTTP timeout | No execute, escalate + audit | < 60s |
| Safety gate deny | Gate check | Escalate, ghi audit | Immediate |
| Execute fail | K8s API error | Rollback + circuit breaker | < 120s |
```

### 4.3 Template: `03_security_design.md`

**Tier: Medium (1000-2500 từ)** — hoặc Heavy nếu đủ depth.

```markdown
# Security Design - Task Force 3 Self-Heal Engine - CDO-02

## 1. IAM model
- IRSA (IAM Roles for Service Accounts) cho executor + AI Engine
- Least privilege: executor chỉ có quyền restart/scale/patch trong allowed namespaces
- Per-tenant RBAC Role/RoleBinding
- Kubernetes RBAC:
  - Executor ServiceAccount trong namespace `self-heal-system`
  - Role: chỉ có verbs cần thiết (get, list, patch, delete pods)
  - RoleBinding scoped theo tenant namespace (`tenant-a`, `tenant-b`)
  - ClusterRole không dùng — tránh quyền quá rộng

## 2. Secrets management
- AWS Secrets Manager / K8s Secrets cho API keys, DB credentials
- Rotation policy: manual rotation cho sandbox, target auto-rotation production
- Không lưu kubeconfig/secret trong repo, log hoặc container image
- K8s Secrets mount qua volume, không qua env vars (giảm exposure risk)
- `.gitignore` + `gitleaks` scan để chặn secret commit

## 3. Network policy
- VPC topology: private subnets, NAT gateway, VPC endpoints (S3/DynamoDB)
- NetworkPolicy chặn **inter-tenant communication** (tenant-a ↔ tenant-b blocked)
- AI Engine chỉ nhận traffic từ executor (namespace `self-heal-system`)
- Security groups: EKS node SG chỉ allow internal cluster traffic
- WAF/Shield: không implement trong sandbox, documented cho production consideration

## 4. Audit trail
- Format: JSON schema, keyed by `correlation_id`
- Storage: S3 Object Lock (Governance mode), retention ≥ 90 ngày
- Query: CloudWatch Logs Insights / Athena
- Mọi action (detect/decide/execute/verify/escalate/deny) đều ghi audit record

## 5. Compliance touch
- **SOC2 controls touched:**
  - CC6.1 (Logical access): RBAC least privilege + IRSA + namespace isolation
  - CC7.2 (System monitoring): CloudWatch Logs + Container Insights + audit trail
  - CC8.1 (Change management): ArgoCD GitOps + git history = audit trail cho mọi thay đổi
- **Data residency:** Tất cả data trong `us-east-1`, không cross-region replication trong sandbox
- **GDPR-style tenant data deletion + retention:**
  - Tenant data isolated theo namespace → xóa namespace = xóa toàn bộ workload data
  - Audit logs giữ ≥ 90 ngày (S3 Object Lock Governance) → sau retention period có thể delete
  - DynamoDB idempotency records TTL auto-delete sau 24 giờ
  - Không lưu PII trong audit log (chỉ `tenant_id`, `correlation_id`, action metadata)

## 6. Safety Gate (app-level security — CDO-02 specific)
- Validate: `tenant_id` match, namespace trong `allowed_namespaces`
- Blast-radius check: replicas ≤ 10, memory ≤ 4Gi
- Verify: local rollback path + `verify_policy` bắt buộc trước execute
- Kyverno admission webhook: layer 3 defense (cluster-level, independent từ executor code)

## 7. Threat model (STRIDE)
| Threat | Component | Mitigation |
|---|---|---|
| Spoofing | AI endpoint | K8s NetworkPolicy + ServiceAccount |
| Tampering | Audit log | S3 Object Lock (Governance mode) |
| Repudiation | Execute action | `correlation_id` trace end-to-end |
| Information Disclosure | Cross-tenant | RBAC + namespace isolation + NetworkPolicy |
| Denial of Service | Executor | Circuit breaker + rate limit per tenant |
| Elevation of Privilege | K8s RBAC | Least privilege + Kyverno admission |

## 8. Incident response runbook (high-level)
- **Detection**: CloudWatch Alarms + executor error logs + Kyverno deny events
- **Containment**: Circuit breaker halt executor + isolate affected namespace
- **Eradication**: Identify root cause via `correlation_id` trace + audit logs
- **Recovery**: ArgoCD rollback hoặc manual kubectl restore
- **Post-mortem**: Document trong ADR nếu cần design change
```

### 4.4 Template: `04_deployment_design.md`

**Tier: Medium (1000-2500 từ)** — IaC + CI/CD + GitOps.

```markdown
# Deployment & CI/CD Design - Task Force 3 Self-Heal Engine - CDO-02

## 1. IaC strategy
- Tool: Terraform >= 1.10
- Module structure: vpc/, eks/, iam/, observability/, audit/, kyverno/, argocd/
- State: S3 backend (target), hiện đang local state (known gap)

## 2. CI/CD pipeline
- GitHub Actions: lint → test → build → scan → deploy
- Quality gates: Terraform plan review, container image scan

## 3. GitOps — ArgoCD
- ArgoCD sync manifests/ → EKS cluster
- Sync waves: namespaces → RBAC → workloads → executor → AI Engine
- Drift detection: ArgoCD auto-sync

## 4. Deployment strategy
- Deferred actions: Git commit → ArgoCD sync (GitOps path)
- Urgent actions: Direct K8s API (RTO < 60s)
- Rollback: ArgoCD rollback hoặc executor local rollback

## 5. Environment separation
- Sandbox (duy nhất trong capstone)
- Production considerations documented nhưng không implement

## 6. Secrets in pipeline
- IRSA: không cần AWS credentials trong pipeline
- K8s secrets: managed qua ArgoCD sealed secrets hoặc External Secrets
```

### 4.5 Template: `05_cost_analysis.md`

**Tier: Light (800-1500 từ)** — Pack #2 phải có **measured actual**.

```markdown
# Cost Analysis - Task Force 3 Self-Heal Engine - CDO-02

## 1. Cost model per component
| Component | Unit cost | Usage (sandbox 10 days) | Total |
|---|---|---|---|
| EKS Cluster | $0.10/h | 240h | $24.00 |
| EC2 t3.medium × 2 | $0.0416/h/node | 240h | $20.00 |
| NAT Gateway | $0.045/h | 240h | $10.80 |
| S3 Audit | $0.023/GB | ~500MB | $0.04 |
| DynamoDB | On-Demand | ~5K WCU/day | $0.06 |
| SQS | Free tier | ~100K msg/day | $0.00 |
| CloudWatch | $0.50/GB ingested | ~5GB | $2.50 |
| **Total sandbox** | | | **~$80-90** |

## 2. Cost per tenant (production forecast)
| Tenants | Monthly estimate | Per-tenant |
|---|---|---|
| 2 | ~$160 | ~$80 |
| 10 | ~$400 | ~$40 |
| 50 | ~$1200 | ~$24 |

## 3. Cost optimization applied
- Single NAT Gateway (thay vì per-AZ) cho sandbox
- VPC Gateway Endpoints cho S3/DynamoDB (miễn phí)
- DynamoDB On-Demand + TTL auto-delete 24h
- SQS Free Tier

## 4. Cost vs alternatives (cùng task force)
- CDO khác: ước tính $X/tenant
- CDO-02: ước tính ~$80/tenant/sandbox — trade-off: EKS cluster cost cao nhưng sát đề K8s-heavy

## 5. Measured actual (capstone) — W12 REQUIRED
- AWS Cost Explorer data split by service
- Screenshot hoặc CSV từ AWS Billing
```

### 4.6 Template: `07_test_eval_report.md`

**Tier: Medium (1000-2500 từ)** — Pack #2 mới bắt buộc.

```markdown
# Test & Eval Report - Task Force 3 Self-Heal Engine - CDO-02

## 1. Test coverage
| Type | Tool | Scope | Status |
|---|---|---|---|
| Contract test | JSON schema | /v1/detect, /v1/decide, /v1/verify | Planned → Done |
| Safety unit test | pytest | allow-list, tenant match, blast-radius | Planned → Done |
| Integration test | Mock AI + executor | Full workflow | Planned → Done |
| E2E scenario test | Scenario injector | ≥10 scenarios, ≥4h window | Planned → Done |
| Load test | k6/Locust | Sustained flow | Planned → Done |
| Security test | RBAC abuse cases | Cross-tenant deny | Planned → Done |

## 2. Test Case Matrix (≥10 scenarios)
| ID | Scenario | Tenant | Expected result |
|---|---|---|---|
| TC-01 | Service stuck / latency spike | tenant-a | Auto-resolved via RESTART_DEPLOYMENT |
| TC-02 | Error rate spike | tenant-a | Auto-resolved via RESTART_DEPLOYMENT |
| TC-03 | OOM / memory pressure | tenant-b | Auto-resolved via PATCH_MEMORY_LIMIT |
| TC-04 | Secret/cert expiry | tenant-a | Deferred via ROTATE_SECRET (GitOps) |
| TC-05 | Queue backlog (synthetic) | tenant-b | Deferred via SCALE_REPLICAS (GitOps) |
| TC-06 | Duplicate scenario | tenant-a | Deduplicated via idempotency |
| TC-07 | Cross-tenant attempt | tenant-b→tenant-a | DENIED by safety gate |
| TC-08 | AI timeout/503 | tenant-a | No execute, escalate + audit |
| TC-09 | Low confidence response | tenant-b | No action, log warning |
| TC-10 | Disallowed namespace | tenant-a | DENIED by safety gate |

## 3. SLO Evidence
| SLO | Target | Measured | Pass/Fail |
|---|---|---|---|
| Executor availability | ≥ 99.5% | TBD | TBD |
| AI detect p99 | < 300ms | TBD | TBD |
| AI decide p99 | < 3000ms (LLM) | TBD | TBD |
| E2E auto-heal latency | < 5 min | TBD | TBD |
| Unsafe action rate | 0% | TBD | TBD |
| Auto-resolve rate | ≥ 60% | TBD | TBD |
| Audit coverage | 100% | TBD | TBD |

## 4. Chaos test results (Curveball — W12)
- Curveball #1 (small): ... response + outcome
- Curveball #2 (medium): ... response + outcome
- Curveball #3 (chaos): ... response + outcome

## 5. Security test
- Cross-tenant deny: confirmed via TC-07
- RBAC least privilege: verified
- Secret exposure check: passed

## 6. Failure analysis
| Failure | Root cause | Fix | Final status |
|---|---|---|---|
| TBD | TBD | TBD | TBD |

## 7. Load test results
- Tool: k6/Locust
- Synthetic load: X concurrent scenarios
- Observed behavior: ...
```

### 4.7 Template: `08_adrs.md`

**Tier: Light (800-1500 từ)** — Append-only, ≥3 ADRs cho Pack #1, ≥5 ADRs cho Pack #2.

```markdown
# Architecture Decision Records - CDO-02

## ADR-NNN - <Short title>
- **Status**: Proposed | Accepted | Superseded | Rejected
- **Date**: YYYY-MM-DD
- **Context**: 1-3 câu tại sao có decision này
- **Decision**: chốt cụ thể gì
- **Consequences**: trade-off + impact downstream
- **Alternatives considered**: bullet list với pros/cons từng option
```

**ADRs đã có của CDO-02** (tính đến W11):

| ADR | Title | Status |
|---|---|---|
| ADR-001 | Chọn K8s-heavy / Kubernetes Workflow Orchestration | Accepted |
| ADR-002 | AI là decision service, CDO executor là execution boundary | Accepted |
| ADR-003 | Namespace-based tenant isolation + RBAC least privilege | Accepted |
| ADR-004 | CDO self-host AI Engine container trong EKS | Accepted |
| ADR-005 | Kyverno admission webhook thay vì OPA Gatekeeper | Accepted |
| ADR-006 | S3 Object Lock Governance mode thay vì Compliance mode | Accepted |
| ADR-007 | SQS làm CDO-internal telemetry buffer | Accepted |

> W12 cần thêm ADRs cho: curveball response, GitOps deferred path, circuit breaker strategy, v.v.

---

## 5. Format Conventions — CDO-02

### File format
- **Markdown only** (`.md`) — không Google Doc / PDF rời rạc
- File live trong repo `docs/`, không attach binary
- Char encoding UTF-8

### Diagrams
- **Mermaid** preferred — embed inline, version-controllable
- PNG/draw.io export OK → place trong `docs/assets/` hoặc `docs/docs_ObservabilityStack/picture/`
- **BẮT BUỘC**: mọi diagram phải có caption + 2-3 dòng giải thích bên dưới

### Code blocks
- Dùng fenced code blocks với language tag: ` ```yaml `, ` ```python `, ` ```hcl `
- Doc chỉ chứa pseudo-code/snippet; full implementation ở `executor/` hoặc `infra/`

### ADR format (strict)
```markdown
## ADR-NNN - <Short title>
- **Status**: Proposed | Accepted | Superseded | Rejected
- **Context**: 1-3 câu tại sao
- **Decision**: chốt cụ thể gì
- **Consequence**: trade-off + impact downstream
- **Alternatives considered**: bullet list
```

### Cross-references
- Refer docs qua relative path: `[xem 02_infra_design.md](02_infra_design.md)`
- Refer ADR: `ADR-005`
- Refer contracts: `[AI API Contract](../new-contract/ai-api-contract.md)`

---

## 6. Scoring Integration — CDO-02

Doc artifacts map vào rubric pillar trong playbook:

### W11 Scoring (Evidence Pack #1)

| Rubric Pillar | % Điểm | Docs đóng góp (CDO-02) |
|---|---|---|
| P1 "Platform Design Doc" | **35%** | `01_requirements_analysis.md` + `02_infra_design.md` + `03_security_design.md` + `04_deployment_design.md` + `08_adrs.md` |
| P2 "Contract Acceptance" | **20%** | Contract review notes (3 contracts signed 2026-06-25) |
| P3 "Base Infra Ready" | **35%** | Build artifacts + `04_deployment_design.md` — VPC/EKS/Observability chạy được |
| P4 "Task Force Sync" | **10%** | Commit T3 angle no-overlap (K8s-heavy locked 2026-06-23) |

### W12 Scoring (Evidence Pack #2)

| Rubric Pillar | % Điểm | Docs đóng góp (CDO-02) |
|---|---|---|
| P1 "Infrastructure Quality" | **40%** | Build + `02_infra_design.md` updated + curveball adaptation |
| P2 "AI Engine Integration" | **25%** | E2E demo + `07_test_eval_report.md` + scenario evidence |
| P3 "Present Performance" | **25%** | Buổi chấm (không từ doc) |
| P4 "Individual Defense" | **15%** | Buổi chấm (không từ doc) |

### Chiến lược điểm cho CDO-02

> **W11**: P1 (35%) + P3 (35%) = 70% điểm đến từ docs + infra working. → **Ưu tiên viết docs chất lượng + có base infra chạy được.**
>
> **W12**: P1 (40%) + P2 (25%) = 65% điểm đến từ infra quality + AI integration. → **Ưu tiên integration working + test evidence + measured cost.**

---

## 7. Repo Structure — CDO-02 Actual

```
TF3-Self-Heal-Agent-AWS/
├── docs/                                    # Tất cả 7 evidence docs
│   ├── 01_requirements_analysis.md          # Ready
│   ├── 02_infra_design.md                   # Ready
│   ├── 03_security_design.md                # Ready
│   ├── 04_deployment_design.md              # Ready
│   ├── 05_cost_analysis.md                  # Draft → W12 measured
│   ├── 07_test_eval_report_v2.0.md      # Draft → W12 evidence
│   ├── 08_adrs.md                           # Ready (7 ADRs)
│   ├── standup_notes.md                     # Standup notes
│   └── docs_ObservabilityStack/             # Observability docs + diagrams
│
├── executor/                                # CDO Self-Heal Executor (Python)
│   ├── main.py                              # Main orchestrator
│   ├── ai_client.py                         # AI endpoint client
│   ├── safety_gate.py                       # Safety validation
│   ├── pre_decide_gate.py                   # Pre-decide filtering
│   ├── audit.py                             # Audit logging
│   ├── k8s_client.py                        # Kubernetes client
│   ├── circuit_breaker.py                   # Circuit breaker
│   ├── idempotency.py                       # Idempotency lock
│   ├── escalation.py                        # Escalation logic
│   ├── executors/                           # Action executors
│   ├── scenarios/                           # Test scenarios
│   ├── tests/                               # Unit tests
│   └── mock_ai_server.py                    # Mock AI for testing
│
├── infra/                                   # Terraform IaC
│   ├── modules/
│   │   ├── vpc/                             # VPC, subnets, route tables
│   │   ├── eks/                             # EKS cluster, node groups
│   │   ├── iam/                             # IRSA, policies
│   │   ├── observability/                   # CloudWatch, alarms
│   │   ├── audit/                           # S3 Object Lock, DynamoDB, SQS
│   │   ├── kyverno/                         # Kyverno Helm release
│   │   ├── argocd/                          # ArgoCD Helm release
│   │   ├── ecr/                             # ECR registry
│   │   └── secrets/                         # Secrets management
│   ├── envs/dev/                            # Sandbox environment wiring
│   └── bootstrap/                           # Bootstrap scripts
│
├── manifests/                               # K8s Manifests (ArgoCD managed)
│   ├── namespaces/                          # tenant-a, tenant-b, self-heal-system
│   ├── rbac/                                # RBAC roles/bindings
│   ├── networkpolicies/                     # Inter-tenant block
│   ├── workloads/                           # Sample workloads (Online Boutique)
│   ├── executor/                            # CDO executor deployment
│   ├── ai-engine/                           # AI Engine deployment
│   ├── kyverno/                             # Kyverno policies
│   └── argocd/                              # ArgoCD configs
│
├── new-contract/                            # AI Contracts (signed)
│   ├── telemetry-contract.md
│   ├── ai-api-contract.md
│   └── deployment-contract.md
│
├── CAPSTONE_GUIDE/                          # Templates & references
│   ├── CAPSTONE_EVIDENCE_PACK_FORMAT.md     # File gốc (template)
│   └── TF3_SELFHEAL_LEARNER.md              # Đề tài chi tiết
    ├── templates/                            # Doc templates
    └── EVIDENCE_PACK_CDO02_TF3.md           # FILE NÀY
```

---

## 8. Checklist Submission — CDO-02 Specific

### Progress #1 (EOD T4 W11) — light

- [x] `01_requirements_analysis.md` (draft) — K8s-heavy angle declared
- [x] `02_infra_design.md` (draft + angle declared + multi-tenant approach)
- [x] `08_adrs.md` (≥2 ADRs) — hiện có 7 ADRs

### Evidence Pack #1 (EOD T6 W11) — MAIN 

- [x] `01_requirements_analysis.md` — ready, comprehensive
- [x] `02_infra_design.md` (with multi-tenant approach) — ready
- [x] `03_security_design.md` (draft) — ready
- [x] `04_deployment_design.md` (draft) — ready
- [x] `05_cost_analysis.md` (skeleton) — draft available
- [x] `08_adrs.md` (≥3 ADRs) — 7 ADRs available
- [x] Base infra (VPC + EKS + Observability) chạy được — Terraform modules exist

### Progress #2 (EOD T2 W12) — light

- [ ] AI engine integration started — deploy AI container vào EKS
- [ ] Tenant onboarding flow draft — `tenant-a`, `tenant-b` namespaces + RBAC
- [ ] Docs updated với progress notes

### Evidence Pack #2 (EOD T4 W12) — MAIN + code freeze 18h

- [ ] All 7 docs **final**
- [ ] `05_cost_analysis.md` **measured** — AWS Cost Explorer actual data
- [ ] `07_test_eval_report.md` **new** với:
  - [ ] ≥10 scenario test results
  - [ ] ≥4h simulation window evidence
  - [ ] ≥60% auto-resolve rate
  - [ ] 0 unsafe action
  - [ ] SLO measured values (không còn TBD)
  - [ ] Chaos/curveball response evidence
  - [ ] Failure analysis cho scenarios fail
- [ ] `08_adrs.md` final (≥5 ADRs) — hiện có 7, cần thêm curveball ADRs
- [ ] Platform infra deployed + integrated với AI engine
- [ ] E2E demo evidence: screenshot/log/video
- [ ] `git tag final` trên repo

---

## 9. Anti-patterns — CDO-02 Cần Tránh

| Anti-pattern | Tại sao nguy hiểm | CDO-02 phải làm gì |
|---|---|---|
| Doc viết 1 phát cuối T6/T4 | Git history thấy ngay → trừ điểm nặng | Commit docs đều đặn theo từng milestone |
| Doc < 500 từ (Light/Medium tier) | Thiếu depth, reviewer đánh rớt | Check word count trước submit |
| Doc > word target × 1.5 | Fluff, nên split sub-doc | Tách thành sub-section hoặc appendix |
| Diagram không có caption | Vô nghĩa, reviewer không hiểu | Mọi diagram: caption + 2-3 dòng giải thích |
| ADR chỉ "we chose X" | Không show reasoning | Bắt buộc: Context + Alternatives + Consequences |
| Copy-paste từ nhóm CDO khác cùng TF | Bị detect → 0 điểm | CDO-02 có K8s-heavy angle riêng, viết từ góc nhìn riêng |
| Doc Pack #2 không update sau curveball | Show không adapt → trừ điểm | Thêm ADR mới + update design docs sau mỗi curveball |
| Cost analysis chỉ estimate, không measured | Pack #2 bắt buộc actual data | Chạy AWS Cost Explorer, screenshot billing |
| Eval report chỉ metric, không failure analysis | Thiếu learning → thấp điểm | Mỗi failure: root cause → fix → result |
| Executor không có audit trail | Bằng chứng compliance thiếu | Mọi action có `correlation_id` → S3 Object Lock |

---

## 10. Tips Đạt Điểm Cao — CDO-02 Specific

### Nguyên tắc chung

1. **WHY first, WHAT after** — "Tại sao chọn K8s-heavy thay vì serverless?" quan trọng hơn "EKS cluster config dùng t3.medium"
2. **Numbers > adjectives** — "p99 latency 420ms, auto-resolve rate 70%" beats "hệ thống chạy ổn"
3. **Diagram > prose** — Mermaid sequence diagram rõ hơn 5 đoạn văn mô tả workflow
4. **Honesty about trade-off** — "Chọn K8s-heavy nhưng chấp nhận cost cao hơn serverless-first" beats "K8s-heavy là best"

### CDO-02 cụ thể

5. **Show execution boundary rõ ràng** — AI = decide, CDO = validate + execute + verify + audit. Reviewer cần thấy ownership clear.
6. **Demo safety gate thật** — Không chỉ viết, mà screenshot/log chứng minh cross-tenant deny, blast-radius check, dry-run.
7. **Audit trail traceable** — Show 1 scenario đầy đủ từ alert → detect → decide → safety → execute → verify → audit, query được bằng `correlation_id`.
8. **Curveball adaptation** — Khi nhận curveball W12, thêm ADR mới giải thích design change, update docs tương ứng.
9. **Cross-link giữa docs** — "Xem thêm tại [03_security_design.md](03_security_design.md#5-audit-trail)" cho thấy coherent thinking.
10. **Cập nhật doc theo build** — Mỗi commit code kèm 1 doc update (git history evidence).

### Khi present buổi chấm T5 W12

- Chuẩn bị **E2E demo flow**: inject scenario → watch executor auto-heal → verify success → show audit log
- Chuẩn bị trả lời **"Tại sao?"** cho mọi quyết định lớn (xem ADRs)
- Chuẩn bị **số liệu concrete**: auto-resolve rate, latency, cost actual, SLO pass/fail
- Chuẩn bị **failure story**: scenario nào fail → tại sao → fix thế nào → học được gì

---

## 11. Hướng Dẫn Thu Thập Bằng Chứng Chi Tiết (Evidence Collection Guide)

> 📸 Section này liệt kê **chính xác** cần chụp screenshot gì, chạy command gì, lưu output ở đâu cho từng document và checkpoint. Lưu tất cả evidence vào `docs/assets/evidence/`.

### 11.0 Chuẩn bị thư mục evidence

```bash
# Tạo thư mục lưu bằng chứng
mkdir -p docs/assets/evidence/infra
mkdir -p docs/assets/evidence/security
mkdir -p docs/assets/evidence/deployment
mkdir -p docs/assets/evidence/cost
mkdir -p docs/assets/evidence/test
mkdir -p docs/assets/evidence/audit
mkdir -p docs/assets/evidence/e2e-demo
mkdir -p docs/assets/evidence/git-history
```

### 11.1 Evidence cho `01_requirements_analysis.md`

**Loại bằng chứng cần:** Không cần screenshot nhiều — doc này chủ yếu là viết. Nhưng cần evidence cho differentiation angle.

| Evidence | Cách lấy | Lưu ở đâu |
|---|---|---|
| **Git commit history** cho file này | `git log --oneline -- docs/01_requirements_analysis.md` | Paste output vào doc hoặc lưu screenshot terminal |
| **Differentiation angle lock commit** | `git log --oneline --after="2026-06-22" --before="2026-06-24" -- docs/01_requirements_analysis.md` | Chứng minh angle declared T3 W11 |

```bash
# Chụp git history chứng minh doc không viết 1 phát
git log --pretty=format:"%h %ad %s" --date=short -- docs/01_requirements_analysis.md
# → Lưu output: docs/assets/evidence/git-history/01_req_git_log.txt
```

---

### 11.2 Evidence cho `02_infra_design.md`

**Loại bằng chứng cần:** Architecture diagram + Infra running proof.

| Evidence | Cách lấy | Lưu ở đâu |
|---|---|---|
| **Architecture diagram** | Mermaid inline hoặc export PNG từ draw.io | Đã có: `docs/image-1.png`, `docs/docs_ObservabilityStack/picture/infra-architecture.png` |
| **EKS Cluster running** | Screenshot AWS Console → EKS → Clusters | `docs/assets/evidence/infra/eks-cluster-console.png` |
| **kubectl cluster-info** | Chạy command bên dưới | `docs/assets/evidence/infra/kubectl-cluster-info.txt` |
| **Node group healthy** | Screenshot AWS Console → EKS → Node Groups | `docs/assets/evidence/infra/eks-nodegroup.png` |
| **Namespace list** | `kubectl get ns` | `docs/assets/evidence/infra/namespaces.txt` |
| **VPC topology** | Screenshot AWS Console → VPC → Your VPCs | `docs/assets/evidence/infra/vpc-console.png` |
| **Subnets** | Screenshot AWS Console → VPC → Subnets (filter by VPC) | `docs/assets/evidence/infra/subnets-console.png` |

```bash
# 1. EKS Cluster info
kubectl cluster-info > docs/assets/evidence/infra/kubectl-cluster-info.txt 2>&1

# 2. Namespace list — chứng minh tenant-a, tenant-b, self-heal-system tồn tại
kubectl get ns -o wide > docs/assets/evidence/infra/namespaces.txt

# 3. Node status
kubectl get nodes -o wide > docs/assets/evidence/infra/nodes.txt

# 4. Tất cả pods đang chạy
kubectl get pods --all-namespaces -o wide > docs/assets/evidence/infra/all-pods.txt

# 5. Terraform state list — chứng minh infra modules deployed
cd infra/envs/dev && terraform state list > ../../../docs/assets/evidence/infra/terraform-state-list.txt

# 6. Terraform plan (no changes = stable)
cd infra/envs/dev && terraform plan -no-color > ../../../docs/assets/evidence/infra/terraform-plan-output.txt 2>&1
```

**Screenshot AWS Console cần chụp:**
1. **EKS Console**: Mở `https://console.aws.amazon.com/eks/` → chọn cluster → chụp tab "Overview" (thấy status Active, K8s version, endpoint)
2. **EKS Node Groups**: Tab "Compute" → Node Groups → chụp thấy desired/min/max và status
3. **VPC Console**: `https://console.aws.amazon.com/vpc/` → chọn VPC → chụp CIDR, subnets, route tables
4. **Subnets**: Filter theo VPC → chụp thấy public/private subnets, AZ distribution

---

### 11.3 Evidence cho `03_security_design.md`

**Loại bằng chứng cần:** RBAC proof, NetworkPolicy proof, tenant isolation proof.

| Evidence | Cách lấy | Lưu ở đâu |
|---|---|---|
| **RBAC Roles** | `kubectl get roles -n tenant-a` | `docs/assets/evidence/security/rbac-roles-tenant-a.txt` |
| **RBAC RoleBindings** | `kubectl get rolebindings -n tenant-a` | `docs/assets/evidence/security/rbac-bindings-tenant-a.txt` |
| **NetworkPolicies** | `kubectl get networkpolicies --all-namespaces` | `docs/assets/evidence/security/networkpolicies.txt` |
| **Kyverno Policies** | `kubectl get clusterpolicies` | `docs/assets/evidence/security/kyverno-policies.txt` |
| **Cross-tenant deny test** | Chạy TC-07 scenario, capture log | `docs/assets/evidence/security/cross-tenant-deny-log.txt` |
| **IAM Roles (IRSA)** | Screenshot AWS Console → IAM → Roles | `docs/assets/evidence/security/iam-irsa-roles.png` |
| **S3 Object Lock config** | Screenshot S3 Console → bucket → Properties | `docs/assets/evidence/security/s3-object-lock.png` |

```bash
# 1. RBAC — list roles và role bindings
kubectl get roles -n tenant-a -o yaml > docs/assets/evidence/security/rbac-roles-tenant-a.yaml
kubectl get roles -n tenant-b -o yaml > docs/assets/evidence/security/rbac-roles-tenant-b.yaml
kubectl get rolebindings -n tenant-a -o yaml > docs/assets/evidence/security/rbac-bindings-tenant-a.yaml
kubectl get rolebindings -n tenant-b -o yaml > docs/assets/evidence/security/rbac-bindings-tenant-b.yaml

# 2. ClusterRoles cho executor
kubectl get clusterroles | grep -i "executor\|self-heal\|platform" > docs/assets/evidence/security/clusterroles.txt

# 3. NetworkPolicies
kubectl get networkpolicies --all-namespaces -o yaml > docs/assets/evidence/security/networkpolicies-full.yaml

# 4. Kyverno policies
kubectl get clusterpolicies -o wide > docs/assets/evidence/security/kyverno-clusterpolicies.txt
kubectl get clusterpolicies -o yaml > docs/assets/evidence/security/kyverno-clusterpolicies-full.yaml

# 5. ServiceAccount của executor
kubectl get sa -n self-heal-system -o yaml > docs/assets/evidence/security/executor-sa.yaml

# 6. Test cross-tenant deny (chạy executor với wrong namespace)
# → Output từ scenario TC-07, xem section 11.7

# 7. Kyverno deny test — thử scale vượt limit
kubectl apply --dry-run=server -f - <<EOF > docs/assets/evidence/security/kyverno-deny-test.txt 2>&1
apiVersion: apps/v1
kind: Deployment
metadata:
  name: test-overlimit
  namespace: tenant-a
spec:
  replicas: 15
  selector:
    matchLabels:
      app: test
  template:
    metadata:
      labels:
        app: test
    spec:
      containers:
      - name: test
        image: nginx
        resources:
          limits:
            memory: "8Gi"
EOF
```

**Screenshot AWS Console cần chụp:**
1. **IAM → Roles**: Tìm role IRSA executor → chụp tab "Permissions" (thấy policies attached)
2. **IAM → Roles**: Tìm role IRSA AI Engine → chụp tab "Permissions"
3. **S3 → Audit bucket → Properties**: Scroll xuống "Object Lock" → chụp thấy Governance mode enabled
4. **S3 → Audit bucket → Properties**: Chụp "Default retention" setting (≥ 90 days)

---

### 11.4 Evidence cho `04_deployment_design.md`

**Loại bằng chứng cần:** Terraform modules, ArgoCD running, deployment status.

| Evidence | Cách lấy | Lưu ở đâu |
|---|---|---|
| **Terraform modules structure** | `tree infra/modules/` hoặc `dir /s` | `docs/assets/evidence/deployment/terraform-tree.txt` |
| **Terraform apply output** | `terraform apply` log | `docs/assets/evidence/deployment/terraform-apply.txt` |
| **ArgoCD UI** | Screenshot ArgoCD dashboard | `docs/assets/evidence/deployment/argocd-dashboard.png` |
| **ArgoCD applications** | `kubectl get applications -n argocd` | `docs/assets/evidence/deployment/argocd-apps.txt` |
| **Executor deployment status** | `kubectl get deploy -n self-heal-system` | `docs/assets/evidence/deployment/executor-deployment.txt` |
| **AI Engine deployment** | `kubectl get deploy -n self-heal-system` | `docs/assets/evidence/deployment/ai-engine-deployment.txt` |
| **GitHub Actions CI** | Screenshot GitHub → Actions tab | `docs/assets/evidence/deployment/github-actions.png` |

```bash
# 1. Terraform module structure
# Windows:
Get-ChildItem -Recurse infra/modules -Name > docs/assets/evidence/deployment/terraform-tree.txt
# Linux/Mac:
# tree infra/modules/ > docs/assets/evidence/deployment/terraform-tree.txt

# 2. ArgoCD applications
kubectl get applications -n argocd -o wide > docs/assets/evidence/deployment/argocd-apps.txt 2>&1

# 3. ArgoCD application details (sync status)
kubectl get applications -n argocd -o yaml > docs/assets/evidence/deployment/argocd-apps-detail.yaml 2>&1

# 4. Executor deployment
kubectl get deploy,rs,pods -n self-heal-system -o wide > docs/assets/evidence/deployment/executor-status.txt

# 5. AI Engine deployment
kubectl get deploy,rs,pods -n self-heal-system -o wide > docs/assets/evidence/deployment/ai-engine-status.txt 2>&1

# 6. All deployments across namespaces
kubectl get deploy --all-namespaces -o wide > docs/assets/evidence/deployment/all-deployments.txt

# 7. Helm releases (ArgoCD, Kyverno)
helm list --all-namespaces > docs/assets/evidence/deployment/helm-releases.txt 2>&1
```

**Screenshot cần chụp:**
1. **ArgoCD Dashboard**: Mở ArgoCD UI → chụp trang chính thấy tất cả applications + sync status (Synced/Healthy)
2. **ArgoCD Application Detail**: Click vào từng app → chụp resource tree (thấy namespace, deployments, pods)
3. **GitHub Actions**: Mở repo → Actions tab → chụp workflow runs (thấy pipeline pass/fail)
4. Nếu có **CI pipeline chạy**: Chụp chi tiết 1 successful run (build → test → scan → deploy)

---

### 11.5 Evidence cho `05_cost_analysis.md` (CRITICAL — W12)

**Loại bằng chứng cần:** AWS Cost Explorer actual data — **KHÔNG được chỉ estimate, phải có measured actual.**

| Evidence | Cách lấy | Lưu ở đâu |
|---|---|---|
| **AWS Cost Explorer — by service** | Screenshot AWS Console | `docs/assets/evidence/cost/cost-explorer-by-service.png` |
| **AWS Cost Explorer — daily trend** | Screenshot AWS Console | `docs/assets/evidence/cost/cost-explorer-daily.png` |
| **AWS Billing Dashboard** | Screenshot AWS Console | `docs/assets/evidence/cost/billing-dashboard.png` |
| **Cost by service CSV export** | Export từ Cost Explorer | `docs/assets/evidence/cost/cost-by-service.csv` |
| **EC2 running instances** | Screenshot EC2 Console | `docs/assets/evidence/cost/ec2-instances.png` |

**Hướng dẫn chụp AWS Cost Explorer step-by-step:**

1. **Mở AWS Cost Explorer:**
   - Login AWS Console → search "Cost Explorer" → Open
   - Hoặc trực tiếp: `https://us-east-1.console.aws.amazon.com/cost-management/home#/cost-explorer`

2. **Chụp Chi phí theo Service (quan trọng nhất):**
   - Date range: Chọn từ ngày bắt đầu sandbox → ngày hiện tại
   - Group by: **Service**
   - Granularity: **Daily**
   - → Chụp screenshot biểu đồ + bảng chi tiết bên dưới
   - → Lưu: `docs/assets/evidence/cost/cost-explorer-by-service.png`

3. **Chụp Chi phí theo Usage Type:**
   - Group by: **Usage Type**
   - → Chụp screenshot — thấy chi tiết EKS, EC2, NAT, S3, DynamoDB
   - → Lưu: `docs/assets/evidence/cost/cost-explorer-by-usage.png`

4. **Export CSV:**
   - Trong Cost Explorer → Click "Download CSV"
   - → Lưu: `docs/assets/evidence/cost/cost-export.csv`

5. **Chụp Billing Dashboard:**
   - AWS Console → Billing → Dashboard
   - → Chụp "Month-to-date costs by service"
   - → Lưu: `docs/assets/evidence/cost/billing-dashboard.png`

6. **Chụp EC2 instances đang chạy:**
   - EC2 Console → Instances → filter Running
   - → Chụp thấy instance type (t3.medium), state, AZ
   - → Lưu: `docs/assets/evidence/cost/ec2-instances.png`

```bash
# AWS CLI lấy cost data (alternative nếu có CLI configured)
aws ce get-cost-and-usage \
  --time-period Start=2026-06-23,End=2026-07-04 \
  --granularity DAILY \
  --metrics "UnblendedCost" \
  --group-by Type=DIMENSION,Key=SERVICE \
  --output json > docs/assets/evidence/cost/cost-by-service.json

# Lấy current month cost
aws ce get-cost-and-usage \
  --time-period Start=2026-06-01,End=2026-06-30 \
  --granularity MONTHLY \
  --metrics "UnblendedCost" \
  --group-by Type=DIMENSION,Key=SERVICE \
  --output table > docs/assets/evidence/cost/monthly-cost-summary.txt
```

---

### 11.6 Evidence cho `07_test_eval_report.md` (CRITICAL — W12)

**Loại bằng chứng cần:** Scenario test results, SLO measurements, chaos response, security tests.

#### 11.6.1 Scenario Test Evidence (≥10 scenarios, ≥4h window)

| Evidence | Cách lấy | Lưu ở đâu |
|---|---|---|
| **Scenario runner output** | `python run_scenarios.py` | `docs/assets/evidence/test/scenario-run-output.txt` |
| **Scenario summary table** | Parse runner output | Paste vào `07_test_eval_report.md` |
| **Start/End timestamps** | Từ log/audit records | Chứng minh ≥4h window |
| **Auto-resolve rate** | Count pass/total | Paste vào doc, target ≥60% |

```bash
# 1. Chạy scenario test và capture output
cd executor
python run_scenarios.py 2>&1 | tee ../docs/assets/evidence/test/scenario-run-output.txt

# 2. Chạy unit tests
cd executor
python -m pytest tests/ -v --tb=short 2>&1 | tee ../docs/assets/evidence/test/pytest-output.txt

# 3. Test coverage
cd executor
python -m pytest tests/ --cov=. --cov-report=term-missing 2>&1 | tee ../docs/assets/evidence/test/coverage-report.txt

# 4. Ghi lại start/end time
echo "Test Start: $(date -u +%Y-%m-%dT%H:%M:%SZ)" > docs/assets/evidence/test/test-window.txt
# ... chạy test ...
echo "Test End: $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> docs/assets/evidence/test/test-window.txt
```

#### 11.6.2 Từng Test Case — Evidence cụ thể

**TC-01: Service stuck / latency spike (tenant-a)**
```bash
# Inject scenario: service stuck
# 1. Khiến pod unhealthy (kill process hoặc inject high latency)
kubectl exec -n tenant-a deploy/<target-deploy> -- kill 1
# hoặc dùng scenario injector:
python run_scenarios.py --scenario service-stuck --tenant tenant-a 2>&1 | tee docs/assets/evidence/test/tc01-output.txt

# 2. Chờ executor detect + auto-heal
# 3. Capture pod events sau khi heal
kubectl get events -n tenant-a --sort-by='.lastTimestamp' | tail -20 > docs/assets/evidence/test/tc01-events.txt

# 4. Capture executor log cho scenario này
kubectl logs -n self-heal-system deploy/self-heal-executor --tail=100 | grep -A20 "TC-01\|service_stuck\|RESTART_DEPLOYMENT" > docs/assets/evidence/test/tc01-executor-log.txt

# 5. Verify pod đã restart thành công
kubectl get pods -n tenant-a -o wide > docs/assets/evidence/test/tc01-pods-after.txt
```

**TC-03: OOM / Memory pressure (tenant-b)**
```bash
# 1. Inject OOM scenario
# Dùng stress tool hoặc scenario injector
python run_scenarios.py --scenario oom --tenant tenant-b 2>&1 | tee docs/assets/evidence/test/tc03-output.txt

# 2. Capture OOM events
kubectl get events -n tenant-b --field-selector reason=OOMKilled > docs/assets/evidence/test/tc03-oom-events.txt

# 3. Capture executor response
kubectl logs -n self-heal-system deploy/self-heal-executor --tail=100 | grep -A20 "OOM\|PATCH_MEMORY_LIMIT" > docs/assets/evidence/test/tc03-executor-log.txt
```

**TC-07: Cross-tenant deny (CRITICAL — chứng minh tenant isolation)**
```bash
# 1. Chạy scenario: executor nhận action plan cho tenant-a nhưng incident thuộc tenant-b
python run_scenarios.py --scenario cross-tenant --tenant tenant-b 2>&1 | tee docs/assets/evidence/test/tc07-output.txt

# 2. PHẢI thấy DENIED trong log
kubectl logs -n self-heal-system deploy/self-heal-executor --tail=50 | grep -i "denied\|cross_tenant\|safety" > docs/assets/evidence/test/tc07-deny-log.txt

# 3. Audit record phải ghi denied_cross_tenant
# Query audit từ S3 hoặc CloudWatch
```

**TC-08: AI timeout/503**
```bash
# 1. Simulate AI down hoặc timeout
# Tắt AI endpoint hoặc inject delay
python run_scenarios.py --scenario ai-timeout --tenant tenant-a 2>&1 | tee docs/assets/evidence/test/tc08-output.txt

# 2. Verify: KHÔNG có execute, phải escalate
kubectl logs -n self-heal-system deploy/self-heal-executor --tail=50 | grep -i "timeout\|escalate\|no_execute" > docs/assets/evidence/test/tc08-log.txt
```

#### 11.6.3 SLO Measurement Evidence

```bash
# 1. Executor availability — pod uptime trong test window
kubectl get pods -n self-heal-system -o wide > docs/assets/evidence/test/slo-executor-uptime.txt
# Check restarts count (0 restart = high availability)

# 2. AI endpoint latency — từ executor logs
kubectl logs -n self-heal-system deploy/self-heal-executor | grep "latency\|duration\|elapsed" > docs/assets/evidence/test/slo-ai-latency.txt

# 3. CloudWatch metrics (nếu có)
# Screenshot CloudWatch → Metrics → Custom Metrics → filter executor
# → Lưu: docs/assets/evidence/test/slo-cloudwatch-metrics.png
```

**Screenshot cần chụp cho SLO:**
1. **CloudWatch Metrics**: Graph showing executor request latency over test window
2. **CloudWatch Logs Insights**: Query kết quả cho detect/decide/verify latency
3. **Executor Pod status**: `kubectl get pods -n self-heal-system` — thấy 0 restarts, Running

**CloudWatch Logs Insights query (copy paste vào console):**
```
# Query latency cho AI calls
fields @timestamp, @message
| filter @message like /latency|duration|elapsed/
| sort @timestamp desc
| limit 50
```
→ Chụp screenshot kết quả → `docs/assets/evidence/test/slo-cwl-query.png`

#### 11.6.4 Chaos/Curveball Evidence (W12)

```bash
# Khi nhận curveball từ reviewer:
# 1. Ghi lại curveball description
echo "Curveball #1 received: <mô tả>" > docs/assets/evidence/test/curveball-1.txt

# 2. Ghi lại response/adaptation
echo "Response: <những gì đã thay đổi>" >> docs/assets/evidence/test/curveball-1.txt

# 3. Chạy lại test scenario liên quan
python run_scenarios.py --scenario <curveball-related> 2>&1 | tee -a docs/assets/evidence/test/curveball-1.txt

# 4. Thêm ADR mới giải thích design change
# → Append vào docs/08_adrs.md

# 5. Screenshot diff showing adaptation
git diff docs/ > docs/assets/evidence/test/curveball-1-diff.txt
```

#### 11.6.5 Load Test Evidence

```bash
# 1. Chạy load test bằng k6 hoặc Locust hoặc replay runner
# k6 example:
k6 run --out json=docs/assets/evidence/test/k6-results.json load-test.js 2>&1 | tee docs/assets/evidence/test/load-test-output.txt

# Hoặc chạy scenario replay nhanh liên tục:
for i in $(seq 1 20); do
  python run_scenarios.py --scenario all --tenant tenant-a &
done
wait

# 2. Capture resource usage during load
kubectl top pods -n self-heal-system > docs/assets/evidence/test/load-resource-usage.txt 2>&1
kubectl top nodes > docs/assets/evidence/test/load-node-usage.txt 2>&1

# 3. Check SQS queue depth (nếu có)
aws sqs get-queue-attributes \
  --queue-url <your-sqs-url> \
  --attribute-names ApproximateNumberOfMessages \
  --output json > docs/assets/evidence/test/sqs-queue-depth.json
```

#### 11.6.6 Security Test Evidence

```bash
# 1. RBAC abuse test — executor cố access namespace không được phép
kubectl auth can-i --as=system:serviceaccount:platform:self-heal-executor list pods -n kube-system > docs/assets/evidence/security/rbac-abuse-kube-system.txt 2>&1
# Expected: "no"

kubectl auth can-i --as=system:serviceaccount:platform:self-heal-executor delete namespace -n tenant-a > docs/assets/evidence/security/rbac-abuse-delete-ns.txt 2>&1
# Expected: "no"

kubectl auth can-i --as=system:serviceaccount:platform:self-heal-executor get pods -n tenant-a > docs/assets/evidence/security/rbac-can-get-pods.txt 2>&1
# Expected: "yes" (cần quyền này)

# 2. NetworkPolicy test — test connectivity bị chặn
# Tạo pod test trong tenant-a, cố curl tenant-b service
kubectl run netpol-test -n tenant-a --rm -it --image=curlimages/curl -- curl -s --max-time 5 http://<tenant-b-service>.<tenant-b>.svc.cluster.local 2>&1 | tee docs/assets/evidence/security/netpol-cross-tenant-test.txt
# Expected: timeout / connection refused

# 3. Secret exposure check — tìm secret trong logs
kubectl logs -n self-heal-system deploy/self-heal-executor | grep -i "password\|secret\|token\|key" > docs/assets/evidence/security/secret-leak-check.txt 2>&1
# Expected: empty hoặc chỉ có field names, không có values
```

---

### 11.7 Evidence cho `08_adrs.md`

**Loại bằng chứng cần:** Git history chứng minh ADR được thêm dần, không viết 1 cục.

```bash
# 1. Git log cho ADR file
git log --pretty=format:"%h %ad %s" --date=short -- docs/08_adrs.md > docs/assets/evidence/git-history/adr_git_log.txt

# 2. Đếm số ADR
grep -c "^## ADR-" docs/08_adrs.md
# Expected: ≥5 cho Pack #2

# 3. Word count check
wc -w docs/08_adrs.md
# Expected: 800-1500 từ (Light tier)
```

---

### 11.8 Evidence cho Audit Trail (cross-cutting)

**Audit trail là bằng chứng quan trọng nhất** — chứng minh toàn bộ flow traceable bằng `correlation_id`.

| Evidence | Cách lấy | Lưu ở đâu |
|---|---|---|
| **S3 audit objects** | List objects trong audit bucket | `docs/assets/evidence/audit/s3-audit-list.txt` |
| **1 audit record sample** | Download 1 JSON từ S3 | `docs/assets/evidence/audit/sample-audit-record.json` |
| **Audit trace by correlation_id** | Query CloudWatch hoặc S3 | `docs/assets/evidence/audit/trace-by-correlation-id.txt` |
| **S3 Object Lock proof** | Screenshot S3 Console | `docs/assets/evidence/audit/s3-object-lock-proof.png` |
| **DynamoDB idempotency records** | Screenshot DynamoDB Console | `docs/assets/evidence/audit/dynamodb-idempotency.png` |

```bash
# 1. List audit objects trong S3
aws s3 ls s3://<audit-bucket-name>/ --recursive | head -30 > docs/assets/evidence/audit/s3-audit-list.txt

# 2. Download 1 audit record mẫu
aws s3 cp s3://<audit-bucket-name>/<path-to-record>.json docs/assets/evidence/audit/sample-audit-record.json

# 3. Xem nội dung audit record (pretty print)
cat docs/assets/evidence/audit/sample-audit-record.json | python -m json.tool

# 4. Query toàn bộ events của 1 correlation_id trong CloudWatch Logs
# → Mở CloudWatch Console → Logs Insights → chọn log group → chạy query:
# fields @timestamp, @message
# | filter @message like /<correlation_id_value>/
# | sort @timestamp asc
# → Chụp screenshot kết quả → docs/assets/evidence/audit/cwl-correlation-trace.png

# 5. DynamoDB scan — thấy idempotency records
aws dynamodb scan \
  --table-name <idempotency-table-name> \
  --limit 5 \
  --output json > docs/assets/evidence/audit/dynamodb-records.json

# 6. S3 Object Lock verification
aws s3api get-object-lock-configuration \
  --bucket <audit-bucket-name> \
  --output json > docs/assets/evidence/audit/s3-object-lock-config.json

# 7. S3 object retention check (pick 1 object)
aws s3api get-object-retention \
  --bucket <audit-bucket-name> \
  --key <path-to-audit-object> \
  --output json > docs/assets/evidence/audit/s3-object-retention.json
```

**Screenshot cần chụp:**
1. **S3 Console → Audit bucket**: Mở bucket → chụp danh sách objects (thấy audit records)
2. **S3 → Object detail**: Click 1 object → chụp "Object Lock" section (thấy Governance mode + retention date)
3. **DynamoDB Console**: Mở table idempotency → chụp "Items" tab (thấy records)
4. **CloudWatch Logs Insights**: Chạy query correlation_id → chụp kết quả trace

---

### 11.9 Evidence cho E2E Demo (buổi chấm T5 W12)

**Đây là bằng chứng quan trọng nhất cho buổi present.** Chuẩn bị 1 E2E flow đầy đủ.

#### Kịch bản demo đề xuất

```
1. Show cluster healthy (kubectl get pods --all-namespaces)
2. Inject scenario: Service stuck in tenant-a
3. Watch executor detect anomaly (tail executor log)
4. Watch executor call AI /v1/detect → /v1/decide
5. Watch safety gate validate action
6. Watch executor perform dry-run → execute restart
7. Watch AI /v1/verify confirm fix
8. Query audit record bằng correlation_id
9. Show zero cross-tenant impact
```

```bash
# 1. Terminal 1: Watch executor logs (live)
kubectl logs -n self-heal-system deploy/self-heal-executor -f

# 2. Terminal 2: Watch tenant-a pods (live)
kubectl get pods -n tenant-a -w

# 3. Terminal 3: Inject scenario
python executor/run_scenarios.py --scenario service-stuck --tenant tenant-a

# 4. Chờ auto-heal xong → Capture final state
kubectl get pods -n tenant-a -o wide > docs/assets/evidence/e2e-demo/final-pods.txt
kubectl get events -n tenant-a --sort-by='.lastTimestamp' | tail -20 > docs/assets/evidence/e2e-demo/final-events.txt

# 5. Query audit
aws s3 ls s3://<audit-bucket>/ --recursive | tail -5 > docs/assets/evidence/e2e-demo/latest-audit-objects.txt
```

**Ghi màn hình (screen recording):**
- Dùng **OBS Studio** hoặc **Windows Game Bar** (`Win + G`) để ghi lại toàn bộ E2E demo
- Lưu video: `docs/assets/evidence/e2e-demo/e2e-demo-recording.mp4`
- Ghi ít nhất 1 scenario happy path + 1 scenario deny (cross-tenant)

**Screenshot cần chụp cho E2E:**
1. **Before inject**: `kubectl get pods -n tenant-a` (pods healthy)
2. **During inject**: executor log showing detect → decide → safety check
3. **After heal**: `kubectl get pods -n tenant-a` (pod restarted, new AGE)
4. **Audit record**: S3 object hoặc CloudWatch log showing full trace

---

### 11.10 Evidence cho Git History (chứng minh process)

**Git history là bằng chứng process thinking** — reviewer sẽ check commit timeline.

```bash
# 1. Git log tổng quan (30 commits gần nhất)
git log --oneline -30 > docs/assets/evidence/git-history/recent-commits.txt

# 2. Git log cho docs/ folder — chứng minh docs được commit dần
git log --pretty=format:"%h %ad %an: %s" --date=short -- docs/ > docs/assets/evidence/git-history/docs-commit-history.txt

# 3. Git shortlog — thấy ai commit gì, bao nhiêu lần
git shortlog -s -n > docs/assets/evidence/git-history/contributor-summary.txt

# 4. Git log cho mỗi file doc — chứng minh không viết 1 cục
for f in docs/01_requirements_analysis.md docs/02_infra_design.md docs/03_security_design.md docs/04_deployment_design.md docs/05_cost_analysis.md docs/08_adrs.md; do
  echo "=== $f ===" >> docs/assets/evidence/git-history/per-file-history.txt
  git log --oneline -- $f >> docs/assets/evidence/git-history/per-file-history.txt
  echo "" >> docs/assets/evidence/git-history/per-file-history.txt
done

# 5. Git tag final (Pack #2 — code freeze)
git tag final
git push origin final
```

---

### 11.11 Evidence cho Word Count (tránh bị reject)

```bash
# Đếm word count tất cả docs — kiểm tra trước submit
for f in docs/01_requirements_analysis.md docs/02_infra_design.md docs/03_security_design.md docs/04_deployment_design.md docs/05_cost_analysis.md docs/07_test_eval_report_v2.0.md docs/08_adrs.md; do
  words=$(wc -w < "$f")
  echo "$f: $words words"
done > docs/assets/evidence/git-history/word-count-all-docs.txt

# Kiểm tra nhanh:
# Light tier (01, 05, 08): 800-1500 từ, tối đa 2250
# Medium tier (02, 03, 04, 07): 1000-2500 từ, tối đa 3750
# FAIL nếu < 500 từ cho bất kỳ doc nào
```

---

### 11.12 Script tổng hợp: Thu thập toàn bộ evidence một lần

```bash
#!/bin/bash
# File: collect_evidence.sh
# Chạy script này để thu thập tất cả evidence tự động

echo "=== CDO-02 Evidence Collection Script ==="
echo "Start: $(date -u)"

# Create directories
mkdir -p docs/assets/evidence/{infra,security,deployment,cost,test,audit,e2e-demo,git-history}

echo "[1/8] Collecting INFRA evidence..."
kubectl cluster-info > docs/assets/evidence/infra/kubectl-cluster-info.txt 2>&1
kubectl get ns -o wide > docs/assets/evidence/infra/namespaces.txt 2>&1
kubectl get nodes -o wide > docs/assets/evidence/infra/nodes.txt 2>&1
kubectl get pods --all-namespaces -o wide > docs/assets/evidence/infra/all-pods.txt 2>&1

echo "[2/8] Collecting SECURITY evidence..."
kubectl get roles -n tenant-a -o yaml > docs/assets/evidence/security/rbac-roles-tenant-a.yaml 2>&1
kubectl get roles -n tenant-b -o yaml > docs/assets/evidence/security/rbac-roles-tenant-b.yaml 2>&1
kubectl get rolebindings -n tenant-a -o yaml > docs/assets/evidence/security/rbac-bindings-tenant-a.yaml 2>&1
kubectl get rolebindings -n tenant-b -o yaml > docs/assets/evidence/security/rbac-bindings-tenant-b.yaml 2>&1
kubectl get networkpolicies --all-namespaces -o yaml > docs/assets/evidence/security/networkpolicies-full.yaml 2>&1
kubectl get clusterpolicies -o wide > docs/assets/evidence/security/kyverno-clusterpolicies.txt 2>&1
kubectl get sa -n self-heal-system -o yaml > docs/assets/evidence/security/executor-sa.yaml 2>&1

echo "[3/8] Collecting DEPLOYMENT evidence..."
kubectl get applications -n argocd -o wide > docs/assets/evidence/deployment/argocd-apps.txt 2>&1
kubectl get deploy,rs,pods -n self-heal-system -o wide > docs/assets/evidence/deployment/executor-status.txt 2>&1
kubectl get deploy --all-namespaces -o wide > docs/assets/evidence/deployment/all-deployments.txt 2>&1
helm list --all-namespaces > docs/assets/evidence/deployment/helm-releases.txt 2>&1

echo "[4/8] Collecting AUDIT evidence..."
# Uncomment and fill bucket name:
# aws s3 ls s3://<audit-bucket>/ --recursive | head -30 > docs/assets/evidence/audit/s3-audit-list.txt

echo "[5/8] Collecting GIT HISTORY evidence..."
git log --oneline -30 > docs/assets/evidence/git-history/recent-commits.txt
git log --pretty=format:"%h %ad %an: %s" --date=short -- docs/ > docs/assets/evidence/git-history/docs-commit-history.txt
git shortlog -s -n > docs/assets/evidence/git-history/contributor-summary.txt

echo "[6/8] Collecting WORD COUNT..."
for f in docs/01_requirements_analysis.md docs/02_infra_design.md docs/03_security_design.md docs/04_deployment_design.md docs/05_cost_analysis.md docs/08_adrs.md; do
  words=$(wc -w < "$f" 2>/dev/null || echo "FILE NOT FOUND")
  echo "$f: $words words"
done > docs/assets/evidence/git-history/word-count-all-docs.txt

echo "[7/8] Collecting RBAC ABUSE tests..."
kubectl auth can-i --as=system:serviceaccount:platform:self-heal-executor list pods -n kube-system > docs/assets/evidence/security/rbac-abuse-kube-system.txt 2>&1
kubectl auth can-i --as=system:serviceaccount:platform:self-heal-executor delete namespace -n tenant-a > docs/assets/evidence/security/rbac-abuse-delete-ns.txt 2>&1

echo "[8/8] Running UNIT TESTS..."
cd executor && python -m pytest tests/ -v --tb=short > ../docs/assets/evidence/test/pytest-output.txt 2>&1
cd ..

echo ""
echo "=== Evidence collection complete ==="
echo "End: $(date -u)"
echo "Review files in: docs/assets/evidence/"
echo ""
echo "MANUAL STEPS STILL NEEDED:"
echo "  1. Screenshot AWS Console: EKS, VPC, IAM, S3 Object Lock"
echo "  2. Screenshot AWS Cost Explorer (section 11.5)"
echo "  3. Screenshot ArgoCD Dashboard"
echo "  4. Screenshot CloudWatch Logs Insights queries"
echo "  5. Screen record E2E demo flow"
echo "  6. Run full scenario test (run_scenarios.py) and capture output"
```

---

### 11.13 Checklist Screenshot Tổng Hợp

Danh sách tất cả screenshot cần chụp, sắp theo ưu tiên:

| # | Screenshot | Ở đâu | Dùng cho doc | Priority |
|---|---|---|---|---|
| 1 | AWS Cost Explorer — by service | Cost Explorer Console | `05_cost_analysis.md` | 🔴 MUST |
| 2 | AWS Cost Explorer — daily trend | Cost Explorer Console | `05_cost_analysis.md` | 🔴 MUST |
| 3 | AWS Billing Dashboard | Billing Console | `05_cost_analysis.md` | 🔴 MUST |
| 4 | EKS Cluster Overview | EKS Console | `02_infra_design.md` | 🔴 MUST |
| 5 | EKS Node Groups | EKS Console → Compute | `02_infra_design.md` | 🟡 HIGH |
| 6 | S3 Audit Bucket — Object Lock | S3 Console → Properties | `03_security_design.md` | 🔴 MUST |
| 7 | ArgoCD Dashboard — all apps | ArgoCD UI | `04_deployment_design.md` | 🟡 HIGH |
| 8 | ArgoCD App Detail — resource tree | ArgoCD UI → click app | `04_deployment_design.md` | 🟡 HIGH |
| 9 | IAM IRSA Roles — Permissions | IAM Console → Roles | `03_security_design.md` | 🟡 HIGH |
| 10 | CloudWatch Logs — correlation trace | CloudWatch Logs Insights | `07_test_eval_report.md` | 🔴 MUST |
| 11 | CloudWatch Metrics — executor latency | CloudWatch Metrics | `07_test_eval_report.md` | 🟡 HIGH |
| 12 | VPC Topology | VPC Console | `02_infra_design.md` | 🟢 NICE |
| 13 | DynamoDB — Idempotency items | DynamoDB Console | `03_security_design.md` | 🟢 NICE |
| 14 | EC2 Running Instances | EC2 Console | `05_cost_analysis.md` | 🟢 NICE |
| 15 | GitHub Actions — CI pipeline | GitHub → Actions | `04_deployment_design.md` | 🟢 NICE |
| 16 | E2E Demo — before/during/after | Terminal screenshots | Buổi chấm | 🔴 MUST |
| 17 | E2E Demo — screen recording (video) | OBS/Game Bar | Buổi chấm | 🟡 HIGH |

> **Tip**: Chụp screenshot với timestamp visible (đồng hồ hệ thống) để chứng minh timeline. Trên Windows dùng `Win + Shift + S` (Snipping Tool).

---

## Appendix: Quick Reference Links

| Resource | Path |
|---|---|
| Template gốc | `CAPSTONE_GUIDE/CAPSTONE_EVIDENCE_PACK_FORMAT.md` |
| Đề tài chi tiết | `CAPSTONE_GUIDE/TF3_SELFHEAL_LEARNER.md` |
| CDO Templates | `capstone-phase2/templates/cdo/docs/` |
| AI Contracts | `new-contract/` |
| Executor Code | `executor/` |
| Terraform IaC | `infra/` |
| K8s Manifests | `k8s/` |
| Existing Docs | `docs/` |
| W12 Tasks | `W12_TASKS.md` |

---

> Note **File này là bản customize cho CDO-02 TF3**. Khi chỉnh sửa docs, luôn đối chiếu với template gốc tại `CAPSTONE_GUIDE/CAPSTONE_EVIDENCE_PACK_FORMAT.md` để đảm bảo không thiếu section nào.
