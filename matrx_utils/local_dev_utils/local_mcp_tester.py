import json
import requests
from matrx_utils import vcprint, clear_terminal

HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json, text/event-stream",
}


def parse_mcp_response(resp):
    """MCP servers can reply with plain JSON or SSE. Handle both."""
    text = resp.text
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        for line in text.splitlines():
            if line.startswith("data: "):
                try:
                    data = json.loads(line[6:])
                    break
                except json.JSONDecodeError:
                    continue
        else:
            return {"_raw": text}

    # Unwrap MCP text content — if result.content is a list of text items
    # whose text field is itself a JSON string, parse it out.
    try:
        content = data["result"]["content"]
        if isinstance(content, list) and len(content) == 1 and content[0].get("type") == "text":
            inner = content[0]["text"]
            try:
                data["result"]["content"] = json.loads(inner)
            except (json.JSONDecodeError, TypeError):
                pass
    except (KeyError, TypeError):
        pass

    return data


def _init_session(base: str) -> dict:
    """Initialize an MCP session and return session-scoped headers."""
    init = requests.post(base, headers=HEADERS, json={
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "py-client", "version": "1.0"},
        },
    })
    init.raise_for_status()
    sid = init.headers.get("mcp-session-id")
    if not sid:
        raise RuntimeError("Server did not return mcp-session-id")

    session_headers = {**HEADERS, "mcp-session-id": sid}

    # notifications/initialized — fire-and-forget, no id
    requests.post(base, headers=session_headers, json={
        "jsonrpc": "2.0",
        "method": "notifications/initialized",
    })

    return session_headers


def list_tools(base: str) -> list[dict]:
    """Return the server's tool catalogue (name, description, inputSchema)."""
    session_headers = _init_session(base)
    resp = requests.post(base, headers=session_headers, json={
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/list",
        "params": {},
    })
    resp.raise_for_status()
    data = parse_mcp_response(resp)
    return data.get("result", {}).get("tools", [])


def list_resources(base: str) -> list[dict]:
    """Return the server's resource catalogue (uri, name, mimeType, etc.)."""
    session_headers = _init_session(base)
    resp = requests.post(base, headers=session_headers, json={
        "jsonrpc": "2.0",
        "id": 2,
        "method": "resources/list",
        "params": {},
    })
    resp.raise_for_status()
    data = parse_mcp_response(resp)
    return data.get("result", {}).get("resources", [])


def read_resource(base: str, uri: str) -> dict:
    """Read a specific resource by URI."""
    session_headers = _init_session(base)
    resp = requests.post(base, headers=session_headers, json={
        "jsonrpc": "2.0",
        "id": 2,
        "method": "resources/read",
        "params": {"uri": uri},
    })
    resp.raise_for_status()
    return parse_mcp_response(resp)


def list_prompts(base: str) -> list[dict]:
    """Return the server's prompt template catalogue."""
    session_headers = _init_session(base)
    resp = requests.post(base, headers=session_headers, json={
        "jsonrpc": "2.0",
        "id": 2,
        "method": "prompts/list",
        "params": {},
    })
    resp.raise_for_status()
    data = parse_mcp_response(resp)
    return data.get("result", {}).get("prompts", [])


def get_prompt(base: str, name: str, arguments: dict | None = None) -> dict:
    """Render a prompt template by name with optional arguments."""
    session_headers = _init_session(base)
    resp = requests.post(base, headers=session_headers, json={
        "jsonrpc": "2.0",
        "id": 2,
        "method": "prompts/get",
        "params": {"name": name, "arguments": arguments or {}},
    })
    resp.raise_for_status()
    return parse_mcp_response(resp)


def call_mcp_tool(base: str, tool_name: str, arguments: dict) -> dict:
    session_headers = _init_session(base)
    resp = requests.post(base, headers=session_headers, json={
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/call",
        "params": {"name": tool_name, "arguments": arguments},
    })
    resp.raise_for_status()
    return parse_mcp_response(resp)


if __name__ == "__main__":
    clear_terminal()

    BASE = "https://seo-mcp.matrxserver.com/mcp"
    title = "Your title here"

    # Uncomment the one call you want to run:

    result = list_tools(BASE)

    # result = list_resources(BASE)

    # result = read_resource(BASE, uri="some://resource/uri")

    # result = list_prompts(BASE)

    # result = get_prompt(BASE, name="some-prompt", arguments={"key": "value"})

    # result = call_mcp_tool(BASE, tool_name="check_meta_title", arguments={"title": title})

    vcprint(result, "[MCP TESTER] Result", color="cyan")