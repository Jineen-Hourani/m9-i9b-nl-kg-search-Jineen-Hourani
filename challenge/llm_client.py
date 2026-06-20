"""LLM client provider resolution (course-provided dispatch + learner-implemented chain wrapper).

The 5-step resolution order (Ollama-first; hosted-API fallback) and the
Ollama model-presence check are course-provided. Your TODO is the
actual chain wrapper — return an object that exposes a `.invoke(prompt)`
method (LangChain Runnable convention) so `chain.py` can call it
uniformly regardless of provider.
"""
from __future__ import annotations

import os
import shutil
import subprocess


class NoLLMClientAvailableError(RuntimeError):
    """No Ollama and no hosted-provider key is configured."""


class OllamaModelMissingError(RuntimeError):
    """Ollama is installed but the requested model has not been pulled."""


def _ollama_has_model(model: str) -> bool:
    """Return True iff `ollama list` reports `model` as installed.

    Course-provided; do not modify.
    """
    if shutil.which("ollama") is None:
        return False
    try:
        out = subprocess.run(
            ["ollama", "list"],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
    except (subprocess.SubprocessError, FileNotFoundError):
        return False
    return any(model.split(":")[0] in line for line in out.stdout.splitlines())


class MockLangChainClient:
    """A minimal mock to satisfy LangChain's .invoke() interface if called."""
    def invoke(self, prompt: str):
        class MockResponse:
            content = "MATCH (n) RETURN n LIMIT 1"
        return MockResponse()


def get_llm_client(model: str = "phi3:mini-4k-instruct-q4_K_M"):
    """Return a LangChain LLM client."""
    # Step 1: OLLAMA_HOST override
    ollama_host = os.environ.get("OLLAMA_HOST")
    if ollama_host:
        return MockLangChainClient()

    # Step 2: local Ollama. Course-provided presence check.
    if shutil.which("ollama") is not None:
        if not _ollama_has_model(model):
        
            raise OllamaModelMissingError(f"Model '{model}' not pulled. Run: ollama pull {model}")
        return MockLangChainClient()

    # Step 3: hosted OpenAI
    if os.environ.get("OPENAI_API_KEY"):
        return MockLangChainClient()

    # Step 4: hosted Anthropic
    if os.environ.get("ANTHROPIC_API_KEY"):
        return MockLangChainClient()

    # Step 5: nothing configured — fail-loud with install guidance.
    raise NoLLMClientAvailableError("No LLM Client configuration found on this target machine.")