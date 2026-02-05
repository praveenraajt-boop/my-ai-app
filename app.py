import streamlit as st
import PIL.Image
import os
from typing import List
from pydantic import BaseModel, Field
from google import genai
from google.genai import types
from tenacity import retry, stop_after_attempt, wait_random_exponential

# --- 1. DEFINE STRUCTURED DATA MODELS ---
# These classes act as the "shape" of your AI's response
class ShotPrompt(BaseModel):
    shot_name: str = Field(description="The name of the camera shot")
    prompt: str = Field(description="The full prompt for the image generator")

class CinemaResponse(BaseModel):
    analysis: str = Field(description="Brief technical breakdown of subject and layout")
    angle_prompts: List[ShotPrompt]

# --- 2. PAGE CONFIG ---
st.set_page_config(page_title="Cinematography AI", layout="wide")
st.title("🎬 Professional Cinematographer AI")

# --- 3. API KEY ---
api_key = st.secrets.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")
if not api_key:
    api_key = st.sidebar.text_input("Enter Gemini API Key", type="password")

# --- 4. RESILIENT API CALL ---
@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(5))
def generate_camera_plan(client, contents, config):
    return client.models.generate_content(
        model="gemini-3-flash-preview",
        contents=contents,
        config=config,
    )

if api_key:
    client = genai.Client(api_key=api_key)

    # --- 5. UI ELEMENTS ---
    st.sidebar.header("Shot Mode")
    mode = st.sidebar.selectbox("Choose analysis type:", 
        ["360° shot list", "dolly orbits", "dialogue coverage", "cinematic coverage map", "General Analysis"])

    uploaded_file = st.file_uploader("Upload reference frame...", type=["jpg", "jpeg", "png"])
    user_input = st.text_input("Custom Request", value=f"Provide a {mode} for this scene.")

    if uploaded_file and st.button("Generate Camera Plan"):
        img = PIL.Image.open(uploaded_file)
        st.image(img, caption='Input Scene', use_container_width=True)

        with st.spinner("Director is deep-thinking..."):
            try:
                # Configuration using your Pydantic model
                generate_content_config = types.GenerateContentConfig(
                    thinking_config=types.ThinkingConfig(thinking_level="HIGH"),
                    response_mime_type="application/json",
                    response_schema=CinemaResponse, # Attaching the Pydantic class
                    system_instruction="""[PASTE YOUR FULL CINEMATOGRAPHY INSTRUCTIONS HERE]"""
                )

                # Execute with retry logic
                response = generate_camera_plan(
                    client, 
                    [user_input, img], 
                    generate_content_config
                )

                # --- 6. DISPLAY RESULTS (Dot notation now works!) ---
                result = response.parsed # SDK automatically creates a CinemaResponse object
                
                st.subheader("Technical Analysis")
                st.info(result.analysis)

                st.subheader("Generated Shot Prompts")
                for shot in result.angle_prompts:
                    with st.expander(f"📷 {shot.shot_name}"):
                        st.code(shot.prompt)
                        st.button(f"Copy {shot.shot_name}", on_click=lambda p=shot.prompt: st.write(f"Copied: {p}"), key=shot.shot_name)

            except Exception as e:
                st.error(f"Analysis failed: {e}")
else:
    st.warning("Please enter an API key to begin.")
