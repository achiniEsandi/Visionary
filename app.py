import streamlit as st
import pandas as pd
import os
import json
import re
import time
from dotenv import load_dotenv
from google import genai

# =========================================================
# Page Configuration
# =========================================================
st.set_page_config(
    page_title="Visionary – AI Career Finder",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# Load Environment
# =========================================================
load_dotenv()
GEMINI_API_KEY = ""  # keep empty or set in .env

client = genai.Client(api_key=GEMINI_API_KEY)

# =========================================================
# Load Dataset
# =========================================================
DATA_PATH = "data/visionary_careers_sri_lanka_real.csv"
df = pd.read_csv(DATA_PATH)

# =========================================================
# Sidebar (Controls)
# =========================================================
with st.sidebar:
    st.title("🎯 Visionary")
    st.caption("AI-powered career discovery platform")

    st.divider()
    st.subheader("Your Profile")

    sector = st.selectbox(
        "Preferred Sector (optional)",
        [""] + sorted(df["Sector"].unique())
    )

    skills = st.text_input(
        "Skills",
        placeholder="SQL, Testing, Python"
    )

    interests = st.text_input(
        "Interests",
        placeholder="Quality, Automation, Analysis"
    )

    subjects = st.text_input(
        "Subjects Studied",
        placeholder="IT, Statistics"
    )

    st.divider()
    submit = st.button(
        "✨ Discover My Career Path",
        use_container_width=True
    )

# =========================================================
# Hero Section
# =========================================================
st.markdown("""
<div style="
    padding: 42px 28px;
    border-radius: 24px;
    background: linear-gradient(135deg, #4f46e5, #6366f1);
    color: white;
    margin-bottom: 35px;
">
    <h1 style="margin-bottom:6px;">Visionary</h1>
    <h3 style="font-weight:400; opacity:0.95;">
        AI-Powered Career Discovery
    </h3>
    <p style="margin-top:14px; font-size:16px; opacity:0.9;">
        Turn your skills, interests, and education into a clear career direction.
    </p>
</div>
""", unsafe_allow_html=True)

# =========================================================
# Helper Functions
# =========================================================
def get_ai_recommendation(prompt):
    if not GEMINI_API_KEY:
        return None, "Missing GEMINI_API_KEY"
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        return response.text, None
    except Exception as e:
        return None, str(e)


def extract_json_substring(text):
    patterns = [r"(\[.*\])", r"(\{.*\})"]
    for pat in patterns:
        match = re.search(pat, text, flags=re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except Exception:
                pass
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

# =========================================================
# Main Logic
# =========================================================
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

    with st.spinner("Mapping your profile to future careers..."):
        time.sleep(1.2)
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
        st.info("AI confidence was low — using verified dataset recommendations.")
        recommendations = dataset_recommendations(
            sector, skills, interests, subjects
        )

    # =====================================================
    # Results Section
    # =====================================================
    st.subheader("🎓 Career Matches Tailored for You")

    if not recommendations:
        st.warning("No suitable career paths found for the given inputs.")
    else:
        for rec in recommendations:
            st.markdown(f"""
            <div style="
                padding: 22px;
                border-radius: 18px;
                background-color: rgba(255,255,255,0.04);
                border-left: 6px solid #6366f1;
                margin-bottom: 18px;
                box-shadow: 0 6px 18px rgba(0,0,0,0.08);
            ">
                <h4 style="margin-bottom:6px;">
                    {rec.get("Career Name", "N/A")}
                </h4>
                <span style="
                    font-size: 12px;
                    background-color: #1e293b;
                    padding: 4px 12px;
                    border-radius: 999px;
                ">
                    {rec.get("Sector", "Various")}
                </span>
                <p style="margin-top:12px; opacity:0.9;">
                    {rec.get("Description", "")}
                </p>
            </div>
            """, unsafe_allow_html=True)

    st.success("Career analysis completed successfully.")

# =========================================================
# Footer
# =========================================================
st.markdown("""
<hr>
<p style="text-align:center; font-size:13px; opacity:0.6;">
Visionary • AI-Driven Career Guidance • Sri Lanka Dataset
</p>
""", unsafe_allow_html=True)
