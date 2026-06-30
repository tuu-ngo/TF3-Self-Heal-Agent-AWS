# 📸 TASK PHÂN CÔNG CHỤP ẢNH MÀN HÌNH (MANUAL SCREENSHOTS)

> **Mục đích**: File này **chỉ liệt kê những evidence BẮT BUỘC phải lên giao diện (AWS Console, ArgoCD, GitHub) để chụp hình hoặc quay video**. Những thứ còn lại đã được script terminal tự động thu thập.
> **Cách dùng**: Gửi file này cho team, chia nhau người phụ trách, tick `[x]` khi chụp xong và lưu ảnh vào đúng thư mục `docs/assets/evidence/...`.

---

## 1. 🌐 Nhóm Hạ Tầng & Networking (AWS Console)
*Thư mục lưu ảnh: `docs/assets/evidence/infra/`*

| Status | Tên ảnh | Nơi chụp | Cần thấy gì trên ảnh | Người làm |
|---|---|---|---|---|
| [ ] | `eks-cluster-console.png` | **EKS → Clusters** → chọn cluster | Tab "Overview" thấy: status **Active**, K8s version, endpoint URL. | _______ |
| [ ] | `eks-nodegroup.png` | **EKS → Clusters** → tab Compute | Thấy Node group t3.medium, desired/min/max counts, status Active. | _______ |
| [ ] | `vpc-console.png` | **VPC → Your VPCs** | Thấy CIDR block, Tên VPC, Default VPC = No. | _______ |
| [ ] | `subnets-console.png` | **VPC → Subnets** | Lọc theo VPC dự án. Thấy các public/private subnets chia đều ở các AZ (us-east-1a, 1b). | _______ |

---

## 2. 🛡️ Nhóm Bảo Mật & Audit (AWS Console)
*Thư mục lưu ảnh: `docs/assets/evidence/security/` và `audit/`*

| Status | Tên ảnh | Nơi chụp | Cần thấy gì trên ảnh | Người làm |
|---|---|---|---|---|
| [ ] | `iam-irsa-executor.png` | **IAM → Roles** | Role của executor (tf3-cdo-controller). Tab "Permissions" thấy list policy. | _______ |
| [ ] | `iam-irsa-ai.png` | **IAM → Roles** | Role của AI engine. Tab "Permissions" thấy list policy. | _______ |
| [ ] | `s3-object-lock.png` | **S3 → Audit Bucket** | Tab Properties, cuộn xuống Object Lock. Thấy **Enabled**, mode **Governance**. | _______ |
| [ ] | `s3-retention.png` | **S3 → Audit Bucket** | Tab Properties. Thấy Default retention: ≥ 90 days. | _______ |
| [ ] | `s3-audit-objects.png` | **S3 → Audit Bucket** | Tab Objects. Thấy danh sách các file log JSON sinh ra sau khi test. | _______ |
| [ ] | `dynamodb-items.png` | **DynamoDB → Tables** | Chọn bảng idempotency, tab "Explore items". Thấy các bản ghi lock. | _______ |

---

## 3. 💸 Nhóm Chi Phí / Billing (AWS Console - ⚠️ CỰC QUAN TRỌNG)
*Thư mục lưu ảnh: `docs/assets/evidence/cost/`*
*(Yêu cầu phải có số liệu thật (measured) sau vài ngày chạy)*

| Status | Tên ảnh | Nơi chụp | Cần thấy gì trên ảnh | Người làm |
|---|---|---|---|---|
| [ ] | `cost-explorer-by-service.png`| **Cost Explorer** | Chọn Date = ngày bắt đầu đến nay. Group by: **Service**. Chụp **biểu đồ cột**. | _______ |
| [ ] | `cost-explorer-table.png` | **Cost Explorer** | Cuộn xuống ngay dưới biểu đồ cột trên, chụp **bảng số liệu chi tiết**. | _______ |
| [ ] | `cost-by-usage.png` | **Cost Explorer** | Đổi Group by thành: **Usage Type**. Chụp thấy EKS, EC2, NAT Gateway. | _______ |
| [ ] | `billing-dashboard.png` | **Billing → Dashboard**| Chụp Widget "Month-to-date costs by service". | _______ |
| [ ] | `ec2-instances.png` | **EC2 → Instances** | Lọc state=Running. Thấy 2 instance `t3.medium` (chính là EKS nodes). | _______ |

---

## 4. 🚀 Nhóm Deployment (Giao diện ArgoCD & GitHub)
*Thư mục lưu ảnh: `docs/assets/evidence/deployment/`*

| Status | Tên ảnh | Nơi chụp | Cần thấy gì trên ảnh | Người làm |
|---|---|---|---|---|
| [ ] | `argocd-dashboard.png` | **ArgoCD UI** (Trang chủ)| Thấy các app (ai-engine, executor, workloads). Status **Synced / Healthy**. | _______ |
| [ ] | `argocd-app-detail.png` | **ArgoCD UI** (Chi tiết)| Click vào app executor. Thấy cây resource (Deployments, Pods xanh lá). | _______ |
| [ ] | `github-actions.png` | **GitHub Repo** | Tab **Actions**. Thấy lịch sử pipeline chạy thành công (màu xanh). | _______ |

---

## 5. 📉 Nhóm SLO & CloudWatch (AWS Console)
*Thư mục lưu ảnh: `docs/assets/evidence/test/`*

| Status | Tên ảnh | Nơi chụp | Cần thấy gì trên ảnh | Người làm |
|---|---|---|---|---|
| [ ] | `slo-cloudwatch-metrics.png` | **CloudWatch → Metrics**| Biểu đồ p99 latency của AI / Executor (nếu team có bắn metric lên CW). | _______ |
| [ ] | `slo-cwl-query.png` | **CW → Logs Insights** | Truy vấn log đo thời gian từ lúc nhận lỗi đến lúc execute xong. | _______ |
| [ ] | `cwl-correlation-trace.png`| **CW → Logs Insights** | Query lọc theo 1 `correlation_id` cụ thể, thấy dòng chảy của request. | _______ |

---

## 6. 🎥 Nhóm Quay Video Demo E2E (Màn hình máy tính)
*Thư mục lưu ảnh: `docs/assets/evidence/e2e-demo/`*

| Status | Tên Video | Công cụ | Cần thấy gì trong video | Người làm |
|---|---|---|---|---|
| [ ] | `e2e-demo-happy-path.mp4` | OBS / Win+G / Zoom | Mở 2-3 tab terminal: 1 tab xem log executor (`kubectl logs -f`), 1 tab watch pod (`kubectl get pods -w`), 1 tab chạy kịch bản lỗi. Thấy lỗi xảy ra → executor phát hiện → AI gọi → tự động restart pod. | _______ |
| [ ] | `e2e-demo-deny-case.mp4` | OBS / Win+G / Zoom | Chạy kịch bản cross-tenant (đánh phá tenant khác). Quay lại màn hình log executor báo **DENIED by Safety Gate**. | _______ |

---
**Tổng cộng:** Có **20** tấm ảnh màn hình và **2** video cần thực hiện bằng tay. Bạn hãy gửi list này cho team để nhận việc.
