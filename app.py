import streamlit as st
import PIL.Image
import os
from google import genai
from google.genai import types

# --- PAGE SETUP ---
st.set_page_config(page_title="Cinematography AI", layout="wide")
st.title("🎬 AI Cinematography Assistant (Fast Mode)")

# --- API KEY CONFIGURATION ---
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

        with st.spinner("Analyzing with Flash Reasoning..."):
            try:
                # Gemini 3 Flash supports Thinking levels while remaining highly efficient
                generate_content_config = types.GenerateContentConfig(
                    thinking_config=types.ThinkingConfig(
                        thinking_level="HIGH", # Gemini 3 Flash supports this level for deeper reasoning
                    ),
                    system_instruction="""You are a professional cinematographer... [PASTE YOUR FULL INSTRUCTIONS HERE]"""
                )

                # Switching to the Flash-tier model to avoid the 'limit: 0' Pro error
                response = client.models.generate_content(
                    model="gemini-3-flash-preview", 
                    contents=[user_input, img],
                    config=generate_content_config,
                )

                st.subheader("Director's Recommendation")
                st.markdown(response.text)

            except Exception as e:
                st.error(f"An error occurred: {e}")
                if "429" in str(e):
                    st.warning("Daily limits reached. Please wait for reset or switch to a paid tier.")
else:
    st.warning("Please enter an API key in the sidebar to begin.")
