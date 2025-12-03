# app.py
import streamlit as st
from recommender import CareerRecommender
from llm_wrapper import generate_explanation
from utils import extract_text_from_pdf, summarize_cv_text
import pandas as pd
from io import StringIO

st.set_page_config(page_title="Visionary — Career Path Finder", layout="wide")

@st.cache_resource
def load_recommender():
    return CareerRecommender('data/careers.csv')

recommender = load_recommender()

st.title("Visionary — AI Career Path Finder (Streamlit)")

menu = st.sidebar.selectbox("Page", ["Home", "Upload CV", "Questionnaire", "Recommendations", "Admin"])

if menu == "Home":
    st.write("""
    Welcome — try uploading your CV or answer a short questionnaire.
    The system will suggest career paths and learning resources.
    """)
    st.info("Set LLM_PROVIDER and LLM_API_KEY in your environment to enable explanations.")

if menu == "Upload CV":
    uploaded_file = st.file_uploader("Upload your CV (pdf or txt)", type=['pdf','txt'])
    if uploaded_file:
        if uploaded_file.type == 'application/pdf':
            with open("tmp_cv.pdf", "wb") as f:
                f.write(uploaded_file.getbuffer())
            cv_text = extract_text_from_pdf("tmp_cv.pdf")
        else:
            s = StringIO(uploaded_file.getvalue().decode("utf-8"))
            cv_text = s.read()
        st.subheader("Extracted CV text (preview):")
        st.write(summarize_cv_text(cv_text, max_len=1500))
        st.session_state['user_text'] = cv_text

if menu == "Questionnaire":
    st.header("Tell us about yourself")
    skills = st.text_input("Key skills (comma separated)", "")
    interests = st.text_input("Interests (e.g., ML, frontend, security)", "")
    experience = st.text_area("Brief experience / summary", "")
    if st.button("Save inputs"):
        combined = f"Skills: {skills}. Interests: {interests}. Summary: {experience}"
        st.session_state['user_text'] = combined
        st.success("Saved! Go to Recommendations.")

if menu == "Recommendations":
    st.header("Recommendations")
    user_text = st.session_state.get('user_text', '')
    if not user_text:
        st.warning("No input found. Upload a CV or fill the questionnaire.")
    else:
        top_k = st.slider("Number of suggestions", min_value=1, max_value=10, value=5)
        with st.spinner("Generating recommendations..."):
            recs = recommender.recommend(user_text, top_k=top_k)
        st.write("### Top matches")
        for idx, row in recs.iterrows():
            st.subheader(f"{row['title']}  —  score: {row['score']:.3f}")
            st.write(f"**Skills:** {row.get('skills','')}")
            st.write(f"**Education:** {row.get('education','')}")
            # generate LLM explanation for each
            prompt = (f"User profile: {user_text}\n\nCareer: {row['title']}\nDescription: {row['description']}\n"
                      f"Why is this a good match and what learning path should the user take? Provide 4 concise steps.")
            explanation = generate_explanation(prompt)
            st.markdown(f"**Suggested path / explanation:**\n\n{explanation}")
        # allow download of recommendations as CSV
        csv = recs.to_csv(index=False)
        st.download_button("Download recommendations CSV", csv, file_name="recommendations.csv", mime="text/csv")

if menu == "Admin":
    st.header("Admin: Upload/Preview careers dataset")
    uploaded = st.file_uploader("Upload careers CSV", type=['csv'])
    if uploaded:
        df = pd.read_csv(uploaded)
        st.write(df.head())
        # overwrite local file (optional)
        if st.button("Save to data/careers.csv"):
            df.to_csv("data/careers.csv", index=False)
            st.success("Saved. Reloading recommender...")
            # clear cache
            st.cache_resource.clear()
            st.experimental_rerun()
