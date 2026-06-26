import requests, urllib3, time, sys

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

ARGOCD_URL = "https://localhost:8080"
ARGOCD_USER = "admin"
ARGOCD_PASS = "LH8THwyAupQDuIdU"
ARGOCD_APP_NAME = "my-app"

try:
    resp = requests.post(f"{ARGOCD_URL}/api/v1/session", json={"username": ARGOCD_USER, "password": ARGOCD_PASS}, verify=False, timeout=10)
    token = resp.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Enable sync
    app = requests.get(f"{ARGOCD_URL}/api/v1/applications/{ARGOCD_APP_NAME}", headers=headers, verify=False, timeout=10).json()
    app["spec"]["syncPolicy"] = {"automated": {"prune": True, "selfHeal": True}}
    requests.put(f"{ARGOCD_URL}/api/v1/applications/{ARGOCD_APP_NAME}", headers=headers, json=app, verify=False, timeout=10)

    # Force sync
    requests.post(f"{ARGOCD_URL}/api/v1/applications/{ARGOCD_APP_NAME}/sync", headers=headers, json={}, verify=False, timeout=10)
    print("Sync triggered successfully.")
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
