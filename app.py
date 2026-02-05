import streamlit as st
from google import genai
import PIL.Image

# 1. Setup the UI
st.title("🎬 AI Cinematography Assistant")
st.write("Upload a frame to get blocking and lighting feedback.")

# 2. Get your API Key (Securely)
api_key = st.sidebar.text_input("Enter Gemini API Key", type="password")

# 3. Handle File Upload
uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

if uploaded_file and api_key:
    # Display the image
    img = PIL.Image.open(uploaded_file)
    st.image(img, caption='Uploaded Frame', use_column_width=True)
    
    # 4. Connect to Gemini
    client = genai.Client(api_key=api_key)
    
    if st.button('Analyze Blocking'):
        with st.spinner('Director is thinking...'):
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=["Analyze the camera blocking and lighting in this shot.", img]
            )
            st.markdown(response.text)
