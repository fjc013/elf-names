"""
Festive Christmas Holiday Elf Name Generator - Streamlit Application

A family-friendly web application that generates whimsical, personalized 
Santa's elf names using AI.
"""

import streamlit as st
import sys
from pathlib import Path

# Add src directory to path for imports
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from bedrock_client import BedrockClient
from name_generation_pipeline import NameGenerationPipeline
from exceptions import InputValidationError, NameGenerationError, BedrockAPIError


def apply_festive_theme():
    """Apply Christmas-themed CSS styling to the application."""
    festive_css = """
    <style>
    /* Christmas color palette: red, green, gold, white */
    :root {
        --christmas-red: #C41E3A;
        --christmas-green: #165B33;
        --christmas-gold: #FFD700;
        --christmas-white: #FFFAFA;
        --christmas-dark-green: #0F4C28;
    }
    
    /* Main app background */
    .stApp {
        background: linear-gradient(135deg, #FFFAFA 0%, #F0E6E6 100%);
    }
    
    /* Title styling */
    h1 {
        color: var(--christmas-red) !important;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
        font-family: 'Georgia', serif;
        text-align: center;
        padding: 20px 0;
    }
    
    h3 {
        color: var(--christmas-green) !important;
        text-align: center;
        font-style: italic;
    }
    
    /* Input field styling */
    .stTextInput > div > div > input {
        border: 2px solid var(--christmas-green);
        border-radius: 10px;
        padding: 10px;
        font-size: 16px;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: var(--christmas-red);
        box-shadow: 0 0 10px rgba(196, 30, 58, 0.3);
    }
    
    /* Select box styling */
    .stSelectbox > div > div > div {
        border: 2px solid var(--christmas-green);
        border-radius: 10px;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, var(--christmas-red) 0%, var(--christmas-dark-green) 100%);
        color: white;
        font-size: 20px;
        font-weight: bold;
        padding: 15px 30px;
        border-radius: 15px;
        border: 3px solid var(--christmas-gold);
        box-shadow: 0 4px 6px rgba(0,0,0,0.2);
        transition: all 0.3s ease;
        width: 100%;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.3);
        border-color: var(--christmas-gold);
    }
    
    /* Decorative borders */
    .element-container {
        border-radius: 10px;
    }
    
    /* Info box styling */
    .stAlert {
        border-radius: 10px;
        border-left: 5px solid var(--christmas-green);
    }
    
    /* Success/result box styling */
    .stSuccess {
        background-color: rgba(22, 91, 51, 0.1);
        border: 2px solid var(--christmas-green);
        border-radius: 15px;
        padding: 20px;
    }
    
    /* Error box styling */
    .stError {
        background-color: rgba(196, 30, 58, 0.1);
        border: 2px solid var(--christmas-red);
        border-radius: 15px;
    }
    
    /* Spinner styling */
    .stSpinner > div {
        border-top-color: var(--christmas-red) !important;
    }
    </style>
    """
    st.markdown(festive_css, unsafe_allow_html=True)


def render_input_form():
    """
    Render the input form for collecting user's first name and birth month.
    
    Returns:
        tuple: (first_name, birth_month, submit_clicked) or (None, None, False)
    """
    # Create a form container with decorative elements
    st.markdown("---")
    st.markdown("### 🎅 Tell Us About Yourself 🎄")
    
    # Create columns for better layout
    col1, col2 = st.columns([1, 1])
    
    with col1:
        # Text input for first name with festive label
        st.markdown("#### ❄️ Your First Name")
        first_name = st.text_input(
            "First Name",
            placeholder="Enter your first name...",
            label_visibility="collapsed",
            key="first_name_input"
        )
    
    with col2:
        # Selectbox for birth month with all 12 months
        st.markdown("#### 🎁 Your Birth Month")
        months = [
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ]
        birth_month = st.selectbox(
            "Birth Month",
            options=["Select a month..."] + months,
            label_visibility="collapsed",
            key="birth_month_select"
        )
    
    # Add decorative spacing
    st.markdown("")
    
    # Generate button with festive styling
    st.markdown("### ✨ Ready to Discover Your Elf Name? ✨")
    submit_clicked = st.button("🎄 Generate My Elf Name! 🎄", use_container_width=True)
    
    # Input validation with error messages
    if submit_clicked:
        errors = []
        
        # Validate first name
        if not first_name or not first_name.strip():
            errors.append("🎅 Please enter your first name")
        
        # Validate birth month
        if birth_month == "Select a month..." or birth_month not in months:
            errors.append("🎁 Please select your birth month")
        
        # Display errors if any
        if errors:
            for error in errors:
                st.error(error)
            return None, None, False
        
        # Return validated inputs
        return first_name.strip(), birth_month, True
    
    return None, None, False


def display_elf_name(name: str):
    """
    Display the generated elf name with festive styling.
    
    Args:
        name: The generated elf name to display
    """
    # Create a visually prominent display with large, ornate font
    st.markdown("---")
    st.markdown("## 🎉 Your Magical Elf Name Is... 🎉")
    
    # Display the name in large, ornate font (48pt+) with festive styling
    elf_name_html = f"""
    <div style="
        text-align: center;
        padding: 40px 20px;
        background: linear-gradient(135deg, #FFFAFA 0%, #FFE4E1 100%);
        border: 5px solid #FFD700;
        border-radius: 20px;
        box-shadow: 0 8px 16px rgba(0,0,0,0.2);
        margin: 20px 0;
    ">
        <div style="
            font-size: 64px;
            font-weight: bold;
            color: #C41E3A;
            font-family: 'Georgia', serif;
            text-shadow: 3px 3px 6px rgba(0,0,0,0.2);
            letter-spacing: 2px;
            line-height: 1.3;
        ">
            ✨ {name} ✨
        </div>
        <div style="
            font-size: 24px;
            color: #165B33;
            margin-top: 20px;
            font-style: italic;
        ">
            🎄 Welcome to Santa's Workshop! 🎄
        </div>
    </div>
    """
    st.markdown(elf_name_html, unsafe_allow_html=True)
    
    # Add decorative elements with snowflakes, stars, and holly emoji
    st.markdown(
        "<div style='text-align: center; font-size: 32px; margin: 20px 0;'>"
        "❄️ ⭐ 🎅 ⭐ ❄️ 🎄 ❄️ ⭐ 🎅 ⭐ ❄️"
        "</div>",
        unsafe_allow_html=True
    )
    
    # Add a festive message
    st.success("🎁 Your elf name has been magically generated! Share it with your friends and family!")
    
    # Add option to generate another name
    st.markdown("---")
    if st.button("🔄 Generate Another Name", use_container_width=True):
        st.rerun()


def display_error(message: str):
    """
    Display error message with festive styling.
    
    Args:
        message: The error message to display
    """
    # Display user-friendly error message with festive styling
    error_html = f"""
    <div style="
        padding: 30px;
        background: linear-gradient(135deg, #FFE4E1 0%, #FFFAFA 100%);
        border: 3px solid #C41E3A;
        border-radius: 15px;
        margin: 20px 0;
        text-align: center;
    ">
        <div style="
            font-size: 48px;
            margin-bottom: 15px;
        ">
            🎅 Oops! 🎄
        </div>
        <div style="
            font-size: 20px;
            color: #C41E3A;
            font-weight: bold;
            margin-bottom: 10px;
        ">
            {message}
        </div>
        <div style="
            font-size: 16px;
            color: #165B33;
            font-style: italic;
        ">
            Don't worry, Santa's elves are here to help! ✨
        </div>
    </div>
    """
    st.markdown(error_html, unsafe_allow_html=True)


def main():
    """Main application entry point."""
    # Set up Streamlit page configuration with festive title
    st.set_page_config(
        page_title="🎄 Festive Elf Name Generator 🎅",
        page_icon="🎄",
        layout="centered",
        initial_sidebar_state="collapsed"
    )
    
    # Apply festive theme
    apply_festive_theme()
    
    # Display title
    st.title("🎄 Festive Christmas Elf Name Generator 🎅")
    st.markdown("### Discover Your Magical Elf Name! ✨")
    
    # Initialize BedrockClient and NameGenerationPipeline
    # Use session state to avoid reinitializing on every rerun
    if 'pipeline' not in st.session_state:
        try:
            bedrock_client = BedrockClient()
            st.session_state.pipeline = NameGenerationPipeline(bedrock_client)
            st.session_state.initialization_error = None
        except BedrockAPIError as e:
            st.session_state.pipeline = None
            st.session_state.initialization_error = str(e)
        except Exception as e:
            st.session_state.pipeline = None
            st.session_state.initialization_error = f"Unexpected error: {str(e)}"
    
    # Check for initialization errors
    if st.session_state.initialization_error:
        display_error(st.session_state.initialization_error)
        st.stop()
    
    # Initialize session state for generated name
    if 'generated_name' not in st.session_state:
        st.session_state.generated_name = None
    if 'generation_error' not in st.session_state:
        st.session_state.generation_error = None
    
    # Display generated name if it exists
    if st.session_state.generated_name:
        display_elf_name(st.session_state.generated_name)
    else:
        # Show welcome message
        st.info("🎁 Enter your information below to generate your unique elf name!")
        
        # Render input form and handle submission
        first_name, birth_month, submit_clicked = render_input_form()
        
        # Process form submission
        if submit_clicked and first_name and birth_month:
            # Show loading spinner during generation
            with st.spinner("✨ The elves are working their magic... 🎄"):
                try:
                    # Generate elf name using the pipeline
                    generated_name = st.session_state.pipeline.generate_elf_name(
                        first_name=first_name,
                        birth_month=birth_month
                    )
                    
                    # Store generated name in session state
                    st.session_state.generated_name = generated_name
                    st.session_state.generation_error = None
                    
                    # Rerun to display the name
                    st.rerun()
                    
                except InputValidationError as e:
                    # Display validation errors with specific message
                    display_error(str(e))
                    st.session_state.generation_error = str(e)
                    
                except BedrockAPIError as e:
                    # Display Bedrock API errors with user-friendly message
                    display_error(str(e))
                    st.session_state.generation_error = str(e)
                    
                except NameGenerationError as e:
                    # Display generation errors with user-friendly message
                    error_message = "Something went wrong while generating your elf name. Please try again!"
                    display_error(error_message)
                    st.session_state.generation_error = str(e)
                    
                    # Log the actual error for debugging
                    st.error(f"Debug info: {str(e)}")
                    
                except Exception as e:
                    # Display general errors with user-friendly message
                    error_message = "An unexpected error occurred. Please try again!"
                    display_error(error_message)
                    st.session_state.generation_error = str(e)
                    
                    # Log the actual error for debugging
                    st.error(f"Debug info: {str(e)}")
        
        # Display any previous generation errors
        if st.session_state.generation_error and not submit_clicked:
            display_error("Please try generating your elf name again.")


if __name__ == "__main__":
    main()
