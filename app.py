import streamlit as st
import PIL.Image
import os
from google import genai
from google.genai import types
from tenacity import retry, stop_after_attempt, wait_random_exponential

# --- PAGE SETUP ---
st.set_page_config(page_title="Cinematography AI", layout="wide")
st.title("🎬 AI Cinematography Assistant")
st.write("Professional camera blocking and shot lists.")

# --- API KEY CONFIGURATION ---
api_key = st.secrets.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")

if not api_key:
    api_key = st.sidebar.text_input("Enter Gemini API Key", type="password")

# --- RESILIENT CALL FUNCTION ---
# This function handles the 503 Overload error automatically
@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(5))
def generate_with_retry(client, model_id, contents, config):
    return client.models.generate_content(
        model=model_id,
        contents=contents,
        config=config,
    )

if api_key:
    client = genai.Client(api_key=api_key)

    # --- SIDEBAR & INPUTS ---
    st.sidebar.header("Shot Mode")
    mode = st.sidebar.selectbox("Choose analysis type:", 
        ["360° shot list", "dolly orbits", "dialogue coverage", "cinematic coverage map", "General Analysis"])

    uploaded_file = st.file_uploader("Upload reference image...", type=["jpg", "jpeg", "png"])
    user_input = st.text_input("User Request", value=f"Provide a {mode} for this scene.")

    if uploaded_file and st.button("Generate Camera Plan"):
        img = PIL.Image.open(uploaded_file)
        st.image(img, caption='Reference Frame', use_container_width=True)

        with st.spinner("Director is thinking (Retrying if busy)..."):
            try:
                # Configuration for Gemini 3 Flash
                generate_content_config = types.GenerateContentConfig(
                    thinking_config=types.ThinkingConfig(thinking_level="HIGH"),
                    system_instruction="""[PASTE YOUR FULL CINEMATOGRAPHY INSTRUCTIONS HERE]"""
                )

                # Attempt the call with the retry logic
                response = generate_with_retry(
                    client, 
                    "gemini-3-flash-preview", 
                    [user_input, img], 
                    generate_content_config
                )

                st.subheader("Director's Recommendation")
                st.markdown(response.text)

            except Exception as e:
                st.error(f"The model is currently too busy even after several retries. Error: {e}")
else:
    st.warning("Please enter an API key in the sidebar to begin.")
