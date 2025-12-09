# Festive Christmas Holiday Elf Name Generator

A family-friendly web application that generates whimsical, personalized Santa's elf names for children using AI.

## Features

- Personalized elf names based on first name and birth month
- Reproducible results - same inputs always generate the same name
- Family-friendly content with safety filtering
- Christmas-themed, whimsical names
- Festive web interface

## Prerequisites

- Python 3.8 or higher
- AWS Account with Bedrock access
- AWS credentials configured

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure AWS Credentials

The application requires AWS credentials to access Amazon Bedrock. You can configure credentials in one of the following ways:

#### Option A: AWS CLI Configuration (Recommended)

Install the AWS CLI and run:

```bash
aws configure
```

Enter your:
- AWS Access Key ID
- AWS Secret Access Key
- Default region (e.g., `us-east-1`)
- Default output format (e.g., `json`)

#### Option B: Environment Variables

Set the following environment variables:

```bash
export AWS_ACCESS_KEY_ID=your_access_key_id
export AWS_SECRET_ACCESS_KEY=your_secret_access_key
export AWS_DEFAULT_REGION=us-east-1
```

On Windows (Command Prompt):

```cmd
set AWS_ACCESS_KEY_ID=your_access_key_id
set AWS_SECRET_ACCESS_KEY=your_secret_access_key
set AWS_DEFAULT_REGION=us-east-1
```

On Windows (PowerShell):

```powershell
$env:AWS_ACCESS_KEY_ID="your_access_key_id"
$env:AWS_SECRET_ACCESS_KEY="your_secret_access_key"
$env:AWS_DEFAULT_REGION="us-east-1"
```

#### Option C: AWS Credentials File

Create or edit `~/.aws/credentials`:

```ini
[default]
aws_access_key_id = your_access_key_id
aws_secret_access_key = your_secret_access_key
```

And `~/.aws/config`:

```ini
[default]
region = us-east-1
```

### 3. Verify Bedrock Access

Ensure your AWS account has access to Amazon Bedrock and the Nova 2 Lite model. You may need to:

1. Enable Bedrock in your AWS account
2. Request access to the Nova 2 Lite model in the Bedrock console
3. Ensure your IAM user/role has the necessary Bedrock permissions

Required IAM permissions:
- `bedrock:InvokeModel`
- `bedrock:InvokeModelWithResponseStream`

## Running the Application

Start the Streamlit application:

```bash
streamlit run app.py
```

The application will open in your default web browser at `http://localhost:8501`.

## Usage

1. Enter your first name
2. Select your birth month
3. Click "Generate My Elf Name"
4. Enjoy your personalized Christmas elf name!

## Running Tests

Run unit tests:

```bash
pytest tests/unit/
```

Run property-based tests:

```bash
pytest tests/property/
```

Run all tests:

```bash
pytest
```

## Project Structure

```
elf-name-generator/
├── src/                    # Source code
├── tests/                  # Test files
│   ├── unit/              # Unit tests
│   └── property/          # Property-based tests
├── config/                # Configuration files
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## Troubleshooting

### Authentication Errors

If you see authentication errors:
- Verify your AWS credentials are correctly configured
- Check that your credentials have not expired
- Ensure your IAM user/role has Bedrock permissions

### Model Access Errors

If you see model access errors:
- Verify you have enabled Bedrock in your AWS account
- Check that you have requested access to Nova 2 Lite in the Bedrock console
- Ensure you're using a region where Bedrock is available

### Rate Limiting

If you encounter rate limiting:
- Wait a moment and try again
- The application will automatically retry with exponential backoff

## License

This project is for educational and personal use.
