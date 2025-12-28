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
# Global UI Styling with new background
# =========================================================
st.markdown("""
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

.stApp {
    background: linear-gradient(135deg, #8ec5fc 0%, #e0c3fc 100%);
    color: #1e293b;
}

section[data-testid="stSidebar"] {
    background: linear-gradient(135deg, #a78bfa, #818cf8);
    color: #f8fafc;
    border-right: 1px solid #6366f1;
}


input, textarea, select {
    border-radius: 12px !important;
}

button[kind="primary"] {
    background: linear-gradient(135deg, #6366f1, #4f46e5);
    border-radius: 14px;
    height: 48px;
    font-weight: 600;
}

h1, h2, h3 {
    letter-spacing: -0.02em;
}
</style>
""", unsafe_allow_html=True)

# =========================================================
# Load Environment
# =========================================================
load_dotenv()
GEMINI_API_KEY = ""
client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None

# =========================================================
# Load Dataset
# =========================================================
DATA_PATH = "data/visionary_careers_sri_lanka_real.csv"
df = pd.read_csv(DATA_PATH)

# =========================================================
# Sidebar
# =========================================================
with st.sidebar:
    st.title("🎯 Visionary")
    st.caption("AI-powered career discovery")

    st.divider()
    st.subheader("👤 Your Profile")

    sector = st.selectbox(
        "Preferred Sector",
        ["Any"] + sorted(df["Sector"].dropna().unique())
    )

    skills = st.text_input(
        "🛠 Skills",
        placeholder="SQL, Manual Testing, Python"
    )

    interests = st.text_input(
        "💡 Interests",
        placeholder="Automation, Quality, Analysis"
    )

    subjects = st.text_input(
        "📘 Subjects Studied",
        placeholder="IT, Statistics"
    )

    st.divider()
    submit = st.button(
        "✨ Discover My Career Path",
        use_container_width=True
    )

    st.caption("💡 Tip: Add at least 2 skills for better results")

# =========================================================
# Hero Section
# =========================================================
st.markdown("""
<div style="
    padding: 50px 36px;
    border-radius: 28px;
    background: linear-gradient(135deg, #6366f1, #4338ca);
    color: white;
    margin-bottom: 40px;
    box-shadow: 0 20px 40px rgba(99,102,241,0.25);
">
    <h1 style="margin-bottom:10px; font-size:48px;">
        Visionary 🎯
    </h1>
    <h3 style="font-weight:400; opacity:0.95;">
        AI-Powered Career Discovery Platform
    </h3>
    <p style="margin-top:16px; font-size:17px; opacity:0.9; max-width:720px;">
        Turn your skills, interests, and education into a clear career direction —
        powered by AI and real Sri Lankan job market data.
    </p>
</div>
""", unsafe_allow_html=True)

# =========================================================
# Helper Functions
# =========================================================
def get_ai_recommendation(prompt):
    if not client:
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
    if sector != "Any":
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
            "Description": f"Matched {row['Score']} profile attributes from dataset"
        }
        for _, row in df_filtered.iterrows()
    ]

def clean_text(text):
    """Remove any HTML tags from AI-generated text"""
    return re.sub(r"<[^>]*>", "", text)

# =========================================================
# Main Logic
# =========================================================
if submit:
    prompt = f"""
Respond ONLY in valid JSON.
DO NOT use HTML or markdown.

Recommend 10 careers for:

Sector: {sector}
Skills: {skills}
Interests: {interests}
Subjects: {subjects}

Return JSON array with:
- Career Name
- Sector
- Description (plain text only)
"""

    with st.spinner("🔍 Mapping your profile to careers..."):
        time.sleep(1)
        ai_text, ai_error = get_ai_recommendation(prompt)

    recommendations = []

    # Parse AI output safely
    if ai_text:
        try:
            recommendations = json.loads(ai_text)
        except Exception:
            parsed = extract_json_substring(ai_text) or parse_loose_list(ai_text)
            if parsed:
                recommendations = parsed

    # Dataset fallback
    if not recommendations:
        st.info("🤖 AI confidence low. Showing dataset recommendations.")
        recommendations = dataset_recommendations(sector, skills, interests, subjects)

    # Clean all descriptions and ensure dicts
    cleaned_recs = []
    for r in recommendations:
        if isinstance(r, dict):
            r["Description"] = clean_text(r.get("Description", ""))
            cleaned_recs.append(r)
        elif isinstance(r, str):
            parsed = parse_loose_list(r)
            if parsed:
                for p in parsed:
                    p["Description"] = clean_text(p.get("Description", ""))
                cleaned_recs.extend(parsed)

    # =========================================================
    # Render Results (User View: HTML safe)
    # =========================================================
    st.subheader("🎓 Career Matches Tailored for You")

    if not cleaned_recs:
        st.warning("No suitable career paths found. Try adding more skills or interests.")
    else:
        for rec in cleaned_recs:
            title = rec.get("Career Name", "N/A")
            sector_label = rec.get("Sector", "Various")
            description = rec.get("Description", "")

            # Render modern card safely
            st.markdown(f"""
            <div style="
                padding: 28px;
                border-radius: 24px;
                background: #ffffff90;
                border-left: 6px solid #6366f1;
                box-shadow: 0 8px 20px rgba(0,0,0,0.12);
                margin-bottom: 24px;
                color:#1e293b;
            ">
                <h3 style="margin-bottom:10px;">{title}</h3>
                <div style="
                    display:inline-block;
                    font-size: 12px;
                    background: #6366f1;
                    color: #f8fafc;
                    padding: 6px 14px;
                    border-radius: 999px;
                    margin-bottom: 12px;
                ">{sector_label}</div>
                <p style="margin-top:14px; line-height:1.6;">
                    {description}
                </p>
            </div>
            """, unsafe_allow_html=True)

    st.success("✅ Career analysis completed successfully!")

# =========================================================
# Footer
# =========================================================
st.markdown("""
<hr style="border-color:#d1d5db;">
<p style="text-align:center; font-size:13px; opacity:0.6;">
Visionary • AI-Driven Career Guidance • Built for Sri Lanka 🇱🇰
</p>
""", unsafe_allow_html=True)
