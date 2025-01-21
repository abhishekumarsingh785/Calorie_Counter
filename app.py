import os
from PIL import Image
from phi.agent import Agent
from phi.model.google import Gemini
import streamlit as st
from phi.tools.duckduckgo import DuckDuckGo
import dotenv  

dotenv.load_dotenv()

st.markdown(
    """
    <style>
    .main {background-color: #121212; color: #ffffff;}
    .sidebar .sidebar-content {background-color: #1f1f1f; color: #ffffff;}
    </style>
    """,
    unsafe_allow_html=True
)

if "GOOGLE_API_KEY" not in st.session_state:
    st.session_state.GOOGLE_API_KEY = ""

with st.sidebar:
    st.title("ℹ️ Configuration")

    api_key_option = st.radio(
        "Select API Key Option:",
        ("Use Default API Key", "Enter Custom API Key")
    )

    if api_key_option == "Use Default API Key":
        st.session_state.GOOGLE_API_KEY = os.environ["GOOGLE_API_KEY"] 
        st.info("Using default API Key.")
    else:
        api_key = st.text_input(
            "Enter your Google API Key:",
            type="password"
        )
        if api_key:
            st.session_state.GOOGLE_API_KEY = api_key
            st.success("API Key saved!")
            st.rerun()

calorie_agent = Agent(
    model=Gemini(
        api_key=st.session_state.GOOGLE_API_KEY,
        id="gemini-2.0-flash-exp"
    ),
    tools=[DuckDuckGo()],
    markdown=True
) if st.session_state.GOOGLE_API_KEY else None

if not calorie_agent:
    st.warning("Please configure your API key in the sidebar to continue")

# Calorie Analysis Query
dish_query = """
You are a highly skilled nutrition expert with extensive knowledge in dietary analysis. Analyze the uploaded food image and structure your response as follows:

### 1. Dish Identification
- List each dish identified in the image
- Provide a brief description for each dish

### 2. Calorie Estimation
- For each dish, search the web using DuckDuckGo to find typical calorie values per serving
- Include references to the sources of calorie data

### 3. Total Calories
- Calculate and display the total calorie count for the entire image

### 4. Suggestions
- Provide healthy dietary tips or alternatives based on the analysis
"""

st.title("🍲 Calorie Calculator App")
st.write("Upload an image of your meal or dishes to calculate the total calorie content.")

# Create containers for better organization
upload_container = st.container()
image_container = st.container()
analysis_container = st.container()

with upload_container:
    uploaded_file = st.file_uploader(
        "Upload Food/Dish Image",
        type=["jpg", "jpeg", "png"],
        help="Supported formats: JPG, JPEG, PNG"
    )

if uploaded_file is not None:
    with image_container:
        # Center the image using columns
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            image = Image.open(uploaded_file)
            # Calculate aspect ratio for resizing
            width, height = image.size
            aspect_ratio = width / height
            new_width = 500
            new_height = int(new_width / aspect_ratio)
            resized_image = image.resize((new_width, new_height))

            st.image(
                resized_image,
                caption="Uploaded Food/Dish Image",
                use_container_width=True
            )

            analyze_button = st.button(
                "🔍 Analyze Image",
                type="primary",
                use_container_width=True
            )

    with analysis_container:
        if analyze_button:
            image_path = "temp_food_image.png"
            with open(image_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            with st.spinner("Please wait⏱️ while I get you the info"):
                try:
                    response = calorie_agent.run(dish_query, images=[image_path])
                    st.markdown("### Results")
                    st.markdown("---")
                    st.markdown(response.content)
                    st.markdown("---")
                except Exception as e:
                    st.error(f"Analysis error: {e}")
                finally:
                    if os.path.exists(image_path):
                        os.remove(image_path)
else:
    st.info("👆 Please upload a food or dish image to begin analysis")
