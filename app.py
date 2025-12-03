import streamlit as st
import pandas as pd
import requests
import time

# ---------------------------
# App Config
# ---------------------------
st.set_page_config(page_title="Visionary - Career Finder", layout="wide")

# ---------------------------
# Theme Toggle
# ---------------------------
theme = st.sidebar.radio("Select Theme", ["Light", "Dark"])
if theme == "Dark":
    st.markdown(
        """
        <style>
        .reportview-container {background-color: #0E1117; color: white;}
        </style>
        """, unsafe_allow_html=True
    )

# ---------------------------
# Load Dataset
# ---------------------------
df = pd.read_csv("data/visionary_careers_sri_lanka.csv")

# ---------------------------
# Sidebar Instructions
# ---------------------------
st.sidebar.title("About Visionary")
st.sidebar.info(
    """
    Welcome to **Visionary - AI Career Finder**!
    
    - Select your **sector** (optional).  
    - Choose your **skills, interests, and subjects**.  
    - Explore recommended careers below.  
    """
)

# ---------------------------
# Inputs
# ---------------------------
st.title("Explore Your Career Path")
st.subheader("Tell us about yourself:")

sector_options = [""] + sorted(df['Sector'].unique().tolist())
selected_sector = st.selectbox("Select Sector (Optional)", sector_options, index=0)

skills_list = sorted(set([skill.strip() for skills in df['Required_Skills'] for skill in skills.split(",")]))
selected_skills = st.multiselect("Your Skills", skills_list)

interests_list = sorted(df['Interests'].unique())
selected_interests = st.multiselect("Your Interests", interests_list)

subjects_list = sorted(set([sub.strip() for subs in df['Required_Subjects'] for sub in subs.split(",")]))
selected_subjects = st.multiselect("Subjects You Studied", subjects_list)

# ---------------------------
# Filter by Sector (Optional)
# ---------------------------
if selected_sector:
    df_filtered = df[df['Sector'] == selected_sector].copy()
else:
    df_filtered = df.copy()

# ---------------------------
# Scoring Function
# ---------------------------
def calculate_score(row):
    score = 0
    career_skills = [s.strip() for s in row['Required_Skills'].split(",")]
    score += len(set(selected_skills).intersection(career_skills))
    career_subjects = [s.strip() for s in row['Required_Subjects'].split(",")]
    score += len(set(selected_subjects).intersection(career_subjects))
    if row['Interests'] in selected_interests:
        score += 1
    return score

df_filtered['score'] = df_filtered.apply(calculate_score, axis=1)
df_filtered = df_filtered[df_filtered['score'] > 0]
df_filtered = df_filtered.sort_values(by='score', ascending=False)

# ---------------------------
# Gemini API Call
# ---------------------------
API_KEY = "AIzaSyDJXh-XUik1vg3h2qER0D7S0sizAGW8xkc"  # Replace with your actual Gemini API key
GEMINI_ENDPOINT = "https://api.gemini.ai/v1/complete"  # Example endpoint

@st.cache_data
def get_career_description(career_name, sector, skills, interests):
    prompt = f"""
    Give a short, encouraging description of the career "{career_name}" in the "{sector}" sector.
    Highlight top skills: {skills}. Mention why someone with interests in {interests} might enjoy this path.
    Keep it positive and motivational.
    """
    try:
        headers = {"Authorization": f"Bearer {API_KEY}"}
        data = {"prompt": prompt, "max_tokens": 150}
        response = requests.post(GEMINI_ENDPOINT, json=data, headers=headers, timeout=10)
        if response.status_code == 200:
            text = response.json().get("text", "")
            return text.strip()
        else:
            return "Description not available."
    except Exception as e:
        return "Description not available."

# ---------------------------
# Recommendation Display
# ---------------------------
st.subheader("Recommended Careers for You:")

if df_filtered.empty:
    st.info("No matching careers found. Try adjusting your inputs!")
else:
    cols = st.columns(3)
    for idx, (_, row) in enumerate(df_filtered.iterrows()):
        col = cols[idx % 3]

        # Color coding (encouraging)
        if row['score'] >= 5:
            box_color = "#4CAF50"  # green
        elif row['score'] >= 3:
            box_color = "#2196F3"  # blue
        else:
            box_color = "#B0BEC5"  # light gray

        # Get LLM-generated description
        description = get_career_description(row['Career_Name'], row['Sector'], row['Required_Skills'], row['Interests'])
        time.sleep(0.1)  # slight delay to prevent API overload

        col.markdown(
            f"""
            <div style="background-color:{box_color}; padding:15px; border-radius:10px; margin-bottom:10px;">
                <h4 style="margin:0; color:white;">{row['Career_Name']}</h4>
                <p style="margin:0; color:white;"><b>Sector:</b> {row['Sector']}</p>
                <p style="margin:0; color:white;"><b>Top Skills:</b> {row['Required_Skills']}</p>
                <p style="margin-top:5px; color:white;">{description}</p>
            </div>
            """,
            unsafe_allow_html=True
        )
