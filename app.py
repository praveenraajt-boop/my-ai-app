import streamlit as st
from google import genai
from google.genai import types
import PIL.Image
import os

# 1. Page Config
st.set_page_config(page_title="Cinematography AI", layout="wide")
st.title("🎬 Professional Cinematographer AI")

# 2. Get API Key from Secrets (Safe for sharing!)
# On Streamlit Cloud, add GEMINI_API_KEY to 'Settings > Secrets'
api_key = st.secrets.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")

if not api_key:
    api_key = st.sidebar.text_input("Enter Gemini API Key", type="password")

if api_key:
    client = genai.Client(api_key=api_key)
    
    # 3. Sidebar for Mode selection
    st.sidebar.header("Director's Booth")
    mode = st.sidebar.selectbox("Select Shot Mode", 
        ["General Analysis", "360° shot list", "dolly orbits", "dialogue coverage", "cinematic coverage map"])

    # 4. Image Upload
    uploaded_file = st.file_uploader("Upload a frame to analyze...", type=["jpg", "jpeg", "png"])
    user_query = st.text_input("Additional Instructions (Optional)", value=f"Requesting a {mode}")

    if uploaded_file:
        img = PIL.Image.open(uploaded_file)
        st.image(img, caption='Reference Frame', width=500)

        if st.button("Generate Camera Plan"):
            with st.spinner("Director is thinking..."):
                # 5. The exact configuration from your code
                generate_content_config = types.GenerateContentConfig(
                    thinking_config=types.ThinkingConfig(thinking_level="HIGH"),
                    tools=[types.Tool(googleSearch=types.GoogleSearch())],
                    system_instruction="""You are a professional cinematographer... [PASTE YOUR FULL INSTRUCTIONS HERE]"""
                )

                # Send both the image and the text query
                response = client.models.generate_content(
                    model="gemini-2.0-flash", # Use 'flash' for speed in web apps
                    contents=[user_query, img],
                    config=generate_content_config
                )
                
                st.subheader("Camera Strategy")
                st.markdown(response.text)
else:
    st.warning("Please provide an API key to start.")
