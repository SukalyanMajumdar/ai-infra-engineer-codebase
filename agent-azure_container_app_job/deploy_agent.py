import os
import shutil
import tempfile

from langchain.agents import create_agent
from langchain_openai import ChatOpenAI

from deploy_agent_tools import (
    configure_azure,
    configure_git,
    commit_and_push,
    create_feature_branch,
    create_pr,
    clone_repo,
    make_tools,
    terraform_init,
    terraform_plan,
)


def make_changes(repo_path, payload):
    model = ChatOpenAI(
        model=os.environ["OPENAI_MODEL"],
        use_responses_api=True,
    )

    agent = create_agent(
        model=model,
        tools=make_tools(repo_path),
        system_prompt="""
You are a Terraform infrastructure engineer.

You are working inside a cloned infrastructure repository.

Your job is to implement the requested JIRA deployment.

Rules:
- Inspect the repository before making changes.
- Understand the existing Terraform structure.
- Make only the changes required by the ticket.
- Do not modify files unnecessarily.
- Do not modify .git contents.
- Do not run git commands.
- Do not run Terraform commands.
- Use only the provided repository tools.
- Do not invent infrastructure requirements.
""",
    )

    request = f"""
JIRA ticket:

Ticket ID:
{payload["ticket_id"]}

Summary:
{payload["summary"]}

Description:
{payload["description"]}

Inspect the repository and implement the requested infrastructure change.
"""

    print("\n========== AGENT START ==========", flush=True)
    print("Sending request to OpenAI...", flush=True)

    result = None
    printed_message_ids = set()

    print("\n========== LIVE AGENT EXECUTION ==========", flush=True)

    for state in agent.stream(
        {"messages": [{"role": "user", "content": request}]},
        stream_mode="values",
    ):
        result = state
        messages = state.get("messages", [])
        if not messages:
            continue

        message = messages[-1]
        message_id = getattr(message, "id", None)

        if message_id and message_id in printed_message_ids:
            continue
        if message_id:
            printed_message_ids.add(message_id)

        print(f"\n--- {type(message).__name__} ---", flush=True)

        name = getattr(message, "name", None)
        if name:
            print(f"TOOL NAME: {name}", flush=True)

        tool_calls = getattr(message, "tool_calls", None)
        if tool_calls:
            print("TOOL CALLS:", flush=True)
            print(tool_calls, flush=True)

        content = getattr(message, "content", None)
        if content:
            print("CONTENT:", flush=True)
            print(content, flush=True)

    if result is None:
        raise RuntimeError("Agent produced no result")

    print("\n========== END AGENT EXECUTION ==========", flush=True)
    final_message = result["messages"][-1]

    print("\n========== AGENT FINAL RESULT ==========", flush=True)
    print(getattr(final_message, "content", ""), flush=True)
    print("========== END AGENT ==========\n", flush=True)

    return result


def deploy(payload):
    repo_url = payload["repo_url"]
    repo_path = tempfile.mkdtemp(prefix="deploy-")

    try:
        clone_repo(repo_url, repo_path)
        configure_git(repo_path)

        branch = create_feature_branch(
            repo_path,
            payload["ticket_id"],
            1,
        )

        print(f"Created branch: {branch}", flush=True)

        make_changes(repo_path, payload)

        commit_and_push(
            repo_path,
            branch,
            payload["ticket_id"],
            1,
        )

        configure_azure()
        terraform_init(repo_path)
        terraform_plan(repo_path)

        pr_url = create_pr(
            repo_path,
            branch,
            payload["ticket_id"],
        )

        print(f"Pull request created: {pr_url}", flush=True)
        print("Deployment agent stopping after PR creation.", flush=True)

    finally:
        shutil.rmtree(repo_path, ignore_errors=True)
