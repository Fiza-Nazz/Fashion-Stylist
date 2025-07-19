import os
import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
import json
from datetime import datetime
import base64
import textwrap

# Load API key from .env
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    st.error("GEMINI_API_KEY not found in .env file. Please set it up.")
    st.stop()
genai.configure(api_key=api_key)

# Initialize Gemini model
model = genai.GenerativeModel("models/gemini-1.5-flash")

# Function to generate outfit suggestion
def generate_outfit(wardrobe, weather, season, mood, event, style_preference, color_preference):
    prompt = f"""
    You are an expert fashion stylist with a keen eye for creativity and trends. Based on the following:
    - Weather: {weather}
    - Season: {season}
    - Mood: {mood}
    - Event: {event}
    - Style Preference: {style_preference}
    - Color Preference: {color_preference}
    - Wardrobe: {", ".join(wardrobe)}

    Suggest a complete, stylish outfit from the wardrobe, including accessories (e.g., scarves, hats, belts, jewelry) suitable for the weather, season, and event. 
    Ensure the outfit matches the user's mood, style, and color preferences. 
    Provide a creative description of how the outfit looks together, including color coordination and styling tips.
    Format the response in markdown with sections: 
    - **Outfit**: List the selected items with emojis (e.g., 👖 for pants, 👕 for shirt).
    - **Visual Preview**: A creative text-based representation of the outfit.
    - **Explanation**: Why this outfit suits the weather, season, mood, event, style, and colors.
    - **Styling Tips**: Tips to enhance the look (e.g., how to accessorize or style hair).
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"❌ Error generating outfit: {str(e)}"

# Function to refine outfit based on user feedback
def refine_outfit(wardrobe, weather, season, mood, event, style_preference, color_preference, feedback):
    prompt = f"""
    You are a fashion stylist refining an outfit based on user feedback. Original inputs:
    - Weather: {weather}
    - Season: {season}
    - Mood: {mood}
    - Event: {event}
    - Style Preference: {style_preference}
    - Color Preference: {color_preference}
    - Wardrobe: {", ".join(wardrobe)}
    - User Feedback: {feedback}

    Suggest a revised outfit that addresses the feedback while staying true to the original inputs. 
    Format the response in markdown with sections: Outfit, Visual Preview, Explanation, and Styling Tips.
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"❌ Error refining outfit: {str(e)}"

# Function to save outfit to history
def save_to_history(outfit, weather, season, mood, event, style_preference, color_preference):
    history_file = "outfit_history.json"
    history_entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "weather": weather,
        "season": season,
        "mood": mood,
        "event": event,
        "style_preference": style_preference,
        "color_preference": color_preference,
        "outfit": outfit
    }
    history = []
    try:
        if os.path.exists(history_file):
            with open(history_file, "r") as f:
                history = json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        st.warning(f"Error reading history file: {str(e)}. Starting with an empty history.")
        history = []
    history.append(history_entry)
    try:
        with open(history_file, "w") as f:
            json.dump(history, f, indent=4)
    except IOError as e:
        st.error(f"Error saving to history file: {str(e)}")

# Function to save wardrobe
def save_wardrobe(wardrobe_name, wardrobe_items):
    wardrobe_file = "wardrobes.json"
    wardrobes = {}
    try:
        if os.path.exists(wardrobe_file):
            with open(wardrobe_file, "r") as f:
                wardrobes = json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        st.warning(f"Error reading wardrobe file: {str(e)}. Starting with an empty wardrobe.")
        wardrobes = {}
    wardrobes[wardrobe_name] = wardrobe_items
    try:
        with open(wardrobe_file, "w") as f:
            json.dump(wardrobes, f, indent=4)
    except IOError as e:
        st.error(f"Error saving wardrobe file: {str(e)}")

# Function to load wardrobes
def load_wardrobes():
    wardrobe_file = "wardrobes.json"
    try:
        if os.path.exists(wardrobe_file):
            with open(wardrobe_file, "r") as f:
                return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        st.warning(f"Error loading wardrobes: {str(e)}. Returning empty wardrobe.")
        return {}
    return {}

# Function to generate LaTeX for PDF export
def generate_latex(outfit_suggestion):
    latex_content = textwrap.dedent(r"""
    \documentclass{article}
    \usepackage[utf8]{inputenc}
    \usepackage{geometry}
    \usepackage{titling}
    \usepackage{xcolor}
    \usepackage{enumitem}
    \geometry{a4paper, margin=1in}
    \title{Chikki Outfit Suggestion}
    \author{Chikki Fashion Stylist}
    \date{\today}
    \begin{document}
    \maketitle
    \section*{Your Stylish Outfit}
    \vspace{10pt}
    \noindent
    \textbf{Generated on:} \today \\
    \vspace{10pt}
    \noindent
    \textbf{Outfit Details:} \\
    \begin{verbatim}
    %s
    \end{verbatim}
    \end{document}
    """ % outfit_suggestion.replace('$', r'\$').replace('&', r'\&').replace('%', r'\%').replace('#', r'\#').replace('_', r'\_').replace('{', r'\{').replace('}', r'\}'))
    return latex_content

# Streamlit UI
st.set_page_config(page_title="Chikki: Fashion Stylist", page_icon="👗", layout="wide")

# Custom CSS for vibrant, modern UI
st.markdown("""
<style>
    .main {
        background: linear-gradient(to bottom, #f5f5f5, #e0e7ff);
    }
    .stButton>button {
        background: linear-gradient(to right, #4CAF50, #45a049);
        color: white;
        border-radius: 10px;
        border: none;
        padding: 10px 20px;
        transition: transform 0.3s ease;
    }
    .stButton>button:hover {
        transform: scale(1.05);
    }
    .stTextInput>div>input, .stTextArea>div>textarea {
        border-radius: 10px;
        border: 2px solid #4CAF50;
    }
    .stSelectbox>div>div>select {
        border-radius: 10px;
        border: 2px solid #4CAF50;
    }
    .stMarkdown {
        font-family: 'Poppins', sans-serif;
    }
    .sidebar .sidebar-content {
        background: linear-gradient(to bottom, #e0e0e0, #d1d5db);
    }
    h1 {
        color: #1e3a8a;
        font-weight: bold;
    }
    h3 {
        color: #3b82f6;
    }
    .stProgress .st-bo {
        background-color: #4CAF50;
    }
    .wardrobe-item {
        background: #ffffff;
        border-radius: 8px;
        padding: 10px;
        margin: 5px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        transition: transform 0.2s;
        color: #1e3a8a; /* Dark navy blue for better contrast */
        font-weight: 500;
    }
    .wardrobe-item:hover {
        transform: scale(1.02);
    }
    .footer {
        background: linear-gradient(to right, #1e3a8a, #d4af37); /* Navy to soft gold */
        color: #ffffff;
        padding: 25px;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        margin-top: 30px;
        font-family: 'Playfair Display', serif;
        font-size: 18px;
        font-weight: 400;
        letter-spacing: 0.5px;
        animation: fadeIn 1.2s ease-in-out;
    }
    @keyframes fadeIn {
        0% { opacity: 0; transform: translateY(15px); }
        100% { opacity: 1; transform: translateY(0); }
    }
    .divider {
        border-top: 3px solid #d4af37; /* Soft gold divider */
        margin: 30px 0;
        animation: slideIn 1.5s ease-in-out;
    }
    @keyframes slideIn {
        0% { width: 0; }
        100% { width: 100%; }
    }
</style>
""", unsafe_allow_html=True)

# Add heading
st.title("Fiza Fashion Stylist")

# Initialize session state
if 'wardrobe' not in st.session_state:
    st.session_state.wardrobe = []
if 'outfit_suggestion' not in st.session_state:
    st.session_state.outfit_suggestion = None
if 'feedback' not in st.session_state:
    st.session_state.feedback = ""

# Tabs for navigation
tabs = st.tabs(["Wardrobe Manager", "Outfit Stylist", "Outfit History"])

# Wardrobe Manager Tab
with tabs[0]:
    st.subheader("Manage Your Wardrobe 🧥")
    wardrobe_name = st.text_input("Wardrobe Name", value="My Wardrobe")
    wardrobe_input = st.text_area("Enter wardrobe items (one per line)", 
                                 value="Blue jeans\nWhite cotton shirt\nBlack leather jacket\nRed hoodie\nWhite sneakers\nBlack heels",
                                 height=150)
    wardrobe_items = [item.strip() for item in wardrobe_input.split("\n") if item.strip()]
    
    if st.button("Save Wardrobe"):
        save_wardrobe(wardrobe_name, wardrobe_items)
        st.session_state.wardrobe = wardrobe_items
        st.success(f"Wardrobe '{wardrobe_name}' saved successfully!")
    
    # Load existing wardrobes
    wardrobes = load_wardrobes()
    if wardrobes:
        selected_wardrobe = st.selectbox("Load Existing Wardrobe", list(wardrobes.keys()))
        if st.button("Load Selected Wardrobe"):
            st.session_state.wardrobe = wardrobes[selected_wardrobe]
            st.success(f"Loaded wardrobe '{selected_wardrobe}'!")
    
    # Display wardrobe items as a gallery
    if st.session_state.wardrobe:
        st.markdown("### Your Wardrobe Items")
        cols = st.columns(4)
        for i, item in enumerate(st.session_state.wardrobe):
            with cols[i % 4]:
                st.markdown(f"<div class='wardrobe-item'>👗 {item}</div>", unsafe_allow_html=True)

# Outfit Stylist Tab
with tabs[1]:
    st.subheader("Get Your Perfect Outfit! ✨")
    with st.form("outfit_form"):
        col1, col2, col3 = st.columns(3)
        with col1:
            weather = st.selectbox("Weather", ["Sunny", "Cold", "Rainy", "Warm"])
            season = st.selectbox("Season", ["Spring", "Summer", "Autumn", "Winter"])
        with col2:
            mood = st.selectbox("Mood", ["Confident", "Casual", "Elegant", "Playful", "Bold"])
            style_preference = st.selectbox("Style Preference", ["Casual", "Formal", "Bohemian", "Streetwear", "Minimalist"])
        with col3:
            event = st.selectbox("Event", ["Office Meeting", "Casual Outing", "Party", "Formal Event", "Date Night"])
            color_preference = st.selectbox("Color Preference", ["Neutral", "Bold", "Pastel", "Monochrome", "Vibrant"])
        
        submitted = st.form_submit_button("Generate Outfit")

    if submitted and st.session_state.wardrobe:
        with st.spinner("Styling your perfect outfit..."):
            progress_bar = st.progress(0)
            for i in range(100):
                progress_bar.progress(i + 1)
            st.session_state.outfit_suggestion = generate_outfit(
                st.session_state.wardrobe, weather, season, mood, event, style_preference, color_preference
            )
            progress_bar.empty()
        
        st.markdown("## Your Outfit Suggestion")
        st.markdown(st.session_state.outfit_suggestion)
        
        # Save to history
        save_to_history(st.session_state.outfit_suggestion, weather, season, mood, event, style_preference, color_preference)
        
        # Download as PDF
        latex_content = generate_latex(st.session_state.outfit_suggestion)
        b64 = base64.b64encode(latex_content.encode()).decode()
        href = f'<a href="data:application/octet-stream;base64,{b64}" download="outfit_suggestion.tex"> Download Outfit as LaTeX</a>'
        st.markdown(href, unsafe_allow_html=True)
    
    # Feedback section
    if st.session_state.outfit_suggestion:
        st.markdown("### Rate This Outfit")
        feedback = st.text_area("Provide feedback to refine your outfit", value=st.session_state.feedback)
        if st.button("Refine Outfit"):
            with st.spinner("Refining your outfit..."):
                st.session_state.outfit_suggestion = refine_outfit(
                    st.session_state.wardrobe, weather, season, mood, event, style_preference, color_preference, feedback
                )
                st.session_state.feedback = feedback
                st.markdown("## Refined Outfit Suggestion")
                st.markdown(st.session_state.outfit_suggestion)
                save_to_history(st.session_state.outfit_suggestion, weather, season, mood, event, style_preference, color_preference)

# Outfit History Tab
with tabs[2]:
    st.subheader("Outfit History 📜")
    history_file = "outfit_history.json"
    if os.path.exists(history_file):
        try:
            with open(history_file, "r") as f:
                history = json.load(f)
            for entry in history:
                with st.expander(f"Outfit from {entry.get('timestamp', 'Unknown Date')}"):
                    st.markdown(f"- **Weather**: {entry.get('weather', 'Not specified')}")
                    st.markdown(f"- **Season**: {entry.get('season', 'Not specified')}")
                    st.markdown(f"- **Mood**: {entry.get('mood', 'Not specified')}")
                    st.markdown(f"- **Event**: {entry.get('event', 'Not specified')}")
                    st.markdown(f"- **Style Preference**: {entry.get('style_preference', 'Not specified')}")
                    st.markdown(f"- **Color Preference**: {entry.get('color_preference', 'Not specified')}")
                    st.markdown(f"### Outfit\n{entry.get('outfit', 'No outfit details available')}")
        except (json.JSONDecodeError, IOError) as e:
            st.warning(f"History file is corrupted or inaccessible: {str(e)}. Starting with an empty history.")

# Clear inputs button
if st.button("Reset App"):
    st.session_state.wardrobe = []
    st.session_state.outfit_suggestion = None
    st.session_state.feedback = ""
    st.rerun()

# Footer
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
st.markdown('<div class="footer">Designed with Style by Fiza ♥ | Powered by Gemini AI ✨</div>', unsafe_allow_html=True)