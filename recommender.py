from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def get_dataset_recommendations(df, skills, interests, subjects, sector):
    """
    Returns top 10 careers from the dataset based on cosine similarity.
    """
    user_text = f"{skills} {interests} {subjects}".lower()
    df["combined"] = (df["Required_Skills"].fillna("") + " " +
                      df["Interests"].fillna("") + " " +
                      df["Required_Subjects"].fillna("")).str.lower()
    
    if sector:
        df_filtered = df[df["Sector"].str.lower() == sector.lower()]
    else:
        df_filtered = df.copy()

    tfidf = TfidfVectorizer().fit_transform(df_filtered["combined"])
    user_vec = TfidfVectorizer().fit(df_filtered["combined"]).transform([user_text])
    sim_scores = cosine_similarity(user_vec, tfidf).flatten()
    df_filtered["score"] = sim_scores

    top_recs = df_filtered.sort_values(by="score", ascending=False).head(10)
    return top_recs.to_dict(orient="records")
