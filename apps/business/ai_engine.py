import urllib.request
import urllib.parse
import json
import random


def verify_ai_api_key(provider: str, api_key: str, model_name: str = "") -> tuple[bool, str]:
    """
    Validates BYOK API keys against official API endpoints via lightweight HTTP ping requests.
    Returns (is_valid: bool, message: str).
    """
    if not api_key or not api_key.strip():
        return False, "API Key cannot be empty."

    key = api_key.strip()
    provider = provider.lower()

    if provider == "openai":
        url = "https://api.openai.com/v1/models"
        headers = {"Authorization": f"Bearer {key}"}
        req = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=8) as resp:
                if resp.status == 200:
                    return True, "OpenAI API Key is valid and active!"
        except Exception as e:
            return False, f"OpenAI verification failed: {str(e)}"

    elif provider == "gemini":
        url = f"https://generativelanguage.googleapis.com/v1beta/models?key={key}"
        req = urllib.request.Request(url)
        try:
            with urllib.request.urlopen(req, timeout=8) as resp:
                if resp.status == 200:
                    return True, "Google Gemini API Key is valid and active!"
        except Exception as e:
            return False, f"Gemini verification failed: {str(e)}"

    elif provider == "groq":
        url = "https://api.groq.com/openai/v1/models"
        headers = {"Authorization": f"Bearer {key}"}
        req = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=8) as resp:
                if resp.status == 200:
                    return True, "Groq API Key is valid and active!"
        except Exception as e:
            return False, f"Groq verification failed: {str(e)}"

    elif provider == "anthropic":
        url = "https://api.anthropic.com/v1/messages"
        headers = {
            "x-api-key": key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
        data = json.dumps({
            "model": "claude-3-5-haiku-20241022",
            "max_tokens": 1,
            "messages": [{"role": "user", "content": "hi"}]
        }).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=8) as resp:
                if resp.status in (200, 400):
                    return True, "Anthropic API Key is valid and active!"
        except Exception as e:
            return False, f"Anthropic verification failed: {str(e)}"

    return True, "API Key format accepted."


def _call_live_llm(provider: str, api_key: str, model_name: str, system_prompt: str, user_prompt: str) -> list[str] | None:
    """
    Executes a live LLM completion call to OpenAI, Gemini, Groq, or Anthropic using the BYOK API Key.
    Returns list of 3 review strings or None on failure.
    """
    key = api_key.strip()
    provider = provider.lower()

    if provider in ("openai", "groq"):
        url = "https://api.openai.com/v1/chat/completions" if provider == "openai" else "https://api.groq.com/openai/v1/chat/completions"
        if provider == "openai":
            model = model_name if (model_name and "gpt" in model_name) else "gpt-4o-mini"
        else:
            model = model_name if (model_name and ("llama" in model_name or "mixtral" in model_name)) else "llama-3.1-8b-instant"
        
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.8,
            "response_format": {"type": "json_object"} if provider == "openai" else None
        }
        headers = {
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json"
        }
        req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=12) as resp:
                result = json.loads(resp.read().decode("utf-8"))
                content = result["choices"][0]["message"]["content"]
                parsed = json.loads(content)
                if isinstance(parsed, dict):
                    for k, v in parsed.items():
                        if isinstance(v, list) and len(v) >= 3:
                            return [str(x) for x in v[:3]]
                elif isinstance(parsed, list) and len(parsed) >= 3:
                    return [str(x) for x in parsed[:3]]
        except Exception as e:
            print(f"[LLM Error {provider}]: {e}")
            pass

    elif provider == "gemini":
        model = model_name if (model_name and "gemini" in model_name) else "gemini-2.5-flash"
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": f"{system_prompt}\n\n{user_prompt}"}
                    ]
                }
            ],
            "generationConfig": {
                "response_mime_type": "application/json"
            }
        }
        headers = {"Content-Type": "application/json"}
        req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=12) as resp:
                result = json.loads(resp.read().decode("utf-8"))
                text = result["candidates"][0]["content"]["parts"][0]["text"]
                clean_text = text.replace("```json", "").replace("```", "").strip()
                parsed = json.loads(clean_text)
                if isinstance(parsed, list) and len(parsed) >= 3:
                    return [str(x) for x in parsed[:3]]
                elif isinstance(parsed, dict):
                    for k, v in parsed.items():
                        if isinstance(v, list) and len(v) >= 3:
                            return [str(x) for x in v[:3]]
        except Exception as e:
            print(f"[LLM Error Gemini]: {e}")
            pass

    return None


def generate_multi_review_options(business_profile, enjoyment_chips: list[str], item_used: str = "", stood_out: str = "") -> list[dict]:
    """
    Generates 3 distinct review variations based on customer inputs & Business AI Context.
    Uses BYOK Live LLM if API Key is configured, or falls back to context-grounded template generator.
    """
    ai_config = getattr(business_profile, "ai_config", None)
    
    # Try Live LLM Call if BYOK is active
    if ai_config and ai_config.is_active and ai_config.api_key:
        system_prompt = f"""You are an AI review assistant for "{business_profile.name}", a {business_profile.category} in {business_profile.location}.
Description: {business_profile.description}
What makes us unique: {business_profile.differentiator}
Facts: {business_profile.important_facts}
Brand Tone: {', '.join(business_profile.brand_tone) if business_profile.brand_tone else 'Friendly, Professional'}
Style: {business_profile.communication_style} ({business_profile.communication_length} length)

EMOJI & TONE GUIDELINES:
- Use tasteful, natural emojis (like ⭐, ✨, 🙌, ☕, 🍕, 💯) appropriate for the business category and customer sentiment.
- Keep reviews positive 5-star authentic feedback.
- Option 1 should be short & direct with 1 subtle emoji.
- Option 2 should be detailed & descriptive with 1-2 natural emojis.
- Option 3 should be warm & enthusiastic with 2-3 expressive emojis.

STRICT SAFETY RULES:
- Never invent business facts or pretend something happened when not provided.

Generate EXACTLY 3 distinct review options in JSON array format:
["Option 1 review text...", "Option 2 review text...", "Option 3 review text..."]"""

        user_prompt = f"""Customer Feedback:
- What they enjoyed: {', '.join(enjoyment_chips) if enjoyment_chips else 'great service'}
- Items/Services used: {item_used or 'N/A'}
- What stood out: {stood_out or 'N/A'}

Return ONLY a valid JSON array containing 3 review strings."""

        llm_results = _call_live_llm(ai_config.provider, ai_config.api_key, ai_config.model_name, system_prompt, user_prompt)
        if llm_results and len(llm_results) >= 3:
            return [
                {"id": 1, "title": "Option 1", "subtitle": "Short & Direct", "text": llm_results[0]},
                {"id": 2, "title": "Option 2", "subtitle": "Detailed Experience", "text": llm_results[1]},
                {"id": 3, "title": "Option 3", "subtitle": "Warm & Enthusiastic", "text": llm_results[2]}
            ]

    # Contextual Template Generator Fallback
    name = business_profile.name or "this business"
    category = (business_profile.category or "business").lower()
    location = f" in {business_profile.location}" if business_profile.location else ""
    differentiator = business_profile.differentiator or "great quality and service"

    enjoyed_str = ", ".join(enjoyment_chips) if enjoyment_chips else "great service"
    item_str = f" ({item_used})" if item_used.strip() else ""
    stood_out_str = f" What really stood out to me: {stood_out.strip()}." if stood_out.strip() else ""

    var_1 = f"Had a fantastic experience at {name}{location}! ⭐ Really enjoyed the {enjoyed_str.lower()}{item_str}. Highly recommended!"
    if stood_out.strip():
        var_1 += f" {stood_out.strip()}"

    var_2 = f"Five stars for {name}! ✨ I tried their {item_used if item_used.strip() else category} and was thoroughly impressed. What makes them unique is how {differentiator.lower()}. The {enjoyed_str.lower()} was top notch! 👌{stood_out_str}"

    var_3 = f"Extremely satisfied with {name}! 🙌 The staff and overall {enjoyed_str.lower()} exceeded my expectations. If you're looking for top quality {category}{location}, look no further! 💯 Will definitely be back."

    return [
        {"id": 1, "title": "Option 1", "subtitle": "Short & Direct", "text": var_1},
        {"id": 2, "title": "Option 2", "subtitle": "Detailed Experience", "text": var_2},
        {"id": 3, "title": "Option 3", "subtitle": "Warm & Enthusiastic", "text": var_3}
    ]


def generate_ai_review_suggestion(business_profile, user_highlights: list[str] = None, rating: int = 5) -> str:
    """
    Single suggestion generator for admin playground.
    """
    opts = generate_multi_review_options(business_profile, user_highlights or [])
    return opts[0]["text"]
