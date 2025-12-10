# Implementation Plan

- [x] 1. Set up project structure and dependencies





  - Create project directory structure with src/, tests/, and config folders
  - Create requirements.txt with dependencies: streamlit, boto3, hypothesis, pytest
  - Create README.md with setup instructions for AWS credentials
  - _Requirements: 7.1, 7.2_

- [x] 2. Implement Bedrock client for AWS integration




  - [x] 2.1 Create BedrockClient class with AWS authentication


    - Implement initialization with boto3 client for Bedrock Runtime
    - Add error handling for authentication failures
    - Configure to use Nova 2 Lite model ID
    - _Requirements: 5.1, 5.2, 5.4_
  - [x] 2.2 Implement invoke_nova_lite method

    - Create method to call Nova Lite with prompt and optional seed
    - Add request/response parsing for Bedrock API format
    - Implement error handling for API failures and timeouts
    - _Requirements: 5.1, 5.2_
  - [x] 2.3 Implement generate_embedding method

    - Create method to generate embeddings using Bedrock embedding model
    - Parse embedding response into list of floats
    - Add error handling for embedding API calls
    - _Requirements: 4.4_

- [x] 3. Implement seed generation component






  - [x] 3.1 Create SeedGenerator class



    - Implement generate_seed method using SHA-256 hashing
    - Concatenate first_name and birth_month, hash, and extract first 8 characters
    - Return hexadecimal string
    - _Requirements: 4.1, 4.2_
  - [x]* 3.2 Write property test for seed generation


    - **Property 7: Seed generation consistency**
    - **Validates: Requirements 4.1, 4.2**

- [x] 4. Implement embedding and style hint generation





  - [x] 4.1 Create EmbeddingGenerator class


    - Implement initialization with BedrockClient dependency
    - Create generate_embedding method that calls Bedrock client
    - _Requirements: 4.4_
  - [x] 4.2 Implement embedding_to_style_hints method

    - Convert embedding vector values to semantic style instructions
    - Map positive values to "cheerful" adjective style
    - Map negative values to "cozy/natural" noun style
    - Map medium values to "playful twist" additions
    - Return dictionary with adjective_style, noun_style, and twist keys
    - _Requirements: 4.5, 4.6, 4.7, 4.8_
  - [ ]* 4.3 Write property test for embedding generation
    - **Property 8: Embedding generation**
    - **Validates: Requirements 4.4**
  - [ ]* 4.4 Write property test for style conversion
    - **Property 9: Embedding to style conversion**
    - **Validates: Requirements 4.5**

- [x] 5. Implement LLM name generator





  - [x] 5.1 Create LLMNameGenerator class


    - Implement initialization with BedrockClient dependency
    - _Requirements: 3.1, 3.2, 3.4_
  - [x] 5.2 Implement _build_prompt method

    - Construct prompt with Christmas theme constraints
    - Include style hints from embeddings in prompt
    - Specify 2-3 word format requirement
    - Include pattern examples (Adjective-WinterObject, etc.)
    - Add safety constraints (no political, religious, body parts, suggestive content)
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 3.1, 3.2, 3.4, 3.5_
  - [x] 5.3 Implement generate_name method

    - Call _build_prompt with seed and style hints
    - Invoke Bedrock client with prompt and seed
    - Parse and return generated name
    - Handle empty or malformed responses with retry logic
    - _Requirements: 1.4, 1.5, 3.1, 3.2, 3.4_

- [x] 6. Implement safety filter




  - [x] 6.1 Create SafetyFilter class


    - Implement initialization with BedrockClient dependency
    - _Requirements: 2.5, 2.6_
  - [x] 6.2 Implement _check_safety method


    - Build safety validation prompt for LLM
    - Call Bedrock to evaluate name for inappropriate content
    - Parse response to determine if name is safe
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_
  - [x] 6.3 Implement validate_name method


    - Call _check_safety on generated name
    - Return tuple of (is_safe, name)
    - Implement retry logic with maximum 3 attempts for unsafe names
    - Add fallback list of safe generic names if all retries fail
    - _Requirements: 2.5, 2.6_

- [x] 7. Implement name generation pipeline




  - [x] 7.1 Create NameGenerationPipeline class


    - Initialize with BedrockClient and all component dependencies
    - Instantiate SeedGenerator, EmbeddingGenerator, LLMNameGenerator, SafetyFilter
    - _Requirements: 1.4, 1.5_
  - [x] 7.2 Implement generate_elf_name orchestration method


    - Call SeedGenerator to create seed from inputs
    - Call EmbeddingGenerator to create embedding and style hints
    - Call LLMNameGenerator to generate name with seed and style hints
    - Call SafetyFilter to validate generated name
    - Implement retry logic for unsafe names
    - Return final validated elf name
    - Add comprehensive error handling for all failure modes
    - _Requirements: 1.4, 1.5, 2.5, 2.6_
  - [ ]* 7.3 Write property test for reproducibility
    - **Property 2: Reproducibility**
    - **Validates: Requirements 1.5**
  - [ ]* 7.4 Write property test for word count
    - **Property 4: Word count constraint**
    - **Validates: Requirements 3.1**
  - [ ]* 7.5 Write property test for Christmas themes
    - **Property 5: Christmas-themed vocabulary**
    - **Validates: Requirements 3.2**
  - [ ]* 7.6 Write property test for family-friendly content
    - **Property 3: Family-friendly content**
    - **Validates: Requirements 2.1, 2.2, 2.3, 2.4, 2.5**

- [x] 8. Checkpoint - Ensure all tests pass





  - Ensure all tests pass, ask the user if questions arise.

- [x] 9. Implement data models





  - [x] 9.1 Create UserInput dataclass

    - Define first_name and birth_month fields
    - Implement validate method to check non-empty name and valid month
    - _Requirements: 1.1, 1.2, 1.3_

  - [x] 9.2 Create GenerationContext dataclass


    - Define seed, embedding, and style_hints fields
    - _Requirements: 4.1, 4.4, 4.5_




  - [x] 9.3 Create StyleHints dataclass


    - Define adjective_style, noun_style, and twist fields
    - Implement from_embedding static method
    - _Requirements: 4.5, 4.6, 4.7, 4.8_






  - [x] 9.4 Create ElfName dataclass

    - Define name, is_safe, and generation_context fields
    - _Requirements: 1.4, 2.5_

- [x] 10. Implement Streamlit UI





  - [x] 10.1 Create main Streamlit app file


    - Set up Streamlit page configuration with festive title
    - Initialize BedrockClient and NameGenerationPipeline
    - _Requirements: 6.1, 7.2_
  - [x] 10.2 Implement apply_festive_theme function


    - Create custom CSS for Christmas colors (red, green, gold, white)
    - Add CSS for decorative elements (borders, backgrounds)
    - Apply CSS using st.markdown with unsafe_allow_html
    - _Requirements: 6.1, 6.2_
  - [x] 10.3 Implement render_input_form function


    - Create text input for first name with festive label
    - Create selectbox for birth month with all 12 months
    - Add decorative Christmas emoji or symbols
    - Add "Generate My Elf Name" button with festive styling
    - Implement input validation with error messages
    - _Requirements: 1.1, 1.2, 1.3_
  - [x] 10.4 Implement display_elf_name function


    - Display generated name in large, ornate font (48pt+)
    - Apply festive styling with Christmas colors
    - Add decorative elements (snowflakes, stars, holly emoji)
    - Ensure text is readable from several feet away
    - _Requirements: 6.3, 6.4, 6.5_
  - [x] 10.5 Implement display_error function


    - Display user-friendly error messages with festive styling
    - Maintain Christmas theme even in error states
    - _Requirements: 5.4_
  - [x] 10.6 Wire up complete user flow


    - Connect input form to pipeline
    - Show loading spinner during generation
    - Display generated name on success
    - Display errors on failure
    - Maintain session state for user experience
    - _Requirements: 1.3, 1.4_

- [x] 11. Add comprehensive error handling





  - [x] 11.1 Implement input validation error handling


    - Add validation for empty name input
    - Add validation for invalid month selection
    - Display appropriate error messages
    - _Requirements: 1.1, 1.2_
  - [x] 11.2 Implement AWS Bedrock error handling


    - Catch and handle authentication failures
    - Catch and handle API rate limiting with exponential backoff
    - Catch and handle model invocation failures
    - Catch and handle network timeouts
    - Display user-friendly error messages for each case
    - _Requirements: 5.4_
  - [x] 11.3 Implement generation error handling


    - Handle empty name generation with retry
    - Handle malformed name generation with retry and fallback
    - Add maximum retry limits
    - _Requirements: 1.4_

- [x] 12. Create test data and utilities






  - [x] 12.1 Create blocklists for safety validation

    - Define list of political terms to block
    - Define list of religious terms to block
    - Define list of body part terms to block
    - Define list of suggestive terms to block
    - _Requirements: 2.1, 2.2, 2.3, 2.4_

  - [x] 12.2 Create Christmas vocabulary list




    - Define comprehensive list of Christmas-themed words
    - Include categories: snow, light, candy, sparkle, animals, warmth, winter
    - _Requirements: 3.2_

  - [x] 12.3 Create fallback safe names list




    - Define list of pre-approved safe elf names for fallback
    - _Requirements: 2.6_

- [x] 13. Fix AWS Bedrock seed compatibility issue


  - [x] 13.1 Remove seed parameter from Nova Lite model calls


    - Modify BedrockClient.invoke_nova_lite to not use seed parameter
    - Update method signature to remove seed parameter
    - Remove seed conversion logic that causes validation errors


    - _Requirements: 5.1, 5.2_
  - [ ] 13.2 Update LLMNameGenerator to use prompt-based reproducibility
    - Modify generate_name method to not pass seed to Bedrock


    - Incorporate user name and month directly into prompt for consistency
    - Ensure deterministic prompt structure for reproducible results
    - _Requirements: 4.1, 4.3_


  - [ ] 13.3 Update NameGenerationPipeline to remove seed dependency
    - Remove SeedGenerator usage from pipeline
    - Update generate_elf_name to use prompt-based approach
    - Maintain reproducibility through consistent prompt formatting
    - _Requirements: 4.1, 4.2, 4.3_
  - [ ] 13.4 Update tests to reflect seed removal
    - Remove seed-related unit tests
    - Update integration tests to verify prompt-based reproducibility
    - Ensure all tests pass with new approach
    - _Requirements: 4.1, 4.2, 4.3_

- [x] 14. Final checkpoint - Ensure all tests pass





  - Ensure all tests pass, ask the user if questions arise.
