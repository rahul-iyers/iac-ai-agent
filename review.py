import os
import requests
from openai import AzureOpenAI

def read_file_safe(filename):
    if os.path.exists(filename):
        with open(filename) as f:
            content = f.read().strip()
            return content if content else None
    return None

diff = read_file_safe("diff.txt")
validate_output = read_file_safe("tf_validate.txt")
plan_output = read_file_safe("tf_plan.txt")

sections = []
if validate_output:
    sections.append(f"Terraform validation errors (if any):\n{validate_output}")
if plan_output:
    sections.append(f"Terraform plan output (if any):\n{plan_output}")
if diff:
    sections.append(f"PR Diff:\n\n{diff}")

if not sections:
    sections.append("No code changes or Terraform output detected. If you see this message, there may be a critical syntax error preventing Terraform from running.")

prompt = "\n\n".join(sections)

client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
)

response = client.chat.completions.create(
    model=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
    messages=[{"role": "user", "content": prompt}],
)

review_comment = response.choices[0].message.content.strip()

# Post to GitHub PR
pr_number = os.getenv("PR_NUMBER")
repo = os.getenv("REPO")
token = os.getenv("GH_TOKEN")

r = requests.post(
    f"https://api.github.com/repos/{repo}/issues/{pr_number}/comments",
    headers={"Authorization": f"Bearer {token}"},
    json={"body": review_comment},
)

print("Comment status:", r.status_code)
print("GitHub API response:", r.text)
