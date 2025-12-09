"""Custom exceptions for the Elf Name Generator application."""


class ElfNameGeneratorError(Exception):
    """Base exception for all elf name generator errors."""
    pass


class InputValidationError(ElfNameGeneratorError):
    """Exception raised for input validation errors."""
    pass


class BedrockAPIError(ElfNameGeneratorError):
    """Exception raised for AWS Bedrock API errors."""
    pass


class NameGenerationError(ElfNameGeneratorError):
    """Exception raised for name generation errors."""
    pass


class SafetyFilterError(ElfNameGeneratorError):
    """Exception raised for safety filter errors."""
    pass
