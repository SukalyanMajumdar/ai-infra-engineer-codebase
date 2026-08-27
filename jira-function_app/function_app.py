import json
import logging
import os
import urllib.request

import azure.functions as func
from azure.identity import DefaultAzureCredential


app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)


@app.route(route="jira-webhook", methods=["POST"])
def jira_webhook(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Received JIRA webhook request")

    try:
        data = req.get_json()

        issue = data["issue"]
        fields = issue["fields"]

        ticket_id = issue["key"]
        summary = fields["summary"]
        description = fields.get("description", "")

        action = None

        if summary.startswith("[DEPLOY]"):
            action = "DEPLOY"
        elif summary.startswith("[FIX]"):
            action = "FIX"

        repo_url = os.environ.get("REPO_URL")

        if not repo_url:
            raise RuntimeError("REPO_URL environment variable is not set")

        # Payload passed to the Azure Container Apps Job.
        jira_payload = {
            "ticket_id": ticket_id,
            "summary": summary,
            "description": description,
            "repo_url": repo_url,
            "action": action
        }

        subscription_id = os.environ["ACA_SUBSCRIPTION_ID"]
        resource_group = os.environ["ACA_RESOURCE_GROUP"]
        job_name = os.environ["ACA_JOB_NAME"]

        credential = DefaultAzureCredential()
        token = credential.get_token(
            "https://management.azure.com/.default"
        ).token

        base_url = (
            f"https://management.azure.com"
            f"/subscriptions/{subscription_id}"
            f"/resourceGroups/{resource_group}"
            f"/providers/Microsoft.App/jobs/{job_name}"
        )

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        # Get the existing ACAJ template.
        request = urllib.request.Request(
            f"{base_url}?api-version=2026-01-01",
            headers=headers
        )

        with urllib.request.urlopen(request) as response:
            job = json.loads(response.read())

        template = job["properties"]["template"]
        containers = template["containers"]

        # Add or replace the JIRA payload in the first container.
        payload = json.dumps(jira_payload)

        env = containers[0].get("env", [])

        for variable in env:
            if variable["name"] == "JIRA_PAYLOAD":
                variable["value"] = payload
                variable.pop("secretRef", None)
                break
        else:
            env.append({
                "name": "JIRA_PAYLOAD",
                "value": payload
            })

        containers[0]["env"] = env

        # Start the ACAJ execution with the updated container configuration.
        start_request = urllib.request.Request(
            f"{base_url}/start?api-version=2026-01-01",
            data=json.dumps({
                "containers": containers,
                "initContainers": template.get("initContainers", [])
            }).encode(),
            headers=headers,
            method="POST"
        )

        with urllib.request.urlopen(start_request) as response:
            execution = json.loads(response.read())

        logging.info("ACAJ execution started: %s", execution.get("name"))

        return func.HttpResponse(
            json.dumps({
                "status": "ACAJ started",
                "execution": execution.get("name")
            }),
            status_code=202,
            mimetype="application/json"
        )

    except ValueError:
        logging.exception("Invalid JSON received")

        return func.HttpResponse(
            json.dumps({"error": "Request body is not valid JSON"}),
            status_code=400,
            mimetype="application/json"
        )

    except KeyError as exc:
        logging.exception("Missing expected field")

        return func.HttpResponse(
            json.dumps({"error": f"Missing expected field: {exc}"}),
            status_code=400,
            mimetype="application/json"
        )

    except Exception:
        logging.exception("Unexpected error")

        return func.HttpResponse(
            json.dumps({"error": "Internal server error"}),
            status_code=500,
            mimetype="application/json"
        )