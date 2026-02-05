import streamlit as st
import PIL.Image
import os
import json
from google import genai
from google.genai import types
from tenacity import retry, stop_after_attempt, wait_random_exponential

# --- PAGE SETUP ---
st.set_page_config(page_title="Cinematography AI", layout="wide")
st.title("🎬 AI Cinematography Assistant")

# --- API KEY CONFIGURATION ---
api_key = st.secrets.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")

if not api_key:
    api_key = st.sidebar.text_input("Enter Gemini API Key", type="password")

# --- RESILIENT CALL FUNCTION ---
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

        with st.spinner("Analyzing with Structured Output..."):
            try:
                # YOUR STRUCTURED OUTPUT SCHEMA
                response_schema = {
                    "type": "OBJECT",
                    "properties": {
                        "analysis": {
                            "type": "STRING",
                            "description": "Brief technical breakdown of subject position and spatial layout"
                        },
                        "angle_prompts": {
                            "type": "ARRAY",
                            "items": {
                                "type": "OBJECT",
                                "properties": {
                                    "shot_name": {"type": "STRING"},
                                    "prompt": {"type": "STRING"}
                                },
                                "required": ["shot_name", "prompt"]
                            }
                        }
                    },
                    "required": ["analysis", "angle_prompts"]
                }

                # Configuration for Gemini 3 Flash
                generate_content_config = types.GenerateContentConfig(
                    thinking_config=types.ThinkingConfig(thinking_level="HIGH"),
                    response_mime_type="application/json", # Required for schema
                    response_schema=response_schema,       # Attaching your schema
                    system_instruction="""[PASTE YOUR FULL CINEMATOGRAPHY INSTRUCTIONS HERE]"""
                )

                # Call the model
                response = generate_with_retry(
                    client, 
                    "gemini-3-flash-preview", 
                    [user_input, img], 
                    generate_content_config
                )

                # PARSING AND DISPLAYING RESULTS
                result = response.parsed # SDK automatically parses JSON when schema is provided
                
                st.subheader("Technical Analysis")
                st.info(result.analysis)

                st.subheader("Generated Shot Prompts")
                for shot in result.angle_prompts:
                    with st.expander(f"📷 {shot.shot_name}"):
                        st.code(shot.prompt)
                        st.button(f"Copy {shot.shot_name}", on_click=lambda p=shot.prompt: st.write(f"Copied: {p}"), key=shot.shot_name)

            except Exception as e:
                st.error(f"Structured analysis failed. Error: {e}")
else:
    st.warning("Please enter an API key in the sidebar to begin.")
