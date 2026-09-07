import logging

from bedrock_agentcore.memory import MemoryClient
from strands.hooks import (
    AgentInitializedEvent,
    HookProvider,
    HookRegistry,
    MessageAddedEvent,
)

logger = logging.getLogger(__name__)

# ===========================================================================
# SHORT-TERM MEMORY HOOK PROVIDER
# ===========================================================================

class ShortTermMemoryHookProvider(HookProvider):
    """
    Gives the agent short-term memory via AgentCore Memory.

    Two hooks:
      1. AgentInitializedEvent — retrieves recent turns and injects them
         into the system prompt before the first model call.
      2. MessageAddedEvent — persists each new message to AgentCore Memory
         so it's available in future invocations.
    """

    def __init__(self, memory_client: MemoryClient, memory_id: str, last_k_turns: int = 5):
        self.memory_client = memory_client
        self.memory_id = memory_id
        self.last_k_turns = last_k_turns

    def register_hooks(self, registry: HookRegistry) -> None:
        """Bind callbacks to the events we care about."""
        registry.add_callback(AgentInitializedEvent, self.on_agent_initialized)
        registry.add_callback(MessageAddedEvent, self.on_message_added)

    def on_agent_initialized(self, event: AgentInitializedEvent) -> None:
        """Load prior conversation turns and inject into the system prompt."""
        actor_id = event.agent.state.get("actor_id")
        session_id = event.agent.state.get("session_id")

        if not actor_id or not session_id:
            return

        recent_turns = self.memory_client.get_last_k_turns(
            memory_id=self.memory_id,
            actor_id=actor_id,
            session_id=session_id,
            k=self.last_k_turns,
        )

        if not recent_turns:
            logger.info("No prior turns found for session %s", session_id)
            return

        lines = []
        for turn in recent_turns:
            for message in turn:
                role = message.get("role", "unknown").capitalize()
                text = message.get("content", {}).get("text", "")
                if text:
                    lines.append(f"{role}: {text}")

        if lines:
            context = "\n".join(lines)
            event.agent.system_prompt += f"\n\nRecent conversation:\n{context}"
            logger.info(
                "Session %s: injected %d prior turns into system prompt",
                session_id, len(recent_turns),
            )

    def on_message_added(self, event: MessageAddedEvent) -> None:
        """Persist new messages to AgentCore Memory."""
        actor_id = event.agent.state.get("actor_id")
        session_id = event.agent.state.get("session_id")

        if not actor_id or not session_id:
            return

        message = event.message
        role = message.get("role", "")

        content = message.get("content", [])
        if not isinstance(content, list) or not content:
            return

        text = content[0].get("text") if isinstance(content[0], dict) else None
        if not text:
            return

        self.memory_client.create_event(
            memory_id=self.memory_id,
            actor_id=actor_id,
            session_id=session_id,
            messages=[(text, role.upper())],
        )
        logger.info("Session %s: persisted %s message", session_id, role)

