import os
import subprocess
import uuid

from langchain.tools import tool


def run(command, cwd=None):
    print(f"\n>>> Running: {' '.join(command)}", flush=True)

    process = subprocess.Popen(
        command,
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        bufsize=1,
    )

    for line in process.stdout:
        print(line, end="", flush=True)

    return_code = process.wait()

    print(
        f">>> Command exited with code: {return_code}\n",
        flush=True
    )

    if return_code != 0:
        raise RuntimeError(
            f"Command failed: {' '.join(command)}"
        )

    return ""


def make_tools(repo_path):
    @tool
    def list_files(path: str = ".") -> str:
        """List files and directories inside the repository."""
        full_path = os.path.join(repo_path, path)

        if not os.path.isdir(full_path):
            return f"{path} is not a directory"

        return "\n".join(sorted(os.listdir(full_path)))

    @tool
    def read_file(path: str) -> str:
        """Read a text file from the repository."""
        full_path = os.path.join(repo_path, path)

        if not os.path.isfile(full_path):
            return f"{path} does not exist"

        with open(full_path, "r", encoding="utf-8") as file:
            return file.read()

    @tool
    def search_files(pattern: str) -> str:
        """Search repository files for a text pattern."""
        result = subprocess.run(
            [
                "grep",
                "-R",
                "-n",
                "--exclude-dir=.git",
                pattern,
                ".",
            ],
            cwd=repo_path,
            text=True,
            capture_output=True,
        )

        if result.returncode == 0:
            return result.stdout

        if result.returncode == 1:
            return "No matches found"

        raise RuntimeError(
            f"grep failed: {result.stderr}"
        )

    @tool
    def write_file(path: str, content: str) -> str:
        """Write or replace a text file in the repository."""
        full_path = os.path.abspath(
            os.path.join(repo_path, path)
        )

        repo_root = os.path.abspath(repo_path)

        if not full_path.startswith(repo_root + os.sep):
            raise RuntimeError(
                "Cannot write outside repository"
            )

        if full_path.startswith(
            os.path.join(repo_root, ".git") + os.sep
        ):
            raise RuntimeError(
                "Cannot modify .git"
            )

        os.makedirs(
            os.path.dirname(full_path),
            exist_ok=True,
        )

        with open(
            full_path,
            "w",
            encoding="utf-8",
        ) as file:
            file.write(content)

        return f"Updated {path}"

    return [
        list_files,
        read_file,
        search_files,
        write_file,
    ]


def clone_repo(repo_url, repo_path):
    run(
        [
            "git",
            "clone",
            repo_url,
            repo_path,
        ]
    )


def configure_git(repo_path):
    run(
        [
            "git",
            "config",
            "user.name",
            "AI Deploy Agent",
        ],
        cwd=repo_path,
    )

    run(
        [
            "git",
            "config",
            "user.email",
            "ai-infra-agent@users.noreply.github.com",
        ],
        cwd=repo_path,
    )

    token = os.environ.get("GITHUB_TOKEN")

    if not token:
        raise RuntimeError("GITHUB_TOKEN is not set")

    os.environ["GH_TOKEN"] = token

    run(
        [
            "gh",
            "auth",
            "setup-git",
        ],
        cwd=repo_path,
    )


def create_feature_branch(repo_path, ticket_id, attempt):
    random_string = uuid.uuid4().hex[:6]

    branch = (
        f"feature/ai-{ticket_id}"
        f"-attempt-{attempt}"
        f"-{random_string}"
    )

    run(
        [
            "git",
            "checkout",
            "-b",
            branch,
        ],
        cwd=repo_path,
    )

    return branch


def commit_and_push(repo_path, branch, ticket_id, attempt):
    run(
        [
            "git",
            "add",
            ".",
        ],
        cwd=repo_path,
    )

    run(
        [
            "git",
            "commit",
            "-m",
            f"{ticket_id}: deployment attempt {attempt}",
        ],
        cwd=repo_path,
    )

    run(
        [
            "git",
            "push",
            "-u",
            "origin",
            branch,
        ],
        cwd=repo_path,
    )


def terraform_init(repo_path):
    init_file = os.environ.get("TERRAFORM_INIT_FILE")

    if not init_file:
        raise RuntimeError(
            "TERRAFORM_INIT_FILE is not set"
        )

    if os.path.dirname(init_file):
        raise RuntimeError(
            "TERRAFORM_INIT_FILE must name a top-level .hcl file"
        )

    if not init_file.endswith(".hcl"):
        raise RuntimeError(
            "TERRAFORM_INIT_FILE must be an .hcl file"
        )

    init_path = os.path.join(
        repo_path,
        init_file,
    )

    if not os.path.isfile(init_path):
        raise RuntimeError(
            f"Terraform init file not found: {init_file}"
        )

    run(
        [
            "terraform",
            "init",
            f"-backend-config={init_file}",
        ],
        cwd=repo_path,
    )


def create_pr(repo_path, branch, ticket_id):
    result = run(
        [
            "gh",
            "pr",
            "create",
            "--base",
            "master",
            "--head",
            branch,
            "--title",
            f"{ticket_id}: deployment",
            "--body",
            f"Automated deployment PR for {ticket_id}.",
        ],
        cwd=repo_path,
    )

    return result.strip()


def configure_azure():
    required = [
        "AZURE_CLIENT_ID",
        "AZURE_CLIENT_SECRET",
        "AZURE_TENANT_ID",
        "AZURE_SUBSCRIPTION_ID",
    ]

    missing = [
        name
        for name in required
        if not os.environ.get(name)
    ]

    if missing:
        raise RuntimeError(
            "Missing Azure environment variables: "
            + ", ".join(missing)
        )

    run(
        [
            "az",
            "login",
            "--service-principal",
            "--username",
            os.environ["AZURE_CLIENT_ID"],
            "--password",
            os.environ["AZURE_CLIENT_SECRET"],
            "--tenant",
            os.environ["AZURE_TENANT_ID"],
        ]
    )

    run(
        [
            "az",
            "account",
            "set",
            "--subscription",
            os.environ["AZURE_SUBSCRIPTION_ID"],
        ]
    )


def terraform_var_files():
    raw = os.environ.get("TERRAFORM_VAR_FILES", "").strip()

    if not raw:
        raise RuntimeError("TERRAFORM_VAR_FILES is not set")

    files = [item.strip() for item in raw.split(",") if item.strip()]

    if not files:
        raise RuntimeError("TERRAFORM_VAR_FILES contains no files")

    return files


def validate_terraform_var_files(repo_path):
    files = terraform_var_files()

    for var_file in files:
        path = os.path.join(repo_path, var_file)

        if not os.path.isfile(path):
            raise RuntimeError(
                f"Terraform var file not found: {var_file}"
            )

    return files


def terraform_plan(repo_path):
    var_files = validate_terraform_var_files(repo_path)

    command = ["terraform", "plan"]

    for var_file in var_files:
        command.append(f"-var-file={var_file}")

    run(command, cwd=repo_path)


def terraform_apply(repo_path):
    var_files = validate_terraform_var_files(repo_path)

    command = ["terraform", "apply", "-auto-approve"]

    for var_file in var_files:
        command.append(f"-var-file={var_file}")

    run(command, cwd=repo_path)
