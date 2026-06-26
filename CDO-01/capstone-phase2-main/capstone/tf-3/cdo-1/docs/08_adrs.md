# Architecture Decision Records - CDO 1 · Task force 3 (Self-Heal Engine)

<!-- Doc owner: CDO Team TF3
     Status: Ongoing log W11-W12
     Format: 1 ADR per major decision. Append-only - không xóa ADR cũ.
     Target: >= 3 ADR cho Pack #1 (W11) · >= 5 ADR cho Pack #2 (W12)
     Tier: Light -->

---

## ADR-001 - Chọn EKS + Karpenter làm nền tảng compute cho Sandbox

* **Status**: Accepted

* **Date**: 2026-06-22

* **Context**:

Self-Heal Engine cần vận hành trên môi trường Kubernetes để thực hiện các hành động như restart deployment, scale worker, verify trạng thái workload và tích hợp GitOps thông qua ArgoCD. Ngoài ra hệ thống còn cần chạy ADOT Collector, Argo Workflows và các thành phần observability trong cùng một cluster. Nhóm đánh giá giữa Lambda, ECS Fargate và EKS. Đây là quyết định có chi phí thay đổi cao vì việc đổi compute platform sau này sẽ ảnh hưởng đến toàn bộ deployment topology, RBAC và workflow orchestration.

* **Decision**:

Chọn EKS làm nền tảng compute chính và sử dụng Karpenter để tự động provision node khi workload tăng. Toàn bộ thành phần của Self-Heal Engine sẽ chạy trực tiếp trong cluster thay vì tách sang các dịch vụ serverless riêng lẻ.

* **Consequence**:

  * ✅ Hỗ trợ đầy đủ Kubernetes-native tooling như ArgoCD, Argo Workflows và ADOT Collector.
  * ✅ Scale linh hoạt theo workload thay vì phải duy trì số lượng node cố định.
  * ⚠️ Phải quản lý cluster và node lifecycle.
  * ⚠️ Chi phí cao hơn mô hình hoàn toàn serverless khi cluster chạy liên tục.

* **Alternatives considered**:

  * Option A: ECS Fargate (rejected because không hỗ trợ DaemonSet, trong khi ADOT Collector yêu cầu chạy ở mức node).
  * Option B: AWS Lambda (rejected because không phù hợp với workflow orchestration dài và Kubernetes-native workload).

---

## ADR-002 - Dual Execution Path: GitOps (deferred) kết hợp Direct K8s API Patch (urgent)

* **Status**: Accepted

* **Date**: 2026-06-22

* **Context**:

Client yêu cầu hệ thống xử lý nhiều loại sự cố khác nhau. Một số sự cố như OOMKilled hoặc Service Stuck cần được khắc phục trong vài giây để giảm downtime. Trong khi đó các thay đổi cấu hình như Queue Backlog hoặc worker scaling cần được quản lý thông qua GitOps để đảm bảo auditability và rollback. Nếu chỉ sử dụng một cơ chế duy nhất thì hoặc tốc độ xử lý sẽ chậm hoặc mất khả năng kiểm soát thay đổi.

* **Decision**:

Áp dụng hai đường thực thi riêng biệt. Các hành động khẩn cấp sẽ gọi trực tiếp Kubernetes API để giảm độ trễ. Các thay đổi cấu hình dài hạn sẽ được thực hiện thông qua Git commit → ArgoCD Sync → Verify.

* **Consequence**:

  * ✅ Đảm bảo phản hồi nhanh cho các incident cần xử lý tức thời.
  * ✅ Vẫn duy trì được audit trail và rollback cho các thay đổi cấu hình.
  * ⚠️ Logic orchestration phức tạp hơn vì phải quản lý hai luồng xử lý.
  * ⚠️ Cần xác định rõ pattern nào thuộc Direct Patch và pattern nào thuộc GitOps.

* **Alternatives considered**:

  * Option A: Chỉ dùng GitOps (rejected because thời gian apply và sync quá chậm cho các sự cố cần phản hồi tức thời).
  * Option B: Chỉ dùng Direct Patch (rejected because mất auditability và khó rollback đối với thay đổi cấu hình).

---

## ADR-003 - S3 Object Lock (COMPLIANCE mode) + Kinesis Firehose là nguồn kiểm toán bất biến duy nhất

* **Status**: Accepted

* **Date**: 2026-06-22

* **Context**:

Client yêu cầu mọi hành động remediation phải có audit trail tamper-evident với retention tối thiểu 90 ngày nhằm phục vụ yêu cầu compliance và điều tra sau sự cố. Audit log phải chứng minh được ai thực hiện hành động gì, thời điểm nào và kết quả ra sao. Hệ thống cần một nơi lưu trữ mà dữ liệu không thể bị chỉnh sửa hoặc xoá ngoài ý muốn.

* **Decision**:

Sử dụng Kinesis Firehose để thu thập audit event và ghi trực tiếp vào S3 Object Lock ở chế độ Compliance Mode. S3 được xem là nguồn sự thật duy nhất cho mọi dữ liệu kiểm toán.

* **Consequence**:

  * ✅ Đáp ứng yêu cầu tamper-evident và retention của client.
  * ✅ Chi phí thấp, dễ mở rộng và hỗ trợ truy vấn bằng Athena.
  * ⚠️ Log sau khi ghi gần như không thể sửa đổi.
  * ⚠️ Cần thiết kế schema audit ngay từ đầu để tránh phải migrate sau này.

* **Alternatives considered**:

  * Option A: Audit log trong DynamoDB (rejected because không cung cấp mức độ bất biến mạnh như Object Lock).
  * Option B: Audit log trong RDS (rejected because có thể bị chỉnh sửa bởi tài khoản có quyền quản trị).

---

## ADR-004 - DynamoDB State Machine với Conditional Write Lock và Auto-Expiry TTL cho Incident Tracking

* **Status**: Accepted

* **Date**: 2026-06-22

* **Context**:

Self-Heal Engine có thể nhận nhiều alert giống nhau trong thời gian ngắn. Nếu cùng một incident được xử lý nhiều lần thì có thể dẫn đến scale lặp, restart lặp hoặc ghi audit trùng lặp. Hệ thống cần một cơ chế đảm bảo idempotency đồng thời phải có khả năng tự dọn dẹp dữ liệu cũ để giảm chi phí vận hành.

* **Decision**:

Sử dụng DynamoDB làm incident state store. Mỗi incident được khóa bằng Conditional Write để chỉ một workflow được phép xử lý. TTL được dùng để tự động xóa state đã hết hạn.

* **Consequence**:

  * ✅ Ngăn chặn xử lý trùng lặp cho cùng một incident.
  * ✅ Chi phí thấp nhờ mô hình On-Demand và TTL tự động dọn dẹp dữ liệu.
  * ⚠️ Không phù hợp với các truy vấn quan hệ phức tạp.
  * ⚠️ Cần thiết kế partition key cẩn thận để tránh hot partition.

* **Alternatives considered**:

  * Option A: Redis Lock (rejected because phải vận hành thêm một hệ thống stateful chạy 24/7).
  * Option B: RDS Transaction Lock (rejected because chi phí và độ phức tạp cao hơn nhu cầu thực tế của capstone).

---

## ADR-005 - Bổ sung Pattern thứ 5 (Designed-only): Disk Space Exceeded trên EKS Node

* **Status**: Accepted

* **Date**: 2026-06-22

* **Context**:

Client yêu cầu tối thiểu 3 pattern được triển khai và thêm các pattern được thiết kế dưới dạng playbook. Ngoài các lỗi OOMKilled, Service Stuck và Queue Backlog, nhóm muốn bổ sung một tình huống hạ tầng phổ biến hơn ở tầng node. Disk đầy trên EKS node có thể khiến pod scheduling thất bại hoặc container bị eviction.

* **Decision**:

Bổ sung "Disk Space Exceeded trên EKS Node" làm pattern designed-only. Runbook đề xuất sẽ bao gồm phát hiện dung lượng vượt ngưỡng, xác minh blast radius, cordon node, drain workload và thay thế node nếu cần.

* **Consequence**:

  * ✅ Tăng độ bao phủ của hệ thống đối với các sự cố hạ tầng.
  * ✅ Chứng minh khả năng mở rộng framework remediation cho các pattern mới.
  * ⚠️ Chưa được triển khai đầy đủ trong phạm vi capstone.
  * ⚠️ Việc tự động drain node cần kiểm soát chặt để tránh ảnh hưởng workload khác.

* **Alternatives considered**:

  * Option A: Cert Expiring (rejected because yêu cầu tích hợp quản lý secret và certificate phức tạp hơn phạm vi demo).
  * Option B: Network Latency Spike (rejected because khó mô phỏng và khó xác minh remediation thành công trong sandbox).
