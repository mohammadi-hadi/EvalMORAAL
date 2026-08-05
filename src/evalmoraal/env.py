"""
Environment helper for API keys and provider availability.

Keys are read from environment variables, optionally topped up from a
local ``.env`` file (simple KEY=VALUE lines). Environment variables that
are already set always win over the ``.env`` file.

Supported providers and their variables:

- ``openai``    -> ``OPENAI_API_KEY``
- ``anthropic`` -> ``ANTHROPIC_API_KEY``
- ``google``    -> ``GOOGLE_API_KEY``
"""

import logging
import os
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

ENV_VARS = {
    "openai": "OPENAI_API_KEY",
    "anthropic": "ANTHROPIC_API_KEY",
    "google": "GOOGLE_API_KEY",
}

# Fallback models used when no explicit model list is given.
DEFAULT_API_MODELS = {
    "openai": ["gpt-4o-mini"],
    "anthropic": ["claude-3-5-haiku-latest"],
    "google": ["gemini-1.5-flash"],
}


class EnvLoader:
    """Loads API keys from the environment and an optional .env file."""

    def __init__(self, env_file: Optional[Path] = None):
        """
        Args:
            env_file: Path to a .env file (default: ./.env if present)
        """
        self.env_file = Path(env_file) if env_file else Path(".env")
        self._file_values: Dict[str, str] = {}
        if self.env_file.exists():
            self._file_values = self._parse_env_file(self.env_file)
            logger.info(f"Loaded {len(self._file_values)} entries from {self.env_file}")

    @staticmethod
    def _parse_env_file(path: Path) -> Dict[str, str]:
        values = {}
        for line in path.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            values[key.strip()] = value.strip().strip("'\"")
        return values

    def get_api_key(self, provider: str) -> Optional[str]:
        """Return the API key for a provider ('openai', 'anthropic', 'google')."""
        var = ENV_VARS.get(provider.lower())
        if var is None:
            return None
        return os.environ.get(var) or self._file_values.get(var) or None

    def has_key(self, provider: str) -> bool:
        return bool(self.get_api_key(provider))

    def get_api_keys(self) -> Dict[str, str]:
        """Return all configured keys as {provider: key}."""
        keys = {}
        for provider in ENV_VARS:
            key = self.get_api_key(provider)
            if key:
                keys[provider] = key
        return keys

    def get_environment_info(self) -> Dict:
        """Summarize which providers are configured."""
        info: Dict[str, object] = {f"has_{provider}": self.has_key(provider) for provider in ENV_VARS}
        info["configured_providers"] = [p for p in ENV_VARS if self.has_key(p)]
        return info

    def get_available_models(self) -> Dict[str, List[str]]:
        """Return default model names for every provider with a configured key.

        Returns:
            {'api': [model, ...]} listing usable API models
        """
        models = []
        for provider, defaults in DEFAULT_API_MODELS.items():
            if self.has_key(provider):
                models.extend(defaults)
        return {"api": models}


_loader: Optional[EnvLoader] = None


def get_env_loader(env_file: Optional[Path] = None) -> EnvLoader:
    """Return a shared EnvLoader instance."""
    global _loader
    if _loader is None or env_file is not None:
        _loader = EnvLoader(env_file=env_file)
    return _loader
