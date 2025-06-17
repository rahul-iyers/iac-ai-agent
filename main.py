# server.py
from mcp.server.fastmcp import FastMCP

# Create an MCP server
mcp = FastMCP("Demo")


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
    return "Analyzed AWS resources."


@mcp.tool()
def analyze_azure(terraform_code: str) -> str:
    """
    Analyze Azure Terraform resources for best practices.
    (Stub for now)
    """
    return "Analyzed Azure resources."


@mcp.tool()
def analyze_gcp(terraform_code: str) -> str:
    """
    Analyze GCP Terraform resources for best practices.
    (Stub for now)
    """
    return "Analyzed GCP resources."


# Add a dynamic greeting resource
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    return f"Hello, {name}!"

if __name__ == "__main__":
    print("Starting MCP Server")
    mcp.run()