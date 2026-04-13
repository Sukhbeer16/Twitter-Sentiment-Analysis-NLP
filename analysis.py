import pandas as pd
import numpy as np

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline

import joblib
import re


# ---------------- LOAD DATA ----------------
df = pd.read_csv("twitter.csv")   # your dataset file

# ---------------- CLEANING FUNCTIONS ----------------
def clean_text(text):
    text = str(text).lower()

    # remove URLs
    text = re.sub(r'http\S+|www.\S+', '', text)

    # remove retweets
    text = re.sub(r'\brt\b', '', text)

    # remove special characters
    text = re.sub(r'[^a-z\s]', '', text)

    # remove extra spaces
    text = re.sub(r'\s+', ' ', text).strip()

    return text


# ---------------- APPLY CLEANING ----------------
df['text'] = df['text'].fillna("").apply(clean_text)

# ---------------- FEATURES & LABEL ----------------
X = df['text']
y = df['sentiment']   # Positive / Negative / Neutral

# ---------------- ML PIPELINE ----------------
model = Pipeline([
    ('tfidf', TfidfVectorizer(ngram_range=(1,2), max_features=5000)),
    ('clf', RandomForestClassifier(n_estimators=100, random_state=42))
])

# ---------------- TRAIN MODEL ----------------
model.fit(X, y)

# ---------------- TEST EXAMPLE ----------------
print(model.predict(["I love this product"]))
print(model.predict(["This is the worst experience"]))

# ---------------- SAVE MODEL ----------------
joblib.dump(model, "sentiment_model.pkl")

print("✅ Model trained and saved successfully!")
