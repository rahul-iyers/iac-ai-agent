import requests
import json
import os

def main():
    with open("plan.txt") as f:
        plan = f.read()
    with open("diff.patch") as f:
        diff = f.read()

    payload = {
        "terraform_plan": plan,
        "git_diff": diff,
        "pr_title": os.getenv("PR_TITLE", ""),
        "pr_number": os.getenv("PR_NUMBER", ""),
        "repository": os.getenv("REPO_NAME", "")
    }

    resp = requests.post(
        "https://your-mcp-server.com/models/Terraform MCP Server/tools/analyze_tf/invoke",
        json={"input": {"terraform_code": plan + "\n\n" + diff}}
    )

    print("Response status:", resp.status_code)
    print("Response content:", resp.text)

    feedback = resp.json().get("output", "No feedback.")
    with open("review.md", "w") as f:
        f.write(feedback)

if __name__ == "__main__":
    main()
