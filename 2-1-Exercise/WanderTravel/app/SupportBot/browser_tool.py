"""AgentCore browser wired for an async ASGI server.

The upstream Strands browser tool bridges its sync @tool body to async Playwright
via ``nest_asyncio.apply()`` (strands_tools/browser/browser.py:948-954). That call
globally swaps ``asyncio.Task``/``asyncio.Future`` for their pure-Python versions
(nest_asyncio.py:47-50), which makes ``asyncio.current_task()`` return None for the
C-level tasks anyio/starlette already created. Every later streaming response then
dies in anyio's task group with "cannot create weak reference to 'NoneType'", so the
first browser call would brick the runtime process for all subsequent invocations.

Running the coroutines on a dedicated background loop avoids nest_asyncio entirely
and keeps every Playwright object bound to one stable loop.
"""

import asyncio
import threading

from strands_tools.browser import AgentCoreBrowser


class AsyncSafeAgentCoreBrowser(AgentCoreBrowser):
    """AgentCoreBrowser that never patches the ambient asyncio module."""

    # Playwright calls can be slow (cold browser session + page load).
    CALL_TIMEOUT_SECONDS = 300

    def __init__(self, *args, **kwargs):
        try:
            previous_loop = asyncio.get_event_loop_policy().get_event_loop()
        except RuntimeError:
            previous_loop = None

        super().__init__(*args, **kwargs)

        # Base __init__ points this thread at its private loop; we drive that loop
        # from our own thread instead, so hand the current thread back what it had.
        asyncio.set_event_loop(previous_loop)

        self._loop_thread = threading.Thread(
            target=self._loop.run_forever,
            name="agentcore-browser-loop",
            daemon=True,
        )
        self._loop_thread.start()

    def _execute_async(self, action_coro):
        """Run the coroutine on the dedicated loop rather than nesting one here."""
        future = asyncio.run_coroutine_threadsafe(action_coro, self._loop)
        return future.result(timeout=self.CALL_TIMEOUT_SECONDS)
