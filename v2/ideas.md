# Festive Christmas Holiday Elf Name Generator

## Context

You generate light-hearted, family-friendly Christmas holiday themed names that may represent names of Santa's elves.

Each name must be whimsical, non-offensive, and appropriate for all ages. 

Never reference political topics, religion, body parts, or anything suggestive.

Use playful imagery like snow, light, candy, sparkle, animals, warmth, winter mischief, etc.

Produce short, fun two or three-word names.

Do not repeat names across requests unless given the same seed.

Some examples:

- Figgy IceEyes
- Jingle SnowTree
- Figgy MerryMan
- Molly SugarFlakes
- Sugarplum Toe-Bells
- Lucky TinselFlakes
- Dancer CocoaDoodle 

## Operation

### User Interaction

A user (i.e., a child) will type their first name, then select (i.e., click) on their birth month.

Input example:

- Name: Timmy
- Month: April

After processing, you  will display a single generated elf name

### Processing

You are to use a large language model to produce the elf name

To avoid static lists, create a seed from the user input and feed it into the prompt

Example:
- User imput: "Timmy", "April"
- Hash it

```bash
SEED=$(printf "%s%s" "Timmy" "April" | sha256sum | head -c 8)
echo $SEED
```

- use this seed to guide randomness, and generate a whimsical Santa's elf name.
- The LLM will use the seed to create a reproducible style without using a static table

Pattern Guidance:

- Provide the LLM a structure, but let it fill it with new words every time
- Prompt pattern examples:
  - Adjective + Winter Object
  - Playful Verb + Cozy Noun
  - Silly Character Name with Seasonal Flair
- Use new, invented words sparingly (e.g., "Frostwhim", "JingleTuft"), but keep them readable and cute

Safety Classification Filters:

Before returning the name, run it through an LLM filter:

Filter prompt

```text
Evaluate the string below. Confirm it is safe, non-offensive, family-friendly, and free of any adult, political, or sensitive content.

If unsafe, regenerate a corrected version.
```

Add "soft semantic embeddings" for variation:

Encourage variation by embedding the user input and using the vectors values as hints.

Example:

- Convert the name + month to an embedding vector
- Take the first few values (e.g., [0.92, -0.15, 0.33])
- Convert those numbers into semantic instructions:
  - Positive value = "use a cheerful adjective"
  - Negative value = "use a cozy/natural noun"
  - Medium value = "add a playful twist word"

In other words, embed the "feel" of the name without being deterministic


### Example Pipeline

Input: "Timmy", "April"

Pipeline:

1. Hash the name + month to produce the seed
2. Embed it to create variation cues
3. Generate with LLM using constraints
4. Validate through safety filters

Possible output:

- “Twinkleberry Froststride”
- “Holly Jumblebright”
- “Peppermint Whimdart”

Each of the above is:

- unique
- PG-rated
- Thematically coherent
- Not from a static list

## Technology

Implement the application with the following tech stack

- Python version > 3.8
- Streamlit application framework
- Large language models
  - Amazon Nova 2 lite - name generation
  - Amazon Titan v2 - text embeddings


