import streamlit as st
import PIL.Image
import os
import time
from google import genai
from google.genai import types
from st_copy_to_clipboard import st_copy_to_clipboard

st.set_page_config(page_title="Cinematography AI", layout="wide")

# --- SIDEBAR ---
with st.sidebar:
    st.title("🎬 Settings")
    api_key = st.secrets.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")
    if not api_key:
        api_key = st.text_input("Enter Gemini API Key", type="password")
    st.info("Switched to Gemini 3 Flash for maximum free-tier stability.")

# --- MAIN APP ---
st.title("Professional Cinematographer AI")
uploaded_file = st.file_uploader("Upload a frame...", type=["jpg", "jpeg", "png"])

if uploaded_file:
    col1, col2 = st.columns([1, 1])
    with col1:
        img = PIL.Image.open(uploaded_file)
        st.image(img, use_container_width=True)

    if st.button("Generate Camera Plan", type="primary"):
        if api_key:
            with st.spinner("Analyzing..."):
                try:
                    # Added a tiny delay to prevent rapid-fire RPM hits
                    time.sleep(0.5) 
                    
                    client = genai.Client(api_key=api_key)
                    
                    # Gemini 3 Flash is more reliable for free tier
                    # REMOVED thinking_config to prevent quota rejection
                    response = client.models.generate_content(
                        model="gemini-3-flash-preview", 
                        contents=["""Analyze this image based on the cinematography rules provided.""", img],
                        config=types.GenerateContentConfig(
                            system_instruction="""[PASTE_YOUR_SYSTEM_INSTRUCTIONS_HERE]"""
                        )
                    )

                    with col2:
                        st.markdown(response.text)
                        st_copy_to_clipboard(response.text)
                except Exception as e:
                    st.error(f"Quota reached. Please wait 60 seconds and try again. Error: {e}")
        else:
            st.warning("Please enter an API key.")
