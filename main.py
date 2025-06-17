from mcp.server.fastmcp import FastMCP
from langchain_community.chat_models import AzureChatOpenAI
from langchain.schema import HumanMessage
import os

from dotenv import load_dotenv
load_dotenv()


def analyze_with_llm(terraform_code: str) -> str:
    llm = AzureChatOpenAI(
        azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version=os.getenv("AZURE_OPENAI_API_VERSION")
    )

    messages = [
        HumanMessage(content=(
            "You are an expert in Terraform infrastructure and cloud security. "
            "Analyze the following Terraform code and return a short and efficient summary of any issues, "
            "potential security risks, and optimization suggestions. These comments should be "
            "beneficial as a comment on a developer's pull request in GitHub."
            f"Terraform Code:\n\n{terraform_code}"
        ))
    ]

    response = llm.invoke(messages)
    return response.content



def detect_provider(tf_code: str) -> str:
    import hcl2, io
    try:
        parsed = hcl2.load(io.StringIO(tf_code))
        
        # First try provider block
        providers = parsed.get("provider", [])
        for p in providers:
            for name in p:
                return name  # e.g. "aws", "azurerm", "google"

        # Fallback to resource type prefix
        resources = parsed.get("resource", [])
        for block in resources:
            for resource_type in block:
                if resource_type.startswith("aws_"):
                    return "aws"
                elif resource_type.startswith("azurerm_"):
                    return "azurerm"
                elif resource_type.startswith("google_"):
                    return "google"

        return "unknown"
    except Exception:
        return "invalid"
    

# Create an MCP server
mcp = FastMCP("Terraform MCP Server")

@mcp.tool()
def extract_tf_blocks(terraform_code: str) -> list[str]:
    """
    Extract top-level block types from Terraform code.
    Determines if provided code is valid TF format.
    Example: resource, provider, variable.
    """
    import hcl2
    import io

    try:
        parsed = hcl2.load(io.StringIO(terraform_code))
        return list(parsed.keys())
    except Exception as e:
        return [f"Error parsing Terraform: {str(e)}"]


@mcp.tool()
def analyze_tf(terraform_code: str) -> str:
    provider = detect_provider(terraform_code)

    if provider == "aws":
        return analyze_aws(terraform_code)
    elif provider == "azurerm":
        return analyze_azure(terraform_code)
    elif provider == "google":
        return analyze_gcp(terraform_code)
    else:
        return f"Unsupported or unknown provider: {provider}"


@mcp.tool()
def analyze_aws(terraform_code: str) -> str:
    """
    Analyze AWS Terraform resources for best practices.
    (Stub for now)
    """
    return analyze_with_llm(terraform_code)


@mcp.tool()
def analyze_azure(terraform_code: str) -> str:
    """
    Analyze Azure Terraform resources for best practices.
    (Stub for now)
    """
    return analyze_with_llm(terraform_code)


@mcp.tool()
def analyze_gcp(terraform_code: str) -> str:
    """
    Analyze GCP Terraform resources for best practices.
    (Stub for now)
    """
    return analyze_with_llm(terraform_code)

if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(mcp.app(), host="0.0.0.0", port=port)