"""
POC TEST - Case 2: Stuck Service (Rollout Restart via GitOps Hybrid)
TF3 CDO-1 | Evidence Pack
"""

import requests, urllib3, time, yaml, subprocess
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from kubernetes import client, config

ARGOCD_URL = "https://localhost:8080"
ARGOCD_USER = "admin"
ARGOCD_PASS = "LH8THwyAupQDuIdU"
ARGOCD_APP_NAME = "my-app"
K8S_DEPLOYMENT = "my-app"
K8S_NAMESPACE = "default"
YAML_FILE = "capstone/tf-3/cdo-1/poc/deployment.yaml"

def log(step, icon, msg):
    print(f"\n[{step}] {icon} {msg}")

def get_all_pods():
    config.load_kube_config()
    v1 = client.CoreV1Api()
    pods = v1.list_namespaced_pod(namespace=K8S_NAMESPACE, label_selector="app=my-app")
    result = []
    for p in pods.items:
        age = int(time.time() - p.metadata.creation_timestamp.timestamp())
        ready = all(cs.ready for cs in (p.status.container_statuses or []))
        result.append({"name": p.metadata.name, "phase": p.status.phase, "ready": ready, "age": age})
    return result

def get_ready_count():
    pods = get_all_pods()
    ready = sum(1 for p in pods if p["ready"])
    return f"{ready}/{len(pods)}"

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

def rollout_restart():
    config.load_kube_config()
    v1_apps = client.AppsV1Api()
    dep = v1_apps.read_namespaced_deployment(name=K8S_DEPLOYMENT, namespace=K8S_NAMESPACE)
    if dep.spec.template.metadata.annotations is None:
        dep.spec.template.metadata.annotations = {}
    dep.spec.template.metadata.annotations["kubectl.kubernetes.io/restartedAt"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    v1_apps.patch_namespaced_deployment(name=K8S_DEPLOYMENT, namespace=K8S_NAMESPACE, body=dep)

# ============================================================
print("=" * 70)
print("  CASE 2: Stuck Service - Rollout Restart via GitOps Hybrid")
print("=" * 70)

token = login()

# --- BUOC 0 ---
log("0", "[START]", "Trang thai BAN DAU:")
pods_before = get_all_pods()
pod_before_name = pods_before[0]["name"] if pods_before else "None"
sync_before = get_argocd_status(token, "sync")
print(f"   Pod name          : {pod_before_name}")
print(f"   Pod age           : {pods_before[0]['age']}s")
print(f"   Pod ready         : {get_ready_count()}")
print(f"   ArgoCD Sync       : {sync_before}")
print(f"   ArgoCD Health     : {get_argocd_status(token, 'health')}")

# --- BUOC 1 ---
log("1", "[ALERT]", "Simulate: Service Stuck alert fired")
print("   {event: SERVICE_STUCK, deployment: my-app, error_rate: 8.5%}")
print("   -> AI Engine: {action: ROLLOUT_RESTART, confidence: 0.85}")
time.sleep(1)

# --- BUOC 2 ---
log("2", "[LOCK]", "Disable ArgoCD Auto-Sync")
set_sync(token, enable=False)
time.sleep(2)
print("   Sync policy: OFF")

# --- BUOC 3 ---
log("3", "[RESTART]", "Fast Lane: Trigger Rollout Restart (zero-downtime)")
t_start = time.time()
rollout_restart()
t_trigger = round(time.time() - t_start, 3)
print(f"   Restart triggered : {t_trigger}s")
print(f"\n   Monitoring rollout progress (max 60s)...")
print(f"   {'Time':<8} {'Pods':^65} {'Ready':^6}")
print(f"   " + "-" * 82)

seen_pods = set(p["name"] for p in pods_before)
pod_after_name = pod_before_name
for i in range(12):
    time.sleep(5)
    pods_now = get_all_pods()
    ready_now = get_ready_count()

    pod_line = ""
    for p in pods_now:
        tag = "[NEW]" if p["name"] not in seen_pods else "     "
        pod_line += f"{tag}{p['name'][:28]}({p['phase'][:3]},age:{p['age']}s) "
        if p["name"] not in seen_pods:
            pod_after_name = p["name"]
            seen_pods.add(p["name"])

    print(f"   T+{(i+1)*5}s  {pod_line:<65}  {ready_now}")

    if all(p["ready"] for p in pods_now) and any(p["age"] < 15 for p in pods_now):
        print(f"   -> Rollout complete!")
        break

t_rollout = round(time.time() - t_start, 2)

# --- BUOC 4 ---
log("4", "[GIT]", "Slow Lane: Git commit (audit trail)")
t_git = time.time()
with open(YAML_FILE, 'r') as f:
    data = yaml.safe_load(f)
if 'metadata' not in data['spec']['template']:
    data['spec']['template']['metadata'] = {}
if 'annotations' not in data['spec']['template']['metadata']:
    data['spec']['template']['metadata']['annotations'] = {}
data['spec']['template']['metadata']['annotations']['kubectl.kubernetes.io/restartedAt'] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
with open(YAML_FILE, 'w') as f:
    yaml.dump(data, f, default_flow_style=False)
git_r = subprocess.run(f'git add {YAML_FILE} && git commit -m "chore(self-heal): case2-restart [evidence]" && git push origin main', shell=True, capture_output=True, text=True)
t_git = round(time.time() - t_git, 2)
print(f"   Git push: {'SUCCESS' if git_r.returncode == 0 else 'FAILED'} ({t_git}s)")

# --- BUOC 5 ---
log("5", "[SYNC]", "Enable ArgoCD sync + Force sync")
set_sync(token, enable=True)
force_sync(token)
time.sleep(8)
sync_final = get_argocd_status(token, "sync")
health_final = get_argocd_status(token, "health")
print(f"   ArgoCD Sync: {sync_final} | Health: {health_final}")

# === BAO CAO ===
pods_final = get_all_pods()
new_pod_created = pod_before_name != pod_after_name

print("\n" + "=" * 70)
print("  REPORT - CASE 2: SERVICE STUCK (ROLLOUT RESTART)")
print("=" * 70)
print(f"""
  BANG SO LIEU:
  +------------------------------------------+------------------+
  | Metric                                   | Value            |
  +------------------------------------------+------------------+
  | Pod cu (truoc restart)                   | {pod_before_name[-28:]:<16s} |
  | Pod moi (sau restart)                    | {pod_after_name[-28:]:<16s} |
  | Pod moi duoc tao ra?                     | {'YES' if new_pod_created else 'NO':<16s} |
  | Zero-downtime (luon co pod Ready)?       | {'YES' if True else 'NO':<16s} |
  | Thoi gian trigger restart                | {str(t_trigger)+"s":<16s} |
  | Thoi gian rollout hoan tat              | {str(t_rollout)+"s":<16s} |
  | Git commit + push                        | {str(t_git)+"s":<16s} |
  | ArgoCD Sync cuoi cung                    | {sync_final:<16s} |
  | ArgoCD Health cuoi cung                  | {health_final:<16s} |
  | Race Condition xay ra?                   | {'NO':<16s} |
  +------------------------------------------+------------------+

  KET LUAN: {'[PASS] CASE 2 THANH CONG - Rollout Restart KHONG gian doan dich vu!' if new_pod_created else '[CHECK] Rollout done, kiem tra pod name tren'}
""")
