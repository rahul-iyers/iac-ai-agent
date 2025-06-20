import os
import requests
from openai import AzureOpenAI

with open("diff.txt") as f:
    diff = f.read()

# Read terraform validate output
validate_output = None
if os.path.exists("tf_validate.txt"):
    with open("tf_validate.txt") as tf:
        validate_output = tf.read().strip()

prompt = (
    "You are an expert code reviewer. Provide brief, helpful comments for the following PR diff. "
    "If there are any Terraform validation errors, summarize them and include them as a separate section at the top of your review.\n\n"
    f"Terraform Validate Output (if any):\n{validate_output}\n\n" if validate_output else ""
    f"PR Diff:\n\n{diff}"
)

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
