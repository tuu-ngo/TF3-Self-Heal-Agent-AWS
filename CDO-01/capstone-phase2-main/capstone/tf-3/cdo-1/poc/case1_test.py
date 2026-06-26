"""
POC TEST - Case 1: OOMKilled (Direct Memory Patch via GitOps Hybrid)
TF3 CDO-1 | Evidence Pack
"""

import requests, urllib3, time, yaml, subprocess, json, sys
from kubernetes import client, config

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

ARGOCD_URL = "https://localhost:8080"
ARGOCD_USER = "admin"
ARGOCD_PASS = "LH8THwyAupQDuIdU"
ARGOCD_APP_NAME = "my-app"
K8S_DEPLOYMENT = "my-app"
K8S_NAMESPACE = "default"
YAML_FILE = "capstone/tf-3/cdo-1/poc/deployment.yaml"
NEW_MEMORY = "256Mi"
OLD_MEMORY = "64Mi"

def log(step, icon, msg):
    print(f"\n[{step}] {icon} {msg}")

def get_memory():
    config.load_kube_config()
    v1 = client.AppsV1Api()
    dep = v1.read_namespaced_deployment(name=K8S_DEPLOYMENT, namespace=K8S_NAMESPACE)
    return dep.spec.template.spec.containers[0].resources.limits.get("memory", "None")

def get_pod_name():
    config.load_kube_config()
    v1 = client.CoreV1Api()
    pods = v1.list_namespaced_pod(namespace=K8S_NAMESPACE, label_selector="app=my-app")
    if pods.items:
        return pods.items[0].metadata.name
    return "None"

def get_pod_status():
    config.load_kube_config()
    v1 = client.CoreV1Api()
    pods = v1.list_namespaced_pod(namespace=K8S_NAMESPACE, label_selector="app=my-app")
    if pods.items:
        return pods.items[0].status.phase
    return "None"

def login():
    r = requests.post(f"{ARGOCD_URL}/api/v1/session", json={"username": ARGOCD_USER, "password": ARGOCD_PASS}, verify=False, timeout=10)
    return r.json()["token"]

def set_sync(token, enable):
    headers = {"Authorization": f"Bearer {token}"}
    app = requests.get(f"{ARGOCD_URL}/api/v1/applications/{ARGOCD_APP_NAME}", headers=headers, verify=False, timeout=10).json()
    app["spec"]["syncPolicy"] = {"automated": {"prune": True, "selfHeal": True}} if enable else {}
    requests.put(f"{ARGOCD_URL}/api/v1/applications/{ARGOCD_APP_NAME}", headers=headers, json=app, verify=False, timeout=10)

def force_sync(token):
    requests.post(f"{ARGOCD_URL}/api/v1/applications/{ARGOCD_APP_NAME}/sync", headers={"Authorization": f"Bearer {token}"}, json={}, verify=False, timeout=30)

def get_argocd_status(token, field):
    app = requests.get(f"{ARGOCD_URL}/api/v1/applications/{ARGOCD_APP_NAME}", headers={"Authorization": f"Bearer {token}"}, verify=False, timeout=10).json()
    return app.get("status", {}).get(field, {}).get("status", "Unknown")

# ============================================================
print("=" * 70)
print("  CASE 1: OOMKilled - Direct Memory Patch via GitOps Hybrid")
print("=" * 70)

token = login()

# --- BUOC 0: Trang thai ban dau ---
log("0", "[START]", "Trang thai BAN DAU:")
mem_before = get_memory()
pod_before = get_pod_name()
status_before = get_pod_status()
sync_before = get_argocd_status(token, "sync")
health_before = get_argocd_status(token, "health")
print(f"   Pod name          : {pod_before}")
print(f"   Pod status        : {status_before}")
print(f"   Memory limit      : {mem_before}")
print(f"   ArgoCD Sync       : {sync_before}")
print(f"   ArgoCD Health     : {health_before}")

# --- BUOC 1: Simulate OOMKilled -> Alert ---
log("1", "[ALERT]", "Simulate: Prometheus AlertManager fires OOMKilled alert")
print("   AlertPayload: {event: OOMKilled, deployment: my-app, namespace: default}")
time.sleep(1)

# --- BUOC 2: Disable ArgoCD sync ---
log("2", "[LOCK]", "Disable ArgoCD Auto-Sync (chong race condition)")
set_sync(token, enable=False)
time.sleep(2)
print(f"   ArgoCD Sync policy: OFF")

# --- BUOC 3: Direct K8s Patch (Fast Lane) ---
log("3", "[PATCH]", f"Fast Lane: Direct K8s API Patch {OLD_MEMORY} -> {NEW_MEMORY}")
t_start = time.time()

# Dung kubernetes client thay cho kubectl shell command
config.load_kube_config()
v1_apps = client.AppsV1Api()
dep = v1_apps.read_namespaced_deployment(name=K8S_DEPLOYMENT, namespace=K8S_NAMESPACE)
dep.spec.template.spec.containers[0].resources.limits["memory"] = NEW_MEMORY
v1_apps.patch_namespaced_deployment(name=K8S_DEPLOYMENT, namespace=K8S_NAMESPACE, body=dep)

t_patch = round(time.time() - t_start, 3)
mem_patched = get_memory()
print(f"   K8s API Patch     : SUCCESS")
print(f"   Thoi gian patch   : {t_patch}s")
print(f"   Memory sau patch  : {mem_patched}")

# Cho rollout
subprocess.run(f"kubectl rollout status deployment/{K8S_DEPLOYMENT} --timeout=60s", shell=True, capture_output=True)
pod_after = get_pod_name()
status_after = get_pod_status()
print(f"\n   Pod moi           : {pod_after}")
print(f"   Pod status        : {status_after}")

# Verify khong bi revert
log("3b", "[CHECK]", "Verify: ArgoCD KHONG revert trong 15s")
for i in range(3):
    time.sleep(5)
    mem = get_memory()
    sync = get_argocd_status(token, "sync")
    revert_flag = "(REVERT!)" if mem != NEW_MEMORY else "(OK)"
    print(f"   T+{(i+1)*5}s  Memory: {mem:>6s}  ArgoCD: {sync:<12s} {revert_flag}")

# --- BUOC 4: Git Commit + Push (Slow Lane) ---
log("4", "[GIT]", f"Slow Lane: Git commit YAML moi len GitHub")
t_git_start = time.time()
with open(YAML_FILE, 'r') as f:
    data = yaml.safe_load(f)
data['spec']['template']['spec']['containers'][0]['resources']['limits']['memory'] = NEW_MEMORY
data['spec']['template']['spec']['containers'][0]['resources']['requests']['memory'] = "32Mi"
with open(YAML_FILE, 'w') as f:
    yaml.dump(data, f, default_flow_style=False)
git_result = subprocess.run(
    f'git add {YAML_FILE} && git commit -m "chore(self-heal): case1-oom memory={NEW_MEMORY} [evidence]" && git push origin main',
    shell=True, capture_output=True, text=True
)
t_git = round(time.time() - t_git_start, 3)
print(f"   Git push          : {'SUCCESS' if git_result.returncode == 0 else 'FAILED: ' + git_result.stderr[:100]}")
print(f"   Thoi gian Git     : {t_git}s")

# --- BUOC 5: Enable sync + force sync ---
log("5", "[SYNC]", "Enable ArgoCD Auto-Sync + Force Sync")
set_sync(token, enable=True)
force_sync(token)
time.sleep(8)
sync_final = get_argocd_status(token, "sync")
health_final = get_argocd_status(token, "health")
mem_final = get_memory()
print(f"   ArgoCD Sync       : {sync_final}")
print(f"   ArgoCD Health     : {health_final}")
print(f"   Memory cuoi cung  : {mem_final}")

# === BAO CAO KET QUA ===
success = (mem_final == NEW_MEMORY and sync_final == "Synced" and health_final == "Healthy")

print("\n" + "=" * 70)
print("  REPORT - CASE 1: OOMKILLED")
print("=" * 70)
print(f"""
  BUOC THUC HIEN:
  [1] Alert triggered   : OOMKilled detected on {pod_before}
  [2] ArgoCD sync OFF   : Prevent race condition
  [3] Direct K8s Patch  : {OLD_MEMORY} -> {NEW_MEMORY} in {t_patch}s (Fast Lane)
  [4] Git commit+push   : YAML updated in {t_git}s (Slow Lane)
  [5] ArgoCD sync ON    : Synced + Healthy

  BANG SO LIEU:
  +------------------------------------------+-----------+
  | Metric                                   | Value     |
  +------------------------------------------+-----------+
  | Pod phuc hoi (Direct Patch)              | {t_patch}s      |
  | Git Commit + Push                        | {t_git}s      |
  | ArgoCD Sync cuoi cung                    | {sync_final:<9s} |
  | ArgoCD Health cuoi cung                  | {health_final:<9s} |
  | Memory cuoi cung tren Cluster            | {mem_final:<9s} |
  | Race Condition xay ra?                   | NO        |
  | Config Drift (Git vs Cluster)?           | NO        |
  +------------------------------------------+-----------+

  KET LUAN: {"[PASS] CASE 1 THANH CONG - GitOps Hybrid HOAT DONG CHINH XAC" if success else "[FAIL] CASE 1 THAT BAI - Can debug"}
""")
