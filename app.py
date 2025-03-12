# app.py
import streamlit as st
import requests

# A predefined list of languages (for dropdown)
languages = [
    "English", "Spanish", "French", "German", "Italian", "Hindi", "Kannada",
    "Tamil", "Telugu", "Russian", "Chinese", "Arabic", "Japanese", "Korean",
    "Portuguese", "Bengali", "Urdu", "Dutch", "Swedish", "Greek", "Polish"
]

st.title("Translator")

# File uploader
uploaded_file = st.file_uploader("Upload a file (PDF, PPT/PPTX, HTML, or Text)", type=["pdf", "txt", "html", "ppt", "pptx"])

# Dropdown for predefined languages
target_language_dropdown = st.selectbox("Select Target Language", languages)

# Search bar for custom input
target_language_custom = st.text_input("Or Type Target Language")

# Let the user choose between dropdown or custom input
if target_language_custom:
    target_language = target_language_custom  # Use custom input
else:
    target_language = target_language_dropdown  # Use dropdown selection

# Initialize session state for the translation result
if 'previous_language' not in st.session_state:
    st.session_state.previous_language = None
if 'previous_file' not in st.session_state:
    st.session_state.previous_file = None

# Reset previous translation if the language or file changes
if st.session_state.previous_language != target_language or st.session_state.previous_file != uploaded_file:
    st.session_state.previous_language = target_language
    st.session_state.previous_file = uploaded_file
    st.session_state.translation_result = None

# Add the "Translate" button
if uploaded_file and target_language:
    if st.button("Translate"):
        # Ensure target_language is not empty
        if not target_language.strip():
            st.error("Target language cannot be empty.")
        else:
            # Prepare the file and form data
            files = {"file": (uploaded_file.name, uploaded_file, uploaded_file.type)}
            data = {"target_language": target_language}

            # Log the request data for debugging
            print(f"Sending request to translate content in: {uploaded_file.name} to target_language: {target_language}")
            st.write(f"Sending request to translate content in: {uploaded_file.name}, to {target_language} language")

            try:
                # Send POST request to FastAPI with form data
                response = requests.post(
                    "http://127.0.0.1:8000/translate-file/",
                    files=files,
                    data=data
                )

                # Handle API response
                if response.status_code == 200:
                    st.success("Translation Successful!")
                    result = response.json()
                    st.session_state.translation_result = result.get("translated_text")
                    st.write(st.session_state.translation_result)
                else:
                    st.error(f"Error in translation: {response.text}")
            except Exception as e:
                st.error(f"Failed to connect to the backend: {str(e)}")
else:
    st.warning("Please upload a file and select or type a target language to proceed.")