import hashlib
import random
import json
from typing import Dict, List
import boto3

# ============================================================
#  AWS BEDROCK CLIENT
# ============================================================

bedrock = boto3.client("bedrock-runtime", region_name="us-east-2")

def call_bedrock_claude(messages, system=None, max_tokens=500, temperature=0.9):
    """Call Anthropic Claude (Sonnet) on AWS Bedrock."""
    body_params = {
        "anthropic_version": "bedrock-2023-05-31",
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature
    }
    if system:
        body_params["system"] = system
    
    response = bedrock.invoke_model(
        modelId="global.anthropic.claude-haiku-4-5-20251001-v1:0",
        #modelId="us.amazon.nova-2-lite-v1:0",
        contentType="application/json",
        accept="application/json",
        body=json.dumps(body_params)
    )

    body = json.loads(response["body"].read())
    return body["content"][0]["text"]


# ============================================================
#  SEED UTILS
# ============================================================

def make_seed(user_input: str) -> int:
    """Create deterministic integer seed from user input."""
    h = hashlib.sha256(user_input.encode("utf-8")).hexdigest()
    return int(h[:16], 16)

def make_hex_seed(user_input: str) -> str:
    """Short hex used as a prompt hint."""
    return hashlib.sha256(user_input.encode("utf-8")).hexdigest()[:8]


# ============================================================
#  LLM – GENERATE FRAGMENTS (ADJ + NOUN)
# ============================================================

def llm_generate_fragments(seed_hint: str, role_hint: str,
                           n_adjs=20, n_nouns=20) -> Dict[str, List[str]]:
    """
    Call Claude Sonnet to create fresh whimsical adjective/noun fragments.
    The model returns JSON only.
    """
    system_prompt = (
        "You generate safe, whimsical, family-friendly word fragments. "
        "Avoid political, religious, adult, or violent terms. "
        "Output JSON only."
    )
    
    messages = [
        {
            "role": "user",
            "content": f"""
SeedHint: "{seed_hint}"
RoleHint: "{role_hint}"

Return JSON:
{{
  "adjectives": [... {n_adjs} whimsical short adjectives ...],
  "nouns": [... {n_nouns} whimsical short nouns ...]
}}
Rules:
- Words must be playful, season-themed, snowy, sparkly, candy-like, cozy, etc.
- Keep entries short (1–2 syllables).
- No offensive content.
- Output valid JSON ONLY.
"""
        }
    ]

    text = call_bedrock_claude(messages, system=system_prompt)
    return json.loads(text)


# ============================================================
#  NAME ASSEMBLY USING PRNG
# ============================================================

def assemble_names_from_fragments(fragments: Dict[str, List[str]],
                                  seed_int: int,
                                  count=6,
                                  patterns=None) -> List[str]:
    if patterns is None:
        patterns = [
            "{adj} {noun}",
            "{adj}{noun}",
            "{noun} {adj}",
            "{adj} of {noun}"
        ]

    rnd = random.Random(seed_int)
    candidates = []

    for _ in range(count * 3):
        pat = rnd.choice(patterns)
        adj = rnd.choice(fragments["adjectives"])
        noun = rnd.choice(fragments["nouns"])

        # Some gentle mutation
        if rnd.random() < 0.15:
            adj += rnd.choice(["ling", "let", "-o", "bie"])
        if rnd.random() < 0.10:
            noun += rnd.choice(["kin", "ster", "bloss"])

        name = pat.format(adj=adj, noun=noun).strip()
        name = " ".join(name.split())
        candidates.append(name)

    # Deduplicate
    seen = set()
    final = []
    for c in candidates:
        if c.lower() not in seen:
            final.append(c)
            seen.add(c.lower())
        if len(final) >= count:
            break

    return final


# ============================================================
#  LLM SAFETY FILTER
# ============================================================

def llm_safety_check(name: str) -> bool:
    """
    Ask Claude to classify if the name is safe.
    Returns True/False.
    """
    system_prompt = (
        "You are a safety classifier. "
        "Return ONLY 'safe' or 'unsafe'."
    )
    
    messages = [
        {
            "role": "user",
            "content": f"""
Evaluate the string: "{name}"

Rules:
- If it contains adult content, violence, slurs, politics, or personal attacks → unsafe.
- If fully family-friendly, whimsical, and neutral → safe.

Respond ONLY with one word: safe OR unsafe.
"""
        }
    ]

    text = call_bedrock_claude(messages, system=system_prompt).strip().lower()
    return text.startswith("safe")


# ============================================================
#  MAIN PIPELINE
# ============================================================

def generate_seasonal_names(user_input: str,
                            role_hint="winter elf name",
                            count=6) -> List[str]:

    hex_seed = make_hex_seed(user_input)
    seed_int = make_seed(user_input)

    fragments = llm_generate_fragments(hex_seed, role_hint)
    candidates = assemble_names_from_fragments(fragments, seed_int, count=count)

    safe = []
    for cand in candidates:
        if llm_safety_check(cand):
            safe.append(cand)
        if len(safe) >= count:
            break

    # If we don’t get enough safe names, regenerate deterministically
    if len(safe) < count:
        more = assemble_names_from_fragments(fragments, seed_int + 999, count=count)
        for cand in more:
            if llm_safety_check(cand):
                safe.append(cand)
            if len(safe) >= count:
                break

    return safe[:count]


# ============================================================
#  DEMO
# ============================================================

if __name__ == "__main__":
    user = "Frank Combopiano"
    names = generate_seasonal_names(user, role_hint="christmas elf generator")
    print("Generated names:")
    for n in names:
        print(" •", n)