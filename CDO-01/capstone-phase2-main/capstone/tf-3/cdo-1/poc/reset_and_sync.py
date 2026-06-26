import requests, urllib3, time, yaml, subprocess

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

ARGOCD_URL = "https://localhost:8080"
ARGOCD_USER = "admin"
ARGOCD_PASS = "LH8THwyAupQDuIdU"
ARGOCD_APP_NAME = "my-app"
K8S_DEPLOYMENT = "my-app"
K8S_NAMESPACE = "default"
YAML_FILE = "capstone/tf-3/cdo-1/poc/deployment.yaml"

# Reset Git YAML ve 64Mi
with open(YAML_FILE, 'r') as f:
    data = yaml.safe_load(f)
data['spec']['template']['spec']['containers'][0]['resources']['limits']['memory'] = "64Mi"
with open(YAML_FILE, 'w') as f:
    yaml.dump(data, f, default_flow_style=False)

# Push len GitHub
subprocess.run(f'git add {YAML_FILE} && git commit -m "chore(reset): reset before case1 [reset]" && git push origin main', shell=True, capture_output=True)

# Login ArgoCD
r = requests.post(f"{ARGOCD_URL}/api/v1/session", json={"username": ARGOCD_USER, "password": ARGOCD_PASS}, verify=False, timeout=10)
token = r.json()["token"]
headers = {"Authorization": f"Bearer {token}"}

# Enable sync + force
app = requests.get(f"{ARGOCD_URL}/api/v1/applications/{ARGOCD_APP_NAME}", headers=headers, verify=False, timeout=10).json()
app["spec"]["syncPolicy"] = {"automated": {"prune": True, "selfHeal": True}}
requests.put(f"{ARGOCD_URL}/api/v1/applications/{ARGOCD_APP_NAME}", headers=headers, json=app, verify=False, timeout=10)
requests.post(f"{ARGOCD_URL}/api/v1/applications/{ARGOCD_APP_NAME}/sync", headers=headers, json={}, verify=False, timeout=30)
time.sleep(10)

# Verify
from kubernetes import client, config
config.load_kube_config()
v1 = client.AppsV1Api()
dep = v1.read_namespaced_deployment(name=K8S_DEPLOYMENT, namespace=K8S_NAMESPACE)
mem = dep.spec.template.spec.containers[0].resources.limits.get("memory", "None")
print(f"Reset complete. Cluster memory: {mem}")
