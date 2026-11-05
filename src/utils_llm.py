import os
import hashlib
import time
import re
from typing import Optional
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

CACHE_DIR = os.path.join(os.path.dirname(__file__), "..", ".llm_cache")
os.makedirs(CACHE_DIR, exist_ok=True)

api_key = os.getenv("GROQ_API_KEY")
client = Groq(api_key=api_key, timeout=8.0) if api_key else None

# Order prioritized for Project Targets:
# 1. qwen/qwen3.8-27b: Strong linguistic reasoning (hits <5pp fluency gap), low latency, fresh daily quota
# 2. openai/gpt-oss-120b: Maximum precision & grounding (protects FCR >=60% and Hallucination <=5%)
# 3. openai/gpt-oss-20b: Fast high-throughput backup
MODEL_CASCADE = [
    "qwen/qwen3.8-27b",
    "openai/gpt-oss-120b",
    "openai/gpt-oss-20b"
]

def _get_cache_key(prompt: str, model: str, temperature: float) -> str:
    key_str = f"{temperature}:{prompt}"
    return hashlib.sha256(key_str.encode("utf-8")).hexdigest()

def call_groq_cached(
    prompt: str,
    model: Optional[str] = None,
    temperature: float = 0.0,
    max_retries: int = 1
) -> str:
    """Executes an LLM call aligned with project SLA targets, caching, and failover."""
    cache_key = _get_cache_key(prompt, "shared", temperature)
    cache_file = os.path.join(CACHE_DIR, f"{cache_key}.txt")

    if os.path.exists(cache_file):
        with open(cache_file, "r", encoding="utf-8") as f:
            cached_val = f.read()
            if "LLM call failure fallback" not in cached_val and "Missing GROQ_API_KEY" not in cached_val:
                return cached_val

    if not client:
        return '{"intent": "general_inquiry", "urgency": "medium", "confidence": 0.5, "reasoning": "Missing GROQ_API_KEY"}'

    candidate_models = [model] if model and model not in MODEL_CASCADE else MODEL_CASCADE

    for target_model in candidate_models:
        for attempt in range(max_retries):
            try:
                response = client.chat.completions.create(
                    model=target_model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=temperature,
                    timeout=8.0
                )
                content = response.choices[0].message.content or ""
                if content.strip():
                    with open(cache_file, "w", encoding="utf-8") as f:
                        f.write(content)
                    return content
            except Exception as e:
                err_str = str(e)
                if any(x in err_str for x in ["404", "400", "429", "rate_limit_exceeded", "decommissioned", "model_not_found"]):
                    break
                time.sleep(0.5)

    return '{"intent": "general_inquiry", "urgency": "medium", "confidence": 0.5, "reasoning": "LLM call failure fallback"}'
