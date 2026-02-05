import streamlit as st
import PIL.Image
import os
from google import genai
from google.genai import types

# --- PAGE SETUP ---
st.set_page_config(page_title="Cinematography AI", layout="wide")
st.title("🎬 AI Cinematography Assistant")
st.write("Upload a frame to get professional camera blocking and shot lists.")

# --- API KEY CONFIGURATION ---
# This looks for your key in Streamlit Secrets (for sharing) or a local Environment Variable
api_key = st.secrets.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")

if not api_key:
    api_key = st.sidebar.text_input("Enter Gemini API Key", type="password")
    st.sidebar.info("Get your key at ai.google.dev")

if api_key:
    client = genai.Client(api_key=api_key)

    # --- SIDEBAR OPTIONS ---
    st.sidebar.header("Shot Mode")
    mode = st.sidebar.selectbox("Choose analysis type:", 
        ["360° shot list", "dolly orbits", "dialogue coverage", "cinematic coverage map", "General Analysis"])

    # --- MAIN INTERFACE ---
    uploaded_file = st.file_uploader("Upload reference image...", type=["jpg", "jpeg", "png"])
    user_input = st.text_input("User Request", value=f"Provide a {mode} for this scene.")

    if uploaded_file and st.button("Generate Camera Plan"):
        img = PIL.Image.open(uploaded_file)
        st.image(img, caption='Reference Frame', use_container_width=True)

        with st.spinner("Analyzing with High Reasoning..."):
            try:
                # Configuration exactly as requested in your SDK snippet
                generate_content_config = types.GenerateContentConfig(
                    thinking_config=types.ThinkingConfig(
                        thinking_level="HIGH", # Supported by Gemini 3
                    ),
                    tools=[types.Tool(googleSearch=types.GoogleSearch())],
                    system_instruction="""You are a professional cinematographer and camera blocking director.
Your job is to analyze the uploaded image and infer where the main subject is, face and body orientation, spatial depth, and layout. 
Only camera position, lens, framing, and movement are allowed to change. 
[... REST OF YOUR SYSTEM INSTRUCTIONS HERE ...]"""
                )

                # Send request using Gemini 3 Pro
                response = client.models.generate_content(
                    model="gemini-3-pro-preview",
                    contents=[user_input, img],
                    config=generate_content_config,
                )

                st.subheader("Director's Recommendation")
                st.markdown(response.text)

            except Exception as e:
                st.error(f"An error occurred: {e}")
                st.info("Tip: Ensure your API key has access to Gemini 3 Pro Preview.")
else:
    st.warning("Please enter an API key in the sidebar to begin.")
