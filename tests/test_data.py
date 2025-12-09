"""
Test data and utilities for elf name generator testing.

This module contains blocklists for safety validation, Christmas vocabulary,
and fallback safe names used in testing and validation.
"""

# Blocklists for safety validation (Requirements 2.1, 2.2, 2.3, 2.4)

POLITICAL_TERMS = [
    "trump", "biden", "democrat", "republican", "liberal", "conservative",
    "congress", "senate", "president", "election", "vote", "campaign",
    "politician", "politics", "government", "capitol", "white house",
    "maga", "antifa", "socialist", "communist", "fascist", "nazi",
    "left-wing", "right-wing", "partisan", "impeach", "brexit"
]

RELIGIOUS_TERMS = [
    "jesus", "christ", "god", "lord", "allah", "buddha", "krishna",
    "prophet", "messiah", "savior", "holy", "sacred", "divine",
    "church", "mosque", "temple", "synagogue", "cathedral",
    "bible", "quran", "torah", "scripture", "gospel",
    "prayer", "worship", "blessed", "saint", "angel", "demon",
    "heaven", "hell", "sin", "salvation", "baptism", "communion"
]

BODY_PART_TERMS = [
    "butt", "buttocks", "boob", "breast", "chest", "nipple",
    "groin", "crotch", "genitals", "penis", "vagina", "testicle",
    "anus", "rectum", "bladder", "prostate", "uterus",
    "sexy", "hot", "naked", "nude", "bare"
]

SUGGESTIVE_TERMS = [
    "sexy", "seductive", "sensual", "erotic", "kinky", "naughty",
    "dirty", "nasty", "horny", "aroused", "intimate", "provocative",
    "flirty", "sultry", "steamy", "passionate", "lusty",
    "strip", "tease", "seduce", "fondle", "caress"
]

# Combine all blocklists for easy checking
ALL_BLOCKED_TERMS = (
    POLITICAL_TERMS + 
    RELIGIOUS_TERMS + 
    BODY_PART_TERMS + 
    SUGGESTIVE_TERMS
)

# Christmas vocabulary list (Requirement 3.2)

CHRISTMAS_VOCABULARY = {
    "snow": [
        "snow", "snowflake", "snowball", "snowman", "snowy", "frost",
        "frosty", "icicle", "ice", "frozen", "blizzard", "flurry"
    ],
    "light": [
        "sparkle", "twinkle", "glitter", "shimmer", "glow", "gleam",
        "shine", "bright", "radiant", "luminous", "starlight", "moonlight"
    ],
    "candy": [
        "candy", "peppermint", "gingerbread", "cookie", "sweet", "sugar",
        "chocolate", "caramel", "marshmallow", "gumdrop", "lollipop", "treat"
    ],
    "sparkle": [
        "sparkle", "glitter", "tinsel", "ornament", "bauble", "decoration",
        "festive", "merry", "jolly", "cheerful", "bright", "shiny"
    ],
    "animals": [
        "reindeer", "deer", "fox", "rabbit", "bunny", "squirrel",
        "owl", "cardinal", "dove", "robin", "bear", "penguin"
    ],
    "warmth": [
        "cozy", "warm", "toasty", "snug", "comfort", "hearth",
        "fireplace", "cocoa", "cider", "blanket", "mittens", "scarf"
    ],
    "winter": [
        "winter", "december", "solstice", "evergreen", "pine", "holly",
        "mistletoe", "wreath", "garland", "bell", "sleigh", "sled"
    ],
    "christmas_specific": [
        "christmas", "xmas", "noel", "yuletide", "festive", "holiday",
        "santa", "claus", "elf", "elves", "workshop", "north pole",
        "gift", "present", "stocking", "chimney", "tree", "star",
        "angel", "joy", "peace", "hope", "wonder", "magic"
    ]
}

# Flatten Christmas vocabulary for easy checking
ALL_CHRISTMAS_WORDS = []
for category_words in CHRISTMAS_VOCABULARY.values():
    ALL_CHRISTMAS_WORDS.extend(category_words)

# Fallback safe names list (Requirement 2.6)

FALLBACK_SAFE_NAMES = [
    "Sparkle Snowflake",
    "Twinkle Toes",
    "Jingle Bell",
    "Candy Cane",
    "Frosty Mittens",
    "Merry Snowball",
    "Jolly Gingerbread",
    "Cozy Cocoa",
    "Starlight Shimmer",
    "Peppermint Twist",
    "Snowy Whiskers",
    "Tinsel Twirl",
    "Cookie Crumble",
    "Glitter Glow",
    "Holly Berry",
    "Icicle Sparkle",
    "Moonbeam Magic",
    "Nutmeg Sprinkle",
    "Pine Needle",
    "Ribbon Dancer",
    "Sleigh Bell",
    "Sugar Plum",
    "Velvet Bow",
    "Winter Wonder",
    "Yuletide Joy"
]


def is_safe_name(name: str) -> bool:
    """
    Check if a name is safe (doesn't contain blocked terms).
    
    Args:
        name: The name to check
        
    Returns:
        True if the name is safe, False otherwise
    """
    name_lower = name.lower()
    for term in ALL_BLOCKED_TERMS:
        if term in name_lower:
            return False
    return True


def contains_christmas_theme(name: str) -> bool:
    """
    Check if a name contains Christmas-themed vocabulary.
    
    Args:
        name: The name to check
        
    Returns:
        True if the name contains at least one Christmas word, False otherwise
    """
    name_lower = name.lower()
    for word in ALL_CHRISTMAS_WORDS:
        if word in name_lower:
            return True
    return False


def get_random_fallback_name() -> str:
    """
    Get a random fallback safe name.
    
    Returns:
        A random name from the fallback list
    """
    import random
    return random.choice(FALLBACK_SAFE_NAMES)
