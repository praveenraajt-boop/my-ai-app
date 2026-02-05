import streamlit as st
import PIL.Image
import os
import json
from google import genai
from google.genai import types
from st_copy_to_clipboard import st_copy_to_clipboard

# --- 1. PAGE CONFIG ---
st.set_page_config(page_title="Cinematography AI", layout="wide")

# --- 2. SIDEBAR ---
with st.sidebar:
    st.title("🎬 Director Settings")
    api_key = st.secrets.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")
    if not api_key:
        api_key = st.text_input("Enter Gemini API Key", type="password")
    
    st.divider()
    mode = st.selectbox("Shot Mode", 
        ["General Analysis", "360° shot list", "dolly orbits", "dialogue coverage", "cinematic coverage map"])
    st.info("Using Gemini 3 Flash for Free Tier stability.")

# --- 3. MAIN INTERFACE ---
st.title("Professional Cinematographer AI")
uploaded_file = st.file_uploader("Upload reference frame...", type=["jpg", "jpeg", "png"])

if uploaded_file:
    col1, col2 = st.columns([1, 1])
    with col1:
        img = PIL.Image.open(uploaded_file)
        st.image(img, caption='Reference Frame', use_container_width=True)

    if st.button("Generate Camera Plan", type="primary"):
        if not api_key:
            st.error("Please provide an API key in the sidebar.")
        else:
            with st.spinner("Analyzing blocking..."):
                try:
                    client = genai.Client(api_key=api_key)
                    
                    # Exact Response Schema from your SDK snippet
                    response_schema = {
                        "type": "OBJECT",
                        "required": ["analysis", "angle_prompts"],
                        "properties": {
                            "analysis": {"type": "STRING", "description": "Brief breakdown"},
                            "angle_prompts": {
                                "type": "ARRAY",
                                "items": {
                                    "type": "OBJECT",
                                    "required": ["shot_name", "prompt"],
                                    "properties": {
                                        "shot_name": {"type": "STRING"},
                                        "prompt": {"type": "STRING"}
                                    }
                                }
                            }
                        }
                    }

                    config = types.GenerateContentConfig(
                        system_instruction="""[PASTE_YOUR_FULL_CINEMATOGRAPHY_INSTRUCTIONS_HERE]""",
                        response_mime_type="application/json",
                        response_schema=response_schema
                    )

                    # Using the Flash model to avoid Quota Exhausted errors
                    response = client.models.generate_content(
                        model="gemini-3-flash-preview",
                        contents=[f"Requesting a {mode}", img],
                        config=config
                    )

                    # Parse the JSON response
                    data = json.loads(response.text)

                    with col2:
                        st.subheader("Technical Analysis")
                        st.info(data.get("analysis", "No analysis provided."))

                        st.subheader("Generated Shot Prompts")
                        for i, item in enumerate(data.get("angle_prompts", [])):
                            with st.expander(f"Shot {i+1}: {item['shot_name']}", expanded=True):
                                st.code(item['prompt'], language="text")
                                # Individual Copy Button for this specific prompt
                                st_copy_to_clipboard(item['prompt'], key=f"copy_{i}")
                                st.caption("Click above to copy this specific shot prompt.")

                except Exception as e:
                    st.error(f"Execution Error: {e}")
                    st.info("Ensure your API key is correct and you haven't exceeded your per-minute requests.")
