import json
import os

from deploy_agent import deploy


payload = os.environ.get("JIRA_PAYLOAD")

if not payload:
    raise RuntimeError("JIRA_PAYLOAD is not set")

data = json.loads(payload)

if data.get("action") == "DEPLOY":
    deploy(data)

elif data.get("action") == "FIX":
    print("Incident agent is not implemented yet")

else:
    raise RuntimeError(
        f"Unsupported action: {data.get('action')}"
    )
