# Seasonal Name Generator

A deterministic, AI-powered name generator that creates whimsical, family-friendly seasonal names using AWS Bedrock and Amazon Nova.

## Design

### Architecture

The system uses a hybrid approach combining LLM creativity with deterministic PRNG assembly:

1. **LLM Fragment Generation**: Amazon Nova generates creative word fragments (adjectives and nouns)
2. **Deterministic Assembly**: SHA-256 seeded PRNG combines fragments into names
3. **Safety Filtering**: LLM validates each name for family-friendly content

### Key Features

- **Deterministic**: Same input always produces same names
- **Safe**: Built-in content filtering for family-friendly output
- **Customizable**: Configurable themes via role hints
- **Scalable**: Automatic regeneration if insufficient safe names

## Tech Stack

- **Python 3.x**
- **AWS Bedrock**: Serverless AI model hosting
- **Amazon Nova 2 Lite**: Fast, cost-effective LLM
- **boto3**: AWS SDK for Python

## Prerequisites

1. AWS Account with Bedrock access
2. Amazon Nova model enabled in us-east-2 region
3. AWS credentials configured
4. Python packages: `boto3`

## Installation

```bash
pip install boto3
```

Configure AWS credentials:
```bash
aws configure
```

## Usage

### Basic Usage

```python
from nova_elf_names import generate_seasonal_names

names = generate_seasonal_names("Your Name Here")
print(names)
```

### Custom Theme

```python
names = generate_seasonal_names(
    user_input="Jane Doe",
    role_hint="halloween spooky name",
    count=10
)
```

### Run Demo

```bash
python nova-elf-names.py
```

## API Reference

### generate_seasonal_names()

```python
def generate_seasonal_names(
    user_input: str,
    role_hint: str = "winter elf name",
    count: int = 6
) -> List[str]
```

**Parameters:**
- `user_input`: Seed string for deterministic generation
- `role_hint`: Theme/style guidance for the LLM
- `count`: Number of names to generate

**Returns:** List of safe, whimsical names

## Configuration

Modify these constants in the code:

- **Region**: Change `region_name` in bedrock client (line 11)
- **Model**: Update `modelId` (line 35)
- **Temperature**: Adjust creativity in `call_bedrock_claude()` (line 13)
- **Name Patterns**: Customize in `assemble_names_from_fragments()` (line 113)

## Cost Considerations

Amazon Nova 2 Lite pricing (us-east-2):
- Input: ~$0.00006 per 1K tokens
- Output: ~$0.00024 per 1K tokens

Typical cost per run: < $0.01

## Troubleshooting

**JSON Decode Error**: Nova may wrap JSON in markdown. The code strips ` ```json ` blocks automatically.

**Validation Error**: Ensure Nova model is enabled in your AWS region.

**No Safe Names**: Adjust `role_hint` to be more specific or increase generation count.

## License

MIT
