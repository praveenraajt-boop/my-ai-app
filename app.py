import streamlit as st
import PIL.Image
import os
from google import genai
from google.genai import types
from st_copy_to_clipboard import st_copy_to_clipboard

# --- 1. PAGE CONFIG (Must be the first Streamlit command) ---
st.set_page_config(page_title="Cinematography AI", layout="wide")

# --- 2. SIDEBAR FOR SETTINGS ---
with st.sidebar:
    st.title("🎬 Director Settings")
    # API Key handling: checks secrets first, then environment, then user input
    api_key = st.secrets.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")
    if not api_key:
        api_key = st.text_input("Enter Gemini API Key", type="password")
    
    st.divider()
    mode = st.selectbox("Select Analysis Mode", 
        ["General Analysis", "360° shot list", "dolly orbits", "dialogue coverage", "cinematic coverage map"])
    st.info("Using Gemini 3 Flash for faster performance and higher limits.")

# --- 3. MAIN PAGE INTERFACE ---
st.title("Professional Cinematographer AI")
st.write("Upload a frame to generate precise camera plans and prompts.")

uploaded_file = st.file_uploader("Upload a reference frame...", type=["jpg", "jpeg", "png"])
user_query = st.text_input("Additional Instructions (Optional)", value=f"Requesting a {mode}")

# --- 4. PROCESSING LOGIC ---
if uploaded_file:
    # Display the image neatly in a column
    col1, col2 = st.columns([1, 1])
    with col1:
        img = PIL.Image.open(uploaded_file)
        st.image(img, caption='Reference Frame', use_container_width=True)

    if st.button("Generate Camera Plan", type="primary"):
        if not api_key:
            st.error("Please provide an API key in the sidebar.")
        else:
            with st.spinner("Analyzing blocking and lighting..."):
                try:
                    client = genai.Client(api_key=api_key)
                    
                    # Full instructions block
                    system_instructions = """You are a professional cinematographer and camera blocking director.
[PASTE_YOUR_FULL_SYSTEM_INSTRUCTIONS_HERE]"""

                    config = types.GenerateContentConfig(
                        system_instruction=system_instructions,
                        tools=[types.Tool(googleSearch=types.GoogleSearch())]
                    )

                    # Send to Gemini 3 Flash (Fast and stable)
                    response = client.models.generate_content(
                        model="gemini-3-flash-preview",
                        contents=[user_query, img],
                        config=config
                    )

                    with col2:
                        st.subheader("Shot Plan")
                        st.markdown(response.text)
                        
                        # Dedicated copy section
                        st.write("---")
                        st.write("### Copy for Nano Banana:")
                        st_copy_to_clipboard(response.text)
                        st.caption("Click above to copy the full response.")

                except Exception as e:
                    st.error(f"Execution Error: {e}")
