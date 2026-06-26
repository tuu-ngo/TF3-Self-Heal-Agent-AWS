# W11 T6 ArgoCD Deploy Status

## Da lam

- Tat app ArgoCD cu `self-heal-agent` tren cluster `cdo-eks-cluster-dev`.
- Xoa runtime cu trong `self-heal-system`, `tenant-a`, `tenant-b` de tranh orphan resources.
- Sua manifest ArgoCD de tro dung repo GitHub:
  - `https://github.com/tuu-ngo/TF3-Self-Heal-Agent-AWS.git`
- Tao cau truc workload dung cho ArgoCD:
  - `manifests/workloads/tenant-a`
  - `manifests/workloads/tenant-b`
- Fix manifest `AppProject` do truoc do co field `spec.syncPolicy` khong hop le.
- Push code len branch moi:
  - `codex-argocd-rewire`
- Apply lai ArgoCD va reconcile thanh cong:
  - `tenant-a-workloads`
  - `tenant-b-workloads`

## Trang thai hien tai

- ArgoCD applications:
  - `tenant-a-workloads`: `Synced`, `Healthy`
  - `tenant-b-workloads`: `Synced`, `Healthy`
- Workloads dang chay:
  - `tenant-a`: `cdo-sample-api` 1 pod Running
  - `tenant-b`: `notification-service` 2 pods Running

## Chua lam xong

- Chua dua AI engine moi va controller self-heal moi len ArgoCD trong repo nay.
- Chua bind GitOps cho cac tai nguyen platform-level khac nhu Kyverno, NetworkPolicy, observability.
- Chua merge vao `main` vi GitHub dang bat protected branch.

## Luu y quan trong

- `main` khong cho push truc tiep. De deploy nhanh, ArgoCD dang tro toi branch:
  - `codex-argocd-rewire`
- Pull request de merge ve `main`:
  - `https://github.com/tuu-ngo/TF3-Self-Heal-Agent-AWS/pull/new/codex-argocd-rewire`

## Goi y buoc tiep theo

1. Merge branch `codex-argocd-rewire` vao `main`.
2. Doi `targetRevision` trong hai file `Application` ve `main`.
3. Dua them AI engine skeleton va executor/controller vao repo theo cau truc GitOps.
4. Neu can demo W11-T6 ngay, co the dung 2 workload hien tai lam evidence cho ArgoCD multi-tenant sync.
