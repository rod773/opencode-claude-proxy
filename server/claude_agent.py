import os
from typing import List, Dict, Any, Tuple, Optional

from anthropic import Anthropic

class ClaudeAgent:
    """Thin wrapper around the Anthropic Claude client that matches the OpenAI payload format."""

    def __init__(self) -> None:
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")
        self.client = Anthropic(api_key=api_key)

    def _extract_system_prompt(self, messages: List[Dict[str, Any]]) -> Tuple[Optional[str], List[Dict[str, Any]]]:
        """Separate system messages from the OpenAI request.

        Returns a combined system prompt (or None) and the list of remaining messages
        in the format expected by the Anthropic client.
        """
        system_parts: List[str] = []
        filtered: List[Dict[str, Any]] = []
        for msg in messages:
            role = msg.get("role")
            content = msg.get("content")
            if role == "system":
                system_parts.append(content)
            else:
                filtered.append({"role": role, "content": content})
        system_prompt = "\n".join(system_parts) if system_parts else None
        return system_prompt, filtered

    def chat(self, model: str, messages: List[Dict[str, Any]], temperature: float = 0.7) -> str:
        """Send a chat request to Claude and return the assistant's reply text.

        Parameters
        ----------
        model: str
            The Claude model identifier (e.g., "claude-3-opus-20240229").
        messages: List[Dict]
            List of messages in OpenAI format (role + content).
        temperature: float, optional
            Sampling temperature.
        """
        system_prompt, claude_messages = self._extract_system_prompt(messages)

        response = self.client.messages.create(
            model=model,
            max_tokens=1024,
            temperature=temperature,
            system=system_prompt,
            messages=claude_messages,
        )
        # Anthropic returns either a plain string or a list of block dicts.
        if isinstance(response.content, str):
            return response.content
        # If it's a list of blocks, concatenate the "text" fields.
        return "".join(block.get("text", "") for block in response.content if isinstance(block, dict))
