import streamlit as st
import PIL.Image
import os
from pydantic import BaseModel, Field
from typing import List
from google import genai
from google.genai import types
from tenacity import retry, stop_after_attempt, wait_random_exponential

# --- 1. DATA MODELS ---
class ShotPrompt(BaseModel):
    shot_name: str
    prompt: str

class CinemaResponse(BaseModel):
    analysis: str
    angle_prompts: List[ShotPrompt]

# --- 2. INITIALIZE SESSION STATE ---
# This acts as the app's memory
if "cinema_result" not in st.session_state:
    st.session_state.cinema_result = None

def clear_results():
    """Callback to wipe the app memory"""
    st.session_state.cinema_result = None

# --- 3. PAGE SETUP & API ---
st.set_page_config(page_title="Cinematography AI", layout="wide")
st.title("🎬 Professional Cinematographer AI")

api_key = st.secrets.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")
if not api_key:
    api_key = st.sidebar.text_input("Enter Gemini API Key", type="password")

@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(5))
def generate_camera_plan(client, contents, config):
    return client.models.generate_content(
        model="gemini-3-flash-preview",
        contents=contents,
        config=config,
    )

if api_key:
    client = genai.Client(api_key=api_key)

    # --- 4. UI INPUTS ---
    st.sidebar.header("Controls")
    mode = st.sidebar.selectbox("Shot Mode:", ["360° shot list", "dolly orbits", "dialogue coverage", "General Analysis"])
    
    # Add the Clear button to the sidebar
    st.sidebar.button("Clear Results", on_click=clear_results, type="primary")

    uploaded_file = st.file_uploader("Upload reference frame...", type=["jpg", "jpeg", "png"])
    user_input = st.text_input("Custom Request", value=f"Provide a {mode} for this scene.")

    if uploaded_file and st.button("Generate Camera Plan"):
        img = PIL.Image.open(uploaded_file)
        st.image(img, caption='Input Scene', width=400)

        with st.spinner("Director is deep-thinking..."):
            try:
                config = types.GenerateContentConfig(
                    thinking_config=types.ThinkingConfig(thinking_level="HIGH"),
                    response_mime_type="application/json",
                    response_schema=CinemaResponse,
                    system_instruction="""[PASTE YOUR FULL INSTRUCTIONS HERE]"""
                )

                response = generate_camera_plan(client, [user_input, img], config)
                
                # STORE IN MEMORY so it survives reruns
                st.session_state.cinema_result = response.parsed
                
            except Exception as e:
                st.error(f"Analysis failed: {e}")

    # --- 5. PERSISTENT DISPLAY ---
    # This block runs every time the page refreshes
    if st.session_state.cinema_result:
        result = st.session_state.cinema_result
        
        st.divider()
        st.subheader("Technical Analysis")
        st.info(result.analysis)

        st.subheader("Generated Shot Prompts")
        # Use columns to make it look like a professional dashboard
        for idx, shot in enumerate(result.angle_prompts):
            with st.expander(f"📷 {shot.shot_name}", expanded=True):
                st.code(shot.prompt)
                # Unique keys (btn_0, btn_1...) prevent button conflicts
                if st.button(f"Copy {shot.shot_name}", key=f"btn_{idx}"):
                    st.success(f"Prompt for '{shot.shot_name}' ready to copy!")
else:
    st.warning("Please enter an API key to begin.")
