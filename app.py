import streamlit as st
import PIL.Image
import os
from google import genai
from google.genai import types
from st_copy_to_clipboard import st_copy_to_clipboard

# --- PAGE SETUP ---
st.set_page_config(page_title="Cinematography AI", layout="wide")
st.title("🎬 Professional Cinematographer AI")

# --- API KEY CONFIGURATION ---
api_key = st.secrets.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")

if not api_key:
    api_key = st.sidebar.text_input("Enter Gemini API Key", type="password")

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
        st.image(img, caption='Reference Frame', width=500)

        with st.spinner("Director is thinking..."):
            try:
                # Optimized for Gemini 3 Flash to avoid 429 errors
                generate_content_config = types.GenerateContentConfig(
                    system_instruction="""You are a professional cinematographer... [PASTE YOUR FULL INSTRUCTIONS HERE]"""
                )

                response = client.models.generate_content(
                    model="gemini-3-flash-preview", 
                    contents=[user_input, img],
                    config=generate_content_config,
                )

                st.subheader("Director's Recommendation")
                
                # Display the response
                result_text = response.text
                st.markdown(result_text)
                
                # THE FUNCTIONAL COPY BUTTON
                st.write("---")
                st.write("### Copy Prompt for Nano Banana:")
                st_copy_to_clipboard(result_text)
                st.success("Click the button above to copy the prompt!")

            except Exception as e:
                st.error(f"Error: {e}")
else:
    st.warning("Please provide an API key in the sidebar.")
