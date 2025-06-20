import os
import requests
from openai import AzureOpenAI

# Read PR diff
try:
    with open("diff.txt") as f:
        diff = f.read().strip()
except Exception:
    diff = None

# Read terraform validate output
validate_output = None
if os.path.exists("tf_validate.txt"):
    with open("tf_validate.txt") as tf:
        validate_output = tf.read().strip()

# Read terraform plan output
plan_output = None
if os.path.exists("tf_plan.txt"):
    with open("tf_plan.txt") as tf:
        plan_output = tf.read().strip()

# Compose prompt
sections = []
if validate_output:
    sections.append(f"Terraform validation errors (if any):\n{validate_output}")
if plan_output:
    sections.append(f"Terraform plan output (if any):\n{plan_output}")
if diff:
    sections.append(f"PR Diff:\n\n{diff}")
else:
    sections.append("No code changes detected.")

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
