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


NEGATIVE_KEYWORDS = {
    "bad", "terrible", "horrible", "worst", "dirty", "rude", "poor", "disappointed",
    "disappointment", "avoid", "disgusting", "never again", "waste of money", "slow",
    "cold", "stale", "awful", "unfriendly", "overpriced", "scam", "unprofessional",
    "nasty", "smelly", "uncomfortable", "hate", "pathetic", "cheated", "fraud"
}

NEGATIVE_PHRASES = [
    "not good", "not great", "not happy", "never coming back", "don't recommend",
    "dont recommend", "waste of time", "waste of money", "stay away", "not worth"
]

FILLER_WORDS = {"bad", "okay", "none", "n/a", "na", "no", "nothing", "nil", "good", "fine", "test", "worst", "ok"}


def is_negative_sentiment(*text_inputs: str) -> bool:
    """
    Scans customer input text to check if it contains negative feedback or complaint intent.
    """
    full_text = " ".join([str(t).lower() for t in text_inputs if t])
    if not full_text.strip():
        return False

    cleaned = "".join([c if c.isalnum() or c.isspace() else " " for c in full_text])
    words = set(cleaned.split())

    if words.intersection(NEGATIVE_KEYWORDS):
        return True

    for phrase in NEGATIVE_PHRASES:
        if phrase in cleaned:
            return True

    return False


def sanitize_input_text(text: str) -> str:
    """
    Sanitizes filler words or non-noun adjectives ("bad", "none", "n/a") to prevent awkward grammar interpolation.
    """
    if not text:
        return ""
    cleaned = text.strip()
    if cleaned.lower() in FILLER_WORDS:
        return ""
    return cleaned


def generate_multi_review_options(business_profile, enjoyment_chips: list[str], item_used: str = "", stood_out: str = "") -> list[dict]:
    """
    Generates 3 distinct review variations based on customer inputs & Business AI Context.
    Uses BYOK Live LLM if API Key is configured, or falls back to context-grounded template generator.
    Includes negative feedback detection & input sanitization.
    """
    # Sanitize customer inputs
    clean_item = sanitize_input_text(item_used)
    clean_stood = sanitize_input_text(stood_out)

    # Check for negative feedback
    if is_negative_sentiment(item_used, stood_out):
        return [{
            "id": 1,
            "is_negative": True,
            "title": "Private Feedback",
            "subtitle": "Sent to Owner",
            "text": "Negative feedback detected."
        }]

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

STRICT SAFETY & QUALITY RULES:
- Never invent fake facts.
- Ensure 100% natural, grammatically fluent English without awkward word interpolations.

Generate EXACTLY 3 distinct review options in JSON array format:
["Option 1 review text...", "Option 2 review text...", "Option 3 review text..."]"""

        user_prompt = f"""Customer Feedback:
- What they enjoyed: {', '.join(enjoyment_chips) if enjoyment_chips else 'great service'}
- Items/Services used: {clean_item or 'N/A'}
- What stood out: {clean_stood or 'N/A'}

Return ONLY a valid JSON array containing 3 review strings."""

        llm_results = _call_live_llm(ai_config.provider, ai_config.decrypted_api_key, ai_config.model_name, system_prompt, user_prompt)
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
    enjoyed_str = ", ".join(enjoyment_chips) if enjoyment_chips else "great service"

    # Clean differentiator formatting
    diff_text = business_profile.differentiator.strip() if business_profile.differentiator else ""
    if diff_text:
        diff_phrase = f" Their emphasis on {diff_text.lower().rstrip('.')} really stands out."
    else:
        diff_phrase = ""

    # Option 1: Short & Direct
    item_bracket = f" ({clean_item})" if clean_item else ""
    var_1 = f"Had a fantastic experience at {name}{location}! ⭐ Really enjoyed the {enjoyed_str.lower()}{item_bracket}. Highly recommended!"
    if clean_stood:
        var_1 += f" {clean_stood}."

    # Option 2: Detailed Experience
    if clean_item:
        var_2 = f"Five stars for {name}! ✨ I tried {clean_item} and was thoroughly impressed with the quality. The {enjoyed_str.lower()} was top notch! 👌{diff_phrase}{' What stood out: ' + clean_stood + '.' if clean_stood else ''}"
    else:
        var_2 = f"Five stars for {name}! ✨ Visiting {name}{location} was a wonderful experience. The {enjoyed_str.lower()} was top notch! 👌{diff_phrase}{' What stood out: ' + clean_stood + '.' if clean_stood else ''}"

    # Option 3: Warm & Enthusiastic
    var_3 = f"Extremely satisfied with {name}! 🙌 The overall {enjoyed_str.lower()} exceeded my expectations. If you're looking for top quality {category}{location}, look no further! 💯 Will definitely be back."
    if clean_stood:
        var_3 += f" {clean_stood}."

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
