import streamlit as st
import pandas as pd
import os
import json
import re
from dotenv import load_dotenv
from google import genai

# === Load .env for GEMINI_API_KEY ===
load_dotenv()
#GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_API_KEY = ""

# === Init client ===
client = genai.Client(api_key=GEMINI_API_KEY)

# === Load dataset ===
DATA_PATH = "data/visionary_careers_sri_lanka_real.csv"
df = pd.read_csv(DATA_PATH)

# === Streamlit config ===
st.set_page_config(page_title="Visionary - AI Career Finder", layout="wide")

# === Theme toggle ===
theme = st.radio("Select Theme", ["Light", "Dark"])
if theme == "Dark":
    st.markdown(
        """<style>
        .stApp { background-color: #111; color: #eee; }
        .stTextInput input { background-color: #222; color: #eee; }
        </style>""",
        unsafe_allow_html=True,
    )

# === Header ===
st.title("About Visionary")
st.markdown(
    """
Welcome to Visionary - AI Career Finder!  
Optional sector selection  
Type your skills, interests, subjects freely  
AI generates motivational career recommendations  
Dataset scoring used to color-code recommendations
"""
)

# === Inputs ===
st.subheader("Explore Your Career Path")
sector = st.selectbox("Select Sector (Optional)", [""] + sorted(df['Sector'].unique()))
skills = st.text_input("Your Skills (comma-separated)")
interests = st.text_input("Your Interests (comma-separated)")
subjects = st.text_input("Subjects You Studied (comma-separated)")

# === AI call ===
def get_ai_recommendation(prompt):
    """Return (text, error) using genai client"""
    if not GEMINI_API_KEY:
        return None, "Missing GEMINI_API_KEY"

    try:
        resp = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
        return resp.text, None
    except Exception as e:
        return None, f"AI Exception: {str(e)}"

# === Helpers to recover JSON ===
def extract_json_substring(text):
    """
    Try to find a JSON array or object substring in text.
    Returns parsed JSON or None.
    """
    # Try find the first [...] or {...} block that parses
    patterns = [r"(\[.*\])", r"(\{.*\})"]
    for pat in patterns:
        match = re.search(pat, text, flags=re.DOTALL)
        if match:
            candidate = match.group(1)
            try:
                return json.loads(candidate)
            except Exception:
                # try to fix common trailing commas
                candidate_fixed = re.sub(r",\s*([}\]])", r"\1", candidate)
                try:
                    return json.loads(candidate_fixed)
                except Exception:
                    continue
    return None

def parse_loose_list(text):
    """
    Parse a loose newline/bullet list into the expected list of dicts.
    Accepts lines like:
      1. Software QA Engineer - IT - You excel at spotting issues.
      - Software QA Engineer | IT | You excel...
    Returns list or None.
    """
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    items = []
    for ln in lines:
        # remove leading numbering or bullets
        ln = re.sub(r"^\s*[\-\*\d\.\)\:]+\s*", "", ln)
        # split on common separators
        if " - " in ln:
            parts = ln.split(" - ", 2)
        elif " | " in ln:
            parts = ln.split(" | ", 2)
        elif " — " in ln:
            parts = ln.split(" — ", 2)
        else:
            # try splitting by comma but limit to 3 parts
            parts = [p.strip() for p in ln.split(",")[:3]]

        if len(parts) >= 2:
            name = parts[0].strip()
            sector_p = parts[1].strip() if len(parts) >= 2 else "Various"
            desc = parts[2].strip() if len(parts) >= 3 else ""
            items.append({
                "Career Name": name,
                "Sector": sector_p,
                "Description": desc
            })

    return items if items else None

# === Scoring fallback (unchanged) ===
def dataset_recommendations(sector, skills, interests, subjects):
    df_filtered = df.copy()
    if sector:
        df_filtered = df_filtered[df_filtered['Sector'] == sector]

    def score_row(row):
        score = 0
        for sk in [s.strip().lower() for s in skills.split(",") if s.strip()]:
            if sk and sk in str(row.get('Required_Skills', "")).lower():
                score += 1
        for intr in [i.strip().lower() for i in interests.split(",") if i.strip()]:
            if intr and intr in str(row.get('Interests', "")).lower():
                score += 1
        for sub in [s.strip().lower() for s in subjects.split(",") if s.strip()]:
            if sub and sub in str(row.get('Required_Subjects', "")).lower():
                score += 1
        return score

    df_filtered['Score'] = df_filtered.apply(score_row, axis=1)
    df_filtered = df_filtered[df_filtered['Score'] > 0]
    df_filtered = df_filtered.sort_values(by='Score', ascending=False)

    recs = []
    for _, row in df_filtered.iterrows():
        recs.append({
            "Career Name": row['Career_Name'],
            "Sector": row['Sector'],
            "Description": f"Dataset match score: {row['Score']}"
        })
    return recs

# === Main action ===
if st.button("Get Recommendations"):
    prompt = f"""
You are an assistant that MUST respond ONLY in valid JSON (no extra commentary).
Recommend 5 careers for someone with the following profile:
Sector: {sector if sector else 'Any'}
Skills: {skills}
Interests: {interests}
Subjects: {subjects}

Return a JSON array of objects. Each object must have these keys exactly:
- "Career Name": short string
- "Sector": short string
- "Description": one-sentence motivational description

Example valid response:
[
  {{
    "Career Name": "Software QA Engineer",
    "Sector": "IT",
    "Description": "You excel at spotting issues early and ensuring quality."
  }}
]
Do not add any explanation or text outside the JSON.
"""

    with st.spinner("Calling AI..."):
        ai_text, ai_error = get_ai_recommendation(prompt)

    ai_recommendations = []

    if ai_text:
        # 1) Try direct JSON parse
        try:
            parsed = json.loads(ai_text)
            if isinstance(parsed, list):
                ai_recommendations = parsed
            elif isinstance(parsed, dict):
                # single object -> wrap
                ai_recommendations = [parsed]
        except Exception:
            parsed = None

            # 2) Try to extract a JSON substring
            try:
                parsed = extract_json_substring(ai_text)
                if parsed:
                    if isinstance(parsed, list):
                        ai_recommendations = parsed
                    elif isinstance(parsed, dict):
                        ai_recommendations = [parsed]
            except Exception:
                parsed = None

            # 3) Try loose parsing from bullet/newline lists
            if not ai_recommendations:
                try:
                    loose = parse_loose_list(ai_text)
                    if loose:
                        ai_recommendations = loose
                except Exception:
                    pass

        # If we recovered something but items are missing keys, try to normalize
        normalized = []
        for item in ai_recommendations:
            if not isinstance(item, dict):
                continue
            name = item.get("Career Name") or item.get("career") or item.get("title") or item.get("name")
            sector_p = item.get("Sector") or item.get("sector") or "Various"
            desc = item.get("Description") or item.get("description") or item.get("desc") or ""
            if name:
                normalized.append({
                    "Career Name": str(name).strip(),
                    "Sector": str(sector_p).strip(),
                    "Description": str(desc).strip()
                })
        ai_recommendations = normalized

        # If still empty, warn user
        if not ai_recommendations:
            st.warning("AI returned content but we couldn't parse valid recommendations from it. Showing dataset recommendations instead.")
            st.info("AI raw output (truncated):")
            st.code(ai_text[:1000])
    else:
        if ai_error:
            st.warning(f"AI generation failed: {ai_error}")
        else:
            st.warning("No AI response received.")

    # === Final fallback to dataset ===
    if not ai_recommendations:
        ai_recommendations = dataset_recommendations(sector, skills, interests, subjects)
        if not ai_recommendations:
            st.info("No dataset matches found for the provided inputs.")

    # === Display Recommendations ===
    st.subheader("Recommended Careers for You:")
    for rec in ai_recommendations:
        career = rec.get("Career Name", "N/A")
        sector_rec = rec.get("Sector", "Various")
        desc = rec.get("Description", "")
        st.markdown(f"**{career}**  \nSector: {sector_rec}  \n{desc}")
