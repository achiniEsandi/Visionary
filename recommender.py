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
        user_vec = self.vectorizer.transform([user_text])
        scores = cosine_similarity(user_vec, self.tfidf_matrix).flatten()

        self.careers_df['score'] = scores

        # Filter out zero scores
        filtered = self.careers_df[self.careers_df['score'] > 0]

        # Sort by highest score
        filtered = filtered.sort_values(by="score", ascending=False)

        # Return only top_k nonzero results
        return filtered.head(top_k)

