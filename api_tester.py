import requests
import json
from typing_extensions import Annotated
from agents import function_tool
from pydantic import Field


@function_tool
def api_request(
    url: Annotated[str, Field(description="API endpoint URL", json_schema_extra={"type": "string"})],
    method: Annotated[str, Field(description="HTTP method (GET, POST, PUT, DELETE)", json_schema_extra={"type": "string"})] = "GET",
    headers: Annotated[str, Field(description="Headers as JSON string", json_schema_extra={"type": "string"})] = "{}",
    params: Annotated[str, Field(description="Query parameters as JSON string", json_schema_extra={"type": "string"})] = "{}",
    body: Annotated[str, Field(description="Request body as JSON string", json_schema_extra={"type": "string"})] = "{}",
    timeout: Annotated[int, Field(description="Timeout in seconds", json_schema_extra={"type": "integer"})] = 10,
) -> str:
    """
    Send an HTTP request to an API endpoint and return the formatted response.
    """
    try:
        # Parse JSON strings into dicts
        headers_dict = json.loads(headers) if headers else None
        params_dict = json.loads(params) if params else None
        body_dict = json.loads(body) if body else None

        response = requests.request(
            method=method.upper(),
            url=url,
            headers=headers_dict,
            params=params_dict,
            json=body_dict,
            timeout=timeout
        )
        response.raise_for_status()

        # Try pretty JSON
        try:
            return json.dumps(response.json(), indent=2)
        except ValueError:
            return response.text

    except Exception as e:
        return f"❌ Error making request: {e}"
