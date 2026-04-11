import os
import time
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# LLM Configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

# Model settings
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "groq")  # "groq" or "google"
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
GOOGLE_MODEL = os.getenv("GOOGLE_MODEL", "gemini-2.0-flash")

# Embedding settings
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# ChromaDB settings
CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
HR_COLLECTION_NAME = "hr_docs"
QA_COLLECTION_NAME = "qa_docs"

# Chunking settings
CHUNK_SIZE = 600
CHUNK_OVERLAP = 100
CHUNK_SEPARATORS = ["\n## ", "\n### ", "\n- ", "\n\n", "\n", " "]

# Data directories
HR_DATA_DIR = "data/hr"
QA_DATA_DIR = "data/qa"

# Retrieval settings
RETRIEVAL_TOP_K = 4
SIMILARITY_THRESHOLD = 0.3


# ── Waterfall LLM Model Chain ────────────────────────────────────────
# Ordered list of models to try. On rate limit / quota errors the system
# automatically falls through to the next model in the chain.

GEMINI_MODELS = [
    "gemini-2.0-flash",
    "gemini-2.0-flash-lite",
]

GROQ_MODELS = [
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
    "meta-llama/llama-4-scout-17b-16e-instruct",
    "qwen/qwen3-32b",
]

# Track which provider is currently active (can switch at runtime)
_active_provider = LLM_PROVIDER
_active_model = GOOGLE_MODEL if LLM_PROVIDER == "google" else GROQ_MODEL
_failed_models: dict[str, float] = {}  # model_key -> timestamp of failure
_FAIL_COOLDOWN = 60  # seconds before retrying a failed model


def _is_skippable_error(error: Exception) -> bool:
    """Detect errors that should trigger fallback to the next model.

    Covers rate limits, quota exhaustion, and model unavailability (404).
    """
    err_str = str(error).lower()
    skip_keywords = [
        "rate limit", "rate_limit", "429", "quota", "resource exhausted",
        "resourceexhausted", "too many requests", "tokens per min",
        "requests per min", "rpm", "tpm", "overloaded",
        "not_found", "not found", "404", "is not found",
        "model not found", "does not exist", "decommissioned",
        "connection error", "apiconnectionerror", "timeout", "502", "503", "504"
    ]
    return any(kw in err_str for kw in skip_keywords)


def _create_gemini_llm(model: str):
    """Create a Google Gemini LLM instance with minimal internal retries.

    The underlying google-genai SDK uses tenacity for retries (ignoring
    LangChain's max_retries). We patch the client after creation to
    limit retries so rate limit errors surface quickly to the waterfall.
    """
    from langchain_google_genai import ChatGoogleGenerativeAI
    llm = ChatGoogleGenerativeAI(
        model=model,
        google_api_key=GOOGLE_API_KEY,
        temperature=0,
        max_retries=0,
    )
    # Patch the underlying google-genai client to stop after 1 attempt
    # instead of the default 5 retries with exponential backoff
    try:
        if hasattr(llm, 'client') and hasattr(llm.client, '_api_client'):
            api_client = llm.client._api_client
            if hasattr(api_client, '_request'):
                import functools
                original_request = api_client._request
                @functools.wraps(original_request)
                def _no_retry_request(http_request, http_options=None, stream=False):
                    return api_client._request_once(http_request, stream)
                api_client._request = _no_retry_request
    except Exception:
        pass  # If patching fails, fall back to default behavior
    return llm


def _create_groq_llm(model: str):
    """Create a Groq LLM instance."""
    from langchain_groq import ChatGroq
    return ChatGroq(
        model=model,
        api_key=GROQ_API_KEY,
        temperature=0,
    )


def get_llm_with_fallback():
    """Get an LLM instance with waterfall fallback across providers.

    Fallback chain (if LLM_PROVIDER=google):
      gemini-2.0-flash → gemini-1.5-flash → gemini-1.5-pro
        → llama-3.3-70b → llama-3.1-8b

    Fallback chain (if LLM_PROVIDER=groq):
      llama-3.3-70b → llama-3.1-8b
        → gemini-2.0-flash → gemini-1.5-flash → gemini-1.5-pro

    Returns a wrapper that auto-retries on rate limit errors.
    """
    global _active_provider, _active_model

    # Build ordered model chain based on configured primary provider
    if LLM_PROVIDER == "google":
        model_chain = (
            [("google", m) for m in GEMINI_MODELS]
            + [("groq", m) for m in GROQ_MODELS]
        )
    else:
        model_chain = (
            [("groq", m) for m in GROQ_MODELS]
            + [("google", m) for m in GEMINI_MODELS]
        )

    # Expire old failures so models get retried after cooldown
    now = time.time()
    expired = [k for k, t in _failed_models.items() if now - t > _FAIL_COOLDOWN]
    for k in expired:
        del _failed_models[k]

    # Skip recently-failed models, but keep them at the end as last resort
    available = [m for m in model_chain if f"{m[0]}:{m[1]}" not in _failed_models]
    failed = [m for m in model_chain if f"{m[0]}:{m[1]}" in _failed_models]
    ordered = available + failed

    return _WaterfallLLM(ordered)


class _WaterfallLLM:
    """LLM wrapper that cascades through models on rate limit errors.

    Behaves like a LangChain LLM — exposes .invoke() and .content on response.
    On rate limit error, marks the model as failed and retries with the next
    model in the waterfall chain.
    """

    def __init__(self, model_chain: list[tuple[str, str]]):
        self.model_chain = model_chain
        self._current_llm = None
        self._current_key = None
        self._init_first()

    def _init_first(self):
        """Initialize with the first available model."""
        if self.model_chain:
            provider, model = self.model_chain[0]
            self._current_llm = self._create(provider, model)
            self._current_key = f"{provider}:{model}"
            logger.info(f"[Waterfall LLM] Initialized with {self._current_key}")

    def _create(self, provider: str, model: str):
        if provider == "google" and GOOGLE_API_KEY:
            return _create_gemini_llm(model)
        elif provider == "groq" and GROQ_API_KEY:
            return _create_groq_llm(model)
        return None

    def invoke(self, input_data, **kwargs):
        """Invoke the LLM with automatic fallback on rate limit errors."""
        global _active_provider, _active_model

        last_error = None

        for provider, model in self.model_chain:
            key = f"{provider}:{model}"

            # Skip models without API keys
            if provider == "google" and not GOOGLE_API_KEY:
                continue
            if provider == "groq" and not GROQ_API_KEY:
                continue

            try:
                llm = self._create(provider, model)
                if llm is None:
                    continue

                response = llm.invoke(input_data, **kwargs)

                # Success — update active state
                if key != self._current_key:
                    logger.info(f"[Waterfall LLM] Switched to {key}")
                    _active_provider = provider
                    _active_model = model
                    self._current_llm = llm
                    self._current_key = key

                return response

            except Exception as e:
                if _is_skippable_error(e):
                    _failed_models[key] = time.time()
                    logger.warning(
                        f"[Waterfall LLM] {key} failed: {str(e)[:120]}. "
                        f"Falling back to next model..."
                    )
                    last_error = e
                    # Brief pause before trying next model to avoid
                    # burning through rate limits on all models instantly
                    time.sleep(1)
                    continue
                else:
                    # Non-rate-limit error — don't swallow it
                    raise

        # All models exhausted
        raise RuntimeError(
            f"All LLM models are rate limited. Last error: {last_error}. "
            f"Tried: {[f'{p}:{m}' for p, m in self.model_chain]}"
        )

    def __repr__(self):
        return f"WaterfallLLM(active={self._current_key}, chain_size={len(self.model_chain)})"
