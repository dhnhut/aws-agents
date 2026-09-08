import os
from typing import Any
from collections import OrderedDict
from strands import Agent
import asyncio
from strands.agent.conversation_manager.null_conversation_manager import NullConversationManager
from strands.tools.mcp.mcp_client import MCPClient
from bedrock_agentcore.runtime import BedrockAgentCoreApp
from model.load import load_model
from mcp.client.streamable_http import streamable_http_client
from mcp_client.client import get_streamable_http_mcp_client
from tools import add_numbers, search_hotels, search_flights

from memory import ShortTermMemoryHookProvider, MemoryClient

# Provides a live web browser for the agent to use.
from browser_tool import AsyncSafeAgentCoreBrowser

REGION = "us-east-1"
MEMORY_NAME = "WandeBot"
GATEWAY_ENDPOINT = "https://wanderbot-gateway-9wroz0cv1h.gateway.bedrock-agentcore.us-east-1.amazonaws.com/mcp"

# CDK grants every runtime readwrite access to every project memory and injects its id as
# MEMORY_<NAME>_ID (see AgentCoreMemory.getEnvVarName in @aws/agentcore-cdk) — the runtime role
# is never granted bedrock-agentcore:ListMemories, so discovering the id via list_memories()
# fails with AccessDeniedException. Read the injected env var instead.
MEMORY_ID_ENV_VAR = f"MEMORY_{MEMORY_NAME.upper()}_ID"

app = BedrockAgentCoreApp()
log = app.logger

# Define a Streamable HTTP MCP Client
mcp_clients = [get_streamable_http_mcp_client()]

DEFAULT_SYSTEM_PROMPT = """You are WanderBot, the AI travel assistant for Horizon Travel.

All of your tools are provided dynamically through the AgentCore Gateway. Discover the available tools at runtime and use them to answer customer questions about bookings, travel plans, and account details.

You have access to a live web browser. Use it to look up destination information
on Wikivoyage (en.wikivoyage.org) — a free, open travel guide.

To browse, call the browser tool in this exact order:
1. init_session with session_name "travel-lookup" (session names must be
   lowercase letters, digits and hyphens only, and at least 10 characters)
2. navigate to https://en.wikivoyage.org/wiki/<DestinationName>
3. get_text with selector "#mw-content-text" to read the article body
   (get_text always requires a CSS selector)
4. close when you are finished

Summarise what you find — highlights, neighbourhoods, practical tips — and always
tell the customer the information came from Wikivoyage. Never invent place names or
attractions: if the browser did not return the detail, say you could not find it.

Guidelines:
- Rely on the tools available to you through the Gateway — do not assume capabilities that aren't exposed as tools.
- Choose the most relevant tool for each request and call it with the required parameters.
- If a request needs information across multiple tools, call them in sequence and combine the results.
- If no available tool can fulfil a request, say so clearly instead of guessing.
- Ask clarifying questions when the user's request is ambiguous or missing required details.
- Present results in a clear, concise, customer-friendly format."""


# Define a collection of tools used by the model
tools = []

_INLINE_FUNCTION_NAMES = set()

# Define a simple function tool
# tools.append(add_numbers)
tools.append(search_hotels)
tools.append(search_flights)

# One shared browser for the process, driven on its own background event loop.
# See browser_tool.py for why the stock AgentCoreBrowser cannot be used directly here.
browser = AsyncSafeAgentCoreBrowser(session_timeout=600)
tools.append(browser.browser)

client = MCPClient(
    lambda: streamable_http_client(url=GATEWAY_ENDPOINT)
)

tools.append(client)

# Add MCP client to tools if available
for mcp_client in mcp_clients:
    if mcp_client:
        tools.append(mcp_client)


def _make_conversation_manager():
    return NullConversationManager()

# Reuses one Agent per session_id so each session keeps its own in-process
# conversation history (best-effort; resets on cold start). The cache is bounded
# to 128 sessions with LRU eviction (least-recently-used is dropped and its
# history reset) so a single process serving many sessions cannot leak history
# between them or grow without limit. For durable history, attach a session manager.
def agent_factory():
    cache = OrderedDict()
    memory_client = MemoryClient(region_name=REGION)
    memory_id = os.environ.get(MEMORY_ID_ENV_VAR)
    if not memory_id:
        raise RuntimeError(
            f"{MEMORY_ID_ENV_VAR} is not set; the '{MEMORY_NAME}' memory must be declared in "
            "agentcore.json so CDK injects it (run `agentcore add memory --name "
            f"{MEMORY_NAME}` and redeploy)"
        )

    def get_or_create_agent(session_id, actor_id):
        if session_id in cache:
            cache.move_to_end(session_id)
            return cache[session_id]
        if len(cache) >= 128:
            cache.popitem(last=False)
        cache[session_id] = Agent(
            model=load_model(),
            system_prompt=DEFAULT_SYSTEM_PROMPT,
            tools=tools,
            conversation_manager=_make_conversation_manager(),
            hooks=[ShortTermMemoryHookProvider(memory_client, memory_id)],
            state={"actor_id": actor_id, "session_id": session_id},
        )
        return cache[session_id]
    return get_or_create_agent
get_or_create_agent = agent_factory()


def strip_trailing_tool_use(messages: Any) -> list[dict]:
    """Strip toolUse blocks from the tail until the last message has none."""
    if not isinstance(messages, list):
        raise ValueError("messages must be a list")

    messages = list(messages)
    while messages:
        last = messages[-1]
        if not isinstance(last, dict):
            raise ValueError("each message must be an object")
        original_content = last.get("content", [])
        if not isinstance(original_content, list) or not all(isinstance(block, dict) for block in original_content):
            raise ValueError("each message content value must be a list of content blocks")

        content = [block for block in original_content if "toolUse" not in block]
        if len(content) == len(original_content):
            break
        if content:
            messages[-1] = {**last, "content": content}
            break
        messages.pop()

    return messages


def _extract_prompt(payload: dict):
    """Accept validated harness messages, tool results, or a plain prompt string."""
    if not isinstance(payload, dict):
        raise ValueError("payload must be a JSON object")
    if "messages" in payload:
        return strip_trailing_tool_use(payload["messages"])
    if "tool_results" in payload:
        tool_results = payload["tool_results"]
        if not isinstance(tool_results, list) or not all(
            isinstance(tool_result, dict) and isinstance(tool_result.get("toolUseId"), str)
            for tool_result in tool_results
        ):
            raise ValueError("tool_results must contain objects with a toolUseId string")
        return [{"role": "user", "content": [{"toolResult": {
            "toolUseId": tr["toolUseId"],
            "status": tr.get("status", "success"),
            "content": tr.get("content", []),
        }} for tr in tool_results]}]
    prompt = payload.get("prompt", "")
    if not isinstance(prompt, str):
        raise ValueError("prompt must be a string")
    return prompt


def _has_inline_function_call(messages) -> bool:
    """Return True if messages contains an assistant toolUse for an inline function tool."""
    if not _INLINE_FUNCTION_NAMES or not isinstance(messages, list):
        return False
    for msg in messages:
        if msg.get("role") == "assistant":
            for block in msg.get("content", []):
                if isinstance(block, dict) and block.get("toolUse", {}).get("name") in _INLINE_FUNCTION_NAMES:
                    return True
    return False


def _is_inline_function_call(event: dict) -> bool:
    """Check if a contentBlockStart event is for an inline function tool."""
    if not _INLINE_FUNCTION_NAMES:
        return False
    cbs = event.get("contentBlockStart", {})
    start = cbs.get("start", {})
    tool_use = start.get("toolUse") if isinstance(start, dict) else None
    return tool_use is not None and tool_use.get("name") in _INLINE_FUNCTION_NAMES



@app.entrypoint
async def invoke(payload, context):
    log.info("Invoking Agent.....")


    session_id = getattr(context, 'session_id', 'default-session')
    actor_id = payload.get("actor_id") if isinstance(payload, dict) else None
    agent = get_or_create_agent(session_id, actor_id or session_id)

    prompt = _extract_prompt(payload)


    async for event in agent.stream_async(
        prompt,
    ):
        if not isinstance(event, dict) or "event" not in event:
            continue
        cbs = event["event"].get("contentBlockStart")
        if cbs is not None and not cbs.get("start"):
            continue
        yield event


if __name__ == "__main__":
    app.run()
