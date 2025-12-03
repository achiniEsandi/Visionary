# recommender.py
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
import numpy as np

class CareerRecommender:
    def __init__(self, careers_csv='data/careers.csv'):
        self.df = pd.read_csv(careers_csv)
        # create a text field
        self.df['text_blob'] = (self.df['title'].fillna('') + ' . ' +
                                self.df['description'].fillna('') + ' . ' +
                                self.df['skills'].fillna(''))
        self.vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1,2))
        self.tfidf_matrix = self.vectorizer.fit_transform(self.df['text_blob'])

    def recommend(self, user_text, top_k=5):
        """
        user_text: string of user's interests/skills/CV summary
        returns DataFrame of top_k careers with scores
        """
        user_vec = self.vectorizer.transform([user_text])
        cosine_similarities = linear_kernel(user_vec, self.tfidf_matrix).flatten()
        top_idx = np.argsort(-cosine_similarities)[:top_k]
        results = self.df.iloc[top_idx].copy()
        results['score'] = cosine_similarities[top_idx]
        return results.reset_index(drop=True)
