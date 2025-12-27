import streamlit as st
import pandas as pd
import os
import json
import re
from dotenv import load_dotenv
from google import genai

# =========================
# App Config
# =========================
st.set_page_config(
    page_title="Visionary – AI Career Finder",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================
# Load Environment
# =========================
load_dotenv()
GEMINI_API_KEY = ""  # keep as-is

client = genai.Client(api_key=GEMINI_API_KEY)

# =========================
# Load Dataset
# =========================
DATA_PATH = "data/visionary_careers_sri_lanka_real.csv"
df = pd.read_csv(DATA_PATH)

# =========================
# Sidebar
# =========================
with st.sidebar:
    st.title("🎯 Visionary")
    st.caption("AI-powered career guidance")

    theme = st.radio("Theme", ["Light", "Dark"], horizontal=True)

    st.divider()
    st.subheader("Your Profile")

    sector = st.selectbox(
        "Preferred Sector (optional)",
        [""] + sorted(df["Sector"].unique())
    )

    skills = st.text_input("Skills", placeholder="SQL, Testing, Python")
    interests = st.text_input("Interests", placeholder="Quality, Automation, Analysis")
    subjects = st.text_input("Subjects Studied", placeholder="IT, Statistics")

    submit = st.button("🚀 Get Recommendations", use_container_width=True)

# =========================
# Theme Styling
# =========================
if theme == "Dark":
    st.markdown(
        """
        <style>
        .stApp {
            background-color: #0f172a;
            color: #e5e7eb;
        }
        div[data-testid="stMetric"] {
            background-color: #020617;
            padding: 12px;
            border-radius: 10px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

# =========================
# Header
# =========================
st.title("Discover Your Career Path")
st.caption(
    "Tell us about your skills and interests — Visionary will guide you towards careers that fit you best."
)

st.divider()

# =========================
# AI Call
# =========================
def get_ai_recommendation(prompt):
    if not GEMINI_API_KEY:
        return None, "Missing GEMINI_API_KEY"
    try:
        resp = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        return resp.text, None
    except Exception as e:
        return None, str(e)

# =========================
# Helpers
# =========================
def extract_json_substring(text):
    patterns = [r"(\[.*\])", r"(\{.*\})"]
    for pat in patterns:
        match = re.search(pat, text, flags=re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except Exception:
                continue
    return None

def parse_loose_list(text):
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    items = []
    for ln in lines:
        ln = re.sub(r"^[\-\*\d\.\)\:]+\s*", "", ln)
        parts = re.split(r"\s[-|—]\s", ln, maxsplit=2)
        if len(parts) >= 2:
            items.append({
                "Career Name": parts[0],
                "Sector": parts[1],
                "Description": parts[2] if len(parts) > 2 else ""
            })
    return items if items else None

# =========================
# Dataset Fallback
# =========================
def dataset_recommendations(sector, skills, interests, subjects):
    df_filtered = df.copy()
    if sector:
        df_filtered = df_filtered[df_filtered["Sector"] == sector]

    def score_row(row):
        score = 0
        for val, col in [
            (skills, "Required_Skills"),
            (interests, "Interests"),
            (subjects, "Required_Subjects")
        ]:
            for token in [v.strip().lower() for v in val.split(",") if v.strip()]:
                if token in str(row.get(col, "")).lower():
                    score += 1
        return score

    df_filtered["Score"] = df_filtered.apply(score_row, axis=1)
    df_filtered = df_filtered[df_filtered["Score"] > 0]
    df_filtered = df_filtered.sort_values("Score", ascending=False)

    return [
        {
            "Career Name": row["Career_Name"],
            "Sector": row["Sector"],
            "Description": f"Dataset match score: {row['Score']}"
        }
        for _, row in df_filtered.iterrows()
    ]

# =========================
# Main Action
# =========================
if submit:
    prompt = f"""
Respond ONLY in valid JSON.
Recommend 5 careers for:
Sector: {sector or "Any"}
Skills: {skills}
Interests: {interests}
Subjects: {subjects}

Return JSON array with:
- Career Name
- Sector
- Description
"""

    with st.spinner("Analyzing your profile..."):
        ai_text, ai_error = get_ai_recommendation(prompt)

    recommendations = []

    if ai_text:
        try:
            recommendations = json.loads(ai_text)
        except Exception:
            parsed = extract_json_substring(ai_text) or parse_loose_list(ai_text)
            if parsed:
                recommendations = parsed

    if not recommendations:
        st.info("Using dataset-based recommendations.")
        recommendations = dataset_recommendations(sector, skills, interests, subjects)

    # =========================
    # Display Results
    # =========================
    st.subheader("🎓 Recommended Careers")

    if not recommendations:
        st.warning("No suitable careers found for the given inputs.")
    else:
        for rec in recommendations:
            st.markdown(
                f"""
                <div style="
                    padding: 18px;
                    margin-bottom: 14px;
                    border-radius: 14px;
                    background-color: rgba(255,255,255,0.04);
                    box-shadow: 0 6px 14px rgba(0,0,0,0.08);
                ">
                    <h4>{rec.get("Career Name", "N/A")}</h4>
                    <p><strong>Sector:</strong> {rec.get("Sector", "Various")}</p>
                    <p>{rec.get("Description", "")}</p>
                </div>
                """,
                unsafe_allow_html=True
            )
