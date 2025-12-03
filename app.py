import streamlit as st
import pandas as pd
import requests
import time

# ---------------------------
# App Config
# ---------------------------
st.set_page_config(page_title="Visionary - AI Career Finder", layout="wide")

# ---------------------------
# Load Dataset
# ---------------------------
df = pd.read_csv("data/visionary_careers_sri_lanka_real.csv")

# ---------------------------
# Sidebar Info & Theme
# ---------------------------
st.sidebar.title("About Visionary")
st.sidebar.info(
    """
    Welcome to **Visionary - AI Career Finder**!

    - Select **sector** (optional)
    - Type your **skills, interests, subjects**
    - Get **color-coded, AI-enhanced career recommendations**
    """
)

theme_choice = st.sidebar.radio("Select Theme", ["Light", "Dark"])
if theme_choice == "Dark":
    card_bg = "#0E1117"
    card_text = "white"
else:
    card_bg = "#FFFFFF"
    card_text = "black"

# ---------------------------
# User Inputs
# ---------------------------
st.title("Explore Your Career Path")
st.subheader("Tell us about yourself:")

# Sector dropdown (optional)
sector_options = [""] + sorted(df['Sector'].unique().tolist())
selected_sector = st.selectbox("Select Sector (Optional)", sector_options, index=0)

# Free-text inputs
user_skills = st.text_input("Your Skills (comma-separated)")
user_skills_list = [s.strip() for s in user_skills.split(",") if s.strip()]

user_interests = st.text_input("Your Interests (comma-separated)")
user_interests_list = [s.strip() for s in user_interests.split(",") if s.strip()]

user_subjects = st.text_input("Subjects You Studied (comma-separated)")
user_subjects_list = [s.strip() for s in user_subjects.split(",") if s.strip()]

# ---------------------------
# Filter Dataset by Sector (optional)
# ---------------------------
df_filtered = df[df['Sector'] == selected_sector].copy() if selected_sector else df.copy()

# ---------------------------
# Scoring Function
# ---------------------------
def calculate_score(row):
    score = 0
    career_skills = [s.strip() for s in row['Required_Skills'].split(",")]
    score += len(set(user_skills_list).intersection(career_skills))
    career_subjects = [s.strip() for s in row['Required_Subjects'].split(",")]
    score += len(set(user_subjects_list).intersection(career_subjects))
    if row['Interests'] in user_interests_list:
        score += 1
    return score

df_filtered['score'] = df_filtered.apply(calculate_score, axis=1)
df_filtered = df_filtered[df_filtered['score'] > 0]
df_filtered = df_filtered.sort_values(by='score', ascending=False)

# ---------------------------
# Gemini API Integration
# ---------------------------
API_KEY = "YOUR_GEMINI_API_KEY"  # Replace with your key
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
            if text.strip() != "":
                return text.strip()
            else:
                return "This career is promising and matches your interests!"
        else:
            return "This career is promising and matches your interests!"
    except Exception:
        return "This career is promising and matches your interests!"

# ---------------------------
# Display Recommendations
# ---------------------------
st.subheader("Recommended Careers for You:")

if df_filtered.empty:
    st.info("No matching careers found. Try adjusting your inputs!")
else:
    cols = st.columns(3)
    for idx, (_, row) in enumerate(df_filtered.iterrows()):
        col = cols[idx % 3]

        # Color coding
        if row['score'] >= 5:
            box_color = "#4CAF50"  # green
        elif row['score'] >= 3:
            box_color = "#2196F3"  # blue
        else:
            box_color = "#B0BEC5"  # light gray

        # LLM description (safe fallback)
        description = get_career_description(row['Career_Name'], row['Sector'], row['Required_Skills'], row['Interests'])
        time.sleep(0.1)  # small delay

        col.markdown(
            f"""
            <div style="background-color:{box_color}; color:{card_text}; padding:15px; border-radius:10px; margin-bottom:10px;">
                <h4 style="margin:0;">{row['Career_Name']}</h4>
                <p style="margin:0;"><b>Sector:</b> {row['Sector']}</p>
                <p style="margin:0;"><b>Top Skills:</b> {row['Required_Skills']}</p>
                <p style="margin:0;"><b>Education:</b> {row['Education_Level']}</p>
                <p style="margin-top:5px;"><b>Average Salary (LKR):</b> {round(row['Average_Salary_LKR']/1000)*1000}</p>
                <p style="margin-top:5px;">{description}</p>
            </div>
            """,
            unsafe_allow_html=True
        )
